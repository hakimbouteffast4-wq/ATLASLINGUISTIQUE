import streamlit as st
import pandas as pd
import numpy as np
import Levenshtein
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.manifold import MDS
import matplotlib.pyplot as plt
import plotly.express as px

# ---------------------------------------------------------
# دالة حساب مصفوفة مسافات ليفنشتاين النسبية بين المناطق
# ---------------------------------------------------------
def calculate_levenshtein_matrix(df, place_col, word_cols):
    places = df[place_col].dropna().unique()
    n = len(places)
    dist_matrix = np.zeros((n, n))
    
    # تجميع الكلمات لكل منطقة
    place_words = {}
    for p in places:
        sub_df = df[df[place_col] == p]
        # دمج الكلمات الصوتية في قائمة واحدة
        words = []
        for col in word_cols:
            words.extend(sub_df[col].dropna().astype(str).tolist())
        place_words[p] = words

    # حساب المسافة بين كل منطقتين
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
                    # مسافة ليفنشتاين النسبية: Levenshtein(w1, w2) / max_len
                    norm_dist = Levenshtein.distance(w1, w2) / max_l
                    distances.append(norm_dist)
            
            avg_dist = np.mean(distances) if distances else 0.0
            dist_matrix[i, j] = avg_dist
            dist_matrix[j, i] = avg_dist
            
    return places, dist_matrix

# ---------------------------------------------------------
# تبويب محرك القياس اللساني والتحليل متعدد الأبعاد (MDS)
# ---------------------------------------------------------
# يمكنك وضع هذا الجزء داخل تبويب الشجرة اللهجية أو تبويب مستقل:
st.header("🔬 محرك القياس اللساني (Méthode Levenshtein & MDS)")

if uploaded_file is not None and df is not None:
    cols = list(df.columns)
    
    st.subheader("⚙️ إعدادات التحليل اللساني")
    col_a, col_b = st.columns(2)
    
    with col_a:
        place_col = st.selectbox("اختر عمود أسماء القرى/المناطق:", cols, index=0)
    with col_b:
        word_cols = st.multiselect("اختر أعمدة الكلمات/المفردات للمقارنة:", cols, default=[cols[-1]])

    if st.button("🚀 تشغيل تحليل Levenshtein و MDS"):
        if len(word_cols) > 0:
            with st.spinner("جاري حساب المسافات اللسانية ومصفوفة التباين..."):
                places, dist_matrix = calculate_levenshtein_matrix(df, place_col, word_cols)
                
                # 1. عرض مصفوفة المسافات اللسانية
                st.subheader("1️⃣ مصفوفة المسافات اللسانية (Difference Matrix)")
                df_dist = pd.DataFrame(dist_matrix, index=places, columns=places)
                st.dataframe(df_dist.style.background_gradient(cmap="Blues"))
                
                # 2. الشجرة اللهجية الحقيقية (Dendrogram)
                st.subheader("2️⃣ الشجرة اللهجية الحقيقية (Dendrogram)")
                condensed_dist = squareform(dist_matrix)
                Z = linkage(condensed_dist, method='ward')
                
                fig, ax = plt.subplots(figsize=(10, 5))
                dendrogram(Z, labels=places, ax=ax, leaf_rotation=90)
                plt.title("التجميع الشجري القائم على مسافة Levenshtein")
                plt.ylabel("درجة التباين اللساني النسبية")
                st.pyplot(fig)
                
                # 3. التحليل متعدد الأبعاد (MDS -> RGB Color Map)
                st.subheader("3️⃣ خريطة الألوان المركبة (MDS RGB Map)")
                if len(places) >= 3:
                    mds = MDS(n_components=3, dissimilarity='precomputed', random_state=42)
                    mds_coords = mds.fit_transform(dist_matrix)
                    
                    # تحويل إحداثيات MDS إلى ألوان RGB (بين 0 و 255)
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
