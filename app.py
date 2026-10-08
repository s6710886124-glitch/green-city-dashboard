import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Green City Dashboard",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Green City Dashboard: เมืองสิ่งแวดล้อมยั่งยืน")
st.caption("ระบบสรุปและวิเคราะห์ข้อมูลการรับรองเมืองสิ่งแวดล้อมยั่งยืน (data.go.th)")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("green-city1.csv", encoding="utf-8-sig")
    except Exception:
        df = pd.read_csv("green-city1.csv", encoding="cp874")
    
    df["size"] = df["size"].replace({"ตำบบล": "ตำบล"})
    return df

df = load_data()

st.sidebar.header("🔍 ตัวกรองข้อมูล (Filter)")

fiscal_years = ["ทั้งหมด"] + sorted(list(df["fiscal year"].unique()))
selected_year = st.sidebar.selectbox("เลือกปีงบประมาณ:", fiscal_years)

regions = ["ทั้งหมด"] + list(df["region"].unique())
selected_region = st.sidebar.selectbox("เลือกภูมิภาค (Region):", regions)

cert_types = ["ทั้งหมด"] + list(df["Type of Certificate"].unique())
selected_cert_type = st.sidebar.selectbox("ระดับใบรับรอง:", cert_types)

types = st.sidebar.multiselect("ประเภทองค์กรปกครองส่วนท้องถิ่น:", options=df["Type"].unique(), default=df["Type"].unique())

filtered_df = df.copy()

if selected_year != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df["fiscal year"] == selected_year]

if selected_region != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df["region"] == selected_region]

if selected_cert_type != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df["Type of Certificate"] == selected_cert_type]

if types:
    filtered_df = filtered_df[filtered_df["Type"].isin(types)]

st.subheader("📊 สรุปข้อมูลภาพรวม")

col1, col2, col3, col4 = st.columns(4)
col1.metric("จำนวนเทศบาลที่ได้รับรางวัล", f"{len(filtered_df):,} แห่ง")
col2.metric("จำนวนจังหวัดที่ครอบคลุม", f"{filtered_df['province'].nunique():,} จังหวัด")
col3.metric("รางวัลระดับประเทศ", f"{len(filtered_df[filtered_df['Type of Certificate'] == 'ระดับประเทศ']):,} รายการ")
col4.metric("รางวัลระดับพื้นที่", f"{len(filtered_df[filtered_df['Type of Certificate'] == 'ระดับพื้นที่']):,} รายการ")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 กราฟที่ 1: จำนวนเมืองยั่งยืนจำแนกตามภาค")
    region_summary = filtered_df.groupby(["region", "Type of Certificate"]).size().reset_index(name="count")
    fig_bar = px.bar(
        region_summary,
        x="region",
        y="count",
        color="Type of Certificate",
        barmode="group",
        text_auto=True,
        labels={"region": "ภูมิภาค", "count": "จำนวน (แห่ง)", "Type of Certificate": "ระดับรางวัล"},
        title="เปรียบเทียบจำนวนตามภูมิภาคและระดับรางวัล"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("🥧 กราฟที่ 2: สัดส่วนขนาดเทศบาลที่ได้รับรางวัล")
    size_summary = filtered_df["size"].value_counts().reset_index()
    size_summary.columns = ["size", "count"]
    fig_pie = px.pie(
        size_summary,
        names="size",
        values="count",
        hole=0.4,
        title="สัดส่วนแยกตามขนาดเทศบาล"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("🏆 10 อันดับจังหวัดที่มีเมืองยั่งยืนมากที่สุด")
top_provinces = filtered_df["province"].value_counts().head(10).reset_index()
top_provinces.columns = ["province", "count"]
fig_top10 = px.bar(
    top_provinces.sort_values(by="count", ascending=True),
    x="count",
    y="province",
    orientation="h",
    text_auto=True,
    labels={"province": "จังหวัด", "count": "จำนวน (แห่ง)"},
    title="10 อันดับจังหวัดแรก"
)
st.plotly_chart(fig_top10, use_container_width=True)

st.markdown("---")

st.subheader("📋 รายละเอียดข้อมูลเมืองสิ่งแวดล้อมยั่งยืน")
st.dataframe(filtered_df, use_container_width=True)

csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 ดาวน์โหลดข้อมูลที่กรองแล้ว (CSV)",
    data=csv_data,
    file_name="filtered_green_city_data.csv",
    mime="text/csv"
)
