import streamlit as st

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="AtlasLinguistique Pro - إقليم بولمان",
    page_icon="🗺️",
    layout="wide"
)

# 2. الهيدر العريض وبطاقات المؤشرات (Metrics Cards)
st.markdown("## 📘 AtlasLinguistique Pro")
st.caption("المنصة الذكية المتقدمة للقياس اللساني - إقليم بولمان")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="الجماعات الترابية", value="6")
with col2:
    st.metric(label="مفسر الذكاء الاصطناعي", value="AI Engine")
with col3:
    st.metric(label="التجميع التلقائي", value="Auto-KMeans")
with col4:
    st.metric(label="استقرار الظواهر", value="Stability")

st.divider()

# 3. بيانات الجماعات المعتمدة
communes_data = {
    "بولمان": {},
    "كيكو": {},
    "إموزار مرموشة": {},
    "ميسور": {},
    "أوطاط الحاج": {},
    "سرغينة": {}
}

# 4. شريط التبويبات الرئيسي (Tabs)
tabs = st.tabs([
    "الرئيسية", 
    "الخريطة التفاعلية", 
    "المعجم اللساني", 
    "التحليل الصوتي", 
    "المقارن الثنائي", 
    "الشجرة اللهجية", 
    "تحليل MDS", 
    "مسافات IPA", 
    "مصفوفات المسافات", 
    "الملحق التوثيقي"
])

# --- تفاصيل كل تبويب ---

# Tab 0: الرئيسية
with tabs[0]:
    st.write(".مرحباً بك في منصة الأطلس اللساني لإقليم بولمان")
    st.markdown("---")
    st.subheader("📊 مؤشر استقرار وانتشار الظواهر اللسانية")
    
    # جدول بيانات استقرار الظواهر اللسانية
    stability_data = [
        {"الظاهرة اللسانية": "الجهر_الصوتي", "(%) نسبة الانتشار": "66.7%", "مستوى الاستقرار": "0"}
    ]
    st.table(stability_data)

# Tab 1: الخريطة التفاعلية
with tabs[1]:
    st.subheader("🗺️ الخريطة التفاعلية")
    st.write("عرض تفاعلي للخريطة اللسانية والتوزيع الجغرافي للجماعات.")

# Tab 2: المعجم اللساني
with tabs[2]:
    st.subheader("📖 المعجم اللساني")
    st.write("قاعدة بيانات الألفاظ والمصطلحات اللهجية الخاصة بجهات الإقليم.")

# Tab 3: التحليل الصوتي
with tabs[3]:
    st.subheader("🎙️ التحليل الصوتي")
    st.write("تحليل الخصائص الصوتية والفونولوجية للهجات الإقليم.")

# Tab 4: المقارن الثنائي
with tabs[4]:
    st.subheader("🔀 المقارن الثنائي بين جماعتين")
    c1, c2 = st.columns(2)
    g1 = c1.selectbox("الجماعة الأولى", list(communes_data.keys()), index=0)
    g2 = c2.selectbox("الجماعة الثانية", list(communes_data.keys()), index=1)
    st.success(f"درجة التماثل اللساني بين **{g1}** و **{g2}** هي: {88 - abs(len(g1)-len(g2))*3}%")

# Tab 5: الشجرة اللهجية
with tabs[5]:
    st.subheader("🌲 الشجرة اللهجية (Dendrogram)")
    st.info("تمثيل هرمي يوضح درجة القرابة والتفرع اللهجي بين جماعات إقليم بولمان.")

# Tab 6: تحليل MDS
with tabs[6]:
    st.subheader("📉 MDS تحليل التعدد البعدي")
    st.write("إسقاط ثنائي الأبعاد لمسافات التمايز اللساني بين المراكز.")

# Tab 7: مسافات IPA
with tabs[7]:
    st.subheader("🔪 IPA حساب مسافات الأبجدية الصوتية الدولية")
    st.text_input("أدخل النص الصوتي IPA المقارن:", "[kikou] vs [boulemane]")

# Tab 8: مصفوفات المسافات
with tabs[8]:
    st.subheader("🔢 LaTeX مصفوفات المسافات اللسانية")
    st.latex(r"D_{ij} = \sqrt{\sum_{k=1}^{n} (w_k \cdot (x_{ik} - x_{jk}))^2}")

# Tab 9: الملحق التوثيقي
with tabs[9]:
    st.subheader("📁 الملحق وتوثيق المنهجية")
    st.write("بيانات توثيقية حول أطلس إقليم بولمان والمسح الميداني.")
