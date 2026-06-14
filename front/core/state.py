# core/state.py (세션 상태 초기화 및 페이지 상태체크)
import streamlit as st


# [공통] 세션 상태 기본값 초기화
def init():
    ss = st.session_state
    ss.setdefault("name_entered", False)
    ss.setdefault("user_name", "")
    ss.setdefault("step", 1)          # STEP 단계 1~3
    ss.setdefault("inputs", {})       # 누적 입력값
    ss.setdefault("result", None)     # 추천 결과
    ss.setdefault("show_name_warning", False)


# [공통] 이름 입력 여부 체크 (이름만)
def check_name():
    print("[LOG]: 이름 입력 여부 체크 중...")
    if not st.session_state.get("name_entered", False):
        st.session_state.show_name_warning = True
        st.switch_page("pages/1_landing.py")
        st.stop()


# [공통] 추천 결과 없이 결과 페이지 접근 -> 랜딩으로 이동
def check_result():
    if not st.session_state.get("result"):
        st.switch_page("pages/1_landing.py")
        st.stop()


# [공통] 다시하기: 입력/결과만 초기화하고 이름유지
def reset_flow():
    st.session_state.step = 1
    st.session_state.inputs = {}
    st.session_state.result = None
