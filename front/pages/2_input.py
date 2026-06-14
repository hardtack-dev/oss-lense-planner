# pages/2_input.py (조건입력 페이지 - 3단계 입력)
# 레이아웃: left(내 선택 보이기) + right(조건 입력).
# 우측 입력을 먼저 실행해 user_input을 받기 -> 좌측에 렌더링
import streamlit as st
from core import state, api, fov, assets  # 세션가드 / 백엔드통신 / 화각계산 / 이미지에셋

state.init()
state.check_name()


# 카탈로그(카메라/주제/예산범위)는 다시 받지 않도록 캐싱해줌
@st.cache_data(show_spinner=False)
def load_catalog():
    return api.get_catalog()


catalog = load_catalog()
cameras = catalog["cameras"]
subjects = catalog["subjects"]
lens_types = catalog["lens_types"]
budget_range = catalog["budget_range"]

# 현재 단계와 사용자 입력값(세션에 누적 저장)
step = st.session_state.step
user_input = st.session_state.inputs

STEP_TITLES = {1: "📷 내 장비", 2: "🎯 촬영 스타일", 3: "💰 예산 & 마무리"}


def render_summary():
    # 좌측 시각 보조 패널
    # 지금까지 고른 것을 반영 / 현재 입력 중인 단계만 강조해서 렌더링!!

    # 현재 입력 중인 섹션 헤더 (초록 좌측 바)
    def active_header(title):
        st.markdown(
            f"<div style='border-left:4px solid #4CAF50;padding-left:8px;"
            f"font-size:1.1rem;font-weight:700;margin-bottom:4px'>{title} "
            f"<span style='color:#4CAF50;font-size:0.8rem'>입력 중</span></div>",
            unsafe_allow_html=True)

    # 비활성(이미 고른) 섹션의 흐림 구현
    def dim_text(text):
        st.markdown(f"<div style='color:#888;padding:5px 0'>{text}</div>",
                    unsafe_allow_html=True)

    st.markdown("##### 지금 내 선택")

    # 카메라 (항상 카드로 두되, 현재 단계면 강조+펼침)
    with st.container(border=True):
        if step == 1:
            active_header("📷 카메라")
            if user_input.get("cam_title"):
                crop = user_input.get("crop")
                st.markdown(f"**{user_input['cam_title']}**")

                sensor_w = user_input.get("sensor_w_mm")
                sensor_h = user_input.get("sensor_h_mm")
                cam_photo = assets.find_asset("cameras", user_input.get("body_id"))

                # 센서 크기 시각화(left) + 카메라 사진(right, 작게)
                sensor_col, photo_col = st.columns([1, 1], vertical_alignment="center")
                with sensor_col:
                    if sensor_w and sensor_h:
                        st.plotly_chart(
                            fov.sensor_figure(sensor_w, sensor_h, crop, compact=True),
                            width="stretch")
                with photo_col:
                    if cam_photo:
                        st.image(assets.load_image(cam_photo), width="stretch")
                    else:
                        st.caption("사진 없음")

                # 포맷 색상 범례 (차트 윤곽선 색과 동일하게 맞춤)
                if sensor_w and sensor_h:
                    legend = "<div style='line-height:1.8'>" + "&nbsp;&nbsp;&nbsp;".join(
                        f"<span style='color:{color};font-size:15px'>■</span> "
                        f"<span style='font-size:13px'>{name}</span>"
                        for name, _w, _h, color in fov.SENSOR_FORMATS
                    ) + "</div>"
                    st.markdown(legend, unsafe_allow_html=True)

                # 센서 텍스트 (센서 종류/환산 배율만 크게 강조)
                emphasis = "font-size:1.2rem;font-weight:700"
                sensor_text = (
                    f"센서 <span style='{emphasis}'>{user_input.get('sensor', '-')}</span>"
                    f" / 환산 <span style='{emphasis}'>×{crop}</span>")
                if sensor_w and sensor_h:
                    sensor_text += f" / {sensor_w}×{sensor_h}mm"
                if user_input.get("mount"):
                    sensor_text += f" / {user_input['mount']}"
                st.markdown(sensor_text, unsafe_allow_html=True)

                # 크롭 바디면 화각이 좁아진다는 안내
                if sensor_w and sensor_h:
                    if crop and abs(crop - 1.0) > 0.01:
                        st.caption(f"센서가 작은 만큼 화각이 좁아집니다. ( ×{crop:g} 망원처럼 보여요. )")
                    else:
                        st.caption("풀프레임, 표기 그대로의 화각이에요.")
            else:
                st.caption("아직 선택 전")
        else:
            # 비활성: 사진 썸네일 + 흐린 한 줄
            cam_title = user_input.get("cam_title")
            if cam_title:
                cam_photo = assets.find_asset("cameras", user_input.get("body_id"))
                if cam_photo:
                    thumb_col, text_col = st.columns([1, 3], vertical_alignment="center")
                    thumb_col.image(assets.load_image(cam_photo), width="stretch")
                    text_col.markdown(
                        f"<div style='color:#888'>📷 {cam_title}<br>"
                        f"{user_input.get('sensor', '-')} | 환산 ×{user_input.get('crop')}</div>",
                        unsafe_allow_html=True)
                else:
                    dim_text(f"📷 {cam_title} > {user_input.get('sensor', '-')} "
                             f"×{user_input.get('crop')}")
            else:
                dim_text("📷 카메라 (아직 선택 전)")

    # 촬영 주제
    picked_subjects = [s for s in subjects if s["key"] in user_input.get("subjects", [])]
    with st.container(border=True):
        if step == 2:
            active_header("🎯 촬영 주제")
            if picked_subjects:
                # 고른 주제마다 큰 이모지 박스
                for col, subj in zip(st.columns(len(picked_subjects)), picked_subjects):
                    with col:
                        emoji, _, name = subj["label"].partition(" ")
                        st.markdown(
                            f"<div style='display:flex;align-items:center;"
                            f"justify-content:center;height:92px;font-size:46px;"
                            f"background:rgba(76,175,80,0.08);"
                            f"border-radius:12px'>{emoji}</div>",
                            unsafe_allow_html=True)
                        st.caption(name or subj["label"])
            else:
                st.caption("아직 선택 전")
            st.caption(
                f"렌즈 형태 : {user_input.get('lens_type', '상관없음')}　::　"
                f"저조도: {user_input.get('low_light', 3)}/5"
            )
        else:
            # 비활성: 작은 썸네일 + 흐린 요약
            if picked_subjects:
                thumb_col, text_col = st.columns([2, 3], vertical_alignment="center")
                with thumb_col:
                    for col, subj in zip(st.columns(len(picked_subjects)), picked_subjects):
                        with col:
                            emoji, _, _name = subj["label"].partition(" ")
                            st.markdown(
                                f"<div style='display:flex;align-items:center;"
                                f"justify-content:center;height:75px;font-size:26px;"
                                f"background:rgba(76,175,80,0.08);"
                                f"border-radius:8px;margin-bottom:8px'>{emoji}</div>",
                                unsafe_allow_html=True)
                with text_col:
                    st.markdown(
                        "<div style='color:#888;font-weight:700'>"
                        + ", ".join(subj["label"] for subj in picked_subjects)
                        + f"<br>{user_input.get('lens_type', '상관없음')}"
                        + f" | 저조도 {user_input.get('low_light', 3)}/5</div>",
                        unsafe_allow_html=True)
            else:
                dim_text("🎯 촬영 주제 (아직 선택 전)")

    # 예산 & 우선순위
    with st.container(border=True):
        if step == 3:
            active_header("💰 예산 / 우선순위")
            st.markdown(f"**~{user_input.get('budget', budget_range['max']):,}원**")
            st.caption(
                f"우선순위 : {user_input.get('priority', '화질')}　|　"
                f"휴대성 {user_input.get('portability', 3)}/5"
            )
        else:
            dim_text("💰 예산 / 우선순위 (Step 3에서)")


# 좌우 레이아웃: 좌(선택한 거 보기) + 우(입력)
_, left_visual, right_form, _ = st.columns([0.15, 1, 1.3, 0.15], gap="large")

# 우측 입력을 먼저 실행, user_input을 갱신
with right_form:
    with st.container(border=True, height=620):
        st.progress(step / 3)
        st.markdown(f"### Step {step}/3  · {STEP_TITLES[step]}")
        st.write("")
        print(f"[LOG]: 입력 페이지 렌더링 중... (현재 Step: {step})")

        # Step 1 : 내 장비
        if step == 1:
            EXTRA = ["목록에 없어요 / 구매 예정 (직접 선택)"]
            titles = [c["title"] for c in cameras] + EXTRA
            # key=로 선택고정!! 다른 입력으로 rerun돼도 고른 카메라가 풀리지 않게 함
            if "cam_select" not in st.session_state:
                prev = user_input.get("cam_title")
                st.session_state.cam_select = prev if prev in titles else titles[0]
            choice = st.selectbox("내 카메라", titles, key="cam_select")

            if choice not in EXTRA:
                # 목록에서 고른 경우: 카메라 정보 그대로 저장
                selected_cam = next(c for c in cameras if c["title"] == choice)
                user_input.update({
                    "body_id": selected_cam["id"], "cam_title": selected_cam["title"],
                    "mount": selected_cam["mount"], "sensor": selected_cam["sensor"],
                    "crop": selected_cam["crop"],
                    "sensor_w_mm": selected_cam["sensor_w_mm"],
                    "sensor_h_mm": selected_cam["sensor_h_mm"],
                })
                st.success(
                    f"인식됨: {selected_cam['mount']} / {selected_cam['sensor']} "
                    f"/ 환산 ×{selected_cam['crop']}", icon="✅",
                )
            else:
                # 목록에 없으면 브랜드랑 센서만 골라도 추천 가능
                st.info("브랜드랑 센서 종류만 골라도 추천해드려요.", icon="💡")
                brand = st.selectbox(
                    "브랜드", ["Sony", "Canon", "Nikon", "Fujifilm", "Panasonic"])
                sensor = st.radio("센서 종류", ["풀프레임", "APS-C", "마이크로포서드"],
                                  horizontal=True)
                # 센서별 (크롭, 가로mm, 세로mm)
                crop_map = {"풀프레임": (1.0, 35.9, 24.0), "APS-C": (1.5, 23.5, 15.6),
                            "마이크로포서드": (2.0, 17.3, 13.0)}
                crop, sensor_w, sensor_h = crop_map[sensor]
                # 렌즈가 마운트별이라 브랜드로 마운트를 정함
                mount_map = {"Sony": "Sony E", "Canon": "Canon RF", "Nikon": "Nikon Z",
                             "Fujifilm": "Fujifilm X", "Panasonic": "Leica L"}
                mount = mount_map[brand]
                user_input.update({
                    "body_id": None,
                    "cam_title": f"{brand} {sensor}",
                    "mount": mount, "sensor": sensor, "crop": crop,
                    "sensor_w_mm": sensor_w, "sensor_h_mm": sensor_h,
                })
                st.success(f"인식됨: {mount} / {sensor} / 환산 ×{crop}", icon="✅")

        # Step 2 : 촬영 스타일
        elif step == 2:
            MAX_SUBJECTS = 2
            labels = [s["label"] for s in subjects]
            key_by_label = {s["label"]: s["key"] for s in subjects}
            # 이전 선택은 세션 상태(subj_pills)에 그대로 유지시킴 -> UI는 그걸로 보여주고, user_input의 subjects만 갱신
            if "subj_pills" not in st.session_state:
                st.session_state.subj_pills = [
                    s["label"] for s in subjects
                    if s["key"] in user_input.get("subjects", [])
                ]
            picked_labels = st.pills(f"촬영 주제 (주력 최대 {MAX_SUBJECTS}개)", labels,
                                     selection_mode="multi", key="subj_pills")
            user_input["subjects"] = [key_by_label[label] for label in picked_labels]

            # 주력 주제는 좁힐수록 정확하므로 2개로 제한
            if len(picked_labels) > MAX_SUBJECTS:
                st.warning(f"가장 주력으로 찍는 주제 {MAX_SUBJECTS}개만 골라주세요. "
                           "좁힐수록 더 정확한 추천이 가능합니다.", icon="🎯")

            st.write("")
            user_input["lens_type"] = st.radio(
                "렌즈 형태", lens_types,
                index=lens_types.index(user_input.get("lens_type", "상관없음")),
                horizontal=True)
            st.write("")
            user_input["low_light"] = st.slider(
                "빛이 부족한 곳(실내/밤/공연) 촬영 비중", 1, 5,
                user_input.get("low_light", 3),
                help="높을수록 밝은(조리개 큰) 렌즈를 우선 추천. 어두운 곳에서 흔들림/노이즈를 줄이고 배경흐림도 커져요",
            )

        # Step 3 : 예산 & 마무리
        elif step == 3:
            budget_min, budget_max = budget_range["min"], budget_range["max"]
            # 만원 단위로 보이기, 정확한 원 금액은 아래에 콤마로 표기.
            current_budget = user_input.get("budget", budget_max)
            budget_man = st.slider("예산", budget_min // 10000, budget_max // 10000,
                                   current_budget // 10000, step=5, format="%d만원")
            user_input["budget"] = budget_man * 10000
            st.caption(f"~ {user_input['budget']:,}원")

            st.write("")
            user_input["priority"] = st.radio(
                "무엇을 더 중요하게 생각하나요? (동점 시 우선순위)", ["화질", "휴대성", "가성비"],
                index=["화질", "휴대성", "가성비"].index(user_input.get("priority", "화질")),
                horizontal=True)
            st.write("")
            user_input["portability"] = st.slider(
                "가볍고 작은 렌즈를 얼마나 원하시나요?(필요도)", 1, 5,
                user_input.get("portability", 3),
                help="높을수록 가벼운 렌즈를 우선 추천. 들고 다니기 편해요")

        # 하단 내비게이션 (이전 / 다음 또는 추천받기)
        st.write("---")
        col_prev, _, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("< 이전", width="stretch"):
                if step == 1:
                    st.switch_page("pages/1_landing.py")
                else:
                    st.session_state.step -= 1
                    st.rerun()
        with col_next:
            if step < 3:
                if st.button("다음 ➡", type="primary", width="stretch"):
                    # Step 2에서는 주제 선택 개수를 검증하고 넘어가기
                    subject_count = len(user_input.get("subjects", []))
                    if step == 2 and subject_count == 0:
                        st.toast("촬영 주제를 하나 이상 골라주세요.", icon="⚠️")
                    elif step == 2 and subject_count > 2:
                        st.toast("촬영 주제는 2개까지만 골라주세요.", icon="🎯")
                    else:
                        st.session_state.step += 1
                        st.rerun()
            else:
                # 마지막 단계: 입력값을 payload로 묶어 백엔드에 추천 요청
                if st.button("렌즈 추천받기", type="primary", width="stretch"):
                    payload = {
                        "body_id": user_input.get("body_id"),
                        # 직접 선택(목록에 없는 카메라)일 때 백엔드가 쓰는 값
                        "mount": user_input.get("mount"),
                        "sensor": user_input.get("sensor"),
                        "crop": user_input.get("crop"),
                        "cam_title": user_input.get("cam_title"),
                        "subjects": user_input.get("subjects", []),
                        "lens_type": user_input.get("lens_type", "상관없음"),
                        "low_light": user_input.get("low_light", 3),
                        "budget": user_input.get("budget", budget_range["max"]),
                        "priority": user_input.get("priority", "화질"),
                        "portability": user_input.get("portability", 3),
                    }
                    print("[LOG]: 추천 요청 전송, 결과 페이지로 이동...")
                    with st.spinner("추천 계산 중..."):
                        st.session_state.result = api.recommend_lens(payload)
                    st.session_state.balloons_shown = False  # 새 추천이니 풍선 한 번 다시
                    st.switch_page("pages/3_result.py")

# user_input 갱신이 끝난 뒤 좌측 패널을 그리기 (최신값 반영)
with left_visual:
    with st.container(border=False, height=620):
        render_summary()
