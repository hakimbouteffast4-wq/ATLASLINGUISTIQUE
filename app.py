import folium
import geopandas as gpd
import os
import streamlit as st
from streamlit_folium import st_folium

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="التحكم القياسي واللساني", layout="wide", initial_sidebar_state="expanded"
)

# 2. القائمة الجانبية (Sidebar)
st.sidebar.title("⚙️ التحكم القياسي واللساني")

st.sidebar.subheader("تحديد المتغيرات الداخلة في الحساب:")
variables = st.sidebar.multiselect(
    label="المتغيرات",
    options=[
        "الجهر الصوتي",
        "تفخيم الراء",
        "إمالة الألف",
        "احتفاظ بالتلازم",
        "الهمز",
        "الإدغام",
    ],
    default=["الجهر الصوتي", "تفخيم الراء", "إمالة الألف", "احتفاظ بالتلازم"],
)

st.sidebar.subheader("الجماعة المرجعية (Anchor):")
communes_list = [
    "كيكو",
    "بولمان",
    "ميسور",
    "أوتات الحاج",
    "إموزار مرموشة",
    "سرغينة",
]
selected_anchor = st.sidebar.selectbox("اختر الجماعة", options=communes_list)

# 3. محتوى الصفحة الرئيسية (الأبواب/التبويبات)
tabs = st.tabs(
    [
        "🗺️ الخريطة",
        "🚆 المفسر الآلي",
        "📊 استقرار الظواهر",
        "📈 الارتباط",
        "🔀 المقارن الثنائي",
        "🌳 الشجرة اللهجية",
        "📉 MDS تحليل",
        "📏 IPA مسافة",
        "🔢 LaTeX مصفوفات",
        "📁 الملحق",
    ]
)

# 4. تبويب الخريطة
with tabs[0]:
    st.header(f"🗺️ خريطة إقليم بولمان وتوزيع التمايز بالنسبة لـ: [{selected_anchor}]")

    # إحداثيات مركز الخريطة (تقريباً إقليم بولمان / كيكو)
    center_lat, center_lon = 33.1, -4.6
    m = folium.Map(location=[center_lat, center_lon], zoom_start=8)

    # إضافة حدود GeoJSON إن وجدت
    geojson_path = "boundaries.geojson"
    if os.path.exists(geojson_path):
        gdf = gpd.read_file(geojson_path)
        folium.GeoJson(
            gdf,
            name="حدود إقليم بولمان",
            style_function=lambda x: {
                "fillColor": "#3186cc",
                "color": "black",
                "weight": 1.5,
                "fillOpacity": 0.1,
            },
        ).add_to(m)

    # إضافة علامات تفاعلية (Markers) للجماعات
    locations = {
        "كيكو": (33.2039, -4.6869, "red", 0.00),
        "بولمان": (33.3622, -4.7331, "orange", 0.15),
        "ميسور": (32.8583, -3.9961, "green", 0.42),
        "أوتات الحاج": (33.3486, -3.7022, "orange", 0.38),
        "إموزار مرموشة": (33.4833, -4.2833, "orange", 0.29),
    }

    for name, (lat, lon, color, distance) in locations.items():
        popup_html = f"""
        <div style="text-align: right; font-family: Tahoma; direction: rtl;">
            <b>الجماعة:</b> {name}<br>
            <b>المسافة اللسانية:</b> {distance:.2f}
        </div>
        """
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=200),
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(m)

    # عرض الخريطة داخل Streamlit
    st_folium(m, width=1100, height=520)
