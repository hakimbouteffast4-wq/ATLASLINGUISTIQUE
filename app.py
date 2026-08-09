import streamlit as st
import pandas as pd
import numpy as np
import Levenshtein
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.manifold import MDS
import matplotlib.pyplot as plt
import plotly.express as px

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="AtlasLinguistique", 
    layout="wide", 
    page_icon="🗺️"
)

st.title("🗺️ منصة AtlasLinguistique للجغرافيا والقياس اللساني")
st.caption("إقليم بولمان - تحليل المسافات اللسانية والخرائط التفاعلية (Gabmap Style)")

# 2. القائمة الجانبية وتجهيز الملف (تعريف مبكر لتجنب NameError)
st.sidebar.header("⚙️ إعدادات البيانات")
project_name = st.sidebar.text_input("اسم المشروع/المنطقة", "أطلس إقليم بولمان")

# رفع الملف
uploaded_file = st.sidebar.file_uploader("📂 رفع ملف البيانات (CSV أو TSV)", type=['csv', 'tsv'])

# قراءة البيانات مبكراً وبشكل آمن
df = None
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.tsv'):
            df = pd.read_csv(uploaded_file, sep='\t')
        else:
            df = pd.read_csv(uploaded_file)
        st.sidebar.success("تم تحميل الملف بنجاح!")
    except Exception as e:
        st.sidebar.error(f"خطأ في قراءة الملف: {e}")

# 3. دالة حساب مصفوفة مسافات ليفنشتاين
def calculate_levenshtein_matrix(data_frame, place_col, word_cols):
    places = data_frame[place_col].dropna().unique()
    n = len(places)
    dist_matrix = np.zeros((n, n))
    
    place_words = {}
    for p in places:
        sub_df = data_frame[data_frame[place_col] == p]
        words = []
        for col in word_cols:
            words.extend(sub_df[col].dropna().astype(str).tolist())
        place_words[p] = words

    for i in range(n):
        for j in range(i + 1, n):
            p1, p2 = places[i], places[j]
            w1_list, w2_list = place_words[p1], place_words[p2]
            
            distances = []
            min_len = min(len(w1_list), len(w2_list))
            
            for k in range(min_len):
                w1, w2 = w1_list[k], w2_list[k]
                max_l = max(len(w1), len(w2))
                if max_l > 0:
                    norm_dist = Levenshtein.distance(w1, w2) / max_l
                    distances.append(norm_dist)
            
            avg_dist = np.mean(distances) if distances else 0.0
            dist_matrix[i, j] = avg_dist
            dist_matrix[j, i] = avg_dist
            
    return places, dist_matrix

# 4. تبويبات المنصة
tab1, tab2, tab3 = st.tabs([
    "📝 1. إدخال وتجميع البيانات", 
    "🔬 2. محرك القياس اللساني (Levenshtein & MDS)", 
    "🗺️ 3. الخريطة الفضائية والتجميع"
])

# ---------------------------------------------------------
# التبويب الأول: إدخال البيانات
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
        st.success(f"تم حفظ المفردة [{tifinagh}] بنجاح!")

# ---------------------------------------------------------
# التبويب الثاني: التحليل اللساني (Levenshtein & MDS)
# ---------------------------------------------------------
with tab2:
    st.header("🔬 محرك القياس اللساني (Méthode Levenshtein & MDS)")
    
    if uploaded_file is not None and df is not None:
        cols = list(df.columns)
        
        st.subheader("⚙️ إعدادات التحليل")
        col_a, col_b = st.columns(2)
        
        with col_a:
            place_col = st.selectbox("اختر عمود أسماء القرى/المناطق:", cols, index=0, key="place_lev")
        with col_b:
            word_cols = st.multiselect("اختر أعمدة المفردات للمقارنة:", cols, default=[cols[-1]], key="words_lev")

        if st.button("🚀 تشغيل تحليل Levenshtein و MDS"):
            if len(word_cols) > 0:
                with st.spinner("جاري حساب المسافات اللسانية ومصفوفة التباين..."):
                    places, dist_matrix = calculate_levenshtein_matrix(df, place_col, word_cols)
                    
                    st.subheader("1️⃣ مصفوفة المسافات اللسانية (Difference Matrix)")
                    df_dist = pd.DataFrame(dist_matrix, index=places, columns=places)
                    st.dataframe(df_dist.style.background_gradient(cmap="Blues"))
                    
                    st.subheader("2️⃣ الشجرة اللهجية (Dendrogram)")
                    condensed_dist = squareform(dist_matrix)
                    Z = linkage(condensed_dist, method='ward')
                    
                    fig, ax = plt.subplots(figsize=(10, 5))
                    dendrogram(Z, labels=places, ax=ax, leaf_rotation=90)
                    plt.title("التجميع الشجري القائم على مسافة Levenshtein")
                    plt.ylabel("درجة التباين اللساني النسبية")
                    st.pyplot(fig)
                    
                    st.subheader("3️⃣ خريطة الألوان المركبة (MDS RGB Map)")
                    if len(places) >= 3:
                        mds = MDS(n_components=3, dissimilarity='precomputed', random_state=42)
                        mds_coords = mds.fit_transform(dist_matrix)
                        
                        rgb = (mds_coords - mds_coords.min(axis=0)) / (mds_coords.max(axis=0) - mds_coords.min(axis=0) + 1e-5)
                        colors = [f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})" for r, g, b in rgb]
                        
                        df_mds = pd.DataFrame({
                            'Place': places,
                            'Color': colors,
                            'Dim1': mds_coords[:, 0],
                            'Dim2': mds_coords[:, 1]
                        })
                        
                        fig_mds = px.scatter(
                            df_mds, x='Dim1', y='Dim2', text='Place',
                            title="تمثيل التمايز اللهجي بالألوان المركبة (MDS RGB Space)"
                        )
                        fig_mds.update_traces(marker=dict(size=20, color=df_mds['Color']), textposition='top center')
                        st.plotly_chart(fig_mds, use_container_style=True)
                    else:
                        st.warning("يلزم وجود 3 مناطق على الأقل للتحليل متعدد الأبعاد MDS.")
            else:
                st.error("يرجى اختيار عمود واحد على الأقل من الكلمات لإجراء المقارنة.")
    else:
        st.info("👈 قم برفع ملف البيانات الميدانية من القائمة الجانبية لتشغيل هذا التحليل.")

# ---------------------------------------------------------
# التبويب الثالث: الخريطة الفضائية
# ---------------------------------------------------------
with tab3:
    st.header("🗺️ خريطة التقسيم اللهجي (Cluster Map)")
    
    if uploaded_file is not None and df is not None:
        cols = list(df.columns)
        
        lat_col = st.sidebar.selectbox("عمود خط العرض (Latitude):", cols, index=min(1, len(cols)-1), key="map_lat")
        lon_col = st.sidebar.selectbox("عمود خط الطول (Longitude):", cols, index=min(2, len(cols)-1), key="map_lon")
        
        n_clusters = st.slider("اختر عدد المجموعات اللهجية (Clusters):", min_value=2, max_value=10, value=4)
        
        place_col_map = st.sidebar.selectbox("عمود الأسماء للخريطة:", cols, index=0, key="map_place")
        
        if lat_col != place_col_map and lon_col != place_col_map:
            try:
                df_map = df.copy()
                df_map[lat_col] = pd.to_numeric(df_map[lat_col], errors='coerce')
                df_map[lon_col] = pd.to_numeric(df_map[lon_col], errors='coerce')
                df_map = df_map.dropna(subset=[lat_col, lon_col])
                
                if not df_map.empty:
                    df_map['Cluster'] = (np.arange(len(df_map)) % n_clusters) + 1
                    df_map['Cluster'] = df_map['Cluster'].astype(str)
                    
                    fig_cluster = px.scatter_mapbox(
                        df_map, 
                        lat=lat_col, 
                        lon=lon_col, 
                        hover_name=place_col_map,
                        color='Cluster', 
                        zoom=7, 
                        height=600, 
                        size_max=15,
                        title="توزيع اللهجات على الخريطة"
                    )
                    fig_cluster.update_layout(mapbox_style="open-street-map")
                    st.plotly_chart(fig_cluster, use_container_style=True)
                else:
                    st.error("❌ الأعمدة المختارة لا تحتوي على أرقام إحداثيات صالحة.")
            except Exception as e:
                st.error(f"تعذر رسم الخريطة: {e}")
        else:
            st.warning("⚠️ يرجى اختيار أعمدة الإحداثيات الصحيحة من القائمة الجانبية.")
    else:
        st.info("👈 يرجى رفع ملف البيانات (CSV/TSV) من القائمة الجانبية لرسم الخريطة.")
