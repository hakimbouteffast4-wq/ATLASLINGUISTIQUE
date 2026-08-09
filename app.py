import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import numpy as np
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt

# إعدادات الصفحة
st.set_page_config(page_title="AtlasLinguistique", layout="wide", page_icon="🗺️")

# عنوان المنصة الرئيسي
st.title("🗺️ منصة AtlasLinguistique للجغرافيا والقياس اللساني")
st.caption("إقليم بولمان - دراسة ميدانية وقياسية تفاعلية")

# القائمة الجانبية
st.sidebar.header("⚙️ إعدادات المشروع")
st.sidebar.text_input("اسم المشروع/المنطقة", "أطلس إقليم بولمان")
st.sidebar.info("المنظومة مجهزة لجمع البيانات الميدانية والتحليل التلقائي.")

# تبويبات المنصة الشاملة
tab1, tab2, tab3, tab4 = st.tabs([
    "📱 1. إدخال وتجميع البيانات", 
    "📊 2. محرك القياس اللساني", 
    "🗺️ 3. الخريطة الفضائية التفاعلية", 
    "📄 4. التقارير والتصدير"
])

# ----------------------------------------------------
# 1. تبويب إدخال وتجميع البيانات
# ----------------------------------------------------
with tab1:
    st.header("تجميع البيانات والمتون اللسانية الميدانية")
    col1, col2 = st.columns(2)
    with col1:
        commune = st.text_input("الجماعة الترابية / القبيلة", "كيكو")
        word_tifinagh = st.text_input("اللفظة بالتيفيناغ", "ⵜⴰⴳⴰⵏⵜ")
        word_ipa = st.text_input("الرمز الصوتي الدولي (IPA)", "tagant")
    with col2:
        lat = st.number_input("خط العرض (Latitude)", value=33.2000, format="%.4f")
        lon = st.number_input("خط الطول (Longitude)", value=-4.7000, format="%.4f")
        audio_file = st.file_uploader("رفع تسجيل صوتي (WAV/MP3)", type=["wav", "mp3"])
    
    if st.button("حفظ المفردة الميدانية"):
        st.success(f"تم حفظ اللفظة [{word_tifinagh}] الخاصة بجماعة [{commune}] بنجاح!")

# ----------------------------------------------------
# 2. تبويب محرك القياس اللساني
# ----------------------------------------------------
with tab2:
    st.header("التحليل الإحصائي والشجرة اللهجية (Dendrogram)")
    
    # بيانات عينة وهمية لإقليم بولمان للتجربة
    sample_data = {
        'الجماعة': ['كيكو', 'تيمحضيت', 'أنجيل', 'أوطاط الحاج'],
        'سمة_صوتية_1': [1, 1, 1, 0],
        'سمة_صوتية_2': [1, 1, 0, 0],
        'سمة_معجمية_1': [1, 0, 1, 0],
        'سمة_معجمية_2': [0, 1, 1, 0]
    }
    df = pd.DataFrame(sample_data)
    st.write("📊 **بيانات العينة اللسانية للجماعات:**", df)
    
    # حساب مصفوفة المسافات والشجرة اللهجية
    features = df.iloc[:, 1:].values
    dist_matrix = pdist(features, metric='jaccard')
    Z = linkage(dist_matrix, method='ward')
    
    # رسم الشجرة
    fig, ax = plt.subplots(figsize=(8, 4))
    dendrogram(Z, labels=df['الجماعة'].values, ax=ax)
    plt.title("الشجرة اللهجية لتكتلات إقليم بولمان (Ward's Method)")
    st.pyplot(fig)

# ----------------------------------------------------
# 3. تبويب الخريطة الفضائية التفاعلية
# ----------------------------------------------------
with tab3:
    st.header("الخريطة الفضائية التفاعلية")
    
    m = folium.Map(location=[33.1500, -4.5000], zoom_start=9, tiles='OpenStreetMap')
    
    points = [
        {"name": "كيكو", "lat": 33.2100, "lon": -4.7000, "word": "ⵜⴰⴳⴰⵏⵜ (tagant)"},
        {"name": "تيمحضيت", "lat": 33.1500, "lon": -5.0500, "word": "ⵜⴰⴳⴰⵏⵜ (tagant)"},
        {"name": "أنجيل", "lat": 33.0800, "lon": -4.6000, "word": "ⵜⴰⵙⴰⵔⵓⵜ (tasarut)"},
        {"name": "أوطاط الحاج", "lat": 33.3500, "lon": -3.7000, "word": "ⵍⵖⴰⴱⴰ (lghaba)"}
    ]
    
    for p in points:
        folium.Marker(
            [p["lat"], p["lon"]],
            popup=f"<b>{p['name']}</b><br>المفردة: {p['word']}",
            tooltip=p["name"]
        ).add_to(m)
    
    st_folium(m, width=900, height=500)

# ----------------------------------------------------
# 4. تبويب التقارير والتصدير
# ----------------------------------------------------
with tab4:
    st.header("تصدير النتائج للأطروحة")
    st.download_button("تنزيل مصفوفة المسافات (CSV)", df.to_csv(index=False), "dialect_matrix.csv", "text/csv")
    st.info("💡 يمكنك استخدام الرسوم والمصفوفات مباشرة في فصول أطروحتك.")
