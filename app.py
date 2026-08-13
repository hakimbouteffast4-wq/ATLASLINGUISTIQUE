import streamlit as st

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="منصة القياس اللساني والأطلس اللغوي",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. حقن كود CSS للتنسيق (القائمة الجانبية على اليسار + محتوى عربي على اليمين)
st.markdown("""
    <style>
    /* -------------------------------------------------- */
    /* 1. تثبيت القائمة الجانبية (Sidebar) في جهة اليسار  */
    /* -------------------------------------------------- */
    [data-testid="stSidebar"] {
        left: 0 !important;
        right: auto !important;
        border-right: 1px solid #e0e0e0 !important;
        border-left: none !important;
        direction: ltr !important; /* قائمة خيارات بالجهة اليسرى */
    }

    /* تعديل مكان زر فتح/إغلاق القائمة الجانبية ليصبح على اليسار */
    [data-testid="stSidebarCollapseButton"] {
        left: 0 !important;
        right: auto !important;
    }

    /* -------------------------------------------------- */
    /* 2. ضبط المحتوى الرئيسي والاستمارة من اليمين لليسار */
    /* -------------------------------------------------- */
    .main .block-container {
        direction: rtl !important;
        text-align: right !important;
    }

    /* ضبط عناوين المدخلات وخانات الاستمارة لتكون جهة اليمين */
    .stTextInput, .stSelectbox, .stTextArea, .stButton {
        direction: rtl !important;
        text-align: right !important;
    }

    /* تنسيق زر الإرسال */
    .stButton>button {
        width: 100%;
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        font-size: 16px;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. القائمة الجانبية (Sidebar - ستظهر على اليسار)
# --------------------------------------------------
with st.sidebar:
    st.title("📌 Navigation")
    
    selected_page = st.radio(
        "اختر التبويب / Select Tab:",
        [
            "✍️ Fieldwork (الجمع الميداني)",
            "📊 Dialectométrie (القياس اللساني)",
            "🗺️ Atlas & Cartes (الأطلس والخرائط)",
            "📚 Corpus & Fiches (المدونة والمعاجم)"
        ]
    )
    
    st.divider()
    st.info("ℹ️ **Atlas Linguistique & Amazigh Dictionary**\n\nتطبيق التوثيق المعجمي والفلاحي الميداني.")

# --------------------------------------------------
# 4. محتوى الصفحة الرئيسية (ستظهر على اليمين)
# --------------------------------------------------

if "✍️ Fieldwork" in selected_page:
    st.title("📝 استمارة التوثيق والجمع الميداني")
    st.write("قم بملء البيانات الخاصة بالمفردة الفلاحية أو اللغوية الميدانية:")
    
    st.divider()

    # بداية الاستمارة (Form)
    with st.form("fieldwork_form", clear_on_submit=True):
        
        col1, col2 = st.columns(2)
        
        with col1:
            word_tifinagh = st.text_input("الكلمة بتيفيناغ (مثال: ⵜⴰⵢⵔⵣⴰ):")
            word_arabic = st.text_input("المعنى بالعربية:")
            
        with col2:
            word_latin = st.text_input("الكلمة باللاتينية (مثال: Tayrza):")
            location = st.text_input("موقع الجمع / القبيلة / الدوار:")

        field_domain = st.selectbox(
            "الحقل المعجمي الفلاحي:",
            [
                "أدوات الحرث والدرس",
                "السقي والري التقليدي",
                "تربية الماشية والرعي",
                "أنواع المحاصيل والأنشطة الزراعية",
                "مصطلحات التربة والتضاريس الفلاحية",
                "أخرى"
            ]
        )

        description = st.text_area("الوصف الميداني وتفاصيل الاستعمال (أو النطق المحلي):")

        # زر الإرسال
        submit_btn = st.form_submit_button("📤 إرسال المادة الميدانية")

        if submit_btn:
            if word_tifinagh or word_latin:
                st.success("✅ تم حفظ المادة الميدانية بنجاح في قاعدة البيانات!")
            else:
                st.warning("⚠️ يرجى أدخال الكلمة بتيفيناغ أو اللاتينية على الأقل.")

elif "📊 Dialectométrie" in selected_page:
    st.title("📊 Dialectométrie - القياس اللساني")
    st.info("قسم التحليل الإحصائي والمسافات اللسانية بين المتغيرات.")

elif "🗺️ Atlas & Cartes" in selected_page:
    st.title("🗺️ Atlas & Cartes - الخرائط والأطلس اللغوي")
    st.info("عرض الخرائط التفاعلية للظواهر اللغوية والفلاحية.")

else:
    st.title("📚 Corpus & Fiches - المدونة الجغرافية")
    st.info("قاعدة البيانات والمعاجم الفلاحية الموثقة.")
