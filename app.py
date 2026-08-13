import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------------
# 1. إعدادات الصفحة وتصميم CSS متقدم للواجهة المعجمية
# ---------------------------------------------------------
st.set_page_config(
    page_title="أطلس وقاموس الفلاحة الأمازيغية - إقليم بولمان",
    page_icon="🌾",
    layout="wide"
)

st.markdown("""
    <style>
    /* الإعدادات العامة للغة العربية */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f8f9fa;
    }
    div[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    
    /* العناوين والترويسة */
    .header-box {
        background: linear-gradient(135deg, #1e4620 0%, #2e7d32 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    .header-box h1 {
        color: #ffffff;
        font-size: 2.3rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    .header-box p {
        color: #e8f5e9;
        font-size: 1.1rem;
        margin: 0;
    }

    /* بطاقات القاموس المعجمية */
    .word-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;
    }
    .word-card:hover {
        border-color: #2e7d32;
        box-shadow: 0 5px 15px rgba(46, 125, 50, 0.12);
        transform: translateY(-2px);
    }
    .tifinagh-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1e4620;
        margin-bottom: 0.2rem;
    }
    .latin-title {
        font-size: 1.1rem;
        color: #555555;
        font-style: italic;
    }
    .badge-category {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-location {
        background-color: #fff3e0;
        color: #e65100;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    .ipa-text {
        font-family: monospace;
        background-color: #f1f3f4;
        padding: 2px 8px;
        border-radius: 4px;
        color: #d32f2f;
    }
    .proverb-box {
        border-right: 3px solid #2e7d32;
        padding-right: 12px;
        margin-top: 10px;
        background-color: #fafafa;
        padding-top: 6px;
        padding-bottom: 6px;
        font-style: italic;
        color: #333;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. قراءة قاعدة البيانات الخارجية (CSV) بمرونة وآمان
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
# 3. القائمة الجانبية للتصفية المتقدمة
# ---------------------------------------------------------
st.sidebar.markdown("## 🌾 تصفية المعجم")
st.sidebar.markdown("---")

if not df.empty:
    search_query = st.sidebar.text_input("🔍 البحث الشامل:", placeholder="ابحث بالتيفيناغ، العربي، اللاتيني...")
    
    categories = ["الكل"] + sorted([str(x) for x in df['category'].unique() if str(x).strip() != ''])
    selected_category = st.sidebar.selectbox("🎯 الحقل المعجمي:", categories)

    locations = ["الكل"] + sorted([str(x) for x in df['location'].unique() if str(x).strip() != ''])
    selected_location = st.sidebar.selectbox("📍 القبيلة / المنطقة:", locations)

    filtered_df = df.copy()

    if selected_category != "الكل":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]

    if selected_location != "الكل":
        filtered_df = filtered_df[filtered_df['location'] == selected_location]

    if search_query:
        query = search_query.strip().lower()
        filtered_df = filtered_df[
            filtered_df['arabic_meaning'].astype(str).str.contains(query, case=False) |
            filtered_df['word_tifinagh'].astype(str).str.contains(query, case=False) |
            filtered_df['word_latin'].astype(str).str.contains(query, case=False) |
            filtered_df['description'].astype(str).str.contains(query, case=False)
        ]

# ---------------------------------------------------------
# 4. الواجهة الرئيسية
# ---------------------------------------------------------
st.markdown("""
    <div class="header-box">
        <h1>🌾 الأطلس اللغوي وقاموس الفلاحة والرعي الأمازيغي</h1>
        <p>دراسة توثيقية لسانياتية ومعجمية لعتاد الفلاحة وتقنيات السقي والرعي بإقليم بولمان</p>
    </div>
""", unsafe_allow_html=True)

if df.empty:
    st.warning("يرجى التأكد من وجود ملف data.csv في المستودع بصيغة صحيحة.")
else:
    # المؤشرات الإحصائية
    m1, m2, m3 = st.columns(3)
    m1.metric("إجمالي المفردات", len(filtered_df))
    m2.metric("الحقول المعجمية", len([x for x in df['category'].unique() if str(x).strip() != '']))
    m3.metric("المواقع الجغرافية", len([x for x in df['location'].unique() if str(x).strip() != '']))

    st.markdown("---")

    tab1, tab2 = st.tabs(["📚 القاموس والمعجم اللساني", "🗺️ الخريطة اللغوية التفاعلية"])

    # --- التبويب 1: القاموس والواجهة المعجمية ---
    with tab1:
        st.subheader("سجل المصطلحات والمفردات المعجمية")
        
        if filtered_df.empty:
            st.info("لا توجد نتائج تطابق خيارات البحث الحالية.")
        else:
            # نظام الصفحات
            page_size = 10
            total_items = len(filtered_df)
            pages = (total_items // page_size) + (1 if total_items % page_size > 0 else 0)
            
            if pages > 1:
                col_p1, col_p2 = st.columns([1, 4])
                with col_p1:
                    page_num = st.number_input("الصفحة:", min_value=1, max_value=pages, value=1, step=1)
                start_idx = (page_num - 1) * page_size
                end_idx = start_idx + page_size
                current_df = filtered_df.iloc[start_idx:end_idx]
                st.caption(f"عرض {start_idx + 1} - {min(end_idx, total_items)} من أصل {total_items} كلمة")
            else:
                current_df = filtered_df

            # عرض البطاقات المعجمية
            for _, row in current_df.iterrows():
                tifinagh = str(row['word_tifinagh'])
                latin = str(row['word_latin'])
                meaning = str(row['arabic_meaning'])
                ipa = str(row['ipa']) if 'ipa' in row else ''
                category = str(row['category']) if 'category' in row else ''
                location = str(row['location']) if 'location' in row else ''
                description = str(row['description']) if 'description' in row else ''
                proverb = str(row['proverb']) if 'proverb' in row else ''
                image_url = str(row['image']).strip() if 'image' in row else ''

                # تصميم الكارت
                col_card, col_img = st.columns([3, 1]) if (image_url and image_url.startswith("http")) else (st.container(), None)
                
                with col_card:
                    st.markdown(f"""
                    <div class="word-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span class="tifinagh-title">{tifinagh}</span>
                                <span class="latin-title">({latin})</span>
                            </div>
                            <div>
                                {f'<span class="badge-category">{category}</span>' if category else ''}
                                {f'<span class="badge-location">📍 {location}</span>' if location else ''}
                            </div>
                        </div>
                        <hr style="margin: 0.8rem 0; border: 0; border-top: 1px solid #eee;">
                        <p style="font-size: 1.15rem; margin-bottom: 0.5rem;"><b>المعنى بالعربية:</b> {meaning}</p>
                        {f'<p style="margin-bottom: 0.5rem;"><b>الترميز الصوتي (IPA):</b> <span class="ipa-text">[{ipa}]</span></p>' if ipa else ''}
                        {f'<p style="color: #555; margin-bottom: 0.5rem;"><b>الوصف الميداني:</b> {description}</p>' if description else ''}
                        {f'<div class="proverb-box"><b>الشاهد النصي / المثل:</b> "{proverb}"</div>' if proverb else ''}
                    </div>
                    """, unsafe_allow_html=True)
                
                if col_img:
                    with col_img:
                        try:
                            st.image(image_url, caption=meaning, use_column_width=True)
                        except Exception:
                            pass

    # --- التبويب 2: الخريطة اللغوية ---
    with tab2:
        st.subheader("الترسيم الجغرافي للمصطلحات الفلاحية")
        map_df = filtered_df.dropna(subset=['lat', 'lon'])

        m = folium.Map(location=[33.25, -4.50], zoom_start=9, tiles="OpenStreetMap")

        for _, row in map_df.iterrows():
            try:
                popup_html = f"""
                <div style="font-family: sans-serif; text-align: right; width: 180px;">
                    <h4 style="color: #2e7d32; margin: 0;">{str(row['word_tifinagh'])} ({str(row['word_latin'])})</h4>
                    <b>المعنى:</b> {str(row['arabic_meaning'])}<br>
                    <b>الموقع:</b> {str(row['location'])}
                </div>
                """
                folium.Marker(
                    location=[float(row['lat']), float(row['lon'])],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{str(row['word_tifinagh'])} - {str(row['arabic_meaning'])}",
                    icon=folium.Icon(color="green", icon="leaf")
                ).add_to(m)
            except Exception:
                continue

        st_folium(m, width="100%", height=500)

# ---------------------------------------------------------
# 5. التذييل
# ---------------------------------------------------------
st.markdown("---")
st.caption("مركز التوثيق الرقمي والأطلس اللغوي | أطروحة الدكتوراه - إقليم بولمان")
