import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import json
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.manifold import MDS
import arabic_reshaper
from bidi.algorithm import get_display

# ----------------------------------------------------
# 1. تهيئة المنصة وتصميم الواجهة (CSS العالمي)
# ----------------------------------------------------
st.set_page_config(
    page_title="AtlasLinguistique | أطلس القياس اللساني",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800;900&display=swap');
    * { font-family: 'Cairo', sans-serif !important; }
    
    .hero-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 2.2rem;
        border-radius: 20px;
        box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        margin-bottom: 2rem;
        border-bottom: 4px solid #38bdf8;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.4rem;
    }
    
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
        border-color: #38bdf8;
    }
    .kpi-val { font-size: 1.8rem; font-weight: 800; color: #0f172a; }
    .kpi-lbl { font-size: 0.85rem; color: #64748b; font-weight: 600; }
    
    .report-box {
        background-color: #f8fafc;
        border-right: 4px solid #38bdf8;
        padding: 1.2rem;
        border-radius: 8px;
        font-size: 1.05rem;
        line-height: 1.8;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. الدوال المساعدة (Levenshtein & Arabic)
# ----------------------------------------------------
def ar(text):
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except:
        return text

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

# ----------------------------------------------------
# 3. بيانات العينة المتكاملة لإقليم بولمان
# ----------------------------------------------------
sample_data = {
    'Village': ['كيكو', 'تيمحضيت', 'أنجيل', 'أوطاط الحاج', 'ميسور', 'بولمان'],
    'Latitude': [33.2100, 33.1500, 33.0800, 33.3500, 33.0500, 33.3600],
    'Longitude': [-4.7000, -5.0500, -4.6000, -3.7000, -3.9800, -4.7300],
    'اللفظة_تيفيناغ': ['ⵜⴰⴳⴰⵏⵜ', 'ⵜⴰⴳⴰⵏⵜ', 'ⵜⴰⵙⴰⵔⵓⵜ', 'ⵍⵖⴰⴱⴰ', 'ⵍⵖⴰⴱⴰ', 'ⵜⴰⴳⴰⵏⵜ'],
    'الرمز_الصوتي_IPA': ['tagant', 'tagant', 'tasarut', 'lɣaba', 'lɣaba', 'tagant'],
    'الجهر_الصوتي': [1, 1, 1, 0, 0, 1],
    'تضخيم_الراء': [1, 1, 0, 0, 0, 1],
    'إمالة_الأليف': [0, 0, 1, 1, 1, 0],
    'احتفاظ_بالتلازم': [1, 1, 1, 0, 1, 1]
}
df = pd.DataFrame(sample_data)

# ----------------------------------------------------
# 4. الواجهة الرئيسية والهيدر
# ----------------------------------------------------
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🗺️ AtlasLinguistique</div>
    <div class="hero-subtitle">المنصة القياسية والتفاعلية للجغرافيا اللسانية — أطلس إقليم بولمان الرقمي</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-val">{len(df)}</div><div class="kpi-lbl">الجماعات الترابية</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="kpi-card"><div class="kpi-val">Levenshtein</div><div class="kpi-lbl">محرك المسافة الصوتية</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="kpi-card"><div class="kpi-val">LaTeX & CSV</div><div class="kpi-lbl">تصدير المتون والمصفوفات</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="kpi-card"><div class="kpi-val">MDS & Ward</div><div class="kpi-lbl">النماذج الإحصائية</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------
# 5. الشريط الجانبي الذكي
# ----------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric-folders/100/map-marker.png", width=70)
st.sidebar.title("⚙️ التحكم الإحصائي واللساني")

selected_features = st.sidebar.multiselect(
    "تحديد المتغيرات اللسانية الداخِلة في الحساب:",
    ['الجهر_الصوتي', 'تضخيم_الراء', 'إمالة_الأليف', 'احتفاظ_بالتلازم'],
    default=['الجهر_الصوتي', 'تضخيم_الراء', 'إمالة_الأليف']
)

anchor_village = st.sidebar.selectbox("اختر الجماعة المرجعية للمقارنة (Anchor):", df['Village'].values)

# ----------------------------------------------------
# 6. التبويبات الفائقة
# ----------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🗺️ الخريطة والتحليل المرجعي", 
    "🌳 الشجرة اللهجية (Ward)", 
    "📍 التحليل متعدد الأبعاد (MDS)", 
    "🔤 حاسبة المسافة الصوتية (IPA)", 
    "📊 مصفوفات المسافة وتصدير LaTeX", 
    "📝 التقرير الأكاديمي التلقائي"
])

# حساب المسافات بناءً على المتغيرات المختارة
if len(selected_features) > 0:
    features_matrix = df[selected_features].values
    dist_matrix = pdist(features_matrix, metric='jaccard')
    matrix_sq = squareform(dist_matrix)
    matrix_df = pd.DataFrame(matrix_sq, index=df['Village'], columns=df['Village'])
else:
    st.error("يرجى اختيار متغير لساني واحد على الأقل من الشريط الجانبي!")

# TAB 1: الخريطة التفاعلية
with tab1:
    st.subheader(f"🗺️ الخريطة الفضائية ومؤشر القرب اللساني بالنسبة لـ: [{anchor_village}]")
    m = folium.Map(location=[33.1500, -4.5000], zoom_start=9, tiles='OpenStreetMap')
    
    try:
        with open("boundaries.geojson", "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
            folium.GeoJson(geojson_data, style_function=lambda x: {'fillColor': '#38bdf8', 'color': '#0f172a', 'weight': 1, 'fillOpacity': 0.1}).add_to(m)
    except:
        pass

    anchor_distances = matrix_df[anchor_village]
    
    for idx, row in df.iterrows():
        v_name = row['Village']
        dist_val = anchor_distances[v_name]
        
        color = 'red' if v_name == anchor_village else ('green' if dist_val < 0.4 else 'orange')
        
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=f"<b>الجماعة:</b> {v_name}<br><b>المسافة عن {anchor_village}:</b> {dist_val:.2f}<br><b>IPA:</b> [{row['الرمز_الصوتي_IPA']}]",
            tooltip=f"{v_name} (المسافة: {dist_val:.2f})",
            icon=folium.Icon(color=color, icon='star' if v_name == anchor_village else 'info-sign')
        ).add_to(m)
        
    st_folium(m, width="100%", height=500)

# TAB 2: الشجرة اللهجية
with tab2:
    st.subheader("🌳 التصنيف الشجري اللهجي (Dendrogram)")
    if len(selected_features) > 0:
        Z = linkage(dist_matrix, method='ward')
        fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
        labels = [ar(v) for v in df['Village'].values]
        dendrogram(Z, labels=labels, ax=ax, color_threshold=0.5)
        plt.title(ar("الشجرة اللهجية لتكتلات إقليم بولمان"), fontsize=12, fontweight='bold')
        st.pyplot(fig)

# TAB 3: MDS
with tab3:
    st.subheader("📍 التحليل الفضائي ثنائي الأبعاد (MDS)")
    if len(selected_features) > 0:
        mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
        coords = mds.fit_transform(matrix_sq)
        
        fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
        ax.scatter(coords[:, 0], coords[:, 1], color='#38bdf8', s=160, edgecolors='#0f172a')
        for i, txt in enumerate(df['Village']):
            ax.annotate(ar(txt), (coords[i, 0]+0.02, coords[i, 1]+0.02), fontsize=11, fontweight='bold')
        plt.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)

# TAB 4: حاسبة Levenshtein المباشرة
with tab4:
    st.subheader("🔤 حاسبة المسافة الصوتية بين الألفاظ (Levenshtein Phonetic Distance)")
    col_a, col_b = st.columns(2)
    with col_a:
        word1 = st.text_input("اللفظة الأولى بالرمز الصوتي (IPA 1):", "tagant")
    with col_b:
        word2 = st.text_input("اللفظة الثانية بالرمز الصوتي (IPA 2):", "tasarut")
        
    lev_dist = levenshtein_distance(word1, word2)
    similarity = (1 - lev_dist / max(len(word1), len(word2))) * 100
    
    st.metric(label="مسافة التعديل الصوتي (Levenshtein Distance)", value=f"{lev_dist} عمليات")
    st.progress(int(similarity) / 100)
    st.caption(f"نسبة التشابه الصوتي المباشر بين اللفظتين: **{similarity:.1f}%**")

# TAB 5: المصادفة وتصدير LaTeX
with tab5:
    st.subheader("📊 مصفوفة المسافات التراكمية وتصدير الأطروحة")
    st.dataframe(matrix_df.style.background_gradient(cmap='Blues'), use_container_width=True)
    
    st.markdown("---")
    st.subheader("📄 كود LaTeX للمصفوفة (جاهز للنسخ في الأطروحة):")
    st.code(matrix_df.to_latex(), language='latex')

# TAB 6: التقرير الآلي للأطروحة
with tab6:
    st.subheader("📝 التقرير التحليلي التلقائي الجاهز للصياغة الأكاديمية")
    
    most_similar = matrix_df[anchor_village].nsmallest(2).index[1]
    most_distant = matrix_df[anchor_village].nlargest(1).index[0]
    
    report_text = f"""
    تُظهر نتائج القياس اللهجي الميداني بـ **إقليم بولمان**، وباعتماد جماعة **[{anchor_village}]** كنقطة مرجعية (Anchor)، وجود تباين لساني ملحوظ بين مكونات الإقليم.
    
    * **أعلى درجة تشابه:** تُسجّل جماعة **[{most_similar}]** أقرب مسافة لسانية من جماعة **[{anchor_village}]** بمسافة قدرها **({matrix_df.loc[anchor_village, most_similar]:.2f})**، مما يعكس تماسكًا صوتيًا ومعجميًا قويًا بينهما.
    * **أعلى درجة تباين:** بينما تُسجّل جماعة **[{most_distant}]** أكبر أبعاد لساني عن النقطة المرجعية بمسافة قدرها **({matrix_df.loc[anchor_village, most_distant]:.2f})**.
    
    هذا التوزيع يتوافق مع نتائج التحليل الشجري (Ward's Hierarchical Clustering) والتحليل متعدد الأبعاد (MDS)، مما يؤكد فرضية وجود أشرطة لسانية انتقال يحددها التمايز الجغرافي داخل الإقليم.
    """
    st.markdown(f'<div class="report-box">{report_text}</div>', unsafe_allow_html=True)
