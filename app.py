import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# ---------------------------------------------------------
# 1. إعدادات الصفحة
# ---------------------------------------------------------
st.set_page_config(
    page_title="أطلس وقاموس الفلاحة الأمازيغية - إقليم بولمان",
    page_icon="🌾",
    layout="wide"
)

# ---------------------------------------------------------
# 2. تحميل البيانات
# ---------------------------------------------------------
@st.cache_data
def load_data():
    csv_file = "data.csv"
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        # ملء الخانات الفارغة لتجنب أخطاء العرض
        df = df.fillna("")
        return df
    else:
        # بيانات احتياطية في حال عدم وجود ملف CSV
        st.error("⚠️ لم يتم العثور على ملف data.csv! جاري عرض البيانات الافتراضية.")
        return pd.DataFrame([{
            "id": 1, "word_tifinagh": "ⵜⴰⴳⵓⵔⵜ", "word_latin": "Tagurt",
            "ipa": "/taɡurt/", "arabic_meaning": "مقبض المحراث التقليدي",
            "category": "أدوات الحرث والدرس", "location": "كيكو",
            "lat": 33.109, "lon": -4.685,
            "description": "قطعة خشبية أساسية في المحراث الخشبي التقليدي.",
            "proverb": "« ⵢⵓⵎⵥ ⵜⴰⴳⵓⵔⵜ ⵙ ⵓⴼⵓⵙ »", "image": "", "audio": ""
        }])

df = load_data()

# ---------------------------------------------------------
# 3. القائمة الجانبية (Sidebar)
# ---------------------------------------------------------
st.sidebar.markdown("## 🌾 قاموس الفلاحة والرعي")
st.sidebar.markdown("**إقليم بولمان - الأطلس اللغوي**")
st.sidebar.markdown("---")

# الفلاتر
categories = ["الكل"] + sorted([x for x in df['category'].unique() if x])
selected_category = st.sidebar.selectbox("🎯 الحقل المعجمي:", categories)

locations = ["الكل"] + sorted([x for x in df['location'].unique() if x])
selected_location = st.sidebar.selectbox("📍 المنطقة / القبيلة:", locations)

search_query = st.sidebar.text_input("🔍 البحث النصي (تيفيناغ / عربي / لاتيني):")

# تطبيق الفلترة
filtered_df = df.copy()

if selected_category != "الكل":
    filtered_df = filtered_df[filtered_df['category'] == selected_category]

if selected_location != "الكل":
    filtered_df = filtered_df[filtered_df['location'] == selected_location]

if search_query:
    filtered_df = filtered_df[
        filtered_df['arabic_meaning'].astype(str).str.contains(search_query, case=False) |
        filtered_df['word_tifinagh'].astype(str).str.contains(search_query, case=False) |
        filtered_df['word_latin'].astype(str).str.contains(search_query, case=False)
    ]

# ---------------------------------------------------------
# 4. الواجهة الرئيسية
# ---------------------------------------------------------
st.title("🌾 الأطلس اللغوي وقاموس الفلاحة والرعي الأمازيغي")
st.caption("دراسة توثيقية لمعجم العتاد الفلاحي وتقنيات السقي والرعي بإقليم بولمان")
st.markdown("---")

# الإحصائيات السريعة
m1, m2, m3 = st.columns(3)
m1.metric("إجمالي المفردات الموثقة", len(filtered_df))
m2.metric("الحقول المعجمية", len(df['category'].unique()))
m3.metric("المواقع الجغرافية", len(df['location'].unique()))

st.markdown("###")

# التبويبات الرئيسية
tab1, tab2 = st.tabs(["🗺️ الخريطة اللغوية التفاعلية", "📚 المعجم والبطاقات اللسانية"])

# ---------------------------------------------------------
# التبويب 1: الخريطة
# ---------------------------------------------------------
with tab1:
    st.subheader("الخريطة الجغرافية-اللسانية للمصطلحات الفلاحية")
    
    # إنشاء الخريطة متمركزة حول بولمان
    m = folium.Map(location=[33.25, -4.50], zoom_start=9, tiles="OpenStreetMap")
    
    for _, row in filtered_df.iterrows():
        try:
            lat = float(row['lat'])
            lon = float(row['lon'])
            popup_text = f"""
            <div style="font-family: sans-serif; text-align: right; width: 180px;">
                <h4 style="color: #1b5e20; margin: 0;">{row['word_tifinagh']}</h4>
                <b>{row['word_latin']}</b><br>
                <b>المعنى:</b> {row['arabic_meaning']}<br>
                <b>الموقع:</b> {row['location']}
            </div>
            """
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=f"{row['word_tifinagh']} ({row['arabic_meaning']})",
                icon=folium.Icon(color="green", icon="leaf")
            ).add_to(m)
        except ValueError:
            continue

    st_folium(m, width="100%", height=500)

# ---------------------------------------------------------
# التبويب 2: المعجم والبطاقات
# ---------------------------------------------------------
with tab2:
    st.subheader("سجل المصطلحات الفلاحية والرعوية")
    
    if filtered_df.empty:
        st.info("لا توجد نتائج تطابق المعايير المختارة.")
    else:
        for _, row in filtered_df.iterrows():
            with st.expander(f"📌 {row['word_tifinagh']} | {row['word_latin']} — {row['arabic_meaning']}"):
                col_text, col_media = st.columns([2, 1])
                
                with col_text:
                    st.markdown(f"### **{row['word_tifinagh']}** *( {row['word_latin']} )*")
                    st.markdown(f"**الرمز الصوتي (IPA):** `{row['ipa']}`")
                    st.markdown(f"**المعنى بالعربية:** {row['arabic_meaning']}")
                    st.markdown(f"**الحقل المعجمي:** `{row['category']}`")
                    st.markdown(f"**القبيلة/المنطقة:** 📍 {row['location']}")
                    st.markdown("---")
                    st.markdown(f"**الوصف الاستعمالي:** {row['description']}")
                    if row['proverb']:
                        st.markdown(f"**الشاهد النصي / المثل:** *{row['proverb']}*")
                    
                    if row['audio'] and os.path.exists(str(row['audio'])):
                        st.audio(row['audio'])
                
                with col_media:
                    if row['image']:
                        st.image(row['image'], caption=row['arabic_meaning'], use_column_width=True)

# ---------------------------------------------------------
# التذييل
# ---------------------------------------------------------
st.markdown("---")
st.caption("مركز التوثيق الرقمي والأطلس اللغوي | أطروحة الدكتوراه - إقليم بولمان")
