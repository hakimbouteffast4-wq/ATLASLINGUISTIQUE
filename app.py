import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.manifold import MDS
import arabic_reshaper
from bidi.algorithm import get_display
import folium
from streamlit_folium import st_folium

# --- 1. دالة حساب مسافة التحرير (بديل مكتبة lingpy) ---
def edit_dist(s1, s2):
    """حساب مسافة التحرير (Levenshtein Distance) بين الكلمات"""
    s1, s2 = str(s1), str(s2)
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])
    return dp[m][n]

# --- 2. دالة معالجة النصوص العربية للعرض الصحيح ---
def fix_text(text):
    if pd.isna(text):
        return ""
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

# --- 3. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="منصة القياس اللساني والحساب اللهجي",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ منصة التحليل القياسي للهجات واللسانيات")
st.markdown("---")

# --- 4. رفع الملف وإدارته ---
uploaded_file = st.sidebar.file_uploader("قم برفع ملف البيانات (Excel أو CSV)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.sidebar.success("تم تحميل الملف بنجاح!")

        # معاينة البيانات
        st.subheader("📊 معاينة البيانات المرفوعة")
        st.dataframe(df.head())

        # تحديد الأعمدة
        columns = df.columns.tolist()
        loc_col = st.sidebar.selectbox("اختر عمود المواقع/اللهجات:", columns)
        feature_cols = st.sidebar.multiselect("اختر أعمدة المتغيرات اللغوية:", [c for c in columns if c != loc_col])

        if loc_col and feature_cols:
            locations = df[loc_col].astype(str).tolist()
            num_locs = len(locations)

            # مصفوفة المسافات
            dist_matrix = np.zeros((num_locs, num_locs))

            for i in range(num_locs):
                for j in range(num_locs):
                    if i != j:
                        total_dist = 0
                        for col in feature_cols:
                            val1 = df.iloc[i][col]
                            val2 = df.iloc[j][col]
                            total_dist += edit_dist(val1, val2)
                        dist_matrix[i, j] = total_dist / len(feature_cols)

            # --- التبويبات للعرض ---
            tab1, tab2, tab3 = st.tabs(["📏 مصفوفة المسافات", "🌳 الشجرة اللهجية (Dendrogram)", "🗺️ الخريطة التفاعلية"])

            with tab1:
                st.write("### مصفوفة البعد اللساني بين المواقع")
                dist_df = pd.DataFrame(dist_matrix, index=locations, columns=locations)
                st.dataframe(dist_df)

            with tab2:
                st.write("### التحليل العنقودي والشجرة اللهجية")
                fig, ax = plt.subplots(figsize=(10, 6))
                condensed_dist = squareform(dist_matrix)
                Z = linkage(condensed_dist, method='ward')
                
                fixed_labels = [fix_text(loc) for loc in locations]
                dendrogram(Z, labels=fixed_labels, ax=ax)
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig)

            with tab3:
                st.write("### خريطة المواقع")
                lat_col = st.sidebar.selectbox("عمود خط العرض (Latitude) - إن وجد:", ["لا يوجد"] + columns)
                lon_col = st.sidebar.selectbox("عمود خط الطول (Longitude) - إن وجد:", ["لا يوجد"] + columns)

                if lat_col != "لا يوجد" and lon_col != "لا يوجد":
                    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=6)
                    for idx, row in df.iterrows():
                        folium.Marker(
                            location=[row[lat_col], row[lon_col]],
                            popup=str(row[loc_col]),
                            tooltip=str(row[loc_col])
                        ).add_to(m)
                    st_folium(m, width=800, height=500)
                else:
                    st.info("يرجى تحديد أعمدة الإحداثيات لعرض الخريطة التفاعلية.")

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملف: {e}")
else:
    st.info("👋 مرحباً بك! يرجى رفع ملف Excel أو CSV من القائمة الجانبية للبدء في التحليل.")
