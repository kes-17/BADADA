import streamlit as st
import requests
import pandas as pd
import datetime

# 1. 페이지 설정
st.set_page_config(page_title="해수욕장 수질 현황", layout="wide")
st.title("🌊 해수욕장 수질 적합성 조회 대시보드")

# 2. 사이드바 설정
api_key = st.sidebar.text_input("API 인증키 입력", type="password")
sido = st.sidebar.selectbox("시도 선택", ["강원도", "충남", "부산광역시", "제주특별자치도"])

# 3. 데이터 조회 함수
def get_data(api_key, sido):
    current_year = datetime.datetime.now().year
    url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
    
    for year in range(current_year, current_year - 5, -1):
        params = {'ServiceKey': api_key, 'pageNo': '1', 'numOfRows': '100', 'resultType': 'json', 'SIDO_NM': sido, 'RES_YEAR': str(year)}
        response = requests.get(url, params=params)
        data = response.json()
        if 'response' in data and data['response']['body']['totalCount'] > 0:
            return pd.DataFrame(data['response']['body']['items']['item']), year
    return pd.DataFrame(), None

# 4. 실행 버튼
if st.sidebar.button("데이터 조회"):
    if api_key:
        df, year = get_data(api_key, sido)
        if not df.empty:
            st.success(f"{year}년 {sido} 데이터 조회 성공!")
            st.dataframe(df) # 표로 보여주기
        else:
            st.error("데이터를 찾을 수 없습니다.")
    else:
        st.warning("API 인증키를 입력해주세요.")
