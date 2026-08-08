import streamlit as st

# إعداد الصفحة
st.set_page_config(
    page_title="AtlasLinguistique Pro",
    page_icon="📘",
    layout="wide"
)

# هيدر المنصة الرئيسية
st.markdown("## 📘 AtlasLinguistique Pro")
st.caption("المنصة الذكية المتقدمة للقياس اللساني - إقليم بولمان")

# عرض الإحصائيات والبطاقات (Metrics / Cards)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="الجماعات الترابية", value="6")

with col2:
    st.metric(label="مفسر الذكاء الاصطناعي", value="AI Engine")

with col3:
    st.metric(label="التجميع التلقائي", value="Auto-KMeans")

with col4:
    st.metric(label="استقرار الظواهر", value="Stability")

# شريط التبويبات السفلي/الجانبي
tabs = st.tabs([
    "💻 أكواد الملحق", 
    "📊 LaTeX مصفوفات", 
    "🔤 IPA مسافة"
])

with tabs[0]:
    st.subheader("📊 مؤشر استقرار وانتشار الظواهر اللسانية")
    
    # جدول الظواهر اللسانية ومستوى الاستقرار
    data = [
        {"الظاهرة اللسانية": "الجهر_الصوتي", "نسبة الانتشار (%)": "66.7%", "مستوى الاستقرار": "0"}
    ]
    st.table(data)
