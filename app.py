import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# 페이지 설정 (바다 테마)
st.set_page_config(page_title="🌊 해양 환경 대시보드", layout="wide")

# CSS로 디자인 강화
st.markdown("""
    <style>
    .stApp { background-color: #f0f8ff; }
    h1 { color: #006994; }
    </style>
""", unsafe_allow_html=True)

# 데이터 로드
@st.cache_data
def load_data():
    df_loc = pd.read_csv("해수욕장_환경정보_공간.csv")
    df_info = pd.read_csv("해수욕장_정보목록.csv")
    return pd.merge(df_loc, df_info, on='해수욕장명', how='inner')

df_base = load_data()

st.title("🌊 전국 해수욕장 수질 적합성 대시보드 🏖️")
st.sidebar.header("⚙️ 설정 및 인증")
api_key = st.sidebar.text_input("공공데이터 API 인증키 입력", type="password")
selected_year = st.sidebar.selectbox("조사연도 선택", ["2025", "2024"])

if api_key:
    url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
    params = {"ServiceKey": api_key, "resultType": "json", "numOfRows": 500, "RES_YEAR": selected_year}
    
    try:
        response = requests.get(url, params=params).json()
        items = response['getOceansBeachSeawaterInfo']['item']
        df_api = pd.DataFrame(items)
        df_final = pd.merge(df_base, df_api, left_on='해수욕장명', right_on='beachNm')

        # 레이아웃 구성
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📍 해수욕장 수질 현황 지도")
            fig_map = px.scatter_mapbox(df_final, lat="위도", lon="경도", color="adptYn", 
                                        hover_name="해수욕장명", zoom=5, height=500)
            fig_map.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig_map, use_container_width=True)

        with col2:
            st.subheader("📊 수질 통계")
            pie = px.pie(df_final, names='adptYn', title="수질 적합 비율", hole=0.4, color_discrete_sequence=px.colors.sequential.Bluyl)
            st.plotly_chart(pie, use_container_width=True)

        bar = px.bar(df_final.groupby('지자체')['adptYn'].value_counts().unstack().fillna(0), 
                     title="지역별 수질 적합 현황", barmode='group')
        st.plotly_chart(bar, use_container_width=True)

    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
else:
    st.info("👈 사이드바에서 API 인증키를 입력하면 대시보드가 활성화됩니다.")
