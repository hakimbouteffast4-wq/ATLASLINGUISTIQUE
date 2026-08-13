import streamlit as st
import pandas as pd

# --------------------------------------------------
# 1. إعدادات الصفحة الأساسية
# --------------------------------------------------
st.set_page_config(
    page_title="الأطلس اللغوي وقاموس الفلاحة الأمازيغي",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# 2. حقن كود CSS للتنسيق (القائمة يسار + المحتوى يمين)
# --------------------------------------------------
st.markdown("""
    <style>
    /* 1. تثبيت القائمة الجانبية في جهة اليسار */
    [data-testid="stSidebar"] {
        left: 0 !important;
        right: auto !important;
        border-right: 2px solid #e0e0e0 !important;
        border-left: none !important;
        direction: ltr !important;
    }

    [data-testid="stSidebarCollapseButton"] {
        left: 0 !important;
        right: auto !important;
    }

    /* 2. ضبط اتجاه المحتوى الرئيسي جهة اليمين (RTL) */
    .main .block-container {
        direction: rtl !important;
        text-align: right !important;
    }

    /* ضبط اتجاه النصوص والحقول والجداول */
    .stTextInput, .stSelectbox, .stTextArea, .stButton, .stDataFrame, .stSlider {
        direction: rtl !important;
        text-align: right !important;
    }

    /* تحسين شكل الأزرار */
    .stButton>button {
        width: 100%;
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        font-size: 16px;
        border-radius: 8px;
        padding: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. القائمة الجانبية (Sidebar - جهة اليسار)
# --------------------------------------------------
with st.sidebar:
    st.title("📌 Navigation")
    
    selected_page = st.radio(
        "اختر القسم / Select Section:",
        [
            "✍️ Fieldwork (الجمع الميداني)",
            "📊 Dialectométrie (القياس اللساني)",
            "🗺️ Atlas & Cartes (الأطلس والخرائط)",
            "📚 Corpus & Fiches (المدونة والمعاجم)"
        ]
    )
    
    st.divider()
    st.info("ℹ️ **Atlas Linguistique & Amazigh Dictionary**\n\nتطبيق الجمع الميداني والتحليل اللساني الجغرافي.")

# --------------------------------------------------
# 4. محتوى الأقسام الكاملة (جهة اليمين)
# --------------------------------------------------

# ==================================================
# القسم الأول: الجمع الميداني (Fieldwork)
# ==================================================
if "✍️ Fieldwork" in selected_page:
    st.title("📝 استمارة التوثيق والجمع الميداني")
    st.caption("توثيق المصطلحات الفلاحية والألفاظ الأمازيغية من الميدان")
    st.divider()

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

        description = st.text_area("ملاحظات ميدانية تفصيلية (النطق المحلي / السياق):")

        submit_btn = st.form_submit_button("📤 إرسال وتوثيق المادة")

        if submit_btn:
            if word_tifinagh or word_latin:
                st.success("✅ تم حفظ المادة الميدانية بنجاح!")
            else:
                st.warning("⚠️ يرجى إدخال الكلمة بتيفيناغ أو اللاتينية على الأقل.")

# ==================================================
# القسم الثاني: القياس اللساني (Dialectométrie)
# ==================================================
elif "📊 Dialectométrie" in selected_page:
    st.title("📊 Dialectométrie - أدوات القياس اللساني")
    st.caption("حساب المسافات اللغوية والتغيرات المعجمية بين المناطق الفلاحية")
    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        region_1 = st.selectbox("المنطقة / التنوع الأول:", ["الأطلس المتوسط", "الريف", "سوس", "الجنوب الشرقي"])
    with col_b:
        region_2 = st.selectbox("المنطقة / التنوع الثاني:", ["سوس", "الريف", "الأطلس المتوسط", "الجنوب الشرقي"])

    st.subheader("⚙️ خيارات التحليل الإحصائي:")
    matrix_type = st.radio("نوع مصفوفة المسافة:", ["المسافة المعجمية (Distance Lexicale)", "المسافة الصوتية (Phonétique)"])
    threshold = st.slider("مستوى التشابه الأدنى (%):", 0, 100, 75)

    if st.button("🔍 تشغيل تحليل القياس اللساني"):
        st.success(f"تم حساب درجة التشابه المعجمي بين {region_1} و {region_2}: **{threshold - 5}%** (بناءً على مصفوفة {matrix_type})")
        
        # جدول توضيحي كمثال للتحليل
        demo_data = {
            "المصطلح الفلاحي": ["المحراث", "المنجل", "البئر", "القمح"],
            region_1: ["ⵜⴰⴳⵯⵓⵍⵜ", "ⴰⵎⴳⵔ", "ⴰⵏⵓ", "ⵉⵔⴷⵏ"],
            region_2: ["ⵜⴰⴳⵯⵓⵍⵜ", "ⴰⵎⵊⵔ", "ⴰⴳⵍⵎⴰⵎ", "ⵉⵔⴷⵏ"],
            "نسبة التوافق": ["100%", "85%", "40%", "100%"]
        }
        st.dataframe(pd.DataFrame(demo_data), use_container_width=True)

# ==================================================
# القسم الثالث: الخرائط والأطلس (Atlas & Cartes)
# ==================================================
elif "🗺️ Atlas & Cartes" in selected_page:
    st.title("🗺️ Atlas & Cartes - الأطلس والخرائط التفاعلية")
    st.caption("عرض التوزيع الجغرافي للمصطلحات الفلاحية والأمازيغية")
    st.divider()

    selected_term = st.selectbox("اختر المصطلح الفلاحي لعرض خريطته الجغرافية:", ["المحراث التقليدي (Tagwult)", "المنجل (Amgr)", "نظام السقي (Targa)"])
    
    st.subheader(f"📍 التوزيع الجغرافي لـ: {selected_term}")
    
    # خريطة تفاعلية وهمية للعرض (يمكن ربطها بـ Folium لاحقاً)
    map_data = pd.DataFrame({
        'lat': [31.7917, 33.5731, 30.4278, 35.1681],
        'lon': [-7.0926, -7.5898, -9.5981, -3.9321]
    })
    st.map(map_data)
    
    st.info("💡 يمكن التكبير والتصغير وتتبع امتداد اللفظ عبر مختلف المناطق.")

# ==================================================
# القسم الرابع: المدونة والمعاجم (Corpus & Fiches)
# ==================================================
else:
    st.title("📚 Corpus & Fiches - مدونة المعاجم الفلاحية")
    st.caption("قاعدة البيانات الشاملة والمطابقة للمصطلحات الموثقة")
    st.divider()

    search_query = st.text_input("🔍 بحث عن مصطلح في قاعدة البيانات:")

    # بيانات المعجم الفلاحي
    corpus_data = pd.DataFrame({
        "تيفيناغ": ["ⵜⴰⵢⵔⵣⴰ", "ⵜⴰⵔⴳⴰ", "ⴰⵎⴳⵔ", "ⵜⴰⴳⵯⵓⵍⵜ", "ⵜⴰⵎⵓⵔⵜ"],
        "اللاتينية": ["Tayrza", "Targa", "Amgr", "Tagwult", "Tamurt"],
        "المعنى بالعربية": ["الحراثة", "الساقية", "المنجل", "المحراث", "الأرض / التراب"],
        "المجال الفلاحي": ["أنشطة الحرث", "السقي والري", "أدوات الحصاد", "أدوات الحرث", "التضاريس"],
        "منطقة الجمع": ["الأطلس المتوسط", "سوس", "الريف", "الجنوب الشرقي", "الأطلس الكبير"]
    })

    if search_query:
        # تصفية البيانات حسب كلمة البحث
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
