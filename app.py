import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
from sklearn.manifold import MDS

st.set_page_config(page_title="Gabmap Clone - Dialectometry", layout="wide")

st.title("🗺️ Gabmap Interactive Replica - منصة القياس اللهجي")
st.write("رفع البيانات، حساب مسافات Levenshtein، ورسم الخرائط والشجرات اللهجية.")

# 1. رفع البيانات
uploaded_file = st.sidebar.file_uploader("رفع ملف البيانات (TSV أو CSV)", type=["tsv", "csv", "txt"])

def levenshtein(s1, s2):
    s1, s2 = str(s1), str(s2)
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + cost)
    return dp[m][n]

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep='\t' if uploaded_file.name.endswith(('.tsv', '.txt')) else ',')
    st.subheader("📋 معاينة البيانات المرفوعة")
    st.dataframe(df.head())
    
    locations = df['Place'].tolist()
    words_df = df.drop(columns=['Place'])
    
    # حساب المسافات
    num_locs = len(locations)
    dist_matrix = np.zeros((num_locs, num_locs))
    
    for i in range(num_locs):
        for j in range(i + 1, num_locs):
            total_dist = sum(levenshtein(words_df.iloc[i][col], words_df.iloc[j][col]) for col in words_df.columns)
            dist_matrix[i, j] = dist_matrix[j, i] = total_dist / len(words_df.columns)
            
    # الخيارات
    tab1, tab2, tab3 = st.tabs(["📊 مصفوفة الفروق", "🌳 الشجرة اللهجية (Dendrogram)", "🗺️ التدرج MDS"])
    
    with tab1:
        st.write("### مصفوفة مسافات Levenshtein")
        dist_df = pd.DataFrame(dist_matrix, index=locations, columns=locations)
        st.dataframe(dist_df)
        
    with tab2:
        st.write("### الشجرة اللهجية (Ward's Hierarchical Clustering)")
        condensed_dist = squareform(dist_matrix)
        Z = linkage(condensed_dist, method='ward')
        
        fig, ax = plt.subplots(figsize=(10, 5))
        dendrogram(Z, labels=locations, leaf_rotation=45, ax=ax)
        plt.title("Dialect Dendrogram")
        st.pyplot(fig)
        
    with tab3:
        st.write("### المخطط متعدد الأبعاد (Multidimensional Scaling - MDS)")
        mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
        pos = mds.fit_transform(dist_matrix)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(pos[:, 0], pos[:, 1], color='red', s=100)
        for i, txt in enumerate(locations):
            ax.annotate(txt, (pos[i, 0], pos[i, 1] + 0.02), fontsize=12)
        plt.title("MDS Map Projection")
        st.pyplot(fig)
