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

# دالة التحليل متعدد الأبعاد (Classical MDS / PCoA)
def run_mds(dist_matrix, n_components=2):
    n = dist_matrix.shape[0]
    H = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * H.dot(dist_matrix ** 2).dot(H)
    evals, evecs = np.linalg.eigh(B)
    idx = np.argsort(evals)[::-1]
    evals = evals[idx]
    evecs = evecs[:, idx]
    evals_pos = np.maximum(evals[:n_components], 0)
    coords = evecs[:, :n_components] * np.sqrt(evals_pos)
    return coords

st.title("🗺️ منصة أطلس التحليل اللساني والجغرافي المتكامل")
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
        'المتغير_1_الجهر': [1, 1, 1, 0, 0, 0, 0],
        'المتغير_2_الإمالة': [1, 1, 0, 1, 1, 0, 0],
        'المتغير_3_التفخيم': [0, 1, 1, 0, 1, 1, 0],
        'المتغير_4_الاستعلاء': [1, 0, 1, 1, 0, 1, 1]
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
    
    # تحديد المتغيرات اللسانية
    feature_cols = [c for c in columns if c not in [location_col, lat_col, lon_col]]
    selected_features = st.sidebar.multiselect("اختر المتغيرات اللسانية للتحليل:", feature_cols, default=feature_cols)

    # ---------------------------------------------------------
    # التبويبات الرئيسية لكافة مراحل التحليل
    # ---------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🗺️ الخريطة والحدود", 
        "🌳 الشجرة اللهجية", 
        "📍 التحليل متعدد الأبعاد (MDS)", 
        "📊 مصفوفة المسافات والتشابه", 
        "🎨 خرائط التوزيع الظواهري", 
        "📈 الإحصائيات والمؤشرات"
    ])

    # 1. المرحلة الأولى: الخريطة الفضائية والحدود
    with tab1:
        st.subheader("🗺️ خريطة أطلس الفضائية مع حدود الجماعات والإقليم")
        avg_lat, avg_lon = df[lat_col].mean(), df[lon_col].mean()
        
        m = folium.Map(
            location=[avg_lat, avg_lon],
            zoom_start=9,
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google Satellite'
        )
        
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

        for _, row in df.iterrows():
            folium.Marker(
                location=[row[lat_col], row[lon_col]],
                popup=f"<b>{row[location_col]}</b>",
                tooltip=str(row[location_col]),
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)

        folium.LayerControl().add_to(m)
        st_folium(m, width=1000, height=550)

    # إجراء الحسابات اللسانية إذا تم تحديد متغيّرات
    if selected_features:
        data_matrix = df[selected_features].values
        dist_matrix = squareform(pdist(data_matrix, metric='jaccard'))
        similarity_matrix = 1 - dist_matrix
        locations = df[location_col].tolist()

        # 2. المرحلة الثانية: الشجرة اللهجية
        with tab2:
            st.subheader("🌳 التحليل العنقودي والشجرة اللهجية (Dendrogram)")
            st.markdown("تصنيف المواقع اللهجية بناءً على خوارزمية Ward للتجمّع الهرمي:")
            
            condensed_dist = squareform(dist_matrix)
            Z = linkage(condensed_dist, method='ward')
            fixed_labels = [fix_text(loc) for loc in locations]
            
            fig_height = max(5, len(locations) * 0.45)
            fig, ax = plt.subplots(figsize=(10, fig_height))
            
            dendrogram(
                Z, 
                labels=fixed_labels, 
                orientation='left', 
                color_threshold=0.7 * max(Z[:, 2]), 
                above_threshold_color='#2c3e50',
                ax=ax,
                leaf_font_size=11
            )
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_color('#7f8c8d')
            ax.xaxis.grid(True, linestyle='--', alpha=0.5, color='#cccccc')
            ax.set_xlabel("مسافة التباعد اللساني (Linguistic Distance)", fontsize=11, fontweight='bold', labelpad=10)
            
            plt.tight_layout()
            st.pyplot(fig)

        # 3. المرحلة الثالثة: التحليل متعدد الأبعاد (MDS)
        with tab3:
            st.subheader("📍 التحليل متعدد الأبعاد (Multidimensional Scaling - MDS)")
            st.markdown("تمثيل التقارب والتباعد اللساني في فضاء ثنائي الأبعاد:")
            
            coords = run_mds(dist_matrix, n_components=2)
            
            fig_mds, ax_mds = plt.subplots(figsize=(9, 6))
            ax_mds.scatter(coords[:, 0], coords[:, 1], color='#e74c3c', s=120, edgecolors='black', zorder=3)
            
            for i, loc in enumerate(locations):
                ax_mds.annotate(
                    fix_text(loc), 
                    (coords[i, 0], coords[i, 1]), 
                    xytext=(8, 5), 
                    textcoords='offset points',
                    fontsize=10, 
                    fontweight='bold'
                )
                
            ax_mds.grid(True, linestyle=':', alpha=0.6)
            ax_mds.set_title("توزيع المواقع اللهجية حسب درجة التقارب اللساني", fontsize=12, fontweight='bold')
            ax_mds.set_xlabel("البعد الأول (Dimension 1)", fontsize=10)
            ax_mds.set_ylabel("البعد الثاني (Dimension 2)", fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig_mds)

        # 4. المرحلة الرابعة: مصفوفات المسافات والتشابه
        with tab4:
            st.subheader("📊 مصفوفات التباعد والتشابه اللساني")
            
            mat_type = st.radio("اختر نوع المصفوفة المطلوبة:", ["مصفوفة المسافات (Distance Matrix)", "مصفوفة التشابه (Similarity Matrix)"], horizontal=True)
            
            if "المسافات" in mat_type:
                disp_df = pd.DataFrame(dist_matrix, index=locations, columns=locations)
                st.dataframe(disp_df.style.background_gradient(cmap="Blues"))
            else:
                disp_df = pd.DataFrame(similarity_matrix, index=locations, columns=locations)
                st.dataframe(disp_df.style.background_gradient(cmap="YlGn"))

        # 5. المرحلة الخامسة: خرائط التوزيع الجغرافي لكل ظاهرة
        with tab5:
            st.subheader("🎨 خرائط التوزيع الجغرافي للظواهر اللسانية (Isogloss Maps)")
            
            selected_feat = st.selectbox("اختر الظاهرة اللسانية للتحليل التوزيعي:", selected_features)
            
            m_feat = folium.Map(
                location=[avg_lat, avg_lon],
                zoom_start=9,
                tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                attr='Google Satellite'
            )
            
            if geojson_data:
                folium.GeoJson(geojson_data, style_function=lambda x: {'fillColor': '#ffffff', 'color': '#aaaaaa', 'weight': 1, 'fillOpacity': 0.1}).add_to(m_feat)

            for _, row in df.iterrows():
                val = row[selected_feat]
                color = "green" if val == 1 else "orange"
                
                folium.CircleMarker(
                    location=[row[lat_col], row[lon_col]],
                    radius=9,
                    popup=f"<b>{row[location_col]}</b><br>{selected_feat}: {val}",
                    color="white",
                    weight=1.5,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.9
                ).add_to(m_feat)

            st_folium(m_feat, width=1000, height=500)

        # 6. المرحلة السادسة: الإحصائيات والمؤشرات القياسية
        with tab6:
            st.subheader("📈 الإحصائيات والمؤشرات القياسية (Dialectometric Indices)")
            
            mean_dist = np.mean(dist_matrix, axis=1)
            stats_df = pd.DataFrame({
                "الموقع/القبيلة": locations,
                "متوسط التباعد اللساني": np.round(mean_dist, 3),
                "متوسط درجة التشابه": np.round(1 - mean_dist, 3)
            }).sort_values(by="متوسط درجة التشابه", ascending=False)
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.write("#### 🏆 ترتيب المواقع حسب أعلى نسبة تشابه مع بقية Atlas:")
                st.dataframe(stats_df, hide_index=True)
            
            with col_b:
                fig_bar, ax_bar = plt.subplots(figsize=(6, 4.5))
                ax_bar.barh([fix_text(l) for l in stats_df["الموقع/القبيلة"]], stats_df["متوسط درجة التشابه"], color="#2ecc71")
                ax_bar.set_xlabel("مؤشر التشابه العام")
                ax_bar.set_title("مؤشر التشابه اللساني لكل موقع", fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig_bar)

else:
    st.warning("يرجى تحميل ملف البيانات لبدء التحليل.")
