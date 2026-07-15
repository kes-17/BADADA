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

# 헤더 및 API 설정 유지
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
                df = pd.merge(df, df_api, on='해수욕장명', how='left')
    except:
        pass

# 선택 기능 및 지도 유지
selected_beach = st.selectbox("확인하고 싶은 해수욕장을 선택하세요:", df['해수욕장명'].unique())
beach_data = df[df['해수욕장명'] == selected_beach].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    # 한글 지도 및 위치 줌인/강조 레이어 (요청사항 반영)
    view_state = pdk.ViewState(latitude=beach_data['위도'], longitude=beach_data['경도'], zoom=12)
    layer = pdk.Layer("ScatterplotLayer", df, get_position='[경도, 위도]', get_radius=200, get_fill_color=[0, 150, 255])
    st.pydeck_chart(pdk.Deck(initial_view_state=view_state, layers=[layer]))

with col2:
    st.metric(label="🌊 해수욕장명", value=beach_data['해수욕장명'])
    st.write(f"**지자체**: {beach_data['지자체']}")
    st.write(f"**관리청**: {beach_data['관리청']}")
    if 'stdDay' in beach_data:
        st.markdown(f"### 수질 상태: {beach_data['stdDay']}")
    else:
        st.warning("API 정보를 불러와야 수질 상태를 볼 수 있어요!")

if 'stdDay' in df.columns:
    st.divider()
    st.subheader("📊 전국 수질 현황 그래프")
    fig = px.pie(df.dropna(subset=['stdDay']), names='stdDay', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
