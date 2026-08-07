import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.manifold import MDS
from lingpy import edit_dist
import arabic_reshaper
from bidi.algorithm import get_display
import folium
from streamlit_folium import st_folium

# 1. إعداد واجهة المنصة
st.set_page_config(page_title="ATLASLINGUISTIQUE", layout="wide", page_icon="🗺️")

def ar(text):
    if not isinstance(text, str):
        return text
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

st.title("🗺️ ATLASLINGUISTIQUE")
st.markdown("##### **منصة التحليل الجغرافي اللساني والقياس اللهجي التفاعلي**")
st.divider()

# 2. الشريط الجانبي
st.sidebar.header("⚙️ ATLASLINGUISTIQUE")
st.sidebar.subheader("إعدادات البيانات والتحليل")
uploaded_file = st.sidebar.file_uploader("رفع ملف البيانات الميدانية (Excel)", type=["xlsx", "xls"])
num_clusters = st.sidebar.slider("عدد المجموعات اللسانية (Clusters):", min_value=2, max_value=8, value=3)

# 3. تحميل البيانات
if uploaded_file is None:
    data = {
        'Village': ['Skoura_MDaz', 'Guigou', 'Boulemane', 'El_Mers', 'Serghina', 'Enjil', 'Ksabi_Moulouya'],
        'Lat': [33.32, 33.15, 33.36, 33.42, 33.20, 33.08, 32.55],
        'Lon': [-4.56, -5.03, -4.73, -4.43, -4.50, -4.70, -4.26],
        'Word_1': ['nek', 'nek', 'nekki', 'nech', 'nekki', 'nek', 'nech'],
        'Word_2': ['aman', 'aman', 'aman', 'aman', 'aman', 'aman', 'aman'],
        'Word_3': ['taddart', 'tiddert', 'tigemmi', 'taddart', 'taddart', 'taddart', 'axxam']
    }
    df = pd.DataFrame(data)
else:
    df = pd.read_excel(uploaded_file)
    df = df.dropna(how='all', axis=1)

villages = df['Village'].astype(str).tolist()
coords_geo = df[['Lon', 'Lat']].to_numpy()
word_columns = [col for col in df.columns if col.startswith('Word')]

# 4. حساب المسافات
n = len(villages)
matrix = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        total_dist = 0
        valid_cols = 0
        for col in word_columns:
            w1, w2 = str(df.loc[i, col]), str(df.loc[j, col])
            if w1 != '...' and w2 != '...':
                total_dist += edit_dist(w1, w2)
                valid_cols += 1
        matrix[i][j] = total_dist / valid_cols if valid_cols > 0 else 0

matrix = (matrix + matrix.T) / 2.0

# 5. التجميع العنقودي
linked = linkage(matrix, method='ward')
cluster_ids = fcluster(linked, t=num_clusters, criterion='maxclust')
palette = ['#ff4d4d', '#3399ff', '#2eb82e', '#ff9900', '#9933ff', '#00ffff', '#ff3399', '#808000']
village_colors = [palette[(cid - 1) % len(palette)] for cid in cluster_ids]

# 6. عرض جدول البيانات
st.subheader("📋 جدول البيانات الميدانية - ATLASLINGUISTIQUE")
st.dataframe(df)

# 7. التبويبات التفاعلية
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 الخريطة الجغرافية التفاعلية", 
    "🗺️ خريطة Isogloss Voronoi", 
    "🌳 الشجرة العنقودية (Dendrogram)", 
    "📉 التحليل متعدد الأبعاد (MDS)"
])

# 📍 التبويب 1: الخريطة الجغرافية
with tab1:
    st.subheader("الخريطة الجغرافية المباشرة (OpenStreetMap)")
    center_lat = df['Lat'].mean()
    center_lon = df['Lon'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=9, tiles="OpenStreetMap")
    
    for i, row in df.iterrows():
        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=10,
            popup=f"<b>القرية:</b> {row['Village']}<br><b>العنقود اللساني:</b> C{cluster_ids[i]}",
            tooltip=f"{row['Village']} (C{cluster_ids[i]})",
            color="black",
            weight=1.5,
            fill=True,
            fill_color=village_colors[i],
            fill_opacity=0.85
        ).add_to(m)
    
    st_folium(m, width=900, height=500)

# 🗺️ التبويب 2: خريطة Voronoi
with tab2:
    st.subheader("خريطة الحدود اللهجية والمضلعات (Voronoi Isogloss Map)")
    if len(villages) >= 4:
        vor = Voronoi(coords_geo)
        fig, ax = plt.subplots(figsize=(9, 6))
        
        for i, region_index in enumerate(vor.point_region):
            region = vor.regions[region_index]
            if not -1 in region and len(region) > 0:
                polygon = [vor.vertices[j] for j in region]
                ax.fill(*zip(*polygon), color=village_colors[i], alpha=0.35, edgecolor='gray')
                
        voronoi_plot_2d(vor, ax=ax, show_vertices=False, line_colors='darkgray', line_width=1.5, line_style='--')
        
        for i in range(n):
            ax.scatter(coords_geo[i, 0], coords_geo[i, 1], color=village_colors[i], s=130, edgecolors='black', zorder=5)
            ax.annotate(f"{ar(villages[i])} (C{cluster_ids[i]})", 
                        (coords_geo[i, 0] + 0.008, coords_geo[i, 1] + 0.008), 
                        fontsize=10, fontweight='bold')
            
        plt.title(ar("خريطة الحدود والمضلعات اللهجية - ATLASLINGUISTIQUE"))
        plt.xlabel(ar("خط الطول (Longitude)"))
        plt.ylabel(ar("خط العرض (Latitude)"))
        plt.grid(True, linestyle=':', alpha=0.5)
        st.pyplot(fig)

# 🌳 التبويب 3: الشجرة العنقودية
with tab3:
    st.subheader("الشجرة العنقودية للقرى (Ward's Method)")
    fig2, ax2 = plt.subplots(figsize=(9, 4.5))
    dendrogram(linked, labels=villages, orientation='top', distance_sort='descending')
    plt.title(ar("شجرة التجميع العنقودي - ATLASLINGUISTIQUE"))
    plt.xlabel(ar("القرى / النقاط الميدانية"))
    plt.ylabel(ar("المسافة اللسانية"))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig2)

# 📉 التبويب 4: تحليل MDS
with tab4:
    st.subheader("التحليل متعدد الأبعاد (MDS)")
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    coords_mds = mds.fit_transform(matrix)
    
    fig3, ax3 = plt.subplots(figsize=(8, 4.5))
    for i in range(n):
        ax3.scatter(coords_mds[i, 0], coords_mds[i, 1], color=village_colors[i], s=120, edgecolors='black')
        ax3.annotate(ar(villages[i]), (coords_mds[i, 0] + 0.02, coords_mds[i, 1] + 0.02), fontsize=11)
    
    plt.title(ar("إسقاط الفضاء اللهجي ثنائي الأبعاد (MDS)"))
    plt.grid(True, linestyle=':', alpha=0.6)
    st.pyplot(fig3)
