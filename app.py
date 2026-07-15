import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="공공데이터 API 조회", layout="wide")
st.title("🌊 해양수산부 해수욕장 수질 정보")

# 사이드바 설정
st.sidebar.header("조회 설정")
api_key = st.sidebar.text_input("API 인증키 입력", type="password")
sido = st.sidebar.selectbox("시도명", ["강원도", "충남", "부산광역시", "제주특별자치도"])
year = st.sidebar.text_input("조사년도", "2024")

if st.sidebar.button("API 데이터 확인"):
    if not api_key:
        st.warning("인증키를 입력하세요.")
    else:
        # API 엔드포인트
        url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
        params = {
            'ServiceKey': api_key,
            'pageNo': '1',
            'numOfRows': '50',
            'resultType': 'json',
            'SIDO_NM': sido,
            'RES_YEAR': year
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # API 응답 구조 확인 (보통 'response' -> 'body' -> 'items' -> 'item' 순)
            if 'response' in data and 'items' in data['response']['body']:
                items = data['response']['body']['items']
                if items:
                    df = pd.DataFrame(items['item'])
                    st.success(f"{sido} ({year}년) 데이터 {len(df)}건을 불러왔습니다.")
                    st.dataframe(df) # API가 제공하는 원본 데이터 표 출력
                else:
                    st.info("데이터가 없습니다. 다른 연도를 선택해보세요.")
            else:
                st.error("데이터를 가져오는 중 오류가 발생했습니다. 키나 파라미터를 확인하세요.")
        except Exception as e:
            st.error(f"오류: {e}")
