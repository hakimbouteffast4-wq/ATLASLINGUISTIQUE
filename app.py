import streamlit as st
import pandas as pd
import numpy as np
import math

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتنسيق
# ---------------------------------------------------------
st.set_page_config(
    page_title="AtlasLinguistique Pro - Dialectometry Suite",
    page_icon="🧬",
    layout="wide"
)

st.markdown("""
    <style>
    * { font-family: 'Cairo', sans-serif !important; color: #1e293b !important; }
    html, body, .stApp { direction: rtl; background-color: #f8fafc !important; }
    #MainMenu, footer, header { display: none !important; }
    .stTabs [aria-selected="true"] { background: #0284c7 !important; color: #ffffff !important; }
    .stTabs [aria-selected="true"] * { color: #ffffff !important; }
    .stTabs [data-baseweb="tab"] { border-radius: 12px; padding: 8px 16px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. استدعاء المكتبات الرسومية والإحصائية
# ---------------------------------------------------------
try:
    import plotly.graph_objects as go
    import plotly.figure_factory as ff
    from sklearn.manifold import MDS
    from scipy.cluster.hierarchy import linkage, dendrogram
    HAS_ADVANCED = True
except Exception:
    HAS_ADVANCED = False

# ---------------------------------------------------------
# 3. دالة حساب مسافة Levenshtein (محاذاة النصوص)
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 4. بيانات افتراضية للبدء
# ---------------------------------------------------------
def get_sample_data():
    return pd.DataFrame([
        {"commune": "بولمان", "lat": 33.3617, "lon": -4.7314, "خبز": "agrom", "ماء": "aman", "بيت": "taddart"},
        {"commune": "كيكو", "lat": 33.2089, "lon": -4.8483, "خبز": "agrom", "ماء": "aman", "بيت": "taddart"},
        {"commune": "مرموشة", "lat": 33.4833, "lon": -4.2833, "خبز": "agrom", "ماء": "aman", "بيت": "taddert"},
        {"commune": "ميسور", "lat": 33.0486, "lon": -3.9961, "خبز": "khubz", "ماء": "ma", "بيت": "dar"},
        {"commune": "أوطاط الحاج", "lat": 33.3483, "lon": -3.7022, "خبز": "khubz", "ماء": "elma", "بيت": "dar"}
    ])

# ---------------------------------------------------------
# 5. الواجهة الرئيسية واستيراد البيانات (المرحلة 1)
# ---------------------------------------------------------
st.title("🧬 AtlasLinguistique Pro - منصة القياس اللهجي")
st.caption("تطبيق متكامل محاكي لمعايير Gabmap للتحليل الأطلسي واللساني")

df_input = get_sample_data()

with st.expander("📥 1. جمع ورفع البيانات (Collect & Upload Data)", expanded=False):
    uploaded = st.file_uploader("ارفع ملف البيانات اللسانية والجغرافية (CSV / Excel)", type=["csv", "xlsx"])
    if uploaded:
        df_input = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
    st.dataframe(df_input, use_container_width=True)

# ---------------------------------------------------------
# 6. مراحـل التحليل والقياس (المراحل 2 إلى 6)
# ---------------------------------------------------------
tabs = st.tabs([
    "👀 2. المعاينة والخرائط", 
    "📐 3. قياس المسافات (Levenshtein)", 
    "🕸️ 4. شبكة الفروق (Difference Maps)", 
    "📊 5. التدرج والتجميع (MDS & Cluster)", 
    "⛏️ 6. التنقيب عن الميزات (Data Mining)"
])

communes = df_input['commune'].tolist()
word_cols = [c for c in df_input.columns if c not in ['commune', 'lat', 'lon']]

# --- المرحلة 2: المعاينة ---
with tabs[0]:
    st.subheader("🗺️ خريطة الفهرس والتوزيع المبدئي")
    st.map(df_input[['lat', 'lon']])

# --- المرحلة 3: حساب مصفوفة المسافات اللسانية ---
with tabs[1]:
    st.subheader("📐 حساب مسافات Levenshtein وتجميعها (Aggregation)")
    
    # بناء مصفوفة المسافات
    n = len(communes)
    dist_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                total_dist = 0
                for w in word_cols:
                    total_dist += levenshtein_distance(str(df_input.iloc[i][w]), str(df_input.iloc[j][w]))
                dist_matrix[i][j] = total_dist / len(word_cols)
    
    dist_df = pd.DataFrame(dist_matrix, index=communes, columns=communes)
    st.write("### 🔢 مصفوفة المسافات اللسانية المجمعة (Distance Matrix)")
    st.dataframe(dist_df.style.highlight_min(axis=None, color='lightgreen'))

# --- المرحلة 4: خرائط شبكة الفروق ---
with tabs[2]:
    st.subheader("🕸️ شبكة الاختلافات الجغرافية-اللسانية")
    if HAS_ADVANCED:
        edge_x, edge_y, weights = [], [], []
        for i in range(n):
            for j in range(i + 1, n):
                edge_x.extend([df_input.iloc[i]['lon'], df_input.iloc[j]['lon'], None])
                edge_y.extend([df_input.iloc[i]['lat'], df_input.iloc[j]['lat'], None])
                weights.append(dist_matrix[i][j])

        fig_net = go.Figure()
        fig_net.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=2, color='#0284c7')))
        fig_net.add_trace(go.Scatter(
            x=df_input['lon'], y=df_input['lat'], mode='markers+text', 
            text=communes, textposition="top center", marker=dict(size=14, color='#ef4444')
        ))
        fig_net.update_layout(height=450, showlegend=False, template="plotly_white")
        st.plotly_chart(fig_net, use_container_width=True)

# --- المرحلة 5: التدرج متعدد الأبعاد MDS والتجميع Dendrogram ---
with tabs[3]:
    col_mds, col_dendro = st.columns(2)
    
    with col_mds:
        st.subheader("🎨 التدرج متعدد الأبعاد (MDS)")
        if HAS_ADVANCED and n > 2:
            mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
            coords = mds.fit_transform(dist_matrix)
            
            fig_mds = go.Figure()
            fig_mds.add_trace(go.Scatter(
                x=coords[:, 0], y=coords[:, 1], mode='markers+text',
                text=communes, textposition="top center", marker=dict(size=15, color='#10b981')
            ))
            fig_mds.update_layout(title="MDS Map (Dialect Continuum)", height=400, template="plotly_white")
            st.plotly_chart(fig_mds, use_container_width=True)
            
    with col_dendro:
        st.subheader("🌲 الشجرة اللهجية (Dendrogram Cluster)")
        if HAS_ADVANCED and n >= 2:
            fig_dendro = ff.create_dendrogram(dist_matrix, labels=communes)
            fig_dendro.update_layout(height=400, template="plotly_white")
            st.plotly_chart(fig_dendro, use_container_width=True)

# --- المرحلة 6: التنقيب في البيانات ---
with tabs[4]:
    st.subheader("⛏️ محددات التجميع الكاشفة (Cluster Determinants)")
    selected_word = st.selectbox("اختر كلمة لتحليل توزيعها وملاءمتها:", word_cols)
    
    word_summary = df_input[['commune', selected_word]]
    st.table(word_summary)
    
    st.download_button(
        label="📥 تصدير التقرير الكامل (CSV)",
        data=dist_df.to_csv().encode('utf-8-sig'),
        file_name="Gabmap_Analysis_Report.csv",
        mime="text/csv"
    )
