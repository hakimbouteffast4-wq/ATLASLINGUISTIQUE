import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------------
# 1. الإعدادات والتصميم الأكاديمي المتقدم
# ---------------------------------------------------------
st.set_page_config(
    page_title="الأطلس اللغوي الأمازيغي - إقليم بولمان | المنصة الأكاديمية",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
    <style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Amiri', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #fdfdfd;
    }
    div[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
        background-color: #f4f6f8;
    }
    
    /* الترويسة الأكاديمية */
    .academic-header {
        background: #1b365d; /* أزرق أكاديمي كلاسيكي */
        color: white;
        padding: 2rem;
        border-radius: 8px;
        border-bottom: 4px solid #c5a059; /* ذهبي أكاديمي */
        margin-bottom: 1.5rem;
    }
    .academic-header h1 {
        color: #ffffff;
        font-size: 2.2rem;
        margin-bottom: 0.4rem;
        font-weight: bold;
    }
    .academic-header h3 {
        color: #c5a059;
        font-size: 1.2rem;
        margin-top: 0;
        font-weight: normal;
    }
    .meta-info {
        font-size: 0.9rem;
        color: #d1d5db;
        border-top: 1px solid rgba(255,255,255,0.2);
        padding-top: 0.8rem;
        margin-top: 1rem;
    }

    /* بطاقة المادة المعجمية الأكاديمية */
    .lexical-entry {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-right: 5px solid #1b365d;
        border-radius: 6px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .entry-headword {
        font-size: 2rem;
        font-weight: bold;
        color: #1b365d;
        display: inline-block;
    }
    .entry-latin {
        font-size: 1.2rem;
        color: #555555;
        font-style: italic;
        margin-right: 8px;
    }
    .entry-id {
        font-family: monospace;
        background: #eef2f6;
        color: #1b365d;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        float: left;
    }
    .ipa-badge {
        font-family: 'Lucida Sans Unicode', 'Arial Unicode MS', monospace;
        background-color: #f0f4f8;
        padding: 3px 8px;
        border-radius: 4px;
        color: #8b0000;
        border: 1px solid #d0d7de;
        font-size: 1rem;
    }
    .tag-category {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .tag-location {
        background-color: #fff8e1;
        color: #b78103;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .citation-box {
        background-color: #f8f9fa;
        border: 1px dashed #ccc;
        padding: 8px 12px;
        font-size: 0.85rem;
        color: #555;
        margin-top: 10px;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. تحميل قراءة البيانات بأسلوب آمن
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
        st.error(f"خطأ في قراءة ملف قاعدة البيانات: {e}")
        return pd.DataFrame()

df = load_data()

# ---------------------------------------------------------
# 3. الترويسة الأكاديمية ومؤشرات الأطروحة
# ---------------------------------------------------------
st.markdown("""
    <div class="academic-header">
        <h1>🎓 الأطلس اللغوي وقاموس الفلاحة والرعي الأمازيغي</h1>
        <h3>منصة رقمية استكشافية لمعجم عتاد الفلاحة وتقنيات السقي والرعي بإقليم بولمان</h3>
        <div class="meta-info">
            <b>مشروع بحث لنيل شهادة الدكتوراه في اللسانيات الأمازيغية</b> | إعداد الطالب الباحث | تحت إشراف لجنة المناقشة الأكاديمية
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. القائمة الجانبية الضابطة للبحث الميداني
# ---------------------------------------------------------
st.sidebar.markdown("### 🏛️ أدوات الضبط الأكاديمي")
st.sidebar.markdown("---")

if not df.empty:
    categories = ["جميع الحقول المعجمية"] + sorted([str(x) for x in df['category'].unique() if str(x).strip() != ''])
    selected_category = st.sidebar.selectbox("🎯 الحقل المعجمي:", categories)

    locations = ["جميع القبائل والمواقع"] + sorted([str(x) for x in df['location'].unique() if str(x).strip() != ''])
    selected_location = st.sidebar.selectbox("📍 الموقع الجغرافي / القبيلة:", locations)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 تصدير البيانات الميدانية")
    
    # فلترة البيانات
    filtered_df = df.copy()

    if selected_category != "جميع الحقول المعجمية":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]

    if selected_location != "جميع القبائل والمواقع":
        filtered_df = filtered_df[filtered_df['location'] == selected_location]

# ---------------------------------------------------------
# 5. محرك البحث المعجمي السريع
# ---------------------------------------------------------
if not df.empty:
    col_s, col_r = st.columns([5, 1])
    with col_s:
        search_query = st.text_input(
            "البحث اللساني:",
            placeholder="ابحث بالمدخل (تيفيناغ)، بالترميز الصوتي، بالمعنى العربي، بالوصف أو بالشواهد الميدانية...",
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

    # زر تحميل البيانات للباحثين
    csv_data = filtered_df.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button(
        label="📄 تحميل النتائج (CSV/Excel)",
        data=csv_data,
        file_name="dialectal_data_export.csv",
        mime="text/csv",
        use_container_width=True
    )

    # الإحصائيات الأكاديمية
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("عينة المواد المعجمية", len(filtered_df))
    col_m2.metric("الحقول المعجمية", len([x for x in filtered_df['category'].unique() if str(x).strip() != '']))
    col_m3.metric("مواقع المسح الميداني", len([x for x in filtered_df['location'].unique() if str(x).strip() != '']))
    col_m4.metric("نسبة التغطية الميدانية", f"{int((len(filtered_df)/len(df))*100)}%" if len(df)>0 else "0%")

    st.markdown("---")

    # ---------------------------------------------------------
    # 6. التبويبات الأكاديمية
    # ---------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["📚 المدونة المعجمية والبطاقات اللسانية", "🗺️ الأطلس الجغرافي اللغوي", "📊 الإحصاء والتوزيع المعجمي"])

    # --- التبويب 1: المدونة المعجمية ---
    with tab1:
        if filtered_df.empty:
            st.warning("لم تُسفر عملية البحث والفلترة عن نتائج تطابق المعايير المحددة.")
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
                st.caption(f"عرض المواد المعجمية من {start_idx + 1} إلى {min(end_idx, total_items)} (إجمالي العينة: {total_items})")
            else:
                current_df = filtered_df

            # عرض المدخلات المعجمية
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
                    <div class="lexical-entry">
                        <span class="entry-id">{entry_id}</span>
                        <div>
                            <span class="entry-headword">{tifinagh}</span>
                            <span class="entry-latin">({latin})</span>
                        </div>
                        <div style="margin-top: 8px;">
                            {f'<span class="tag-category">الحقل: {category}</span>' if category else ''}
                            {f'<span class="tag-location">📍 النقطة: {location}</span>' if location else ''}
                        </div>
                        <hr style="margin: 0.8rem 0; border: 0; border-top: 1px solid #eeeeee;">
                        <p style="font-size: 1.1rem; margin-bottom: 0.4rem;"><b>الدلالة والترجمة:</b> {meaning}</p>
                        {f'<p style="margin-bottom: 0.4rem;"><b>الترميز الصوتي الدولي (IPA):</b> <span class="ipa-badge">[{ipa}]</span></p>' if ipa else ''}
                        {f'<p style="color: #444; margin-bottom: 0.4rem;"><b>الوصف اللساني والميداني:</b> {description}</p>' if description else ''}
                        {f'<p style="color: #1b365d; font-style: italic; margin-bottom: 0.4rem;"><b>الشاهد النصي / المثل:</b> "{proverb}"</p>' if proverb else ''}
                        
                        <div class="citation-box">
                            📖 <b>كيفية الاستشهاد الأكاديمي بفي هذا المدخل:</b><br>
                            الباحث. (2026). المادة المعجمية "{tifinagh}" ({latin}). <i>الأطلس اللغوي وقاموس الفلاحة بإقليم بولمان</i>. المعرف: {entry_id}.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                if col_media:
                    with col_media:
                        try:
                            st.image(image_url, caption=f"المعطى البصري الميداني: {meaning}", use_column_width=True)
                        except Exception:
                            pass

    # --- التبويب 2: الأطلس الجغرافي اللغوي ---
    with tab2:
        st.subheader("الترسيم الجغرافي للمواد المعجمية المفلترة")
        st.caption("يعرض الأطلس توزيع الظواهر اللغوية والمعجمية عبر نقاط الجمع الميداني بإقليم بولمان.")

        map_df = filtered_df.dropna(subset=['lat', 'lon'])
        m = folium.Map(location=[33.25, -4.50], zoom_start=9, tiles="OpenStreetMap")

        for _, row in map_df.iterrows():
            try:
                popup_html = f"""
                <div style="font-family: sans-serif; text-align: right; width: 200px;">
                    <h4 style="color: #1b365d; margin: 0;">{str(row['word_tifinagh'])} ({str(row['word_latin'])})</h4>
                    <b>المعنى:</b> {str(row['arabic_meaning'])}<br>
                    <b>النقطة الجغرافية:</b> {str(row['location'])}
                </div>
                """
                folium.Marker(
                    location=[float(row['lat']), float(row['lon'])],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{str(row['word_tifinagh'])} - {str(row['arabic_meaning'])}",
                    icon=folium.Icon(color="navy", icon="info-sign")
                ).add_to(m)
            except Exception:
                continue

        st_folium(m, width="100%", height=550)

    # --- التبويب 3: الإحصاء والتحليل المعجمي ---
    with tab3:
        st.subheader("📊 التحليل الإحصائي والتوزيع اللغوي")
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("#### التوزيع حسب الحقول المعجمية")
            cat_counts = filtered_df['category'].value_counts()
            st.bar_chart(cat_counts)
            
        with col_c2:
            st.markdown("#### التوزيع حسب النقاط الجغرافية/القبائل")
            loc_counts = filtered_df['location'].value_counts()
            st.bar_chart(loc_counts)

# ---------------------------------------------------------
# 7. التذييل الأكاديمي الرسمي
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <b>منصة الأطلس اللغوي وقاموس الفلاحة والرعي بالأطلس المتوسط الشرق (إقليم بولمان)</b><br>
        جميع الحقوق محفوظة للباحث © 2026 | مختبر اللسان والمجتمع والتنشئة الثقافية
    </div>
""", unsafe_allow_html=True)
