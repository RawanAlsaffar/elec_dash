import streamlit as st
import pandas as pd
import plotly.express as px

# 1. إعدادات الصفحة والهوية البصرية
st.set_page_config(page_title="  داشبورد لاستهلاك الطاقة ", layout="wide")

# تصميم الهوية الاحترافية
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    .stMetric { 
        border-left: 5px solid #D32F2F; 
        padding: 15px; border-radius: 5px; 
        background-color: #FAFAFA; box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    [data-testid="stMetricLabel"] { color: #555555 !important; font-weight: bold !important; font-size: 14px !important; }
    [data-testid="stMetricValue"] { color: #D32F2F !important; font-size: 24px !important; }
    h1, h2, h3 { color: #D32F2F !important; text-align: right; }
    .stMarkdown { direction: rtl; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # العودة لقراءة ملف الإكسل الأصلي
        df = pd.read_excel('final_electricity_data.xlsx')
        
        # تنظيف عمود الحالة من أي مسافات زائدة
        df['Status'] = df['Status'].astype(str).str.strip()
        
        # تحويل الأعمدة لنصوص نظيفة
        for col in ['Year', 'Contract Account', 'Collective CA']:
            df[col] = df[col].astype(str).str.replace('.0', '', regex=False)
            
        return df
    except Exception as e:
        st.error(f"خطأ في تحميل ملف الإكسل: {e}")
        return None

df = load_data()

if df is None:
    st.error("لم يتم العثور على ملف البيانات. يرجى التأكد من وجوده في المسار الصحيح.")
    st.stop()

# --- 2. القائمة الجانبية (Sidebar) ---
try:
    st.sidebar.image("SRCAlogo_local_cmyk.jpg", use_container_width=True)
except:
    st.sidebar.warning("لم يتم العثور على شعار الهيئة في المستودع.")

st.sidebar.title("   لوحة تحكم ")
صفحة = st.sidebar.radio("انتقل إلى:", ["📊 الملخص التنفيذي المقارن", "📈 تحليل الاستهلاك والنمو", "🔍 التدقيق المالي"])

# الفلاتر
st.sidebar.markdown("---")

# 1. فلتر السنوات
الكل_سنوات = st.sidebar.checkbox("اختيار كل السنوات", value=True)
سنوات_مختارة = sorted(df['Year'].unique()) if الكل_سنوات else st.sidebar.multiselect("السنة:", sorted(df['Year'].unique()))

# 2. فلتر الشهور (الإضافة المطلوبة)
st.sidebar.markdown("---")
الكل_شهور = st.sidebar.checkbox("اختيار كل الشهور", value=True)
قائمة_الشهور = ["January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"]

if الكل_شهور:
    شهور_مختارة = قائمة_الشهور
else:
    # نختار فقط الشهور الموجودة فعلياً في بياناتك
    الشهور_الموجودة = [m for m in قائمة_الشهور if m in df['Month'].unique()]
    شهور_مختارة = st.sidebar.multiselect("الشهر:", الشهور_الموجودة, default=الشهور_الموجودة)

# 3. فلتر الحسابات التجميعية
st.sidebar.markdown("---")
الكل_تجميعي = st.sidebar.checkbox("اختيار كل الحسابات", value=True)
حسابات_مختارة = sorted(df['Collective CA'].unique()) if الكل_تجميعي else st.sidebar.multiselect("الحساب التجميعي:", sorted(df['Collective CA'].unique()))

# تطبيق الفلترة النهائية (تشمل السنة، الشهر، والحساب)
df_filtered = df[
    (df['Year'].isin(سنوات_مختارة)) & 
    (df['Month'].isin(شهور_مختارة)) & 
    (df['Collective CA'].isin(حسابات_مختارة))
]

if df_filtered.empty:
    st.warning("⚠️ لا توجد بيانات مطابقة للفلاتر المختارة.")
    st.stop()

# --- 3. عرض الصفحات ---

# --- الصفحة الأولى: الملخص التنفيذي ---
if صفحة == "📊 الملخص التنفيذي المقارن":
    st.header("النتائج العامة للأداء المالي (2024-2025)")
    
    إجمالي_المبالغ_المفلترة = df_filtered['Net Sales Amount'].sum()
    
    for سنة in sorted(سنوات_مختارة):
        st.subheader(f"📅 إحصائيات ميزانية {سنة}")
        y_df = df_filtered[df_filtered['Year'] == سنة]
        سنة_تكلفة = y_df['Net Sales Amount'].sum()
        نسبة_السنة = (سنة_تكلفة / إجمالي_المبالغ_المفلترة * 100) if إجمالي_المبالغ_المفلترة > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric(f"إجمالي تكلفة {سنة}", f"{سنة_تكلفة:,.0f} ريال")
        c2.metric(f"نسبة الاستهلاك لعام {سنة}", f"{نسبة_السنة:.1f}%")
        c3.metric("متوسط الفواتير", f"{y_df['Net Sales Amount'].mean():,.0f} ريال")
        
        c4, c5, c6 = st.columns(3)
        c4.metric("الوسيط الحسابي", f"{y_df['Net Sales Amount'].median():,.0f} ريال")
        c5.metric("الانحراف المعياري", f"{y_df['Net Sales Amount'].std():,.0f}")
        c6.metric("عدد العدادات ", y_df['Contract Account'].nunique())
        st.markdown("---")

    st.subheader("📈 التوجه العام للاستهلاك (المقارنة المساحية)")
    قائمة_الشهور = ["January", "February", "March", "April", "May", "June", 
                    "July", "August", "September", "October", "November", "December"]
    dash_monthly = df_filtered.groupby(['Year', 'Month'])['Net Sales Amount'].sum().reset_index()
    dash_monthly['Month'] = pd.Categorical(dash_monthly['Month'], categories=قائمة_الشهور, ordered=True)
    
    fig_area_dash = px.area(dash_monthly.sort_values(['Year', 'Month']), x="Month", y="Net Sales Amount", color="Year",
                            color_discrete_sequence=['#D32F2F', '#FFCDD2'], markers=True)
    fig_area_dash.update_layout(plot_bgcolor='white', hovermode="x unified")
    st.plotly_chart(fig_area_dash, use_container_width=True)
    
    st.markdown("---")
    col_a, col_b = st.columns([1.5, 1])
    with col_a:
        st.subheader("🔴 توزيع الحجم المالي لأكبر 15 حساباً")
        top_builds = df_filtered.groupby('Contract Account')['Net Sales Amount'].sum().nlargest(15).reset_index()
        fig_bubbles = px.scatter(top_builds, x='Contract Account', y='Net Sales Amount',
                                 size='Net Sales Amount', color='Net Sales Amount',
                                 hover_name='Contract Account', size_max=60,
                                 color_continuous_scale='Reds')
        fig_bubbles.update_layout(plot_bgcolor='white', xaxis_title="رقم الحساب", yaxis_title="التكلفة (ريال)")
        st.plotly_chart(fig_bubbles, use_container_width=True)
    with col_b:
        st.subheader("📉 توزيع حالة العدادات")
        status_counts = df_filtered['Account_Type'].value_counts().reset_index()
        status_counts.columns = ['الحالة', 'العدد']
        fig_pie = px.pie(status_counts, values='العدد', names='الحالة', 
                         hole=0.5, color_discrete_sequence=['#D32F2F', '#FFCDD2'])
        st.plotly_chart(fig_pie, use_container_width=True)

# --- الصفحة الثانية: تحليل الاستهلاك والنمو ---
elif صفحة == "📈 تحليل الاستهلاك والنمو":
    st.header("تحليل مراكز التكلفة والتوزيع الهيكلي")

    # تحليل أعلى 5 حسابات تجميعية
    st.subheader("🏢 أعلى 5 حسابات تجميعية (مناطق التركز المالي)")
    top_collective = df_filtered.groupby('Collective CA')['Net Sales Amount'].sum().nlargest(5).reset_index()
    fig_top_coll = px.bar(top_collective, x='Collective CA', y='Net Sales Amount',
                          text_auto='.2s', color='Net Sales Amount',
                          color_continuous_scale='Reds',
                          title="أعلى 5 مجموعات حسابات من حيث الإنفاق")
    fig_top_coll.update_layout(xaxis_title="الحساب التجميعي", yaxis_title="إجمالي المبلغ (ريال)", plot_bgcolor='white')
    st.plotly_chart(fig_top_coll, use_container_width=True)

    st.markdown("---")

    # تصحيح الخطأ هنا: TreeMap في عمود كامل بدون استخدام list في الـ context manager
    st.subheader("🗺️ التوزيع الهيكلي للميزانية (حساب تجميعي > عدادات فرعية)")
    fig_tree = px.treemap(df_filtered, path=['Collective CA', 'Contract Account'], values='Net Sales Amount',
                          color='Net Sales Amount', color_continuous_scale='Reds')
    st.plotly_chart(fig_tree, use_container_width=True)

# --- الصفحة الثالثة: التدقيق المالي ---
elif صفحة == "🔍 التدقيق المالي":
    st.header("نتائج الرقابة المالية وكشف الهدر")
    audit_df = df_filtered[df_filtered['Status'] != 'حساب موثق']
    c1, c2 = st.columns(2)
    c1.metric("المبالغ المرصودة للمعالجة", f"{audit_df['Net Sales Amount'].sum():,.0f} ريال")
    c2.error(f"يوجد {len(audit_df)} ملاحظة تتطلب معالجة فورية")
    st.subheader("📋 سجل التدقيق التفصيلي للحسابات")
    st.dataframe(audit_df[['Contract Account', 'Collective CA', 'Status', 'Net Sales Amount']], use_container_width=True)
