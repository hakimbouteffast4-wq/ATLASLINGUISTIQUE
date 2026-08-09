import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.manifold import MDS
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Gabmap Advanced Mapping", layout="wide")

st.title("🗺️ منصة القياس اللهجي الجغرافية (Gabmap Style)")
st.write("تحليل المسافات اللسانية، وتوليد خرائط التجميع الجغرافي وخريطة الألوان المركبة (MDS RGB Map).")

# دالة حساب Levenshtein
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

uploaded_file = st.sidebar.file_uploader("رفع ملف البيانات (TSV أو CSV)", type=["tsv", "csv", "txt"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, sep='\t' if uploaded_file.name.endswith(('.tsv', '.txt')) else ',')
    
    st.sidebar.subheader("⚙️ إعدادات الأعمدة")
    place_col = st.sidebar.selectbox("عمود أسماء القرى/المناطق:", df.columns, index=0)
    
    # البحث عن أعمدة خطوط الطول والعرض
    lat_col = st.sidebar.selectbox("عمود خط العرض (Latitude):", [c for c in df.columns if 'lat' in c.lower()] + list(df.columns), index=0)
    lon_col = st.sidebar.selectbox("عمود خط الطول (Longitude):", [c for c in df.columns if 'lon' in c.lower() or 'lng' in c.lower()] + list(df.columns), index=0)

    locations = df[place_col].tolist()
    
    # استبعاد أعمدة الموقع والمكان للتحليل اللساني
    non_word_cols = [place_col, lat_col, lon_col]
    words_df = df.drop(columns=[c for c in non_word_cols if c in df.columns])
    
    # حساب مصفوفة المسافات
    num_locs = len(locations)
    dist_matrix = np.zeros((num_locs, num_locs))
    
    for i in range(num_locs):
        for j in range(i + 1, num_locs):
            total_dist = sum(levenshtein(words_df.iloc[i][col], words_df.iloc[j][col]) for col in words_df.columns)
            dist_matrix[i, j] = dist_matrix[j, i] = total_dist / len(words_df.columns)

    # تبويبات العرض
    tab_map_cluster, tab_map_rgb, tab_dendrogram = st.tabs([
        "🎨 خريطة التجميع الجغرافي (Cluster Map)", 
        "🌈 خريطة الألوان المركبة (MDS RGB Map)", 
        "🌳 الشجرة اللهجية (Dendrogram)"
    ])

    # 1. خريطة التجميع الجغرافي (Cluster Map)
    with tab_map_cluster:
        st.write("### خريطة التقسيم اللهجي (Cluster Map)")
        n_clusters = st.slider("اختر عدد المجموعات اللهجية (Clusters):", 2, 8, 4)
        
        condensed_dist = squareform(dist_matrix)
        Z = linkage(condensed_dist, method='ward')
        clusters = fcluster(Z, n_clusters, criterion='maxclust')
        
        df_map = df.copy()
        df_map['Cluster'] = [f"مجموعة {c}" for c in clusters]
        
        if lat_col in df.columns and lon_col in df.columns:
            fig_cluster = px.scatter_mapbox(
                df_map, lat=lat_col, lon=lon_col, hover_name=place_col,
                color='Cluster', zoom=7, height=600, size_max=15,
                title="توزيع اللهجات على الخريطة حسب التجميع الشجري"
            )
            fig_cluster.update_traces(marker=dict(size=14))
            fig_cluster.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig_cluster, use_container_style=True)
        else:
            st.warning("⚠️ يرجى التأكد من وجود أعمدة الإحداثيات (Lat و Lon) في ملفك لعرض الخريطة الجغرافية.")

    # 2. خريطة MDS RGB Map (الميزة الأيقونية في Gabmap)
    with tab_map_rgb:
        st.write("### خريطة الألوان المركبة (MDS RGB Map)")
        st.info("💡 طريقة Gabmap: يتم تحويل الأبعاد الثلاثة للمسافات اللسانية إلى قيم ألوان (أحمر، أخضر، أزرق). القرى ذات الألوان المتقاربة تتحدث لهجات متقاربة جداً!")
        
        mds = MDS(n_components=3, dissimilarity='precomputed', random_state=42)
        pos3d = mds.fit_transform(dist_matrix)
        
        # تحويل الأبعاد إلى قيم RGB بين 0 و 255
        norm_pos = (pos3d - pos3d.min(axis=0)) / (pos3d.max(axis=0) - pos3d.min(axis=0) + 1e-9)
        rgb_colors = [f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})" for r, g, b in norm_pos]
        
        df_map['RGB_Color'] = rgb_colors
        
        if lat_col in df.columns and lon_col in df.columns:
            fig_rgb = go.Figure(go.Scattermapbox(
                lat=df_map[lat_col],
                lon=df_map[lon_col],
                mode='markers+text',
                marker=go.scattermapbox.Marker(
                    size=18,
                    color=rgb_colors
                ),
                text=df_map[place_col],
                textposition="top center"
            ))
            fig_rgb.update_layout(
                mapbox_style="open-street-map",
                mapbox=dict(center=dict(lat=df_map[lat_col].mean(), lon=df_map[lon_col].mean()), zoom=7),
                height=600,
                margin={"r":0,"t":30,"l":0,"b":0}
            )
            st.plotly_chart(fig_rgb, use_container_style=True)

    # 3. الشجرة اللهجية
    with tab_dendrogram:
        st.write("### الشجرة اللهجية (Ward's Dendrogram)")
        fig, ax = plt.subplots(figsize=(10, 5))
        dendrogram(Z, labels=locations, leaf_rotation=45, ax=ax)
        st.pyplot(fig)
