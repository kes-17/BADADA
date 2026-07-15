import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

# 1. 디자인 및 설정 (요청사항 유지)
st.set_page_config(page_title="바다로 떠나자! 🏖️", layout="wide")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #b3e5fc, #fff9c4); }
    h1 { color: #006064; text-shadow: 1px 1px 2px #fff; }
    .stMetric { background-color: rgba(255, 255, 255, 0.8); padding: 20px; border-radius: 15px; border-left: 5px solid #ffcc80; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_base_data():
    df_loc = pd.read_csv("해수욕장_환경정보_공간.csv", encoding='utf-8')
    df_info = pd.read_csv("해수욕장_정보목록.csv", encoding='utf-8')
    return pd.merge(df_loc, df_info, on='해수욕장명', how='inner')

st.title("🌊 전국 해수욕장 수질 가이드")
st.markdown("### 🏖️ 가고 싶은 해수욕장의 수질을 확인해보세요!")

df = load_base_data()
api_key = st.sidebar.text_input("공공데이터 API 키", type="password")

# 2. 수질 데이터 강제 로드 (API 키 에러 방어)
if api_key:
    # URL 인코딩 및 파라미터 구성
    url = "http://apis.data.go.kr/1192000/ServiceBeachWaterQuality/getBeachWaterQuality"
    params = {
        "serviceKey": api_key,
        "numOfRows": "300",
        "pageNo": "1",
        "resultType": "json"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # 데이터 구조 탐색
            items = data['response']['body']['items']['item']
            df_api = pd.DataFrame(items)
            df = pd.merge(df, df_api, on='해수욕장명', how='left')
            st.sidebar.success("데이터 로드 성공!")
    except Exception as e:
        st.sidebar.error(f"데이터 로드 실패: {e}")

# 3. UI 및 지도 (한국어 지명 표시)
selected_beach = st.selectbox("확인하고 싶은 해수욕장을 선택하세요:", df['해수욕장명'].unique())
beach = df[df['해수욕장명'] == selected_beach].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    # 한국어 지도를 위한 Pydeck 타일 설정
    view_state = pdk.ViewState(latitude=beach['위도'], longitude=beach['경도'], zoom=12)
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/streets-v11", 
        initial_view_state=view_state,
        layers=[pdk.Layer("ScatterplotLayer", df[df['해수욕장명']==selected_beach], get_position='[경도, 위도]', get_radius=300, get_fill_color=[255, 0, 0])]
    ))

with col2:
    st.metric("🌊 해수욕장명", beach['해수욕장명'])
    st.write(f"**지자체**: {beach['지자체']}")
    
    # 데이터 출력 로직: API 데이터의 컬럼명을 직접 확인
    found_water = False
    for col in df.columns:
        if '수질' in col or '적합' in col or 'recom' in col:
            st.markdown(f"### 수질 상태: {beach[col]}")
            found_water = True
            break
    if not found_water:
        st.warning("데이터가 없습니다. API 키를 다시 확인하세요.")
