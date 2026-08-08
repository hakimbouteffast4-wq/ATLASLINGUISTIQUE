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

# ----------------------------------------------------
# 1. إعدادات الصفحة والتصميم العالمي (Custom CSS)
# ----------------------------------------------------
st.set_page_config(
    page_title="AtlasLinguistique | منصة القياس اللساني",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# نمط CSS احترافي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }

    /* الهيدر الرئيسي الاحترافي */
    .hero-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 0;
    }

    /* بطاقات KPI الإحصائية */
    .metric-card {
        background: #ffffff;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 600;
    }

    /* تحسين الشريط الجانبي */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }

    /* تحسين زر التحديث والتنزيل */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. الهيدر الرئيسي والمؤشرات السريعة (KPIs)
# ----------------------------------------------------
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🗺️ AtlasLinguistique</div>
    <div class="hero-subtitle">المنصة التفاعلية المتقدمة للجغرافيا والقياس اللساني — أطلس إقليم بولمان</div>
</div>
""", unsafe_allow_html=True)

# عرض مؤشرات سريعة في أعلى المنصة
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.markdown('<div class="metric-card"><div class="metric-value">12</div><div class="metric-label">الجماعات الترابية</div></div>', unsafe_allow_html=True)
with col_kpi2:
    st.markdown('<div class="metric-card"><div class="metric-value">150+</div><div class="metric-label">الظواهر اللسانية</div></div>', unsafe_allow_html=True)
with col_kpi3:
    st.markdown('<div class="metric-card"><div class="metric-value">MDS & Ward</div><div class="metric-label">محرك القياس</div></div>', unsafe_allow_html=True)
with col_kpi4:
    st.markdown('<div class="metric-card"><div class="metric-value">GeoJSON</div><div class="metric-label">الخرائط الفضائية</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. دالة معالجة النصوص العربية لـ Matplotlib
# ----------------------------------------------------
def ar(text):
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except:
        return text

# ----------------------------------------------------
# 4. الشريط الجانبي
# ----------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric-folders/100/map-marker.png", width=70)
st.sidebar.title("⚙️ خيارات التحليل")
st.sidebar.info("💡 تحكم في المتغيرات اللسانية وإعدادات الخريطة التفاعلية مباشرة.")

input_method = st.sidebar.radio("طريقة إدخال البيانات:", ["استمارة إدخال مباشرة 📝", "رفع ملف Excel/CSV 📁"])

# ----------------------------------------------------
# 5. التبويبات الرئيسية
# ----------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ الخريطة والحدود الفضائية", 
    "🌳 الشجرة اللهجية (Dendrogram)", 
    "📍 تحليل متعدد الأبعاد (MDS)", 
    "📊 مصفوفة المسافات والتشابه", 
    "📈 الإحصائيات والمؤشرات"
])

# عينة بيانات افتراضية
sample_data = {
    'Village': ['كيكو', 'تيمحضيت', 'أنجيل', 'أوطاط الحاج', 'ميسور', 'بولمان'],
    'Latitude': [33.2100, 33.1500, 33.0800, 33.3500, 33.0500, 33.3600],
    'Longitude': [-4.7000, -5.0500, -4.6000, -3.7000, -3.9800, -4.7300],
    'المتغير_1_الجهر': [1, 1, 1, 0, 0, 1],
    'المتغير_2_التضخيم': [1, 1, 0, 0, 0, 1],
    'المتغير_3_الإمالة': [0, 0, 1, 1, 1, 0]
}
df = pd.DataFrame(sample_data)

# TAB 1: الخريطة
with tab1:
    st.subheader("🗺️ خريطة أطلس الفضائية مع حدود الجماعات والإقليم")
    m = folium.Map(location=[33.1500, -4.5000], zoom_start=9, tiles='OpenStreetMap')
    
    # محاولة تحميل GeoJSON إن وجد
    try:
        with open("boundaries.geojson", "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
            folium.GeoJson(geojson_data, name="حدود الجماعات", style_function=lambda x: {
                'fillColor': '#38bdf8', 'color': '#1e293b', 'weight': 1.5, 'fillOpacity': 0.15
            }).add_to(m)
    except:
        pass

    for idx, row in df.iterrows():
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=f"<b>الجماعة: {row['Village']}</b>",
            tooltip=row['Village'],
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
    st_folium(m, width="100%", height=520)

# TAB 2: الشجرة اللهجية
with tab2:
    st.subheader("🌳 التصنيف التكتلي الشجري (Hierarchical Clustering)")
    features = df.iloc[:, 3:].values
    dist_matrix = pdist(features, metric='jaccard')
    Z = linkage(dist_matrix, method='ward')
    
    fig, ax = plt.subplots(figsize=(9, 4.5))
    labels = [ar(v) for v in df['Village'].values]
    dendrogram(Z, labels=labels, ax=ax)
    plt.title(ar("الشجرة اللهجية لتكتلات إقليم بولمان (Ward's Method)"))
    st.pyplot(fig)

# TAB 3: MDS
with tab3:
    st.subheader("📍 التحليل ثنائي الأبعاد (Multidimensional Scaling - MDS)")
    from sklearn.manifold import MDS
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    matrix_sq = squareform(dist_matrix)
    coords = mds.fit_transform(matrix_sq)
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(coords[:, 0], coords[:, 1], color='#818cf8', s=120)
    for i, txt in enumerate(df['Village']):
        ax.annotate(ar(txt), (coords[i, 0]+0.02, coords[i, 1]+0.02), fontsize=11)
    plt.title(ar("التوزيع الفضائي اللساني للجماعات (MDS Plot)"))
    st.pyplot(fig)

# TAB 4: المصفوفة
with tab4:
    st.subheader("📊 مصفوفة المسافات والتشابه اللساني")
    matrix_df = pd.DataFrame(squareform(dist_matrix), index=df['Village'], columns=df['Village'])
    st.dataframe(matrix_df.style.background_gradient(cmap='Blues'), use_container_width=True)

# TAB 5: الإحصائيات
with tab5:
    st.subheader("📈 المتون والبيانات الميدانية")
    st.dataframe(df, use_container_width=True)
