import streamlit as st
import pandas as pd
import requests

# 1. 페이지 설정 및 데이터 로드
st.set_page_config(page_title="해수욕장 정보 조회", layout="wide")

@st.cache_data
def load_data():
    df_loc = pd.read_csv("해수욕장_환경정보_공간.csv", encoding='utf-8')
    df_info = pd.read_csv("해수욕장_정보목록.csv", encoding='utf-8')
    return pd.merge(df_loc, df_info, on='해수욕장명', how='inner')

df = load_data()

st.title("🏖️ 전국 해수욕장 정보 시스템")

# 2. 사이드바 API 설정
st.sidebar.header("API 설정")
api_key = st.sidebar.text_input("공공데이터 API 인증키 입력", type="password")

# 3. 해수욕장 선택
selected_beach = st.selectbox("확인하고 싶은 해수욕장을 선택하세요:", df['해수욕장명'].unique())
beach_data = df[df['해수욕장명'] == selected_beach].iloc[0]

# 4. 화면 구성
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📍 {selected_beach} 위치")
    st.map(df[df['해수욕장명'] == selected_beach], latitude='위도', longitude='경도')

with col2:
    st.subheader("📋 해수욕장 상세 정보")
    st.write(f"**지자체**: {beach_data['지자체']}")
    st.write(f"**관리청**: {beach_data['관리청']}")
    st.write(f"**길이**: {beach_data['길이(m)']} m")
    st.write(f"**너비**: {beach_data['너비(m)']} m")
    st.write(f"**백사장 면적**: {beach_data['백사장면적(m2)']} m²")

# 5. API 연동 (간단한 예시 구조)
if api_key:
    st.divider()
    st.subheader("🌊 수질 적합 여부 조회")
    # API 요청 예시 (실제 연동 시 필요한 파라미터는 포털 가이드를 참고하세요)
    url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
    params = {
        "ServiceKey": api_key,
        "resultType": "json",
        "numOfRows": 1,
        "pageNo": 1
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            st.success("API 호출 성공! (상세 데이터 구조에 따라 추가 구현이 필요합니다.)")
            st.json(response.json())
        else:
            st.error("API 호출 실패")
    except Exception as e:
        st.error(f"오류 발생: {e}")
