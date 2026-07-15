import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

st.set_page_config(page_title="바다로 떠나자! 🏖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(to bottom, #b3e5fc, #fff9c4); }
    h1 { color: #006064; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df_loc = pd.read_csv("해수욕장_환경정보_공간.csv", encoding='utf-8')
    df_info = pd.read_csv("해수욕장_정보목록.csv", encoding='utf-8')
    return pd.merge(df_loc, df_info, on='해수욕장명', how='inner')

st.title("🌊 전국 해수욕장 수질 가이드")
df = load_data()
api_key = st.sidebar.text_input("공공데이터 API 키", type="password")

# API 연동 (에러 방어 로직 강화)
if api_key:
    url = f"http://apis.data.go.kr/1192000/ServiceBeachWaterQuality/getBeachWaterQuality?serviceKey={api_key}&numOfRows=300&pageNo=1&resultType=json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'body' in data['response']:
                items = data['response']['body']['items']['item']
                df_api = pd.DataFrame(items)
                df = pd.merge(df, df_api, on='해수욕장명', how='left')
                st.sidebar.success("데이터 로드 완료! ✅")
        else:
            st.sidebar.error("API 서버 오류")
    except:
        st.sidebar.error("API 키를 확인해주세요.")

# 해수욕장 선택
selected_name = st.selectbox("확인할 해수욕장을 선택하세요:", df['해수욕장명'].unique())
beach = df[df['해수욕장명'] == selected_name].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    # Pydeck으로 한글 지도 구현 및 클릭 지점 강조
    view_state = pdk.ViewState(latitude=beach['위도'], longitude=beach['경도'], zoom=12)
    layer = pdk.Layer("ScatterplotLayer", df, get_position='[경도, 위도]', get_radius=200, get_fill_color=[0, 150, 255])
    
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[layer]
    ))

with col2:
    st.metric("🏖️ 해수욕장", beach['해수욕장명'])
    st.write(f"**지자체**: {beach['지자체']}")
    if 'stdDay' in beach:
        st.success(f"수질 상태: {beach['stdDay']}")
    else:
        st.info("API 연결 시 수질 확인 가능")
