import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

# 디자인 및 레이아웃 유지
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

# 사이드바 API 키 입력
api_key = st.sidebar.text_input("공공데이터 API 키", type="password")

# 데이터 병합을 위한 전역 변수 초기화
if 'water_data' not in st.session_state:
    st.session_state.water_data = None

if api_key:
    url = f"http://apis.data.go.kr/1192000/ServiceBeachWaterQuality/getBeachWaterQuality?serviceKey={api_key}&numOfRows=300&pageNo=1&resultType=json"
    try:
        res = requests.get(url, timeout=10).json()
        # 구조가 복잡하므로 중첩 탐색
        items = res['response']['body']['items']['item']
        st.session_state.water_data = pd.DataFrame(items)
        st.sidebar.success("데이터 연동 성공!")
    except Exception as e:
        st.sidebar.error(f"연동 실패: {e}")

# 데이터 병합
if st.session_state.water_data is not None:
    df = pd.merge(df, st.session_state.water_data, on='해수욕장명', how='left')

# 선택 및 지도 구현
selected_beach = st.selectbox("확인하고 싶은 해수욕장을 선택하세요:", df['해수욕장명'].unique())
beach = df[df['해수욕장명'] == selected_beach].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    # 지도 구현 (Pydeck, 밝은 스타일)
    view_state = pdk.ViewState(latitude=beach['위도'], longitude=beach['경도'], zoom=12)
    layer = pdk.Layer("ScatterplotLayer", df, get_position='[경도, 위도]', get_radius=200, get_fill_color=[0, 150, 255])
    st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v10", initial_view_state=view_state, layers=[layer]))

with col2:
    st.metric("🌊 해수욕장명", beach['해수욕장명'])
    st.write(f"**지자체**: {beach['지자체']}")
    st.write(f"**관리청**: {beach['관리청']}")
    
    # 수질 데이터가 컬럼에 있는지 확인 후 출력
    found = False
    for col in df.columns:
        if '적합' in col or '수질' in col:
            st.markdown(f"### 수질 상태: {beach[col]}")
            found = True
            break
    if not found:
        st.warning("API 키를 확인하거나, 데이터가 없습니다.")
