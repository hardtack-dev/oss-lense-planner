# pages/1_landing.py (시작 페이지 / 이름 입력)
import streamlit as st
from core import state  # 세션관리

state.init()

# 이름없이 접근 시
if st.session_state.get("show_name_warning"):
    st.toast("먼저 이름을 입력해 주세요.", icon="🚨")
    st.session_state.show_name_warning = False

# 메인 레이아웃 구성 (1 : 2 : 1) - 가운데 정렬
_, main_content, _ = st.columns([1, 2, 1])

with main_content:
    print("[LOG]: 랜딩 페이지 렌더링 중...")
    st.write("")

    # 타이틀 (마크다운)
    st.markdown("<h1 style='text-align:center'>오늘 뭐 찍지?<br>렌즈 플래너</h1>", unsafe_allow_html=True,)
    st.markdown("<p style='text-align:center;color:gray;font-size:1.05rem'>" "촬영 스타일만 고르면 딱 맞는 렌즈와 화각을 찾아줍니다</p>", unsafe_allow_html=True,)
    st.markdown(
        "<div style='text-align:center;margin:2px 0 10px;color:#9aa'>"
        "<span style='font-size:0.85rem'>광각</span>"
        "<span style='font-size:1.15rem;letter-spacing:1px;margin:0 12px'>"
        "16　24　35　<b style='color:#4CAF50'>50</b>　85　135　200"
        "<small style='color:#9aa'>mm</small></span>"
        "<span style='font-size:0.85rem'>망원</span></div>",
        unsafe_allow_html=True,
    )
    st.write("---")

    # 과목 정보 및 제출정보
    with st.container(border=True):
        st.markdown(":violet-badge[:material/star: 오픈소스소프트웨어 실습] "":orange-badge[기말고사 프로젝트]")
        st.caption("Streamlit · FastAPI · Docker · AWS EC2")
        st.markdown("제출자: **하건우**　|　학번: 2023204006")

    st.write("")

    # 이름 입력 (세션에 저장된 값이 있으면 채우기)
    name = st.text_input(
        "이름", value=st.session_state.get("user_name", ""),
        placeholder="이름을 입력하세요.", max_chars=20,
    )

    # 시작하기 버튼 - 이름 검증 후 입력 페이지로 이동
    if st.button("시작하기", type="primary", width="stretch"):
        if name.strip():
            st.session_state.user_name = name.strip()
            st.session_state.name_entered = True
            state.reset_flow()
            print("[LOG]: 이름 입력 완료, 입력 페이지로 이동...")
            st.switch_page("pages/2_input.py")
        else:
            st.error("이름을 입력해 주세요.")
