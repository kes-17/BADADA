import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# 페이지 설정 (바다 테마)
st.set_page_config(page_title="🌊 전국 해수욕장 수질 현황", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #eef9ff; }
    h1 { color: #0077be; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌊 전국 해수욕장 수질 적합성 대시보드 🐬")

# 사이드바 설정
st.sidebar.header("🐬 데이터 조회 설정")
api_key = st.sidebar.text_input("API 인증키 입력", type="password")
sido_nm = st.sidebar.selectbox("시도 선택", ["강원도", "충남", "부산광역시", "제주특별자치도", "경상북도"])
res_year = st.sidebar.text_input("조사년도", "2025")

# 데이터 불러오기 함수
def get_data(key, sido, year):
    url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
    params = {
        'ServiceKey': key,
        'pageNo': '1',
        'numOfRows': '100',
        'resultType': 'json',
        'SIDO_NM': sido,
        'RES_YEAR': year
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        items = data['response']['body']['items']['item']
        return pd.DataFrame(items)
    return pd.DataFrame()

# 메인 로직
if api_key:
    if st.sidebar.button("📊 데이터 분석 시작"):
        with st.spinner('데이터를 불러오는 중...'):
            df = get_data(api_key, sido_nm, res_year)
            
            if not df.empty:
                # 지도 시각화용 데이터 전처리 (API 응답 필드명에 맞게 조정 필요)
                # 예시: 'lat', 'lon' 필드가 있다면 그대로 사용
                st.subheader(f"📍 {sido_nm} 해수욕장 지도 시각화")
                st.map(df)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("수질 적합성 분포 🐟")
                    fig = px.pie(df, names='적합여부', hole=0.3)
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.subheader("지역별 상세 데이터 🏖️")
                    st.dataframe(df)
            else:
                st.error("데이터가 없습니다. 인증키나 파라미터를 확인하세요.")
else:
    st.info("사이드바에 API 인증키를 입력하고 조회 버튼을 누르세요.")
