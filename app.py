import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------------
# 1. الإعدادات والتصميم البصري المتقدم (CSS Custom Styling)
# ---------------------------------------------------------
st.set_page_config(
    page_title="الأطلس اللغوي الأمازيغي - إقليم بولمان",
    page_icon="🌾",
    layout="wide"
)

st.markdown("""
    <style>
    /* الخطوط والخلفية العامة */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
        background-color: #f4f6f9;
    }
    
    /* القائمة الجانبية */
    div[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
        background-color: #ffffff;
        border-left: 1px solid #eaedf1;
    }

    /* الترويسة الرئيسية - متوازنة وموصّطة في المنتصف */
    .hero-header {
        background: linear-gradient(135deg, #1b365d 0%, #2e5b88 100%);
        color: #ffffff;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(27, 54, 93, 0.15);
        border-bottom: 5px solid #c5a059;
        margin-bottom: 2rem;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .hero-header h1 {
        color: #ffffff;
        font-size: 2.3rem;
        font-weight: 700;
        margin-top: 0.6rem;
        margin-bottom: 0.6rem;
        text-align: center;
    }
    .hero-header p {
        color: #e2e8f0;
        font-size: 1.15rem;
        margin-bottom: 0;
        text-align: center;
    }
    .academic-badge {
        background-color: rgba(197, 160, 89, 0.25);
        color: #f3e5ab;
        border: 1px solid #c5a059;
        padding: 5px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
    }

    /* بطاقات المؤشرات الإحصائية */
    .stat-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        border-top: 4px solid #1b365d;
        transition: transform 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-3px);
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #1b365d;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
    }

    /* بطاقات القاموس المعجمية */
    .lexical-card {
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        padding: 1.6rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
        transition: all 0.3s ease;
        position: relative;
    }
    .lexical-card:hover {
        border-color: #c5a059;
        box-shadow: 0 8px 25px rgba(27, 54, 93, 0.08);
        transform: translateY(-2px);
    }
    .word-tifinagh {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1b365d;
        line-height: 1.2;
    }
    .word-latin {
        font-size: 1.15rem;
        color: #64748b;
        font-style: italic;
    }
    .ref-tag {
        font-family: monospace;
        background-color: #f1f5f9;
        color: #475569;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* الشارات الملونة */
    .badge-cat {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .badge-loc {
        background-color: #fef3c7;
        color: #b45309;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .ipa-box {
        font-family: monospace;
        background-color: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.95rem;
    }

    /* المقتبس والأمثال */
    .proverb-container {
        background-color: #f8fafc;
        border-right: 4px solid #1b365d;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-top: 0.8rem;
        color: #334155;
        font-style: italic;
    }
    
    .citation-box {
        background-color: #f8fafc;
        border: 1px dashed #cbd5e1;
        padding: 8px 12px;
        font-size: 0.85rem;
        color: #475569;
        margin-top: 12px;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. قراءة قاعدة البيانات
# ---------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv', dtype=str, encoding='utf-8')
        df = df.fillna('')
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"خطأ في قراءة ملف البيانات data.csv: {e}")
        return pd.DataFrame()

df = load_data()

# ---------------------------------------------------------
# 3. الترويسة الرئيسية والجمالية (موصّطة في منتصف المربع الأزرق)
# ---------------------------------------------------------
st.markdown("""
    <div class="hero-header">
        <span class="academic-badge">🎓 مشروع أطروحة الدكتوراه في اللسانيات الأمازيغية</span>
        <h1>🌾 الأطلس اللغوي وقاموس الفلاحة والرعي الأمازيغي</h1>
        <p>منصة رقمية استكشافية لمعجم عتاد الفلاحة وتقنيات السقي والرعي - إقليم بولمان</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. القائمة الجانبية
# ---------------------------------------------------------
st.sidebar.markdown("### 🏛️ تصفية المعجم والأطلس")
st.sidebar.markdown("---")

if not df.empty:
    categories = ["جميع الحقول المعجمية"] + sorted([str(x) for x in df['category'].unique() if str(x).strip() != ''])
    selected_category = st.sidebar.selectbox("🎯 الحقل المعجمي:", categories)

    locations = ["جميع القبائل والمواقع"] + sorted([str(x) for x in df['location'].unique() if str(x).strip() != ''])
    selected_location = st.sidebar.selectbox("📍 الموقع الجغرافي / القبيلة:", locations)

    filtered_df = df.copy()

    if selected_category != "جميع الحقول المعجمية":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]

    if selected_location != "جميع القبائل والمواقع":
        filtered_df = filtered_df[filtered_df['location'] == selected_location]

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 تصدير البيانات الميدانية")
    csv_data = filtered_df.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button(
        label="📄 تحميل النتائج (CSV/Excel)",
        data=csv_data,
        file_name="atlas_data_export.csv",
        mime="text/csv",
        use_container_width=True
    )

# ---------------------------------------------------------
# 5. محرك البحث والبطاقات الإحصائية
# ---------------------------------------------------------
if not df.empty:
    col_s, col_r = st.columns([5, 1])
    with col_s:
        search_query = st.text_input(
            "البحث اللساني:",
            placeholder="🔍 ابحث بالتيفيناغ، اللاتينية، المعنى العربي، أو بالشواهد الميدانية...",
            label_visibility="collapsed"
        )
    with col_r:
        if st.button("🔄 إعادة ضبط", use_container_width=True):
            st.rerun()

    if search_query:
        query = search_query.strip().lower()
        filtered_df = filtered_df[
            filtered_df['arabic_meaning'].astype(str).str.contains(query, case=False) |
            filtered_df['word_tifinagh'].astype(str).str.contains(query, case=False) |
            filtered_df['word_latin'].astype(str).str.contains(query, case=False) |
            filtered_df['description'].astype(str).str.contains(query, case=False) |
            filtered_df['proverb'].astype(str).str.contains(query, case=False)
        ]

    # بطاقات الإحصاء
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(filtered_df)}</div><div class="stat-label">المواد المعروضة</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len([x for x in filtered_df["category"].unique() if str(x).strip() != ""])}</div><div class="stat-label">الحقول المعجمية</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len([x for x in filtered_df["location"].unique() if str(x).strip() != ""])}</div><div class="stat-label">المواقع الميدانية</div></div>', unsafe_allow_html=True)
    with c4:
        coverage = int((len(filtered_df)/len(df))*100) if len(df)>0 else 0
        st.markdown(f'<div class="stat-card"><div class="stat-number">{coverage}%</div><div class="stat-label">نسبة التغطية</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 6. التبويبات الرئيسية
    # ---------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["📚 المدونة المعجمية والبطاقات", "🗺️ الأطلس الجغرافي اللغوي", "📊 التحليل الإحصائي"])

    # --- التبويب 1: البطاقات المعجمية ---
    with tab1:
        if filtered_df.empty:
            st.info("⚠️ لم يتم العثور على أي نتائج تطابق عملية البحث.")
        else:
            page_size = 10
            total_items = len(filtered_df)
            pages = (total_items // page_size) + (1 if total_items % page_size > 0 else 0)

            if pages > 1:
                col_p1, col_p2 = st.columns([1, 4])
                with col_p1:
                    page_num = st.number_input("الصفحة المعجمية:", min_value=1, max_value=pages, value=1, step=1)
                start_idx = (page_num - 1) * page_size
                end_idx = start_idx + page_size
                current_df = filtered_df.iloc[start_idx:end_idx]
            else:
                current_df = filtered_df

            # عرض الكروت الجميلة
            for idx, row in current_df.iterrows():
                entry_id = f"REF-{str(idx+1).zfill(3)}"
                tifinagh = str(row['word_tifinagh'])
                latin = str(row['word_latin'])
                meaning = str(row['arabic_meaning'])
                ipa = str(row['ipa']) if 'ipa' in row else ''
                category = str(row['category']) if 'category' in row else ''
                location = str(row['location']) if 'location' in row else ''
                description = str(row['description']) if 'description' in row else ''
                proverb = str(row['proverb']) if 'proverb' in row else ''
                image_url = str(row['image']).strip() if 'image' in row else ''

                col_text, col_media = st.columns([3, 1]) if (image_url and image_url.startswith("http")) else (st.container(), None)

                with col_text:
                    st.markdown(f"""
                    <div class="lexical-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <div>
                                <span class="word-tifinagh">{tifinagh}</span>
                                <span class="word-latin">({latin})</span>
                            </div>
                            <span class="ref-tag">{entry_id}</span>
                        </div>
                        <div style="margin-bottom: 0.8rem;">
                            {f'<span class="badge-cat">{category}</span> ' if category else ''}
                            {f'<span class="badge-loc">📍 {location}</span>' if location else ''}
                        </div>
                        <p style="font-size: 1.15rem; margin-bottom: 0.4rem; color: #1e293b;"><b>المعنى بالعربية:</b> {meaning}</p>
                        {f'<p style="margin-bottom: 0.4rem;"><b>الترميز الصوتي (IPA):</b> <span class="ipa-box">[{ipa}]</span></p>' if ipa else ''}
                        {f'<p style="color: #475569; margin-bottom: 0.4rem;"><b>الوصف الميداني:</b> {description}</p>' if description else ''}
                        {f'<div class="proverb-container"><b>الشاهد النصي / المثل:</b> "{proverb}"</div>' if proverb else ''}
                        
                        <div class="citation-box">
                            📖 <b>الاستشهاد الأكاديمي:</b> الباحث. (2026). المادة المعجمية "{tifinagh}" ({latin}). <i>الأطلس اللغوي لإقليم بولمان</i>. المعرف: {entry_id}.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                if col_media:
                    with col_media:
                        try:
                            st.image(image_url, caption=meaning, use_column_width=True)
                        except Exception:
                            pass

    # --- التبويب 2: الخريطة ---
    with tab2:
        st.subheader("📍 الترسيم الجغرافي اللغوي")
        map_df = filtered_df.dropna(subset=['lat', 'lon'])
        m = folium.Map(location=[33.25, -4.50], zoom_start=9, tiles="OpenStreetMap")

        for _, row in map_df.iterrows():
            try:
                popup_html = f"""
                <div style="font-family: sans-serif; text-align: right; width: 180px;">
                    <h4 style="color: #1b365d; margin: 0;">{str(row['word_tifinagh'])} ({str(row['word_latin'])})</h4>
                    <b>المعنى:</b> {str(row['arabic_meaning'])}<br>
                    <b>الموقع:</b> {str(row['location'])}
                </div>
                """
                folium.Marker(
                    location=[float(row['lat']), float(row['lon'])],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{str(row['word_tifinagh'])} - {str(row['arabic_meaning'])}",
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)
            except Exception:
                continue

        st_folium(m, width="100%", height=500)

    # --- التبويب 3: الإحصائيات ---
    with tab3:
        st.subheader("📊 الرسوم البيانية للتوزيع اللغوي")
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.markdown("#### المواد حسب الحقول المعجمية")
            st.bar_chart(filtered_df['category'].value_counts())
        with col_chart2:
            st.markdown("#### المواد حسب النقاط الجغرافية")
            st.bar_chart(filtered_df['location'].value_counts())

# ---------------------------------------------------------
# 7. التذييل الأكاديمي
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.9rem; padding: 1rem 0;">
        <b>منصة الأطلس اللغوي وقاموس الفلاحة والرعي الأمازيغي (إقليم بولمان)</b><br>
        جميع الحقوق محفوظة للباحث © 2026 | أطروحة الدكتوراه في اللسانيات الأمازيغية
    </div>
""", unsafe_allow_html=True)
