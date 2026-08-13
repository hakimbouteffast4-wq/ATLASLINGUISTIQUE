import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتنسيق العربي (RTL)
# ---------------------------------------------------------
st.set_page_config(
    page_title="أطلس وقاموس الفلاحة الأمازيغية - إقليم بولمان",
    page_icon="🌾",
    layout="wide"
)

# ضبط المحاذاة وتصحيح العناوين
st.markdown("""
    <style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    div[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    .custom-title {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1e4620;
        margin-bottom: 0.2rem;
        line-height: 1.4;
    }
    .custom-subtitle {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. قراءة قاعدة البيانات الخارجية (CSV) بمرونة وآمان
# ---------------------------------------------------------
@st.cache_data
def load_data():
    try:
        # قراءة جميع الأعمدة كنصوص تجنباً لمشاكل أنواع البيانات
        df = pd.read_csv('data.csv', dtype=str, encoding='utf-8')
        df.fillna('', inplace=True)
        
        # تحويل الإحداثيات مع تحويل الأخطاء إلى قيم فارغة
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"خطأ في قراءة ملف البيانات data.csv: {e}")
        return pd.DataFrame()

df = load_data()

# ---------------------------------------------------------
# 3. القائمة الجانبية للتصفية والبحث
# ---------------------------------------------------------
st.sidebar.markdown("## 🌾 قاموس الفلاحة والرعي")
st.sidebar.markdown("**إقليم بولمان - الأطلس اللغوي**")
st.sidebar.markdown("---")

if not df.empty:
    categories = ["الكل"] + sorted([str(x) for x in df['category'].unique() if str(x).strip() != ''])
    selected_category = st.sidebar.selectbox("🎯 الحقل المعجمي:", categories)

    locations = ["الكل"] + sorted([str(x) for x in df['location'].unique() if str(x).strip() != ''])
    selected_location = st.sidebar.selectbox("📍 المنطقة / القبيلة:", locations)

    search_query = st.sidebar.text_input("🔍 البحث النصي (تيفيناغ / عربي / لاتيني):")

    filtered_df = df.copy()

    if selected_category != "الكل":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]

    if selected_location != "الكل":
        filtered_df = filtered_df[filtered_df['location'] == selected_location]

    if search_query:
        query = search_query.strip().lower()
        filtered_df = filtered_df[
            filtered_df['arabic_meaning'].astype(str).str.contains(query, case=False) |
            filtered_df['word_tifinagh'].astype(str).str.contains(query, case=False) |
            filtered_df['word_latin'].astype(str).str.contains(query, case=False) |
            filtered_df['description'].astype(str).str.contains(query, case=False)
        ]

# ---------------------------------------------------------
# 4. الواجهة الرئيسية
# ---------------------------------------------------------
st.markdown('<div class="custom-title">🌾 الأطلس اللغوي وقاموس الفلاحة والرعي الأمازيغي</div>', unsafe_allow_html=True)
st.markdown('<div class="custom-subtitle">دراسة توثيقية لمعجم العتاد الفلاحي وتقنيات السقي والرعي بإقليم بولمان</div>', unsafe_allow_html=True)
st.markdown("---")

if df.empty:
    st.warning("يرجى التأكد من وجود ملف data.csv في المستودع بصيغة صحيحة.")
else:
    # المؤشرات الإحصائية
    m1, m2, m3 = st.columns(3)
    m1.metric("إجمالي المفردات المعروضة", len(filtered_df))
    m2.metric("الحقول المعجمية", len([x for x in df['category'].unique() if str(x).strip() != '']))
    m3.metric("المواقع الجغرافية", len([x for x in df['location'].unique() if str(x).strip() != '']))

    st.markdown("###")

    tab1, tab2 = st.tabs(["🗺️ الخريطة اللغوية التفاعلية", "📚 المعجم والبطاقات اللسانية"])

    # --- التبويب 1: الخريطة ---
    with tab1:
        st.subheader("الترسيم الجغرافي للمصطلحات الفلاحية")
        
        # تصفية الصفوف التي تحتوى على إحداثيات جغرافية صحيحة فقط
        map_df = filtered_df.dropna(subset=['lat', 'lon'])

        # مركز الخريطة الافتراضي (إقليم بولمان)
        m = folium.Map(location=[33.25, -4.50], zoom_start=9, tiles="OpenStreetMap")

        for _, row in map_df.iterrows():
            try:
                popup_html = f"""
                <div style="font-family: sans-serif; text-align: right; width: 180px;">
                    <h4 style="color: #2e7d32; margin: 0;">{row['word_tifinagh']} ({row['word_latin']})</h4>
                    <b>المعنى:</b> {row['arabic_meaning']}<br>
                    <b>الموقع:</b> {row['location']}
                </div>
                """
                folium.Marker(
                    location=[float(row['lat']), float(row['lon'])],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{row['word_tifinagh']} - {row['arabic_meaning']}",
                    icon=folium.Icon(color="green", icon="leaf")
                ).add_to(m)
            except Exception:
                continue

        st_folium(m, width="100%", height=500)

    # --- التبويب 2: البطاقات اللسانية ---
    with tab2:
        st.subheader("سجل المصطلحات الفلاحية والرعوية")

        if filtered_df.empty:
            st.warning("لا توجد نتائج تطابق خيارات البحث.")
        else:
            # تقسيم العرض إلى صفحات لسرعة استجابة الموقع مع آلاف المفردات
            page_size = 20
            total_items = len(filtered_df)
            
            if total_items > page_size:
                pages = (total_items // page_size) + (1 if total_items % page_size > 0 else 0)
                page_num = st.number_input("الصفحة:", min_value=1, max_value=pages, value=1, step=1)
                start_idx = (page_num - 1) * page_size
                end_idx = start_idx + page_size
                current_df = filtered_df.iloc[start_idx:end_idx]
                st.info(f"عرض المواد من {start_idx + 1} إلى {min(end_idx, total_items)} من إجمالي {total_items} كلمة")
            else:
                current_df = filtered_df

            for _, row in current_df.iterrows():
                with st.expander(f"📌 {row['word_tifinagh']} | {row['word_latin']} — {row['arabic_meaning']}"):
                    col_text, col_media = st.columns([2, 1])

                    with col_text:
                        st.markdown(f"### **{row['word_tifinagh']}** *( {row['word_latin']} )*")
                        if row.get('ipa'):
                            st.markdown(f"**الرمز الصوتي (IPA):** `{row['ipa']}`")
                        st.markdown(f"**المعنى بالعربية:** {row['arabic_meaning']}")
                        st.markdown(f"**الحقل المعجمي:** `{row['category']}`")
                        st.markdown(f"**القبيلة/المنطقة:** 📍 {row['location']}")
                        st.markdown("---")
                        if row.get('description'):
                            st.markdown(f"**الوصف الميداني:** {row['description']}")
                        if row.get('proverb'):
                            st.markdown(f"**الشاهد النصي / المثل:** *{row['proverb']}*")

                    with col_media:
                        if row.get('image'):
                            st.image(row['image'], caption=row['arabic_meaning'], use_column_width=True)

# ---------------------------------------------------------
# 5. التذييل
# ---------------------------------------------------------
st.markdown("---")
st.caption("مركز التوثيق الرقمي والأطلس اللغوي | أطروحة الدكتوراه - إقليم بولمان")
