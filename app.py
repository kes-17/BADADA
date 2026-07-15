import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정 (바다 테마)
st.set_page_config(page_title="🌊 전국 해수욕장 수질 현황", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f8ff; }
    h1 { color: #0077be; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌊 전국 해수욕장 수질 적합성 대시보드 🏖️")
st.sidebar.header("🐬 설정 및 데이터 조회")

# 2. API 인증키 입력
api_key = st.sidebar.text_input("공공데이터 API 인증키를 입력하세요", type="password")

# 3. 데이터 로드 로직 (가상 데이터)
def get_mock_data():
    data = {
        "해수욕장명": ["해운대", "경포대", "대천", "함덕", "만리포"],
        "적합여부": ["적합", "적합", "부적합", "적합", "적합"],
        "위도": [35.1587, 37.7946, 36.3197, 33.5428, 36.7865],
        "경도": [129.1604, 128.9038, 126.5057, 126.6698, 126.1557]
    }
    return pd.DataFrame(data)

if api_key:
    df = get_mock_data()
    
    tab1, tab2 = st.tabs(["📊 통계 대시보드", "📍 지도 시각화"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(df, names="적합여부", title="수질 적합성 비율", color_discrete_sequence=["#1f77b4", "#ff7f0e"])
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            fig_bar = px.bar(df, x="해수욕장명", y="적합여부", color="적합여부", title="해수욕장별 적합 현황")
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.subheader("지도에서 보는 수질 상태 🐬")
        # [수정된 부분] st.map이 인식할 수 있도록 컬럼명 변경
        map_data = df.rename(columns={'위도': 'lat', '경도': 'lon'})
        st.map(map_data)
else:
    st.info("사이드바에 API 인증키를 입력하면 데이터가 로드됩니다.")
