import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import arabic_reshaper
from bidi.algorithm import get_display
import folium
from streamlit_folium import st_folium
import os
import json

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

# --- 2. معالجة النصوص العربية للعرض الصحيح ---
def fix_text(text):
    if pd.isna(text):
        return ""
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

# --- 3. إعدادات الصفحة ---
st.set_page_config(
    page_title="منصة أطلس التحليل القياسي للهجات",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ منصة أطلس التحليل القياسي للهجات واللسانيات")
st.markdown("---")

# --- 4. اختيار طريقة إدخال البيانات ---
st.sidebar.header("⚙️ طريقة إدخال البيانات")
input_method = st.sidebar.radio("اختر مصدر البيانات:", ["✍️ استمارة إدخال مباشرة", "📁 رفع ملف Excel/CSV"])

df = None

if input_method == "✍️ استمارة إدخال مباشرة":
    st.subheader("📝 استمارة إدخال البيانات اللهجية")
    st.info("قم بتعديل البيانات أو إضافة مناطق جديدة في الجدول أدناه، وستتحدث الخريطة والشجرة فوراً!")

    # بيانات افتراضية أولية للاستمارة
    initial_data = {
        "Village": ["Skoura_MDaz", "Guigou", "Boulemane", "El_Mers", "Serghina", "Imouzzer_Marmoucha", "Timahdite"],
        "Lat": [33.3214, 33.1502, 33.3611, 33.4188, 33.2045, 33.4756, 33.2382],
        "Lon": [-4.5612, -5.0281, -4.7299, -4.4285, -4.4981, -4.2831, -5.0594],
        "Word_1 (أنا)": ["nek", "nek", "nekki", "nech", "nekki", "nech", "nek"],
        "Word_2 (الماء)": ["aman", "aman", "aman", "aman", "aman", "aman", "aman"],
        "Word_3 (البيت)": ["taddart", "tiddert", "tigemmi", "taddart", "taddart", "taddart", "tiddert"],
        "Word_4 (الخيمة/الدار)": ["axxam", "axxam", "tigemmi", "axxam", "axxam", "axxam", "axxam"]
    }
    
    df = st.data_editor(pd.DataFrame(initial_data), num_rows="dynamic", use_container_width=True)

else:
    uploaded_file = st.sidebar.file_uploader("قم برفع ملف البيانات (Excel أو CSV)", type=["xlsx", "csv"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("تم تحميل الملف بنجاح! ✅")
        st.subheader("📊 معاينة البيانات المرفوعة")
        st.dataframe(df)

# --- 5. خيارات طبقة الحدود الجغرافية (GeoJSON) ---
st.sidebar.markdown("---")
st.sidebar.header("🗺️ حدود الجماعات والإقليم")
geojson_file = st.sidebar.file_uploader("رفع ملف حدود الجماعات (GeoJSON)", type=["geojson", "json"])

# --- 6. المعالجة والتحليل الفوري ---
if df is not None and not df.empty:
    columns = df.columns.tolist()

    default_loc = next((c for c in columns if c.lower() in ['village', 'site', 'location', 'dialect', 'اللهجة', 'الموقع', 'القبيلة']), columns[0])
    default_lat = next((c for c in columns if c.lower() in ['lat', 'latitude', 'خط العرض']), None)
    default_lon = next((c for c in columns if c.lower() in ['lon', 'lng', 'longitude', 'خط الطول']), None)
    
    excluded = [default_loc, default_lat, default_lon]
    default_features = [c for c in columns if c not in excluded and c is not None]

    st.sidebar.markdown("---")
    st.sidebar.header("🎯 أعمدة التحليل")
    loc_col = st.sidebar.selectbox("عمود المواقع/القبائل:", columns, index=columns.index(default_loc))
    feature_cols = st.sidebar.multiselect("أعمدة المتغيرات اللغوية:", [c for c in columns if c != loc_col], default=default_features)

    lat_col = st.sidebar.selectbox("خط العرض:", ["لا يوجد"] + columns, index=(columns.index(default_lat) + 1) if default_lat else 0)
    lon_col = st.sidebar.selectbox("خط الطول:", ["لا يوجد"] + columns, index=(columns.index(default_lon) + 1) if default_lon else 0)

    if loc_col and feature_cols and len(df) > 1:
        locations = df[loc_col].astype(str).tolist()
        num_locs = len(locations)

        # حساب مصفوفة المسافات
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
        
        # عرض العدادات فوق التبويبات (مثل الشاشة التراكمية للتطبيق)
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric(label="عدد القبائل/المواقع المدروسة", value=f"{num_locs}")
        with col_stat2:
            st.metric(label="عدد المفردات والكلمات المدروسة", value=f"{len(feature_cols)}")

        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["📏 مصفوفة المسافات", "🌳 الشجرة اللهجية (Dendrogram)", "🗺️ خريطة أطلس الفضائية والحدود"])

        with tab1:
            st.subheader("📏 مصفوفة البعد اللساني بين المواقع")
            dist_df = pd.DataFrame(dist_matrix, index=locations, columns=locations)
            st.dataframe(dist_df.style.background_gradient(cmap="Blues"), use_container_width=True)

        with tab2:
            st.subheader("🌳 التحليل العنقودي والشجرة اللهجية")
            fig, ax = plt.subplots(figsize=(10, 4))
            condensed_dist = squareform(dist_matrix)
            Z = linkage(condensed_dist, method='ward')
            fixed_labels = [fix_text(loc) for loc in locations]
            dendrogram(Z, labels=fixed_labels, ax=ax)
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)

        with tab3:
            st.subheader("🗺️ خريطة أطلس الفضائية مع حدود الجماعات والإقليم")
            if lat_col != "لا يوجد" and lon_col != "لا يوجد":
                valid_coords = df.dropna(subset=[lat_col, lon_col])
                if not valid_coords.empty:
                    avg_lat = pd.to_numeric(valid_coords[lat_col], errors='coerce').mean()
                    avg_lon = pd.to_numeric(valid_coords[lon_col], errors='coerce').mean()
                    
                    # 1️⃣ إنشاء الخريطة
                    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=9, tiles=None)

                    # 2️⃣ إضافة طبقة الأقمار الصناعية (Google Satellite)
                    folium.TileLayer(
                        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                        attr='Google Satellite',
                        name='🛰️ خريطة أطلس الفضائية (Satellite)',
                        overlay=False,
                        control=True
                    ).add_to(m)

                    # 3️⃣ إضافة الطبقة الجغرافية العادية
                    folium.TileLayer(
                        tiles='OpenStreetMap',
                        name='🗺️ الخريطة العادية (Street Map)',
                        overlay=False,
                        control=True
                    ).add_to(m)

                    # 4️⃣ إضافة طبقة حدود الجماعات والإقليم (GeoJSON)
                    geojson_data = None
                    
                    # خيار أ: إذا تم رفع الملف من الشريط الجانبي
                    if geojson_file is not None:
                        geojson_data = json.load(geojson_file)
                    # خيار ب: إذا كان ملف GeoJSON موجوداً في مجلد المشروع باسم boundaries.geojson
                    elif os.path.exists("boundaries.geojson"):
                        with open("boundaries.geojson", "r", encoding="utf-8") as f:
                            geojson_data = json.load(f)

                    if geojson_data is not None:
                        folium.GeoJson(
                            geojson_data,
                            name="🟩 حدود الجماعات المحلية والإقليم",
                            style_function=lambda x: {
                                'fillColor': '#00ffaa',
                                'color': '#ffcc00',      # لون الحدود (أصفر زاهي مثل تطبيقك)
                                'weight': 2.5,          # سمك الخط
                                'fillOpacity': 0.12     # الشفافية
                            },
                            tooltip=folium.GeoJsonTooltip(
                                fields=list(geojson_data['features'][0]['properties'].keys())[:2],
                                aliases=['اسم المنطقة/الجماعة:', 'الرمز/البيانات:'],
                                localize=True
                            )
                        ).add_to(m)

                    # 5️⃣ إضافة دبابيس المواقع والنقاط التفاعلية
                    for idx, row in valid_coords.iterrows():
                        try:
                            info_html = f"<div style='font-family: Arial; direction: rtl; text-align: right; min-width: 160px;'>"
                            info_html += f"<h3 style='margin:0; color:#1a73e8;'>📍 {row[loc_col]}</h3><hr style='margin:5px 0;'>"
                            for col in feature_cols:
                                info_html += f"<b>{col}:</b> {row[col]}<br>"
                            info_html += "</div>"

                            folium.Marker(
                                location=[float(row[lat_col]), float(row[lon_col])],
                                popup=folium.Popup(info_html, max_width=250),
                                tooltip=str(row[loc_col]),
                                icon=folium.Icon(color="red", icon="info-sign")
                            ).add_to(m)
                        except Exception as e:
                            pass

                    # 6️⃣ إضافة التحكم بالطبقات (Layer Control)
                    folium.LayerControl(position='topright').add_to(m)
                    
                    # عرض الخريطة
                    st_folium(m, width="100%", height=580)
