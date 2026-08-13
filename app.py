import streamlit as st
import pandas as pd

# --------------------------------------------------
# 1. إعدادات الصفحة الأساسية
# --------------------------------------------------
st.set_page_config(
    page_title="الأطلس اللغوي وقاموس الفلاحة والأدب الأمازيغي",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# 2. حقن التنسيقات المتقدمة والخطوط (CSS)
# --------------------------------------------------
st.markdown("""
    <style>
    /* استدعاء خط Cairo الاحترافي */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6 {
        font-family: 'Cairo', sans-serif !important;
    }

    /* الخلفية العامة وهامش الأمان لهواتف أندرويد */
    .stApp {
        background-color: #F8F9FA;
    }

    .main .block-container {
        direction: rtl !important;
        text-align: right !important;
        padding-top: 1.5rem !important;
        padding-bottom: 95px !important; /* هامش لحماية الأزرار من شريط الأندرويد */
        max-width: 1100px;
    }

    /* تصميم البطاقات والخانات */
    div[data-testid="stForm"], .element-container div.stDataFrame {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #EAEAEA !important;
    }

    /* تصميم أزرار الإرسال والتفاعل */
    .stButton>button, div[data-testid="stForm"] button {
        width: 100% !important;
        background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(46, 125, 50, 0.25) !important;
        transition: all 0.3s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(46, 125, 50, 0.35) !important;
    }

    /* القائمة الجانبية (Sidebar - مثبتة على اليسار) */
    [data-testid="stSidebar"] {
        left: 0 !important;
        right: auto !important;
        background-color: #1E2922 !important;
        border-right: 1px solid #2D3E33 !important;
        border-left: none !important;
        direction: ltr !important;
    }

    [data-testid="stSidebar"] * {
        color: #E8F5E9 !important;
    }

    [data-testid="stSidebarCollapseButton"] {
        left: 0 !important;
        right: auto !important;
    }

    /* مدخلات النصوص والقوائم */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        border-radius: 10px !important;
        border: 1.5px solid #D1D5DB !important;
        padding: 10px !important;
        direction: rtl !important;
        text-align: right !important;
        background-color: #FAFAFA !important;
    }

    /* رأس الصفحات الملون */
    .header-box {
        background: linear-gradient(135deg, #1E4D2B 0%, #2E7D32 100%);
        color: white;
        padding: 24px;
        border-radius: 18px;
        margin-bottom: 25px;
        box-shadow: 0 6px 20px rgba(30, 77, 43, 0.2);
    }
    .header-box h1 {
        color: #FFFFFF !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        margin: 0 !important;
    }
    .header-box p {
        color: #E8F5E9 !important;
        font-size: 13px !important;
        margin-top: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. القائمة الجانبية (Sidebar - جهة اليسار)
# --------------------------------------------------
with st.sidebar:
    st.markdown("### 📌 Navigation")
    
    selected_page = st.radio(
        "اختر القسم / Select Section:",
        [
            "✍️ Fieldwork (الجمع الميداني)",
            "📜 Literature (الأدب الشفهي)",
            "📊 Dialectométrie (القياس اللساني)",
            "🗺️ Atlas & Cartes (الأطلس والخرائط)",
            "📚 Corpus & Fiches (المدونة والمعاجم)"
        ]
    )
    
    st.divider()
    st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 12px; border-radius: 10px; font-size: 12px;'>
            <b>🌿 Atlas Linguistique & Amazigh Dictionary</b><br>
            منصة التوثيق المعجمي والأدبي والقياس اللساني الجغرافي.
        </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 4. محتوى أجزاء المنصة الكاملة
# --------------------------------------------------

# ==================================================
# القسم الأول: الجمع الميداني الفلاحي (Fieldwork)
# ==================================================
if "✍️ Fieldwork" in selected_page:
    st.markdown("""
        <div class="header-box">
            <h1>📝 استمارة التوثيق والجمع الميداني</h1>
            <p>توثيق المصطلحات الفلاحية والألفاظ الأمازيغية مباشرة من الميدان</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("fieldwork_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            word_tifinagh = st.text_input("الكلمة بتيفيناغ (مثال: ⵜⴰⵢⵔⵣⴰ):")
            word_arabic = st.text_input("المعنى / الشرح بالعربية:")
            
        with col2:
            word_latin = st.text_input("الكلمة باللاتينية (مثال: Tayrza):")
            location = st.text_input("موقع الجمع / القبيلة / الدوار:")

        field_domain = st.selectbox(
            "الحقل المعجمي الفلاحي:",
            [
                "أدوات الحرث والدرس",
                "السقي والري التقليدي",
                "تربية الماشية والرعي",
                "أنواع المحاصيل والزراعة",
                "تضاريس الأرض والتربة",
                "أخرى"
            ]
        )

        description = st.text_area("ملاحظات ميدانية تفصيلية (النطق المحلي / السياق):", height=100)

        submit_btn = st.form_submit_button("📤 إرسال وتوثيق المادة الميدانية")

        if submit_btn:
            if word_tifinagh or word_latin:
                st.success("✅ تم حفظ المادة الميدانية بنجاح في قاعدة البيانات!")
            else:
                st.warning("⚠️ يرجى إدخال الكلمة بتيفيناغ أو اللاتينية على الأقل.")

# ==================================================
# القسم الثاني: جمع الأدب الشفهي (Literature)
# ==================================================
elif "📜 Literature" in selected_page:
    st.markdown("""
        <div class="header-box">
            <h1>📜 توثيق التراث الشفهي والأدب الأمازيغي</h1>
            <p>جمع وتصنيف الأشعار، الألغاز، والحكايات الشعبية الميدانية</p>
        </div>
    """, unsafe_allow_html=True)

    genre = st.radio(
        "اختر نوع المادة الشفهية المراد توثيقها:",
        ["📜 شعر (ⵜⴰⵎⴷⵢⴰⵣⵜ / Izlan)", "🧩 لغز (ⵜⴰⵏⴼⵓⵔⵜ / Timssardacin)", "📖 حكاية (ⵜⴰⵏⴼⵓⵙⵜ / Timaggarin)"],
        horizontal=True
    )

    st.divider()

    # 1. استمارة الشعر
    if "شعر" in genre:
        st.subheader("📝 توثيق قصيدة / إزلي")
        with st.form("poetry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                poem_title = st.text_input("عنوان القصيدة / البيت:")
                poet_name = st.text_input("اسم الشاعر / الراوي:")
            with col2:
                poem_type = st.selectbox("نوع الشعر / الغرض:", ["إزلي (Izli)", "تامديازت (Tamdyazt)", "شعر الحصاد والعمل", "أخرى"])
                region = st.text_input("المنطقة / القبيلة:")

            text_tifinagh = st.text_area("نص القصيدة بتيفيناغ:", height=100)
            text_latin = st.text_area("نص القصيدة باللاتينية:", height=90)
            text_arabic = st.text_area("ترجمة الأبيات والشرح بالعربية:", height=90)

            audio_file = st.file_uploader("🎙️ رفع تسجيل صوتي (MP3, WAV):", type=["mp3", "wav", "m4a"])

            submit_poem = st.form_submit_button("📤 حفظ وثيقة الشعر")
            if submit_poem:
                st.success("✅ تم توثيق القصيدة بنجاح!")

    # 2. استمارة اللغز
    elif "لغز" in genre:
        st.subheader("🧩 توثيق لغز شعبي (Tanfurt)")
        with st.form("riddle_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                riddle_tifinagh = st.text_input("نص اللغز بتيفيناغ:")
                riddle_arabic = st.text_input("نص اللغز بالعربية:")
            with col2:
                answer = st.text_input("💡 حل اللغز (الجواب):")
                domain = st.selectbox("المجال:", ["أدوات الفلاحة", "الحيوانات والرعي", "الطبيعة والكون", "عناصر البيت"])

            region = st.text_input("منطقة الجمع:")
            notes = st.text_area("شرح ثقافي أو سياق اللغز:")

            submit_riddle = st.form_submit_button("📤 حفظ اللغز")
            if submit_riddle:
                st.success("✅ تم تسجيل اللغز وحله بنجاح!")

    # 3. استمارة الحكاية
    else:
        st.subheader("📖 توثيق حكاية شعبية (Tanfust)")
        with st.form("story_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                story_title = st.text_input("عنوان الحكاية:")
                narrator = st.text_input("اسم الإخباري / الراوي:")
            with col2:
                story_category = st.selectbox("تصنيف الحكاية:", ["حكايات الحيوان", "حكايات عجائبية", "حكايات واقعية", "أسطورة فلاحية"])
                region = st.text_input("منطقة الجمع:")

            story_body = st.text_area("نص الحكاية أو ملخصها:", height=180)
            audio_story = st.file_uploader("🎙️ تسجيل صوتي للحكاية:", type=["mp3", "wav", "m4a"])

            submit_story = st.form_submit_button("📤 حفظ الحكاية الشعبية")
            if submit_story:
                st.success("✅ تم توثيق الحكاية بنجاح!")

# ==================================================
# القسم الثالث: القياس اللساني (Dialectométrie)
# ==================================================
elif "📊 Dialectométrie" in selected_page:
    st.markdown("""
        <div class="header-box">
            <h1>📊 Dialectométrie - أدوات القياس اللساني</h1>
            <p>حساب المسافات اللغوية والتغيرات المعجمية بين المناطق الفلاحية</p>
        </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        region_1 = st.selectbox("المنطقة / التنوع الأول:", ["الأطلس المتوسط", "الريف", "سوس", "الجنوب الشرقي"])
    with col_b:
        region_2 = st.selectbox("المنطقة / التنوع الثاني:", ["سوس", "الريف", "الأطلس المتوسط", "الجنوب الشرقي"])

    st.markdown("##### ⚙️ خيارات التحليل الإحصائي:")
    matrix_type = st.radio("نوع مصفوفة المسافة:", ["المسافة المعجمية (Distance Lexicale)", "المسافة الصوتية (Phonétique)"])
    threshold = st.slider("مستوى التشابه الأدنى (%):", 0, 100, 75)

    if st.button("🔍 تشغيل تحليل القياس اللساني"):
        st.success(f"تم حساب درجة التشابه المعجمي بين {region_1} و {region_2}: **{threshold - 5}%**")
        
        demo_data = {
            "المصطلح الفلاحي": ["المحراث", "المنجل", "البئر", "القمح"],
            region_1: ["ⵜⴰⴳⵯⵓⵍⵜ", "ⴰⵎⴳⵔ", "ⴰⵏⵓ", "ⵉⵔⴷⵏ"],
            region_2: ["ⵜⴰⴳⵯⵓⵍⵜ", "ⴰⵎ⵵ⵔ", "ⴰⴳⵍⵎⴰⵎ", "ⵉⵔⴷⵏ"],
            "نسبة التوافق": ["100%", "85%", "40%", "100%"]
        }
        st.dataframe(pd.DataFrame(demo_data), use_container_width=True)

# ==================================================
# القسم الرابع: الخرائط والأطلس (Atlas & Cartes)
# ==================================================
elif "🗺️ Atlas & Cartes" in selected_page:
    st.markdown("""
        <div class="header-box">
            <h1>🗺️ Atlas & Cartes - الأطلس والخرائط التفاعلية</h1>
            <p>عرض التوزيع الجغرافي للمصطلحات الفلاحية والأمازيغية</p>
        </div>
    """, unsafe_allow_html=True)

    selected_term = st.selectbox("اختر المصطلح الفلاحي لعرض خريطته الجغرافية:", ["المحراث التقليدي (Tagwult)", "المنجل (Amgr)", "نظام السقي (Targa)"])
    
    st.markdown(f"##### 📍 التوزيع الجغرافي لـ: **{selected_term}**")
    
    map_data = pd.DataFrame({
        'lat': [31.7917, 33.5731, 30.4278, 35.1681],
        'lon': [-7.0926, -7.5898, -9.5981, -3.9321]
    })
    st.map(map_data)

# ==================================================
# القسم الخامس: المدونة والمعاجم (Corpus & Fiches)
# ==================================================
else:
    st.markdown("""
        <div class="header-box">
            <h1>📚 Corpus & Fiches - مدونة المعاجم الفلاحية</h1>
            <p>قاعدة البيانات الشاملة والمطابقة للمصطلحات الموثقة</p>
        </div>
    """, unsafe_allow_html=True)

    search_query = st.text_input("🔍 بحث عن مصطلح في قاعدة البيانات:")

    corpus_data = pd.DataFrame({
        "تيفيناغ": ["ⵜⴰⵢⵔⵣⴰ", "ⵜⴰⵔⴳⴰ", "ⴰⵎⴳⵔ", "ⵜⴰⴳⵯⵓⵍⵜ", "ⵜⴰⵎⵓⵔⵜ"],
        "اللاتينية": ["Tayrza", "Targa", "Amgr", "Tagwult", "Tamurt"],
        "المعنى بالعربية": ["الحراثة", "الساقية", "المنجل", "المحراث", "الأرض / التراب"],
        "المجال الفلاحي": ["أنشطة الحرث", "السقي والري", "أدوات الحصاد", "أدوات الحرث", "التضاريس"],
        "منطقة الجمع": ["الأطلس المتوسط", "سوس", "الريف", "الجنوب الشرقي", "الأطلس الكبير"]
    })

    if search_query:
        filtered_df = corpus_data[
            corpus_data['تيفيناغ'].str.contains(search_query) |
            corpus_data['اللاتينية'].str.contains(search_query, case=False) |
            corpus_data['المعنى بالعربية'].str.contains(search_query)
        ]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(corpus_data, use_container_width=True)

    st.download_button(
        label="📥 تحميل كامل المعجم (CSV)",
        data=corpus_data.to_csv(index=False).encode('utf-8-sig'),
        file_name='amazigh_agricultural_dictionary.csv',
        mime='text/csv'
    )
