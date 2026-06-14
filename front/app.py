# app.py (메인 엔트리 포인트 - 페이지 설정 및 네비게이션)
import streamlit as st

# 페이지 환경설정
st.set_page_config(
    page_title="오늘 뭐 찍지? · 렌즈 플래너",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 사이드바 숨김처리
st.markdown(
    "<style>[data-testid='stSidebar']{display:none!important;}</style>",
    unsafe_allow_html=True,
)

# 세션 상태 초기화
from core import state
state.init()

# 페이지 네비게이션 정의
pages = st.navigation([
    st.Page("pages/1_landing.py", title="시작", icon="🏠"),
    st.Page("pages/2_input.py",   title="입력", icon="🎛️"),
    st.Page("pages/3_result.py",  title="결과", icon="🏆"),
])

# 앱 실행
pages.run()
