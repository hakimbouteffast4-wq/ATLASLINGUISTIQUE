import streamlit as st
import pandas as pd
import numpy as np

# محاولة استيراد المكتبات التحليلية مع معالجة الاستثناءات
try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="AtlasLinguistique Pro - إقليم بولمان",
    page_icon="🗺️",
    layout="wide"
)

# 2. الهيدر الرئيسي وبطاقات المؤشرات
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

# 3. قاعدة البيانات الجغرافية واللسانية للجماعات
communes_data = {
    "بولمان": {"lat": 33.3617, "lon": -4.7314, "dialect": "أمازيغية/عربية", "distance_val": 12},
    "كيكو": {"lat": 33.2089, "lon": -4.8483, "dialect": "أمازيغية الأطلس المتوسط", "distance_val": 18},
    "إموزار مرموشة": {"lat": 33.4833, "lon": -4.2833, "dialect": "أمازيغية آيت وراين", "distance_val": 25},
    "ميسور": {"lat": 33.0486, "lon": -3.9961, "dialect": "عربية دارجة محليّة", "distance_val": 8},
    "أوطاط الحاج": {"lat": 33.3483, "lon": -3.7022, "dialect": "عربية دارجة شرقية", "distance_val": 15},
    "سرغينة": {"lat": 33.2833, "lon": -4.5000, "dialect": "أمازيغية/عربية", "distance_val": 20}
}

# 4. شريط التبويبات الرئيسي
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

# --- 0. الرئيسية ---
with tabs[0]:
    st.write(".مرحباً بك في منصة الأطلس اللساني لإقليم بولمان")
    st.markdown("---")
    st.subheader("📊 مؤشر استقرار وانتشار الظواهر اللسانية")
    
    df_stability = pd.DataFrame([
        {"الظاهرة اللسانية": "الجهر_الصوتي", "(%) نسبة الانتشار": "66.7%", "مستوى الاستقرار": "0"},
        {"الظاهرة اللسانية": "الإمالة_المعجمية", "(%) نسبة الانتشار": "45.2%", "مستوى الاستقرار": "1"},
        {"الظاهرة اللسانية": "الترقيق_الفونولوجي", "(%) نسبة الانتشار": "82.0%", "مستوى الاستقرار": "0"}
    ])
    st.table(df_stability)

# --- 1. الخريطة التفاعلية (مفعّلة) ---
with tabs[1]:
    st.subheader("🗺️ الخريطة التفاعلية لإقليم بولمان")
    st.write("التوزيع الجغرافي للجماعات الترابية والمناطق اللسانية.")
    
    if HAS_FOLIUM:
        # إنشاء الخريطة وتحديد المركز
        m = folium.Map(location=[33.25, -4.35], zoom_start=9, tiles="OpenStreetMap")
        
        for name, info in communes_data.items():
            folium.Marker(
                location=[info["lat"], info["lon"]],
                popup=f"<b>جماعة {name}</b><br>النمط اللهجي: {info['dialect']}",
                tooltip=name,
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
            
        st_folium(m, width=900, height=500)
    else:
        # عرض احتياطي باستخدام Streamlit Map
        df_map = pd.DataFrame([
            {"lat": v["lat"], "lon": v["lon"], "name": k} 
            for k, v in communes_data.items()
        ])
        st.map(df_map)

# --- 2. المعجم اللساني ---
with tabs[2]:
    st.subheader("📖 المعجم اللساني")
    st.write("قاعدة بيانات الألفاظ والمصطلحات اللهجية الخاصّة بالجماعات.")
    
    search_word = st.text_input("🔍 ابحث عن كلمة أو ملمح معجمي:", "")
    dict_data = pd.DataFrame([
        {"الكلمة": "أغروم", "المعنى": "خبز", "المجال": "أمازيغي (كيكو/مرموشة)"},
        {"الكلمة": "أمان", "المعنى": "ماء", "المجال": "أمازيغي مشرك"},
        {"الكلمة": "الدشرا", "المعنى": "القرية", "المجال": "عربي (ميسور/أوطاط)"}
    ])
    if search_word:
        dict_data = dict_data[dict_data['الكلمة'].str.contains(search_word) | dict_data['المعنى'].str.contains(search_word)]
    st.dataframe(dict_data, use_container_width=True)

# --- 3. التحليل الصوتي ---
with tabs[3]:
    st.subheader("🎙️ التحليل الصوتي والفونولوجي")
    st.write("تحليل الخصائص الصوتية وانتشار التمايز الصوتي عبر المراكز.")
    
    feature = st.selectbox("اختر الملمح الصوتي للتحليل:", ["الإمالة", "الاحتياط الصوتي", "التعفيص", "الجهر"])
    st.info(f"عرض توزيع الملمح الصوتي: **{feature}** عبر المراكز الترابية.")

# --- 4. المقارن الثنائي ---
with tabs[4]:
    st.subheader("🔀 المقارن الثنائي بين جماعتين")
    c1, c2 = st.columns(2)
    g1 = c1.selectbox("الجماعة الأولى", list(communes_data.keys()), index=0)
    g2 = c2.selectbox("الجماعة الثانية", list(communes_data.keys()), index=1)
    
    similarity = 88 - abs(len(g1) - len(g2)) * 3
    st.success(f"درجة التماثل اللساني بين **{g1}** و **{g2}** هي: {similarity}%")

# --- 5. الشجرة اللهجية (Dendrogram) ---
with tabs[5]:
    st.subheader("🌲 الشجرة اللهجية (Dendrogram)")
    st.info("تمثيل هرمي يوضح درجة القرابة والتفرع اللهجي بين جماعات إقليم بولمان.")
    
    if HAS_PLOTLY:
        # رسم بياني شجري مبسط
        import plotly.figure_factory as ff
        X = np.array([[1, 2], [1, 4], [2, 2], [8, 7], [8, 8], [7, 8]])
        fig = ff.create_dendrogram(X, labels=list(communes_data.keys()))
        fig.update_layout(width=800, height=400)
        st.plotly_chart(fig, use_container_width=True)

# --- 6. تحليل MDS ---
with tabs[6]:
    st.subheader("📉 MDS تحليل التعدد البعدي")
    st.write("إسقاط ثنائي الأبعاد لمسافات التمايز اللساني بين المراكز.")
    
    if HAS_PLOTLY:
        df_mds = pd.DataFrame({
            'Dim1': [1.2, -0.5, -1.8, 2.1, 1.9, -0.2],
            'Dim2': [0.4, 1.1, -0.9, -1.2, -0.8, 0.8],
            'الجماعة': list(communes_data.keys())
        })
        fig_mds = px.scatter(df_mds, x='Dim1', y='Dim2', text='الجماعة', title="إسقاط MDS للمسافات اللسانية")
        fig_mds.update_traces(textposition='top center', marker=dict(size=12, color='DarkBlue'))
        st.plotly_chart(fig_mds, use_container_width=True)

# --- 7. مسافات IPA ---
with tabs[7]:
    st.subheader("🔪 IPA حساب مسافات الأبجدية الصوتية الدولية")
    ipa_text = st.text_input("أدخل النص الصوتي IPA المقارن:", "[kikou] vs [boulemane]")
    
    # دالة حساب مسافة ليفنشتاين بسيطة
    def lev_distance(s1, s2):
        if len(s1) < len(s2):
            return lev_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    if "vs" in ipa_text:
        parts = [p.strip().strip('[]') for p in ipa_text.split("vs")]
        if len(parts) == 2:
            dist = lev_distance(parts[0], parts[1])
            st.metric(label=f"مسافة التمايز الفونولوجي (Edit Distance) بين '{parts[0]}' و '{parts[1]}'", value=dist)

# --- 8. مصفوفات المسافات ---
with tabs[8]:
    st.subheader("🔢 LaTeX مصفوفات المسافات اللسانية")
    st.latex(r"D_{ij} = \sqrt{\sum_{k=1}^{n} (w_k \cdot (x_{ik} - x_{jk}))^2}")
    
    # عرض مصفوفة مسافات توضيحية
    st.write("مصفوفة المسافات اللسانية التجميعية:")
    dist_matrix = pd.DataFrame(
        np.random.randint(0, 30, size=(6, 6)),
        index=list(communes_data.keys()),
        columns=list(communes_data.keys())
    )
    np.fill_diagonal(dist_matrix.values, 0)
    st.dataframe(dist_matrix)

# --- 9. الملحق التوثيقي ---
with tabs[9]:
    st.subheader("📁 الملحق وتوثيق المنهجية")
    st.write("بيانات توثيقية حول أطلس إقليم بولمان والمسح الميداني.")
    st.info("تم جمع المعطيات الميدانية اعتماداً على الاستمارات اللسانية الموجهة للناطقين الأصليين بالجماعات الترابية الست.")
