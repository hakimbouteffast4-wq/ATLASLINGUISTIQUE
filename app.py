import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------------
# 1. إعدادات الصفحة وتنسيق اللغة العربية (RTL)
# ---------------------------------------------------------
st.set_page_config(
    page_title="أطلس وقاموس الفلاحة الأمازيغية - إقليم بولمان",
    page_icon="🌾",
    layout="wide"
)

# ضبط الاتجاه من اليمين إلى اليسار (RTL) وتنسيق الخطوط
st.markdown("""
    <style>
    .main, .stApp, div[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    h1, h2, h3, .stMarkdown {
        font-family: 'Segoe UI', 'Amiri', 'Noto Sans Tifinagh', sans-serif;
    }
    /* تعديل عنوان الموقع لمنع التداخل */
    .stTitle {
        direction: rtl;
        text-align: right;
        font-size: 2.2rem !important;
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. قاعدة البيانات الميدانية المدمجة
# ---------------------------------------------------------
@st.cache_data
def load_data():
    data = [
        {
            "id": 1, "word_tifinagh": "ⵜⴰⴳⵓⵔⵜ", "word_latin": "Tagurt", "ipa": "/taɡurt/",
            "arabic_meaning": "مقبض المحراث التقليدي", "category": "أدوات الحرث والدرس",
            "location": "كيكو (آيت يوسي)", "lat": 33.109, "lon": -4.685,
            "description": "قطعة خشبية أساسية في المحراث الخشبي التقليدي يمسك بها الفلاح لتوجيه السكة أثناء الحرث.",
            "proverb": "« ⵢⵓⵎⵥ ⵜⴰⴳⵓⵔⵜ ⵙ ⵓⴼⵓⵙ » (أمسك بمقبض الحرث بيده - دليل على الجدية)",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Charrue_bois_maroc.jpg/320px-Charrue_bois_maroc.jpg"
        },
        {
            "id": 2, "word_tifinagh": "ⵜⴰⵔⴳⴰ", "word_latin": "Targa", "ipa": "/targa/",
            "arabic_meaning": "الساقية / قناة السقي", "category": "تقنيات السقي والماء",
            "location": "إموزار مرموشة (آيت سغروشن)", "lat": 33.479, "lon": -4.283,
            "description": "قناة مائية حفرية تقليدية تُنقل عبرها المياه من العيون والمجاري المائية نحو الحقول.",
            "proverb": "« ⴰⵎⴰⵏ ⴷⴷⴰⵏ ⴳ ⵜⴰⵔⴳⴰ » (عادت المياه إلى الساقية - انفراج الأزمة)",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Irrigation_canal.jpg/320px-Irrigation_canal.jpg"
        },
        {
            "id": 3, "word_tifinagh": "ⴰⵎⴳⵔ", "word_latin": "Amger", "ipa": "/amɡr/",
            "arabic_meaning": "المنجل التقليدي", "category": "أدوات الحصاد والدرس",
            "location": "المرس", "lat": 33.150, "lon": -4.430,
            "description": "أداة حديدية مقوسة ذات أسنان حادة تُستخدم في حصاد الشعير والقمح والأعلاف.",
            "proverb": "« ⵢⵓⵖⴰⵍ ⵓⵎⴳⵔ ⵙ ⵜⴰⴳⴰ » (عادت الأداة إلى نصابها)",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Sickle.jpg/320px-Sickle.jpg"
        },
        {
            "id": 4, "word_tifinagh": "ⵜⴰⵢⵓⴳⴰ", "word_latin": "Tayuga", "ipa": "/tajuga/",
            "arabic_meaning": "زوج أبطال الحرث (ثوران/بغلان)", "category": "أدوات الحرث والدرس",
            "location": "إنجيل", "lat": 33.020, "lon": -4.520,
            "description": "زوج من حيوانات العمل يُقرنان بـ 'النوك' (المقود الخشبي) لجر المحراث.",
            "proverb": "« ⵜⴰⵢⵓⴳⴰ ⵜⴷⴷⴰ ⴳ ⵓⴳⵓⵔ » (اكتمل زوج الحرث في المزرعة)",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Pllowing_oxen.jpg/320px-Pllowing_oxen.jpg"
        },
        {
            "id": 5, "word_tifinagh": "ⵜⵉⵙⵙⵉⵔⵜ", "word_latin": "Tissirt", "ipa": "/tissirt/",
            "arabic_meaning": "الطاحونة المائية / الحجرية", "category": "تقنيات المعالجة والتحويل",
            "location": "بولمان المركز", "lat": 33.366, "lon": -4.733,
            "description": "منشأة تقليدية تعتمد على قوة دفع مياه الساقية لتدوير حجرين مدورين لطحن الحبوب.",
            "proverb": "« ⵜⵉⵙⵙⵉⵔⵜ ⵜⵣⵔⴹ ⴰⵎⴰⵏ ⴷⴷⴰⵏ » (الطاحونة تطحن والماء ينساب)",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Watermill_stone.jpg/320px-Watermill_stone.jpg"
        },
        {
            "id": 6, "word_tifinagh": "ⴰⵣⴰⵖⴰⵔ", "word_latin": "Azaghar", "ipa": "/azaɣar/",
            "arabic_meaning": "السهل / الرعي الشتوي", "category": "مجالات الرعي والمنتجعات",
            "location": "أوطاط الحاج", "lat": 33.350, "lon": -3.700,
            "description": "المناطق السهلية المنخفضة التي ينتقل إليها الرعاة والمواشي في فصل الشتاء هرباً من البرد.",
            "proverb": "« ⵢⵓⴷⴰ ⵓⵣⴰⵖⴰⵔ ⵙ ⵜⵓⴳⴰ » (اخضرت السهول بالكلأ)",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Steppe_landscape.jpg/320px-Steppe_landscape.jpg"
        },
        {
            "id": 7, "word_tifinagh": "ⴰⴼⵔⴰⴳ", "word_latin": "Afrag", "ipa": "/afraɡ/",
            "arabic_meaning": "الزريبة / السياج الشوكي", "category": "الرعي والمواشي",
            "location": "سقورة حداذرة", "lat": 33.280, "lon": -4.800,
            "description": "سياج مصنوع من أغصان الشوك والأشجار لحماية الماشية ليلاً من المفترسات والبرد.",
            "proverb": "« ⵢⵓⵍⵢ ⵓⴼⵔⴰⴳ ⵙ ⵜⵖⴰⵟⵜ » (امتلأت الزريبة بالماشية)",
            "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Enclosure_wood.jpg/320px-Enclosure_wood.jpg"
        }
    ]
    return pd.DataFrame(data)

df = load_data()

# ---------------------------------------------------------
# 3. القائمة الجانبية (Sidebar Filters)
# ---------------------------------------------------------
st.sidebar.markdown("## 🌾 قاموس الفلاحة والرعي")
st.sidebar.markdown("**إقليم بولمان - الأطلس اللغوي**")
st.sidebar.markdown("---")

categories = ["الكل"] + list(df['category'].unique())
selected_category = st.sidebar.selectbox("🎯 الحقل المعجمي:", categories)

locations = ["الكل"] + list(df['location'].unique())
selected_location = st.sidebar.selectbox("📍 المنطقة / القبيلة:", locations)

search_query = st.sidebar.text_input("🔍 البحث النصي (تيفيناغ / عربي / لاتيني):")

filtered_df = df.copy()

if selected_category != "الكل":
    filtered_df = filtered_df[filtered_df['category'] == selected_category]

if selected_location != "الكل":
    filtered_df = filtered_df[filtered_df['location'] == selected_location]

if search_query:
    filtered_df = filtered_df[
        filtered_df['arabic_meaning'].str.contains(search_query, case=False) |
        filtered_df['word_tifinagh'].str.contains(search_query, case=False) |
        filtered_df['word_latin'].str.contains(search_query, case=False)
    ]

# ---------------------------------------------------------
# 4. الواجهة الرئيسية
# ---------------------------------------------------------
st.title("🌾 الأطلس اللغوي وقاموس الفلاحة والرعي الأمازيغي")
st.caption("دراسة توثيقية لمعجم العتاد الفلاحي وتقنيات السقي والرعي بإقليم بولمان")
st.markdown("---")

# المؤشرات
m1, m2, m3 = st.columns(3)
m1.metric("إجمالي المفردات الموثقة", len(filtered_df))
m2.metric("الحقول المعجمية", len(df['category'].unique()))
m3.metric("المواقع الجغرافية", len(df['location'].unique()))

st.markdown("###")

tab1, tab2 = st.tabs(["🗺️ الخريطة اللغوية التفاعلية", "📚 المعجم والبطاقات اللسانية"])

# ---------------------------------------------------------
# التبويب 1: الخريطة
# ---------------------------------------------------------
with tab1:
    st.subheader("الترسيم الجغرافي للمصطلحات الفلاحية بإقليم بولمان")
    
    m = folium.Map(location=[33.25, -4.50], zoom_start=9, tiles="OpenStreetMap")
    
    for _, row in filtered_df.iterrows():
        popup_html = f"""
        <div style="font-family: sans-serif; text-align: right; width: 170px;">
            <h4 style="color: #2e7d32; margin: 0;">{row['word_tifinagh']} ({row['word_latin']})</h4>
            <b>المعنى:</b> {row['arabic_meaning']}<br>
            <b>الموقع:</b> {row['location']}
        </div>
        """
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{row['word_tifinagh']} - {row['arabic_meaning']}",
            icon=folium.Icon(color="green", icon="leaf")
        ).add_to(m)
        
    st_folium(m, width="100%", height=500)

# ---------------------------------------------------------
# التبويب 2: البطاقات اللسانية
# ---------------------------------------------------------
with tab2:
    st.subheader("سجل المصطلحات الفلاحية والرعوية")
    
    if filtered_df.empty:
        st.warning("لا توجد نتائج تطابق خيارات البحث.")
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
                    st.markdown(f"**الوصف الميداني:** {row['description']}")
                    st.markdown(f"**الشاهد النصي / المثل:** *{row['proverb']}*")
                
                with col_media:
                    if row['image']:
                        st.image(row['image'], caption=row['arabic_meaning'], use_column_width=True)

# ---------------------------------------------------------
# 5. التذييل
# ---------------------------------------------------------
st.markdown("---")
st.caption("مركز التوثيق الرقمي والأطلس اللغوي | أطروحة الدكتوراه - إقليم بولمان")
