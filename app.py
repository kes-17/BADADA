import streamlit as st
import requests
import pandas as pd

st.title("API 연동 테스트")

# 1. 사용자로부터 API 키 입력받기
api_key = st.text_input("공공데이터 API 인증키를 입력하세요:", type="password")

if st.button("데이터 불러오기"):
    if not api_key:
        st.warning("인증키를 먼저 입력해 주세요.")
    else:
        # 2. API 요청 정보 설정
        url = "https://apis.data.go.kr/1192000/service/OceansBeachSeawaterService1/getOceansBeachSeawaterInfo1"
        params = {
            "ServiceKey": api_key,
            "resultType": "json",
            "numOfRows": 10,  # 일단 10개만 테스트
            "RES_YEAR": "2025"
        }
        
        try:
            # 3. API 요청
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # 4. 데이터 확인
                if 'getOceansBeachSeawaterInfo' in data:
                    items = data['getOceansBeachSeawaterInfo']['item']
                    df = pd.DataFrame(items)
                    st.success("데이터 호출 성공!")
                    st.write(df[['beachNm', 'adptYn']]) # 해수욕장명과 적합 여부만 출력
                else:
                    st.error("데이터가 없습니다. 응답 내용을 확인하세요.")
                    st.json(data)
            else:
                st.error(f"API 호출 실패. 상태 코드: {response.status_code}")
                
        except Exception as e:
            st.error(f"오류 발생: {e}")
