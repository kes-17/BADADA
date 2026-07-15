import streamlit as st
import pandas as pd
import requests

# 디자인 설정 유지
st.set_page_config(page_title="바다로 떠나자! 🏖️", layout="wide")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #b3e5fc, #fff9c4); }
    h1 { color: #006064; text-shadow: 1px 1px 2px #fff; }
    .stMetric { background-color: rgba(255, 255, 255, 0.8); padding: 20px; border-radius: 15px; border-left: 5px solid #ffcc80; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df_loc = pd.read_csv("해수욕장_환경정보_공간.csv", encoding='utf-8')
    df_info = pd.read_csv("해수욕장_정보목록.csv", encoding='utf-8')
    return pd.merge(df_loc, df_info, on='해수욕장명', how='inner')

st.title("🌊 전국 해수욕장 수질 가이드")
st.markdown("### 🏖️ 가고 싶은 해수욕장의 수질을 확인해보세요!")

df = load_data()
api_key = st.sidebar.text_input("공공데이터 API 키", type="password")

# 수질 데이터가 저장될 공간
if 'beach_water' not in st.session_state:
    st.session_state.beach_water = None

# API 호출 (에러 방어 강화)
if api_key and st.session_state.beach_water is None:
    url = f"http://apis.data.go.kr/1192000/ServiceBeachWaterQuality/getBeachWaterQuality?serviceKey={api_key}&numOfRows=300&pageNo=1&resultType=json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            if 'response' in res_data and 'body' in res_data['response']:
                items = res_data['response']['body']['items']['item']
                st.session_state.beach_water = pd.DataFrame(items)
                st.sidebar.success("데이터 로드 성공!")
    except:
        st.sidebar.warning("데이터를 불러올 수 없습니다.")

# 데이터 병합
if st.session_state.beach_water is not None:
    df = pd.merge(df, st.session_state.beach_water, on='해수욕장명', how='left')

# UI 구현
selected_beach = st.selectbox("확인하고 싶은 해수욕장을 선택하세요:", df['해수욕장명'].unique())
beach = df[df['해수욕장명'] == selected_beach].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    # 지도 구현: 가장 안정적인 st.map 사용
    st.map(df[df['해수욕장명'] == selected_beach], latitude='위도', longitude='경도', zoom=10)

with col2:
    st.metric("🌊 해수욕장명", beach['해수욕장명'])
    st.write(f"**지자체**: {beach['지자체']}")
    
    # 수질 데이터 출력
    cols = [c for c in df.columns if '적합' in c or '수질' in c]
    if cols and pd.notnull(beach[cols[0]]):
        st.markdown(f"### 수질 상태: {beach[cols[0]]}")
    else:
        st.info("API 키를 확인하거나, 수질 정보가 없습니다.")
