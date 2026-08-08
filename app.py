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
# 1. تهيئة المنصة والتصميم البصري الاحترافي
# ----------------------------------------------------
st.set_page_config(
    page_title="AtlasLinguistique | أطلس بولمان اللساني",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# نمط CSS متقدم وشامل
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800;900&display=swap');

    * {
        font-family: 'Cairo', sans-serif !important;
    }

    /* الهيدر الأكاديمي الرئيسي */
    .hero-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 2.2rem;
        border-radius: 20px;
        box-shadow: 0 15px 30px rgba(0,0,0,0.12);
        margin-bottom: 2rem;
        border-bottom: 4px solid #38bdf8;
    }
    
    .hero-title {
        font-size: 2.4rem;
        font-weight: 900;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.4rem;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* بطاقات المؤشرات (KPI) */
    .kpi-card {
        background: #ffffff;
        padding: 1.2rem;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        text-align: center;
        transition: all 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(56, 189, 248, 0.15);
        border-color: #38bdf8;
    }
    .kpi-val {
        font-size: 1.9rem;
        font-weight: 800;
        color: #0f172a;
    }
    .kpi-lbl {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
    }

    /* تحسين العناوين */
    h2, h3 {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. الهيدر العريض والمؤشرات الذكية
# ----------------------------------------------------
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🗺️ AtlasLinguistique</div>
    <div class="hero-subtitle">المنصة التفاعلية المتقدمة للجغرافيا والقياس اللساني — دراسة ميدانية لإقليم بولمان</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="kpi-card"><div class="kpi-val">12</div><div class="kpi-lbl">الجماعات الترابية المدروسة</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="kpi-card"><div class="kpi-val">150+</div><div class="kpi-lbl">متغير صوتي ومعجمي</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="kpi-card"><div class="kpi-val">300 DPI</div><div class="kpi-lbl">دقة الرسوم للأطروحة</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="kpi-card"><div class="kpi-val">MP3 / WAV</div><div class="kpi-lbl">التسجيلات الميدانية</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. معالجة النصوص العربية في المخططات
# ----------------------------------------------------
def ar(text):
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except:
        return text

# ----------------------------------------------------
# 4. عينة بيانات متكاملة لإقليم بولمان
# ----------------------------------------------------
sample_data = {
    'Village': ['كيكو', 'تيمحضيت', 'أنجيل', 'أوطاط الحاج', 'ميسور', 'بولمان'],
    'Latitude': [33.2100, 33.1500, 33.0800, 33.3500, 33.0500, 33.3600],
    'Longitude': [-4.7000, -5.0500, -4.6000, -3.7000, -3.9800, -4.7300],
    'اللفظة_تيفيناغ': ['ⵜⴰⴳⴰⵏⵜ', 'ⵜⴰⴳⴰⵏⵜ', 'ⵜⴰⵙⴰⵔⵓⵜ', 'ⵍⵖⴰⴱⴰ', 'ⵍⵖⴰⴱⴰ', 'ⵜⴰⴳⴰⵏⵜ'],
    'الرمز_الصوتي_IPA': ['tagant', 'tagant', 'tasarut', 'lɣaba', 'lɣaba', 'tagant'],
    'الجهر_الصوتي': [1, 1, 1, 0, 0, 1],
    'تضخيم_الراء': [1, 1, 0, 0, 0, 1],
    'إمالة_الأليف': [0, 0, 1, 1, 1, 0]
}
df = pd.DataFrame(sample_data)

# ----------------------------------------------------
# 5. القائمة الجانبية المتقدمة
# ----------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric-folders/100/map-marker.png", width=70)
st.sidebar.title("⚙️ خيارات الخريطة والظواهر")

phenomenon = st.sidebar.selectbox(
    "تحديد الظاهرة اللسانية للعرض (Isogloss Map):",
    ["تضخيم_الراء", "الجهر_الصوتي", "إمالة_الأليف"]
)

# ----------------------------------------------------
# 6. التبويبات الرئيسية
# ----------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ الخريطة الفضائية والتسجيلات", 
    "🌳 الشجرة اللهجية (Dendrogram)", 
    "📍 التحليل متعدد الأبعاد (MDS)", 
    "📊 مصفوفة المسافات والتشابه", 
    "🎧 المتون الصوتية الميدانية"
])

# TAB 1: الخريطة
with tab1:
    st.subheader(f"🗺️ خريطة توزيع ظاهرة: [{phenomenon}]")
    
    m = folium.Map(location=[33.1500, -4.5000], zoom_start=9, tiles='OpenStreetMap')
    
    try:
        with open("boundaries.geojson", "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
            folium.GeoJson(
                geojson_data,
                name="حدود الجماعات",
                style_function=lambda x: {
                    'fillColor': '#38bdf8', 'color': '#0f172a', 'weight': 1.5, 'fillOpacity': 0.12
                }
            ).add_to(m)
    except:
        pass

    # تلوين النقاظ بناءً على القيمة الخاصة بالظاهرة المختارة
    for idx, row in df.iterrows():
        val = row[phenomenon]
        color = 'green' if val == 1 else 'orange'
        
        popup_html = f"""
        <div style='font-family: Cairo; width: 160px;'>
            <b>الجماعة:</b> {row['Village']}<br>
            <b>اللفظة:</b> {row['اللفظة_تيفيناغ']}<br>
            <b>IPA:</b> [{row['الرمز_الصوتي_IPA']}]<br>
            <b>الظاهرة:</b> {'حاضرة (1)' if val==1 else 'غائبة (0)'}
        </div>
        """
        
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=popup_html,
            tooltip=f"{row['Village']} ({row['اللفظة_تيفيناغ']})",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
        
    st_folium(m, width="100%", height=520)

# TAB 2: الشجرة اللهجية بأعلى دقة للطباعة
with tab2:
    st.subheader("🌳 التصنيف التكتلي الشجري (Hierarchical Clustering - Ward's Method)")
    features = df[['الجهر_الصوتي', 'تضخيم_الراء', 'إمالة_الأليف']].values
    dist_matrix = pdist(features, metric='jaccard')
    Z = linkage(dist_matrix, method='ward')
    
    # دقة عالية فائقة (300 DPI) للقص المباشر في الأطروحة
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=300)
    labels = [ar(v) for v in df['Village'].values]
    dendrogram(Z, labels=labels, ax=ax, color_threshold=0.5, above_threshold_color='#1e293b')
    
    plt.title(ar("الشجرة اللهجية لتكتلات إقليم بولمان (دقة عالية للأطروحة)"), fontsize=12, fontweight='bold')
    plt.ylabel(ar("المسافة اللسانية (Jaccard Distance)"))
    st.pyplot(fig)

# TAB 3: MDS
with tab3:
    st.subheader("📍 التوزيع الفضائي اللساني للجماعات (Multidimensional Scaling - MDS)")
    from sklearn.manifold import MDS
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    matrix_sq = squareform(dist_matrix)
    coords = mds.fit_transform(matrix_sq)
    
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=300)
    ax.scatter(coords[:, 0], coords[:, 1], color='#38bdf8', s=160, edgecolors='#0f172a', linewidth=1.5)
    
    for i, txt in enumerate(df['Village']):
        ax.annotate(ar(txt), (coords[i, 0]+0.02, coords[i, 1]+0.02), fontsize=11, fontweight='bold')
        
    plt.title(ar("مخطط البعدين اللسانيين للجماعات (MDS Plot)"), fontsize=12, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)

# TAB 4: المصفوفة
with tab4:
    st.subheader("📊 مصفوفة المسافات اللسانية البينية")
    matrix_df = pd.DataFrame(squareform(dist_matrix), index=df['Village'], columns=df['Village'])
    st.dataframe(matrix_df.style.background_gradient(cmap='Blues'), use_container_width=True)

# TAB 5: المتون والتسجيلات الصوتية
with tab5:
    st.subheader("🎧 المتون الميدانية والاستماع للتسجيلات الصوتية")
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    st.write("🎵 **مشغل العينات الصوتية الميدانية للجماعات:**")
    selected_village = st.selectbox("اختر الجماعة الترابية لسماع التسجيل الميداني:", df['Village'].values)
    
    # تجربة صوتية تفاعلية
    st.info(f"🔊 تشغيل التسجيل الصوتي الميداني الخاص بجماعة: **[{selected_village}]**")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
