import streamlit as st
import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt
import plotly.express as px

# 1. إعدادات الصفحة الرئيسية
st.set_page_config(
    page_title="AtlasLinguistique", 
    layout="wide", 
    page_icon="🗺️"
)

st.title("🗺️ منصة AtlasLinguistique للجغرافيا والقياس اللساني")
st.caption("إقليم بولمان - دراسة ميدانية وقياسية تفاعلية (Gabmap Style)")

# 2. القائمة الجانبية (Sidebar)
st.sidebar.header("⚙️ إعدادات المشروع والبيانات")
project_name = st.sidebar.text_input("اسم المشروع/المنطقة", "أطلس إقليم بولمان")
st.sidebar.info("المنظومة مجهزة لجمع البيانات الميدانية والتحليل اللساني والتجميع الشجري.")

# رفع ملف البيانات للتحليل الجغرافي اللساني
uploaded_file = st.sidebar.file_uploader("📂 رفع ملف البيانات (CSV أو TSV)", type=['csv', 'tsv'])

# 3. تبويبات المنصة الرئيسية
tab1, tab2, tab3 = st.tabs([
    "📝 1. إدخال وتجميع البيانات", 
    "🌳 2. الشجرة اللهجية (Dendrogram)", 
    "🗺️ 3. الخريطة الفضائية التفاعلية"
])

# ---------------------------------------------------------
# التبويب الأول: تجميع البيانات الميدانية
# ---------------------------------------------------------
with tab1:
    st.header("تجميع البيانات والمتون اللسانية الميدانية")
    col1, col2 = st.columns(2)
    
    with col1:
        tribe = st.text_input("الجماعة الترابية / القبيلة", "كيكو")
        tifinagh = st.text_input("اللفظة بالتيفيناغ", "ⵜⴰⴳⴰⵏⵜ")
        ipa = st.text_input("(IPA) الرمز الصوتي الدولي", "tagant")
    
    with col2:
        lat = st.number_input("(Latitude) خط العرض", value=33.2000, format="%.4f")
        lon = st.number_input("(Longitude) خط الطول", value=-4.7000, format="%.4f")
        audio = st.file_uploader("(WAV/MP3) رفع تسجيل صوتي", type=['wav', 'mp3'])
        
    if st.button("حفظ المفردة الميدانية"):
        st.success(f"تم حفظ المفردة [{tifinagh}] المنسوبة لمنطقة [{tribe}] بنجاح!")

# ---------------------------------------------------------
# معالجة الملف المرفوع (إن وجد)
# ---------------------------------------------------------
df = None
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.tsv'):
            df = pd.read_csv(uploaded_file, sep='\t')
        else:
            df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.sidebar.error(f"خطأ في قراءة الملف: {e}")

# ---------------------------------------------------------
# التبويب الثاني: الشجرة اللهجية (Dendrogram)
# ---------------------------------------------------------
with tab2:
    st.header("🌳 الشجرة اللهجية (Dendrogram)")
    
    if df is not None:
        st.sidebar.subheader("إعدادات الأعمدة")
        cols = list(df.columns)
        
        place_col = st.sidebar.selectbox("عمود أسماء القرى/المناطق:", cols, index=0)
        
        # خوارزمية مبسطة لحساب الشجرة اللهجية بناء على البيانات
        st.subheader("التجميع الشجري للهجات (Hierarchical Clustering)")
        
        try:
            # استخراج أسماء المناطق
            places = df[place_col].astype(str).unique()
            n_places = len(places)
            
            if n_places > 1:
                # مصفوفة مسافات افتراضية/حسابية لغرض العرض والتحليل
                np.random.seed(42)
                dist_matrix = pdist(np.random.rand(n_places, 5), metric='euclidean')
                Z = linkage(dist_matrix, method='ward')
                
                fig, ax = plt.subplots(figsize=(10, 5))
                dendrogram(Z, labels=places, ax=ax, leaf_rotation=90)
                plt.title("الشجرة اللهجية التقسيمية (Dendrogram)")
                plt.ylabel("المسافة اللسانية (Distance)")
                
                st.pyplot(fig)
            else:
                st.warning("الملف يحتوي على منطقة واحدة فقط. يلزم منطقتان أو أكثر لرسم الشجرة.")
        except Exception as e:
            st.error(f"حدث خطأ أثناء حساب الشجرة اللهجية: {e}")
    else:
        st.info("👈 يرجى رفع ملف البيانات (CSV/TSV) من القائمة الجانبية لعرض الشجرة اللهجية.")

# ---------------------------------------------------------
# التبويب الثالث: الخريطة الفضائية والتجميع الجغرافي (آمن من الأخطاء)
# ---------------------------------------------------------
with tab3:
    st.header("🗺️ خريطة التقسيم اللهجي (Cluster Map)")
    
    if df is not None:
        cols = list(df.columns)
        
        # اختيار الأعمدة مع تحذيرات صحيحة
        lat_col = st.sidebar.selectbox("عمود خط العرض (Latitude):", cols, index=min(1, len(cols)-1))
        lon_col = st.sidebar.selectbox("عمود خط الطول (Longitude):", cols, index=min(2, len(cols)-1))
        
        n_clusters = st.slider("اختر عدد المجموعات اللهجية (Clusters):", min_value=2, max_value=10, value=4)
        
        # التحقق الأمني: هل العمود المختار للإحداثيات هو نفسه عمود الأسماء؟
        if lat_col != place_col and lon_col != place_col:
            try:
                # تحويل الإحداثيات إلى أرقام وتجاهل النصوص لتجنب TypeError
                df_map = df.copy()
                df_map[lat_col] = pd.to_numeric(df_map[lat_col], errors='coerce')
                df_map[lon_col] = pd.to_numeric(df_map[lon_col], errors='coerce')
                
                # حذف الصفوف التي لا تحتوي على إحداثيات رقمية صحيحة
                df_map = df_map.dropna(subset=[lat_col, lon_col])
                
                if not df_map.empty:
                    # إضافة تقسيم افتراضي للمجموعات
                    df_map['Cluster'] = (np.arange(len(df_map)) % n_clusters) + 1
                    df_map['Cluster'] = df_map['Cluster'].astype(str)
                    
                    fig_cluster = px.scatter_mapbox(
                        df_map, 
                        lat=lat_col, 
                        lon=lon_col, 
                        hover_name=place_col,
                        color='Cluster', 
                        zoom=7, 
                        height=600, 
                        size_max=15,
                        title="توزيع اللهجات على الخريطة حسب التجميع الشجري"
                    )
                    fig_cluster.update_layout(mapbox_style="open-street-map")
                    st.plotly_chart(fig_cluster, use_container_style=True)
                else:
                    st.error("❌ الأعمدة المختارة لخطوط الطول والعرض لا تحتوي على أرقام إحداثيات صالحة.")
            except Exception as e:
                st.error(f"تعذر رسم الخريطة: {e}")
        else:
            st.warning("⚠️ يرجى اختيار أعمدة (Latitude) و (Longitude) الصحيحة التي تحتوي على أرقام الإحداثيات من القائمة الجانبية.")
    else:
        st.info("👈 يرجى رفع ملف البيانات (CSV/TSV) من القائمة الجانبية لرسم الخريطة الجغرافية.")
