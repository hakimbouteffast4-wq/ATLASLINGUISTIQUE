import streamlit as st

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="ATLAS LINGUISTIQUE - بولمان",
    page_icon="🗺️",
    layout="wide"
)

# بيانات وهمية/توضيحية للجماعات
communes_data = {
    "بولمان": {},
    "كيكو": {},
    "إموزار مرموشة": {},
    "ميسور": {},
    "أوطاط الحاج": {}
}

st.title("🗺️ الأطلس اللساني - إقليم بولمان")

# إنشاء التبويبات (Tabs)
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

# التبويبات الأولى (0-3) - أمثلة واجهة
with tabs[0]:
    st.write("مرحباً بك في منصة الأطلس اللساني لإقليم بولمان.")

# باقي التبويبات لتغطية جميع الواجهات (الظاهرة في لقطة الشاشة من Tab 4 إلى Tab 9)
with tabs[4]:
    st.subheader("🔀 المقارن الثنائي بين جماعتين")
    c1, c2 = st.columns(2)
    g1 = c1.selectbox("الجماعة الأولى", list(communes_data.keys()), index=0)
    g2 = c2.selectbox("الجماعة الثانية", list(communes_data.keys()), index=1)
    st.success(f"درجة التماثل اللساني بين **{g1}** و **{g2}** هي: {88 - abs(len(g1)-len(g2))*3}%")

with tabs[5]:
    st.subheader("🌲 الشجرة اللهجية (Dendrogram)")
    st.info("تمثيل هرمي يوضح درجة القرابة والتفرع اللهجي بين جماعات إقليم بولمان.")

with tabs[6]:
    st.subheader("📉 MDS تحليل التعدد البعدي")
    st.write("إسقاط ثنائي الأبعاد لمسافات التمايز اللساني بين المراكز.")

with tabs[7]:
    st.subheader("🔪 IPA حساب مسافات الأبجدية الصوتية الدولية")
    st.text_input("أدخل النص الصوتي IPA المقارن:", "[kikou] vs [boulemane]")

with tabs[8]:
    st.subheader("🔢 LaTeX مصفوفات المسافات اللسانية")
    st.latex(r"D_{ij} = \sqrt{\sum_{k=1}^{n} (w_k \cdot (x_{ik} - x_{jk}))^2}")

with tabs[9]:
    st.subheader("📁 الملحق وتوثيق المنهجية")
    st.write("بيانات توثيقية حول أطلس إقليم بولمان والمسح الميداني.")
