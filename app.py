import streamlit as st
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="해수욕장 정보 조회", layout="wide")

@st.cache_data
def load_data():
    df_loc = pd.read_csv("해수욕장_환경정보_공간.csv", encoding='utf-8')
    df_info = pd.read_csv("해수욕장_정보목록.csv", encoding='utf-8')
    return pd.merge(df_loc, df_info, on='해수욕장명', how='inner')

df = load_data()

st.title("🌊 전국 해수욕장 수질 가이드")
api_key = st.sidebar.text_input("공공데이터 API 인증키 입력", type="password")

# 2. 필수 파라미터를 추가한 API 호출
if api_key:
    url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
    # 필수 파라미터인 RES_YEAR를 반드시 포함해야 데이터가 나옵니다.
    params = {
        "ServiceKey": api_key,
        "resultType": "json",
        "numOfRows": 300,
        "pageNo": 1,
        "RES_YEAR": "2026" 
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # 'item'이 비어있지 않은지 확인
        if 'getOceansBeachSeawaterInfo' in data and data['getOceansBeachSeawaterInfo']['totalCount'] > 0:
            items = data['getOceansBeachSeawaterInfo']['item']
            df_api = pd.DataFrame(items)
            st.success(f"데이터 로드 성공! 총 {len(df_api)}개의 데이터를 불러왔습니다.")
            st.write(df_api.head()) # 데이터 확인
        else:
            st.warning("데이터가 없습니다. RES_YEAR 파라미터를 2025로 변경해 보거나 API 설정을 확인하세요.")
    except Exception as e:
        st.error(f"오류 발생: {e}")
