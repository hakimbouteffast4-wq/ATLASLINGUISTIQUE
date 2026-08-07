import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import arabic_reshaper
from bidi.algorithm import get_display
import folium
from streamlit_folium import st_folium

# --- 1. دالة حساب مسافة التحرير (Levenshtein Distance) ---
def edit_dist(s1, s2):
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

# --- 2. معالجة النصوص العربية ---
def fix_text(text):
    if pd.isna(text):
        return ""
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

# --- 3. إعدادات الصفحة ---
st.set_page_config(
    page_title="منصة التحليل القياسي للهجات",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ منصة التحليل القياسي للهجات واللسانيات")
st.markdown("---")

# --- 4. رفع الملف ---
uploaded_file = st.sidebar.file_uploader("قم برفع ملف البيانات (Excel أو CSV)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.sidebar.success("تم تحميل الملف بنجاح! ✅")

        # معاينة البيانات
        st.subheader("📊 معاينة البيانات المرفوعة")
        st.dataframe(df)

        columns = df.columns.tolist()

        # التناظر التلقائي مع أسماء الأعمدة (كشف تلقائي)
        default_loc = next((c for c in columns if c.lower() in ['village', 'site', 'location', 'dialect', 'اللهجة', 'الموقع']), columns[0])
        default_lat = next((c for c in columns if c.lower() in ['lat', 'latitude', 'خط العرض']), None)
        default_lon = next((c for c in columns if c.lower() in ['lon', 'lng', 'longitude', 'خط الطول']), None)
        
        # استثناء أعمدة الموقع والإحداثيات من قائمة الكلمات
        excluded = [default_loc, default_lat, default_lon]
        default_features = [c for c in columns if c not in excluded and c is not None]

        # خيارات القائمة الجانبية
        st.sidebar.header("⚙️ إعدادات التحليل")
        loc_col = st.sidebar.selectbox("اختر عمود المواقع/اللهجات:", columns, index=columns.index(default_loc))
        feature_cols = st.sidebar.multiselect("اختر أعمدة المتغيرات اللغوية:", [c for c in columns if c != loc_col], default=default_features)

        lat_col = st.sidebar.selectbox("عمود خط العرض (Latitude):", ["لا يوجد"] + columns, index=(columns.index(default_lat) + 1) if default_lat else 0)
        lon_col = st.sidebar.selectbox("عمود خط الطول (Longitude):", ["لا يوجد"] + columns, index=(columns.index(default_lon) + 1) if default_lon else 0)

        # تنفيذ التحليل عند اختيار الميزات
        if loc_col and feature_cols:
            locations = df[loc_col].astype(str).tolist()
            num_locs = len(locations)

            # حساب مصفوفة المسافات اللسانية
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

            st.markdown("---")

            # عرض النتائج في تبويبات واضحة
            tab1, tab2, tab3 = st.tabs(["📏 مصفوفة المسافات", "🌳 الشجرة اللهجية (Dendrogram)", "🗺️ الخريطة التفاعلية"])

            with tab1:
                st.subheader("📏 مصفوفة البعد اللساني بين المواقع")
                dist_df = pd.DataFrame(dist_matrix, index=locations, columns=locations)
                st.dataframe(dist_df.style.background_gradient(cmap="Blues"))

            with tab2:
                st.subheader("🌳 التحليل العنقودي والشجرة اللهجية")
                fig, ax = plt.subplots(figsize=(10, 5))
                condensed_dist = squareform(dist_matrix)
                Z = linkage(condensed_dist, method='ward')
                
                fixed_labels = [fix_text(loc) for loc in locations]
                dendrogram(Z, labels=fixed_labels, ax=ax)
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig)

            with tab3:
                st.subheader("🗺️ الخريطة التفاعلية لمواقع اللهجات")
                if lat_col != "لا يوجد" and lon_col != "لا يوجد":
                    # إنشاء الخريطة وتحديد المركز
                    avg_lat = df[lat_col].mean()
                    avg_lon = df[lon_col].mean()
                    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=8)

                    # إضافة العلامات على الخريطة
                    for idx, row in df.iterrows():
                        folium.Marker(
                            location=[row[lat_col], row[lon_col]],
                            popup=f"<b>{row[loc_col]}</b>",
                            tooltip=str(row[loc_col]),
                            icon=folium.Icon(color="red", icon="info-sign")
                        ).add_to(m)

                    # عرض الخريطة
                    st_folium(m, width=900, height=500)
                else:
                    st.warning("⚠️ يرجى تحديد أعمدة خط العرض وخط الطول من القائمة الجانبية لعرض الخريطة.")

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملف: {e}")
else:
    st.info("👋 مرحباً بك! يرجى رفع ملف Excel أو CSV للبدء في إظهار الخريطة والتحاليل.")
