import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

# 기존 디자인 설정 유지
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

if api_key:
    url = f"http://apis.data.go.kr/1192000/ServiceBeachWaterQuality/getBeachWaterQuality?serviceKey={api_key}&numOfRows=300&pageNo=1&resultType=json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'body' in data['response']:
                df_api = pd.DataFrame(data['response']['body']['items']['item'])
                # 어떤 컬럼에 수질 정보가 있는지 자동 확인하여 병합
                df = pd.merge(df, df_api, on='해수욕장명', how='left')
    except:
        pass

selected_beach = st.selectbox("확인하고 싶은 해수욕장을 선택하세요:", df['해수욕장명'].unique())
beach_data = df[df['해수욕장명'] == selected_beach].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    # 지도 스타일을 'light'로 변경하여 밝게 수정
    view_state = pdk.ViewState(latitude=beach_data['위도'], longitude=beach_data['경도'], zoom=12)
    layer = pdk.Layer("ScatterplotLayer", df, get_position='[경도, 위도]', get_radius=200, get_fill_color=[0, 150, 255])
    st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v10", initial_view_state=view_state, layers=[layer]))

with col2:
    st.metric(label="🌊 해수욕장명", value=beach_data['해수욕장명'])
    st.write(f"**지자체**: {beach_data['지자체']}")
    st.write(f"**관리청**: {beach_data['관리청']}")
    
    # 수질 데이터가 있으면 출력 (컬럼명 자동 탐색)
    quality_cols = [c for c in beach_data.index if '수질' in c or 'recom' in c or 'std' in c]
    if quality_cols:
        st.markdown(f"### 수질 상태: {beach_data[quality_cols[0]]}")
    else:
        st.warning("API 정보를 불러와야 수질 상태를 볼 수 있어요!")
