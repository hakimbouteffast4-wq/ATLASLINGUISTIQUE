import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import json
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.stats import pearsonr
from sklearn.manifold import MDS
import arabic_reshaper
from bidi.algorithm import get_display

# ----------------------------------------------------
# 1. تهيئة المنصة والتصميم (CSS)
# ----------------------------------------------------
st.set_page_config(
    page_title="AtlasLinguistique | المنصة القياسية الفائقة للقياس اللساني",
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
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        margin-bottom: 2rem;
        border-bottom: 4px solid #38bdf8;
    }
    
    .hero-title {
        font-size: 2.6rem;
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
    
    .ai-box {
        background-color: #f0fdf4;
        border-right: 5px solid #22c55e;
        padding: 1.5rem;
        border-radius: 10px;
        font-size: 1.05rem;
        line-height: 1.9;
        color: #14532d;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. الدوال المساعدة والرياضية وتصحيح الرسم العربي
# ----------------------------------------------------
def ar(text):
    """تجهيز النص العربي للعرض في مكتبة Matplotlib فقط"""
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except:
        return str(text)

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

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

# ----------------------------------------------------
# 3. قاعدة البيانات الميدانية لإقليم بولمان
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
# 4. الهيدر العادي ومؤشرات الأداء
# ----------------------------------------------------
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🗺️ AtlasLinguistique Pro</div>
    <div class="hero-subtitle">المنصة الذكية المتقدمة للقياس اللساني والتحليل الجغرافي الآلي</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-val">{len(df)}</div><div class="kpi-lbl">الجماعات الترابية</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="kpi-card"><div class="kpi-val">AI Engine</div><div class="kpi-lbl">مفسر الذكاء الاصطناعي</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="kpi-card"><div class="kpi-val">Auto-KMeans</div><div class="kpi-lbl">التجميع اللهجي التلقائي</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="kpi-card"><div class="kpi-val">Stability</div><div class="kpi-lbl">مؤشر استقرار الظواهر</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------
# 5. الشريط الجانبي
# ----------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric-folders/100/map-marker.png", width=70)
st.sidebar.title("⚙️ التحكم القياسي واللساني")

selected_features = st.sidebar.multiselect(
    "تحديد المتغيرات الداخِلة في الحساب:",
    ['الجهر_الصوتي', 'تضخيم_الراء', 'إمالة_الأليف', 'احتفاظ_بالتلازم'],
    default=['الجهر_الصوتي', 'تضخيم_الراء', 'إمالة_الأليف', 'احتفاظ_بالتلازم']
)

anchor_village = st.sidebar.selectbox("الجماعة المرجعية (Anchor):", df['Village'].values)

# حساب مصفوفة المسافات اللسانية والجغرافية
if len(selected_features) > 0:
    features_matrix = df[selected_features].values
    dist_matrix = pdist(features_matrix, metric='jaccard')
    matrix_sq = squareform(dist_matrix)
    matrix_df = pd.DataFrame(matrix_sq, index=df['Village'], columns=df['Village'])

coords_array = df[['Latitude', 'Longitude']].values
geo_dist_matrix = pdist(coords_array, lambda u, v: haversine(u[0], u[1], v[0], v[1]))
geo_matrix_sq = squareform(geo_dist_matrix)
geo_matrix_df = pd.DataFrame(geo_matrix_sq, index=df['Village'], columns=df['Village'])

# ----------------------------------------------------
# 6. التبويبات الفائقة (10 تبويبات احترافية)
# ----------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "🗺️ الخريطة والتحليل المرجعي", 
    "🤖 المفسر الآلي (AI Engine)",
    "📊 استقرار الظواهر اللسانية",
    "📐 الارتباط الجغرافي-اللساني",
    "⚔️ المقارن الثنائي للجماعات",
    "🌳 الشجرة اللهجية (Ward)", 
    "📍 التحليل ثنائي الأبعاد (MDS)", 
    "🔤 حاسبة المسافة الصوتية (IPA)", 
    "📊 مصفوفات المسافة وتصدير LaTeX", 
    "💻 أكواد الملحق الأكاديمي (R/Python)"
])

# TAB 1: الخريطة
with tab1:
    st.subheader(f"🗺️ الخريطة الفضائية وتوزيع التمايز بالنسبة لـ: [{anchor_village}]")
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
            popup=f"<b>الجماعة:</b> {v_name}<br><b>المسافة:</b> {dist_val:.2f}",
            tooltip=f"{v_name} (المسافة: {dist_val:.2f})",
            icon=folium.Icon(color=color, icon='star' if v_name == anchor_village else 'info-sign')
        ).add_to(m)
        
    st_folium(m, width="100%", height=480)

# TAB 2: الذكاء الاصطناعي والمفسر الآلي
with tab2:
    st.subheader("🤖 المفسر اللساني الذكي (Automated Dialectological Analyst)")
    
    most_sim = matrix_df[anchor_village].nsmallest(2).index[1]
    most_dist = matrix_df[anchor_village].nlargest(1).index[0]
    sim_score = (1 - matrix_df.loc[anchor_village, most_sim]) * 100
    dist_score = matrix_df.loc[anchor_village, most_dist]
    
    ai_analysis = f"""### 💡 القراءة التفسيرية الآلية للنتائج (جماعة {anchor_village}):

1. **الامتداد واللهجة الأم:**
   تُظهر نتائج الخوارزمية القياسية أن جماعة **[{most_sim}]** هي الأقرب لسانيًا لـ **[{anchor_village}]** بنسبة توافق تصل إلى **{sim_score:.1f}%**. يشير هذا إلى وجود اتصال جغرافي أو تاريخي يعزز التماثل في السمات الصوتية والمركبات المعجمية.

2. **عوامل التباين والجدران اللسانية:**
   تسجل جماعة **[{most_dist}]** أعلى مسافة تباين بـ **({dist_score:.2f})**. يعود هذا التباين بشكل عام إلى العوائق الجغرافية (مثل التضاريس الجبلية لإقليم بولمان) أو التحولات الديموغرافية واللسانية نحو المراكز الحضرية.

3. **التوصية الميدانية للباحث:**
   يُنصح بالتركيز على الشريط الانتقالي بين **{anchor_village}** و **{most_dist}** لجمع المزيد من العينات الميدانية لتحديد نقطة الانكسار اللساني (Isogloss Boundary) بدقة أكبر.
"""
    st.markdown(f'<div class="ai-box">{ai_analysis}</div>', unsafe_allow_html=True)

# TAB 3: مؤشر استقرار الظواهر
with tab3:
    st.subheader("📊 مؤشر استقرار وانتشار الظواهر اللسانية")
    
    feat_stats = []
    for f in selected_features:
        presence_rate = df[f].mean() * 100
        stability = "🟢 مرتفع جداً (شائع)" if presence_rate > 70 else ("🟡 متوسط (متذبذب)" if presence_rate >= 30 else "🔴 منخفض (مهدد/محلي)")
        feat_stats.append({'الظاهرة اللسانية': f, 'نسبة الانتشار (%)': f"{presence_rate:.1f}%", 'مستوى الاستقرار': stability})
        
    st.table(pd.DataFrame(feat_stats))

# TAB 4: الارتباط الجغرافي-اللساني
with tab4:
    st.subheader("📐 تحليل الارتباط واختبار الدلالة الإحصائية بين الجغرافيا واللسانيات")
    
    corr, p_val = pearsonr(geo_dist_matrix, dist_matrix)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.metric(label="معامل ارتباط بيرسون (Pearson r)", value=f"{corr:.3f}")
    with col_c2:
        st.metric(label="القيمة الاحتمالية (p-value)", value=f"{p_val:.4f}")
        
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    ax.scatter(geo_dist_matrix, dist_matrix, color='#38bdf8', s=120, edgecolors='#0f172a')
    
    m_slope, b_intercept = np.polyfit(geo_dist_matrix, dist_matrix, 1)
    ax.plot(geo_dist_matrix, m_slope * geo_dist_matrix + b_intercept, color='#f43f5e', linestyle='--', label=f"Line of best fit (r={corr:.2f})")
    
    plt.xlabel(ar("المسافة الجغرافية (كم)"))
    plt.ylabel(ar("المسافة اللسانية (Jaccard)"))
    plt.title(ar("العلاقة بين التباعد الجغرافي والتمايز اللساني لإقليم بولمان"))
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    st.pyplot(fig)

# TAB 5: المقارن الثنائي
with tab5:
    st.subheader("⚔️ التحليل المقارن المباشر بين جماعتين ترابيتين")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        v1 = st.selectbox("اختر الجماعة الأولى:", df['Village'].values, index=0)
    with col_g2:
        v2 = st.selectbox("اختر الجماعة الثانية:", df['Village'].values, index=4)
        
    if v1 and v2:
        v1_data = df[df['Village'] == v1].iloc[0]
        v2_data = df[df['Village'] == v2].iloc[0]
        
        dist_v1_v2 = matrix_df.loc[v1, v2]
        geo_v1_v2 = geo_matrix_df.loc[v1, v2]
        similarity_pct = (1 - dist_v1_v2) * 100
        
        st.markdown("---")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label=f"نسبة التوافق اللساني بين {v1} و {v2}", value=f"{similarity_pct:.1f}%")
            st.progress(similarity_pct / 100)
        with col_m2:
            st.metric(label=f"المسافة الجغرافية المباشرة", value=f"{geo_v1_v2:.1f} كم")
        
        comp_df = pd.DataFrame({
            'المتغير اللساني': selected_features,
            v1: [v1_data[f] for f in selected_features],
            v2: [v2_data[f] for f in selected_features]
        })
        comp_df['الحالة'] = comp_df.apply(lambda r: "✅ متطابق" if r[v1] == r[v2] else "❌ مختلف", axis=1)
        st.table(comp_df)

# TAB 6: الشجرة اللهجية
with tab6:
    st.subheader("🌳 التصنيف الشجري اللهجي (Dendrogram)")
    if len(selected_features) > 0:
        Z = linkage(dist_matrix, method='ward')
        fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
        labels = [ar(v) for v in df['Village'].values]
        dendrogram(Z, labels=labels, ax=ax, color_threshold=0.5)
        plt.title(ar("الشجرة اللهجية لتكتلات إقليم بولمان"), fontsize=12, fontweight='bold')
        st.pyplot(fig)

# TAB 7: MDS
with tab7:
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

# TAB 8: Levenshtein Distance
with tab8:
    st.subheader("🔤 حاسبة المسافة الصوتية بين الألفاظ (Levenshtein Distance)")
    col_a, col_b = st.columns(2)
    with col_a:
        word1 = st.text_input("اللفظة الأولى (IPA 1):", "tagant")
    with col_b:
        word2 = st.text_input("اللفظة الثانية (IPA 2):", "tasarut")
        
    lev_dist = levenshtein_distance(word1, word2)
    similarity = (1 - lev_dist / max(len(word1), len(word2))) * 100
    
    st.metric(label="مسافة التعديل الصوتي (Levenshtein Distance)", value=f"{lev_dist} عمليات")
    st.progress(int(similarity) / 100)
    st.caption(f"نسبة التشابه الصوتي المباشر: **{similarity:.1f}%**")

# TAB 9: LaTeX Export
with tab9:
    st.subheader("📊 مصفوفات المسافة وتصدير LaTeX للأطروحة")
    st.write("📊 **مصفوفة المسافات اللسانية:**")
    st.dataframe(matrix_df.style.background_gradient(cmap='Blues'), use_container_width=True)
    
    st.write("🌐 **مصفوفة المسافات الجغرافية (بالكيلومتر):**")
    st.dataframe(geo_matrix_df.style.background_gradient(cmap='Greens'), use_container_width=True)
    
    st.markdown("---")
    st.subheader("📄 كود LaTeX للمصفوفة اللسانية:")
    st.code(matrix_df.to_latex(), language='latex')

# TAB 10: Reproducibility Code
with tab10:
    st.subheader("💻 أكواد الملحق الأكاديمي (Reproducibility Code)")
    st.write("يمكنك إرفاق هذه الأكواد في ملحق الأطروحة لإتاحة إمكانية إعادة إنتاج النتائج بنفس الشفافية العلمية الدولية:")
    
    python_code = """import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr

# تحميل البيانات وحساب مصفوفة المسافات اللسانية
features = ['الجهر_الصوتي', 'تضخيم_الراء', 'إمالة_الأليف', 'احتفاظ_بالتلازم']
dist_matrix = pdist(df[features].values, metric='jaccard')
print(squareform(dist_matrix))
"""
    st.code(python_code, language='python')
