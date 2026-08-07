import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import json
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد الصفحة
st.set_page_config(
    page_title="منصة أطلس التحليل اللساني",
    page_icon="🗺️",
    layout="wide"
)

# دالة معالجة النصوص العربية للعرض الصحيح في Matplotlib
def fix_text(text):
    if isinstance(text, str):
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    return text

st.title("🗺️ منصة أطلس التحليل اللساني والجغرافي")
st.markdown("---")

# القائمة الجانبية - إدخال البيانات والإعدادات
st.sidebar.header("⚙️ إعدادات البيانات والتحليل")

input_option = st.sidebar.radio(
    "طريقة إدخال البيانات:",
    ["استمارة إدخال مباشرة ✍️", "رفع ملف Excel/CSV 📁"]
)

df = None

if input_option == "رفع ملف Excel/CSV 📁":
    uploaded_file = st.sidebar.file_uploader("قم برفع ملف البيانات (CSV/XLSX):", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.sidebar.success("تم تحميل الملف بنجاح! ✅")
        except Exception as e:
            st.sidebar.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
    # بيانات افتراضية توضيحية
    default_data = {
        'Village': ['Boulemane', 'Guigou', 'Timahdite', 'El_Mers', 'Skoura_MDaz', 'Serghina', 'Outat_El_Haj'],
        'Latitude': [33.36, 33.43, 33.23, 33.47, 33.64, 33.31, 33.67],
        'Longitude': [-4.73, -5.03, -5.06, -4.45, -4.56, -4.41, -3.70],
        'Variable_1': [1, 1, 1, 0, 0, 0, 0],
        'Variable_2': [1, 1, 0, 1, 1, 0, 0],
        'Variable_3': [0, 1, 1, 0, 1, 1, 0],
        'Variable_4': [1, 0, 1, 1, 0, 1, 1]
    }
    df = pd.DataFrame(default_data)
    st.sidebar.info("تتم معالجة النموذج بالبيانات التوضيحية الافتراضية 💡")

# تحميل ملف الحدود الجغرافية GeoJSON إذا كان موجوداً
geojson_data = None
try:
    with open("boundaries.geojson", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
except Exception:
    geojson_data = None

if df is not None:
    # اختيار الأعمدة
    st.sidebar.subheader("🎯 أعمدة التحليل")
    columns = df.columns.tolist()
    
    location_col = st.sidebar.selectbox("عمود المواقع/القبائل:", columns, index=0 if 'Village' in columns else 0)
    lat_col = st.sidebar.selectbox("عمود الخطوط العريضة (Latitude):", columns, index=columns.index('Latitude') if 'Latitude' in columns else 0)
    lon_col = st.sidebar.selectbox("عمود خطوط الطول (Longitude):", columns, index=columns.index('Longitude') if 'Longitude' in columns else 0)
    
    # تحديد المتغيرات اللسانية (الأعمدة الثنائية/الملاحظات)
    feature_cols = [c for c in columns if c not in [location_col, lat_col, lon_col]]
    selected_features = st.sidebar.multiselect("اختر المتغيرات اللسانية للتحليل:", feature_cols, default=feature_cols)

    # التبويبات الرئيسية للمنصة
    tab1, tab2, tab3 = st.tabs(["🗺️ خريطة أطلس الفضائية والحدود", "🌳 التحليل العنقودي والشجرة اللهجية", "📊 مصفوفة المسافات اللسانية"])

    # 1. التبويب الأول: الخريطة
    with tab1:
        st.subheader("🗺️ خريطة أطلس الفضائية مع حدود الجماعات والإقليم")
        
        # حساب مركز الخريطة
        avg_lat = df[lat_col].mean()
        avg_lon = df[lon_col].mean()
        
        # إنشاء الخريطة باستخدام Google Satellite
        m = folium.Map(
            location=[avg_lat, avg_lon],
            zoom_start=9,
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google Satellite'
        )
        
        # إضافة ملف الحدود GeoJSON إذا توفر
        if geojson_data:
            folium.GeoJson(
                geojson_data,
                name="حدود الجماعات والأقاليم",
                style_function=lambda x: {
                    'fillColor': '#f1c40f',
                    'color': '#f39c12',
                    'weight': 1.2,
                    'fillOpacity': 0.15
                }
            ).add_to(m)

        # إضافة النقاط/المواقع
        for _, row in df.iterrows():
            folium.Marker(
                location=[row[lat_col], row[lon_col]],
                popup=f"<b>{row[location_col]}</b>",
                tooltip=str(row[location_col]),
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)

        folium.LayerControl().add_to(m)
        st_folium(m, width=1000, height=600)

    # حساب مصفوفة المسافات اللسانية (Jaccard Distance)
    if selected_features:
        data_matrix = df[selected_features].values
        # حساب المسافة بناءً على مقياس Jaccard
        dist_matrix = squareform(pdist(data_matrix, metric='jaccard'))
        locations = df[location_col].tolist()

        # 2. التبويب الثاني: الشجرة اللهجية الأفقية الأكاديمية
        with tab2:
            st.subheader("🌳 التحليل العنقودي والشجرة اللهجية (Dendrogram)")
            st.markdown("تصنيف المواقع اللهجية بناءً على مصفوفة البعد اللساني:")
            
            # 1. إعداد المسافات والربط العنقودي
            condensed_dist = squareform(dist_matrix)
            Z = linkage(condensed_dist, method='ward')
            fixed_labels = [fix_text(loc) for loc in locations]
            
            # 2. تحديد ارتفاع الشكل بحسب عدد المواقع لضمان عدم تداخل الأسماء
            fig_height = max(5, len(locations) * 0.45)
            fig, ax = plt.subplots(figsize=(10, fig_height))
            
            # 3. رسم الشجرة بصورة أفقية ملونة احترافية
            ddata = dendrogram(
                Z, 
                labels=fixed_labels, 
                orientation='left',            # اتجاه أفقي كما في الأبحاث والمجلات العلميّة
                color_threshold=0.7 * max(Z[:, 2]), # تلوين الفروع المتميزة تلقائياً
                above_threshold_color='#2c3e50',
                ax=ax,
                leaf_font_size=11
            )
            
            # 4. تحسين مظهر المحاور والخطوط
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_color('#7f8c8d')
            
            ax.xaxis.grid(True, linestyle='--', alpha=0.5, color='#cccccc')
            ax.set_xlabel("مسافة التباعد اللساني (Linguistic Distance)", fontsize=11, fontweight='bold', labelpad=10)
            
            plt.tight_layout()
            st.pyplot(fig)

        # 3. التبويب الثالث: مصفوفة المسافات
        with tab3:
            st.subheader("📊 مصفوفة المسافات اللسانية (Distance Matrix)")
            dist_df = pd.DataFrame(dist_matrix, index=locations, columns=locations)
            st.dataframe(dist_df.style.background_gradient(cmap="Blues"))

else:
    st.warning("يرجى تحميل ملف البيانات لبدء التحليل.")
