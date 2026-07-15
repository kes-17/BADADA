import streamlit as st
import pandas as pd
import requests

# 1. 페이지 설정
st.set_page_config(page_title="해수욕장 수질 가이드", layout="wide")

# 2. 데이터 로드 및 병합 함수
@st.cache_data
def get_base_data():
    df_loc = pd.read_csv("해수욕장_환경정보_공간.csv", encoding='utf-8')
    df_info = pd.read_csv("해수욕장_정보목록.csv", encoding='utf-8')
    return pd.merge(df_loc, df_info, on='해수욕장명', how='inner')

st.title("🌊 전국 해수욕장 수질 가이드")
api_key = st.sidebar.text_input("공공데이터 API 인증키 입력", type="password")

# 3. API 및 CSV 데이터 통합
df_base = get_base_data()

if api_key:
    url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
    # 필수 파라미터 포함
    params = {"ServiceKey": api_key, "resultType": "json", "numOfRows": 300, "pageNo": 1, "RES_YEAR": "2026"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'getOceansBeachSeawaterInfo' in data and data['getOceansBeachSeawaterInfo']['totalCount'] > 0:
                df_api = pd.DataFrame(data['getOceansBeachSeawaterInfo']['item'])
                
                # API 데이터 컬럼명 정제 (beachNm을 해수욕장명으로 변경)
                if 'beachNm' in df_api.columns:
                    df_api = df_api.rename(columns={'beachNm': '해수욕장명'})
                
                # 병합 수행
                df = pd.merge(df_base, df_api, on='해수욕장명', how='left')
                st.sidebar.success("데이터 병합 완료!")
                
                # 4. 결과 시각화
                selected_beach = st.selectbox("해수욕장 선택:", df['해수욕장명'].unique())
                beach_info = df[df['해수욕장명'] == selected_beach].iloc[0]
                
                col1, col2 = st.columns(2)
                col1.metric("해수욕장명", beach_info['해수욕장명'])
                
                # 수질 데이터가 있는 컬럼 동적 탐색
                water_col = next((c for c in df.columns if '적합' in c or '수질' in c), None)
                if water_col and pd.notnull(beach_info[water_col]):
                    col2.metric("수질 상태", beach_info[water_col])
                else:
                    col2.warning("수질 데이터 미등록")
            else:
                st.warning("API에 데이터가 없습니다. RES_YEAR를 2025로 변경해 보세요.")
    except Exception as e:
        st.error(f"연결 오류: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 입력하면 수질 정보를 불러옵니다.")
