import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. إعدادات الصفحة
st.set_page_config(page_title="    SRCA", layout="wide")

# تصميم الهوية البصرية
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-right: 5px solid #D32F2F;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricLabel"] { font-size: 14px !important; font-weight: bold !important; color: #555 !important; }
    [data-testid="stMetricValue"] { color: #D32F2F !important; font-size: 24px !important; }
    h1, h2, h3 { color: #D32F2F !important; text-align: right; font-family: 'Arial'; }
    .stMarkdown { direction: rtl; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = 'كمية جديداستهلاك هيئة الهلال الاحمر السعودي (نسخة بعد المعالجة).xlsx'
    try:
        df = pd.read_excel(file_name)
        df['Year'] = df['Year'].astype(str).str.replace('.0', '', regex=False)
        df['Collective CA'] = df['Collective CA'].astype(str).str.strip()
        df['Contract Account'] = df['Contract Account'].astype(str).str.strip()
        df['Status'] = df['Status'].fillna('غير محدد').astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"❌ تعذر العثور على الملف: {e}")
        return None

df = load_data()

if df is not None:
    # حساب الثوابت العامة
    TOTAL_COUNTERS = df['Contract Account'].nunique()
    TOTAL_COLLECTIVE = df['Collective CA'].nunique()
    MISSING = df.isnull().sum().sum()
    DUPLICATES = df.duplicated().sum()

    # --- القائمة الجانبية (Sidebar) ---
    with st.sidebar:
        try: st.image("SRCAlogo_local_cmyk.jpg", use_container_width=True)
        except: pass
        st.markdown("<h2 style='text-align: center;'>لوحة التحكم</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        all_years = sorted(df['Year'].unique())
        sel_all_years = st.checkbox("اختيار كل السنوات", value=True)
        selected_years = all_years if sel_all_years else st.multiselect("📅 السنوات:", all_years)

        st.markdown("---")
        all_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        sel_all_months = st.checkbox("اختيار كل الشهور", value=True)
        selected_months = all_months if sel_all_months else st.multiselect("🗓️ الشهور:", all_months)

        st.markdown("---")
        all_cas = sorted(df['Collective CA'].unique())
        sel_all_cas = st.checkbox("اختيار كل الحسابات التجميعية", value=True)
        selected_cas = all_cas if sel_all_cas else st.multiselect("🏢 الحسابات التجميعية:", all_cas)

        st.markdown("---")
        available_meters = sorted(df[df['Collective CA'].isin(selected_cas)]['Contract Account'].unique())
        sel_all_meters = st.checkbox("اختيار كل العدادات", value=True)
        selected_meters = available_meters if sel_all_meters else st.multiselect("🔢 ابحث عن رقم عداد معين:", available_meters)

    # تطبيق الفلترة 
    mask = (df['Year'].isin(selected_years)) & \
           (df['Month'].isin(selected_months)) & \
           (df['Collective CA'].isin(selected_cas)) & \
           (df['Contract Account'].isin(selected_meters))
    
    df_filtered = df[mask]

    # تعريف التبويبات
  
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 الملخص التنفيذي والجودة", "📊 التحليل الإحصائي", "🏢 إدارة الأصول", "🤖 التوقعات ل 2026"])

    # ---------------------------------------------------------
    # تبويب 1: الملخص التنفيذي والجودة
    # ---------------------------------------------------------
    with tab1:
        st.header("📊 الملخص المالي ومؤشرات جودة البيانات")
        with st.expander("🛡️ تقرير موثوقية وجودة البيانات", expanded=True):
            check_meters = df_filtered.groupby(['Contract Account']).agg({
                'Net Sales Amount': 'sum',
                'Net Sales Quantity': 'sum'
            }).reset_index()
            
            zero_meters_count = len(check_meters[check_meters['Net Sales Amount'] == 0])
            zero_qty_count = len(check_meters[check_meters['Net Sales Quantity'] == 0])

            q1, q2, q3, q4 = st.columns(4)
            q1.metric("القيم المفقودة", f"✅ {MISSING}")
            q2.metric("السجلات المكررة", f"✅ {DUPLICATES}")
            q3.metric("إجمالي السجلات", f"{len(df_filtered):,}")
            q4.write("**🛠️ مجهود التنظيف:**")
            st.markdown("<p style='font-size:12px; color:gray;'>تم معالجة التكرار وحصر الأصول الخاملة.</p>", unsafe_allow_html=True)
            
            st.markdown("---")
            z1, z2 = st.columns(2)
            z1.warning(f"🏠 **عدادات خاملة في الفترة المختارة:** {zero_meters_count:,} عداد")
            z2.info(f"⚡ **عدادات بدون استهلاك في الفترة المختارة:** {zero_qty_count:,} عداد")

        # KPIs المالية
        m1, m2, m3 = st.columns(3)
        filtered_collective_count = df_filtered['Collective CA'].nunique()
        m1.metric("إجمالي المبالغ", f"{df_filtered['Net Sales Amount'].sum():,.2f} ريال")
        m2.metric("إجمالي الاستهلاك", f"{df_filtered['Net Sales Quantity'].sum():,.0f} وحدة")
        m3.metric("الحسابات التجميعية النشطة", f"{filtered_collective_count} حساب")

        # تحليل الميزانية
        st.subheader("⚖️ تحليل الميزانية السنوية")
        cols = st.columns(len(selected_years)) if len(selected_years) > 0 else st.columns(1)
        for i, year in enumerate(sorted(selected_years)):
            y_amt = df_filtered[df_filtered['Year'] == year]['Net Sales Amount'].sum()
            cols[i].markdown(f"<div style='background-color:#ffffff; padding:15px; border-radius:10px; border-right:5px solid #D32F2F; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'><p style='color:#555555; font-weight:bold; margin-bottom:5px;'>إجمالي ميزانية سنة {year}</p><span style='color:#D32F2F; font-size:24px; font-weight:bold;'>{y_amt:,.0f} ريال</span></div>", unsafe_allow_html=True)

        # إعادة رسم التطور الشهري (الرسم المفقود)
        st.subheader("📈 التطور الشهري للاستهلاك (2024 vs 2025)")
        trend = df_filtered.groupby(['Year', 'Month'])['Net Sales Amount'].sum().reset_index()
        trend['Month'] = pd.Categorical(trend['Month'], categories=all_months, ordered=True)
        fig_trend = px.line(trend.sort_values('Month'), x='Month', y='Net Sales Amount', color='Year', 
                             markers=True, line_shape="spline", 
                             color_discrete_map={'2024': '#555555', '2025': '#D32F2F'})
        st.plotly_chart(fig_trend, use_container_width=True, key="main_line_chart")

        # سجل الحسابات المتوقفة
        st.subheader("⚠️ سجل الحسابات التجميعية المتوقفة")
        ca_24 = set(df[df['Year'] == '2024']['Collective CA'].unique())
        ca_25 = set(df[df['Year'] == '2025']['Collective CA'].unique())
        stopped_accounts = sorted(list(ca_24 - ca_25))
        if stopped_accounts:
            st.warning(f"تم رصد {len(stopped_accounts)} حساب تجميعي توقف في عام 2025")
            stopped_df = pd.DataFrame(stopped_accounts, columns=['رقم الحساب التجميعي المتوقف'])
            st.dataframe(stopped_df, use_container_width=True)
            st.download_button("📥 تحميل قائمة المتوقفين", data=stopped_df.to_csv(index=False).encode('utf-8-sig'), file_name="stopped_accounts.csv")

    # ---------------------------------------------------------
    # تبويب 2: التحليل الإحصائي
    # ---------------------------------------------------------
    with tab2:
        st.header("📈 مجهر التحليل والمقارنة الإحصائية")
        df_24 = df_filtered[df_filtered['Year'] == '2024']
        df_25 = df_filtered[df_filtered['Year'] == '2025']
        
        sum_24, sum_25 = df_24['Net Sales Amount'].sum(), df_25['Net Sales Amount'].sum()
        if sum_24 > 0:
            growth = ((sum_25 - sum_24) / sum_24) * 100
            st.metric(label="📊 معدل التغير (2024 vs 2025)", value=f"{growth:,.2f}%", delta=f"{growth:,.2f}%", delta_color="inverse")
        
        st.markdown("---")
        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown("المتوسط ")
            st.metric("2024", f"{df_24['Net Sales Amount'].mean():,.0f}")
            st.metric("2025", f"{df_25['Net Sales Amount'].mean():,.0f}")
        with k2:
            st.markdown("الوسيط ")
            st.metric("2024", f"{df_24['Net Sales Amount'].median():,.0f}")
            st.metric("2025", f"{df_25['Net Sales Amount'].median():,.0f}")
        with k3:
            st.markdown("الانحراف المعياري")
            st.metric("2024", f"{df_24['Net Sales Amount'].std():,.0f}")
            st.metric("2025", f"{df_25['Net Sales Amount'].std():,.0f}")

        st.markdown("---")
        st.subheader("🚩 أعلى 5 عدادات زيادةً في التكلفة")
        pivot_df = df_filtered.pivot_table(index='Contract Account', columns='Year', values='Net Sales Amount', aggfunc='sum').fillna(0)
        if '2024' in pivot_df.columns and '2025' in pivot_df.columns:
            pivot_df['الفرق'] = pivot_df['2025'] - pivot_df['2024']
            top_5 = pivot_df.sort_values(by='الفرق', ascending=False).head(5).reset_index()
            top_5_melted = top_5.melt(id_vars='Contract Account', value_vars=['2024', '2025'], var_name='السنة', value_name='المبلغ')
            fig_top5 = px.bar(top_5_melted, x='Contract Account', y='المبلغ', color='السنة', barmode='group', color_discrete_map={'2024': '#555555', '2025': '#D32F2F'}, text_auto='.2s')
            st.plotly_chart(fig_top5, use_container_width=True)

    # ---------------------------------------------------------
    # تبويب 3: إدارة الأصول
    # ---------------------------------------------------------
    with tab3:
        st.header("🏢 إدارة الحسابات التجميعية والأصول")
        st.subheader(" الهيكل الشجري")
        df_tree = df_filtered.copy()
        df_tree['Counter'] = 1
        tree_grouped = df_tree.groupby(['Collective CA', 'Contract Account', 'Status']).agg({'Net Sales Amount': 'sum', 'Counter': 'sum'}).reset_index()
        fig_tree = px.treemap(tree_grouped, path=['Collective CA', 'Contract Account', 'Status'], values='Net Sales Amount', color='Net Sales Amount', color_continuous_scale='Reds')
        st.plotly_chart(fig_tree, use_container_width=True, key="tree_map_final")

        st.markdown("---")
        col_dist, col_perf = st.columns(2)
        with col_dist:
            status_dist = df_filtered.groupby('Status')['Contract Account'].nunique().reset_index()
            st.plotly_chart(px.pie(status_dist, values='Contract Account', names='Status', hole=0.5, title="توزيع الحالات", color_discrete_sequence=px.colors.sequential.Reds_r), use_container_width=True)
        with col_perf:
            st.write("📑 **تحليل أداء العدادات **")
            
            # 1. حساب الأداء وتجميع البيانات
            meter_performance = df_filtered.groupby('Contract Account').agg({
                'Net Sales Amount': ['mean', 'median', 'std', 'max']
            }).reset_index()
            
            meter_performance.columns = ['رقم العداد', 'المتوسط', 'الوسيط', 'الانحراف', 'أعلى فاتورة']
            
            # --- ترتيب العدادات حسب المتوسط (الأعلى أولاً) ---
            meter_performance = meter_performance.sort_values(by='المتوسط', ascending=False).reset_index(drop=True)

            # 2. مربع البحث السريع
            search_query = st.text_input("🔍 بحث برقم العداد داخل الجدول:", key="search_meter_v2")

            if search_query:
                # فلترة الجدول بناءً على البحث مع الحفاظ على الترتيب
                meter_performance = meter_performance[meter_performance['رقم العداد'].astype(str).str.contains(search_query)]

            # 3. عرض الجدول المرتب (تفاعلي)
            st.dataframe(
                meter_performance, 
                use_container_width=True,
                height=400 
            )
            
            st.caption(f"💡 تم ترتيب العدادات تنازلياً حسب متوسط الصرف (الأعلى أولاً). إجمالي المعروض: {len(meter_performance)} عداد.")

        st.markdown("---")
        st.subheader("📋 كاشف تفاصيل الحساب التجميعي")
        target_ca = st.selectbox("🎯 اختر حساباً للمعاينة:", sorted(df_filtered['Collective CA'].unique()), key="ca_sel")
        if target_ca:
            ca_details = df_filtered[df_filtered['Collective CA'] == target_ca]
            active = ca_details[ca_details['Net Sales Amount'] > 0]
            unique_list = active.groupby(['Contract Account', 'Status']).agg({'Net Sales Amount': 'sum', 'Net Sales Quantity': 'sum'}).reset_index()
            c1, c2, c3 = st.columns(3)
            c1.metric("عدادات نشطة", len(unique_list))
            c2.metric("إجمالي المبالغ", f"{unique_list['Net Sales Amount'].sum():,.2f}")
            c3.metric("إجمالي الاستهلاك", f"{unique_list['Net Sales Quantity'].sum():,.0f}")
            st.dataframe(unique_list.sort_values('Net Sales Amount', ascending=False), use_container_width=True)

            # ---------------------------------------------------------
# ---------------------------------------------------------
   # ---------------------------------------------------------
   # ---------------------------------------------------------
    # تبويب 4: التوقعات الذكية لعام 2026 (ميزانية كاملة ومقارنة)
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # تبويب 4: التوقعات الذكية لعام 2026 (ميزانية كاملة ومقارنة)
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # تبويب 4: التوقعات الذكية لعام 2026 (النسخة المصححة)
    # ---------------------------------------------------------
   # ---------------------------------------------------------
    # تبويب 4: التوقعات الذكية لعام 2026 (تفاعلي مع الفلاتر)
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # تبويب 4: التوقعات الذكية لعام 2026 (ميزانية مستقلة)
    # ---------------------------------------------------------
    with tab4:
        import joblib
        import os

        st.header("🤖 محرك التنبؤ المالي - ميزانية 2026")
        
        model_path = 'xgb_model_srca.pkl'
        means_path = 'ca_means.pkl'

        if os.path.exists(model_path) and os.path.exists(means_path):
            model_ca = joblib.load(model_path)
            ca_means = joblib.load(means_path)

            if st.button("🔮 توليد توقعات 2026 للفترة المختارة"):
                with st.spinner('جاري بناء الميزانية المتوقعة...'):
                    
                    # تجهيز البيانات بناءً على الفلاتر
                    current_df = df_filtered.copy()
                    active_cas = current_df['Collective CA'].unique()
                    future_data = []
                    
                    # نأخذ آخر استهلاك كمرجع للنمط (Lag)
                    last_amounts = current_df.groupby('Collective CA')['Net Sales Amount'].last().to_dict()

                    for ca in active_cas:
                        for m_idx in range(1, 13):
                            future_data.append({
                                'Collective CA': ca,
                                'Year_Num': 2026,
                                'Month_Num': m_idx,
                                'Quarter': (m_idx-1)//3 + 1,
                                'Last_Month_Sales': last_amounts.get(ca, 0),
                                'CA_Average': ca_means.get(ca, 0)
                            })
                    
                    if future_data:
                        f_df = pd.DataFrame(future_data)
                        features = ['Year_Num', 'Month_Num', 'Quarter', 'Last_Month_Sales', 'CA_Average']
                        f_df['Predicted'] = model_ca.predict(f_df[features])

                        # --- القسم الأول: ميزانية 2026 فقط ---
                        st.subheader("📊 منحنى الميزانية التقديرية لعام 2026")
                        
                        # تجميع التوقعات حسب الشهر
                        pred_monthly = f_df.groupby('Month_Num')['Predicted'].sum().reset_index()
                        
                        fig_2026_only = px.line(pred_monthly, x='Month_Num', y='Predicted',
                                             markers=True, line_shape="spline",
                                             color_discrete_sequence=['#D32F2F'], # اللون الأحمر للهوية
                                             title="توزيع ميزانية 2026 المتوقعة (12 شهر)")
                        
                        fig_2026_only.update_layout(
                            xaxis=dict(tickmode='linear', tick0=1, dtick=1, title="الشهر"),
                            yaxis_title="إجمالي التوقع (ريال)",
                            hovermode="x unified",
                            template="plotly_white"
                        )
                        st.plotly_chart(fig_2026_only, use_container_width=True)

                        # --- القسم الثاني: المقارنة المالية (أعلى 5) ---
                        st.markdown("---")
                        col_p, col_f = st.columns(2)
                        with col_p:
                            st.subheader(f"⬅️ أعلى 5 في {selected_years[0] if selected_years else '2024'}")
                            past_t = current_df.groupby('Collective CA')['Net Sales Amount'].sum().nlargest(5).reset_index()
                            st.dataframe(past_t.rename(columns={'Collective CA': 'الحساب', 'Net Sales Amount': 'صرف فعلي'}), use_container_width=True)
                        with col_f:
                            st.subheader("🔮 أعلى 5 متوقعة (2026)")
                            future_t = f_df.groupby('Collective CA')['Predicted'].sum().nlargest(5).reset_index()
                            st.dataframe(future_t.rename(columns={'Collective CA': 'الحساب', 'Predicted': 'توقع 2026'}), use_container_width=True)

                    else:
                        st.warning("⚠️ يرجى اختيار حسابات تجميعية من القائمة الجانبية.")

            # --- القسم الثالث: تفاصيل الموديل (الزبده) ---
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.info("**الخوارزمية:** \n\n XGBoost Regressor")
            m2.success("**الدقة:** \n\n 97.07% (R2 Score)")
            m3.warning("**الأساس:** \n\n الأنماط الموسمية وتاريخ الاستهلاك")
        else:
            st.warning("⚠️ ملفات الموديل (.pkl) مفقودة")
# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<div style='text-align: center;'><h3 style='margin-bottom: 0px; color: #D32F2F;'>هيئة الهلال الأحمر السعودي</h3><p style='font-size: 16px; color: #555; font-weight: bold;'>استهلاك الكهرباء لعام 2024-2025</p></div>", unsafe_allow_html=True)
