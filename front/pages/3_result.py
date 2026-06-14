# pages/3_result.py (결과 페이지 - 추천 렌즈 / 화각 시뮬 / 나의 입력)
import streamlit as st
from core import state, fov, assets  # 세션상태 확인용 / 화각계산 / 이미지에셋


def eff_focal_num(eff_str):
    # '75mm' or '24-105mm' 에서 넓은쪽(첫) 숫자만 뽑기. (부채꼴 화각 계산 ㅎㅎ)
    head = eff_str.replace("mm", "").split("-")[0].strip()
    return int(head) if head.isdigit() else 50


def alt_badges(alt, best):
    # 대안(2~3위)이 1위와 무엇이 다른지 보여주는 배지 문구들
    # (가벼움 / 더 저렴 / 더 밝음 / 다른 형태 또는 다른 화각)
    badges = []
    weight_diff = best["weight"] - alt["weight"]
    if weight_diff >= 80:
        badges.append(f"🪶 {weight_diff}g 가벼움")
    if alt["price"] <= best["price"] * 0.85:
        badges.append("더 저렴")
    if alt["aperture"] < best["aperture"]:
        badges.append(f"F{alt['aperture']} 더 밝음")
    if alt["type"] != best["type"]:
        badges.append(alt["type"])
    if not badges:  # 위 조건에 안 걸리면 화각 환산 시키기
        badges.append(f"환산 {alt['eff_focal']}")
    return badges[:2]


def render_lens(lens, rank, best, budget, with_badge=True):
    # 렌즈 한 줄(사진 + 텍스트). 1위 카드와 대안 expander 양쪽에서 재사용.
    photo_col, text_col = st.columns([1, 2.3], vertical_alignment="center")
    with photo_col:
        lens_photo = assets.find_asset("lenses", lens.get("img"))
        if lens_photo:
            st.image(assets.load_image(lens_photo), width="stretch")
        else:
            # 사진이 없으면 PlaceHolder 적용
            st.markdown(
                "<div style='display:flex;align-items:center;"
                "justify-content:center;height:110px;font-size:38px;"
                "background:rgba(33,150,243,0.06);border-radius:12px'>🔭</div>",
                unsafe_allow_html=True)
            st.caption("사진 준비 중")
    with text_col:
        # 1위는 '가장 잘 맞음', 대안은 1위와 다른 점 배지
        if with_badge:
            if rank == 0:
                st.markdown(":green-badge[⭐ 가장 잘 맞음]")
            else:
                st.markdown(" ".join(f":orange-badge[{b}]" for b in alt_badges(lens, best)))
        st.markdown(f"##### {lens['name']}")
        st.caption(f"{lens['role']} / 환산 {lens['eff_focal']} / F{lens['aperture']}")
        st.markdown(" ".join(f":blue-badge[{tag}]" for tag in lens["tags"]))
        within_budget = lens["price"] <= budget
        st.markdown(
            f"**{lens['price']:,}원** " + (":green[(예산 내)]" if within_budget else ":red[(예산 초과)]")
        )
        st.caption(lens["reason"])

# 페이지 진입 시 세션 상태 체크 (이름 입력 여부, 추천 결과 존재 여부)
state.init()
state.check_name()
state.check_result()

# 추천 결과와 사용자 입력값을 세션에서 가져오기
result_data = st.session_state.result
user_input = st.session_state.inputs
body = result_data["body"]
crop = body.get("crop", 1.0)
sensor_w = user_input.get("sensor_w_mm", 35.9)
sensor_h = user_input.get("sensor_h_mm", 24.0)
budget = user_input.get("budget", 10 ** 9)

# 메인 레이아웃 구성 (1 : 3 : 1)
_, main_content, _ = st.columns([1, 3, 1])
with main_content:
    print("[LOG]: 결과 페이지 렌더링 중...")
    # 결과 페이지에 처음 들어왔을 때만 풍선 (rerun마다 반복되지 않도록)
    if not st.session_state.get("balloons_shown"):
        st.balloons()
        st.session_state.balloons_shown = True
    st.markdown(f"## {st.session_state.user_name}님께 추천하는 렌즈")
    st.caption(f"{body['title']} | {body.get('mount') or '센서 기준'} | "
               f"{body['sensor']} (×{crop})")
    st.write("---")

    # 보기 선택 (추천 렌즈 / 화각 시뮬레이터 / 나의 입력값)
    views = ["📦 추천 렌즈", "🔭 화각 시뮬", "✍️ 나의 입력"]
    view = st.segmented_control("보기", views, default=views[0],
                                key="result_view", label_visibility="collapsed")
    if view is None:  # 선택된 칸을 다시 누르면 None이 되므로 기본값 설정
        view = views[0]

    # 추천 렌즈 (좌: 추천 목록 / 우: 화각 비교)
    if view == views[0]:
        results = result_data.get("results", [])
        if not results:
            st.warning("조건에 맞는 렌즈가 없어요. 예산을 올리거나 조건을 완화해 보세요.")
        best = results[0] if results else None

        list_col, side_col = st.columns([2, 1], gap="large")

        # 좌측: 1위는 카드로 펼침 / 2~3위 접음
        with list_col:
            for rank, lens in enumerate(results):
                if rank == 0:
                    with st.container(border=True):
                        render_lens(lens, rank, best, budget)
                else:
                    expander_label = (f"{' · '.join(alt_badges(lens, best))}  ·  "
                                      f"{lens['name']}  ·  {lens['price']:,}원")
                    with st.expander(expander_label):
                        render_lens(lens, rank, best, budget, with_badge=False)

        # 우측: 추천된 렌즈들의 화각을 한 번에 겹쳐 비교
        with side_col:
            with st.container(border=True):
                st.markdown("**추천된 렌즈 화각 비교**")
                if results:
                    items = [
                        {"eff_focal": eff_focal_num(lens["eff_focal"]),
                         "h_aov": fov.angle_of_view(eff_focal_num(lens["eff_focal"]), 35.9)}
                        for lens in results
                    ]
                    st.plotly_chart(fov.compare_figure(items), width="stretch")
                else:
                    st.caption("추천 렌즈가 없습니다.")

    # 화각 시뮬레이터 (화각 확인)
    elif view == views[1]:
        st.markdown("#### 초점거리를 바꿔 화각을 살펴보세요")
        default_focal = st.session_state.get("sim_focal", 35)
        default_focal = min(200, max(16, default_focal))
        focal = st.slider("초점거리 (실제 mm)", 16, 200, default_focal)
        point = fov.fov_point(focal, crop, sensor_w, sensor_h)

        # 차트 + 화각 정보 나란히 보여주기
        chart_col, info_col = st.columns([1.2, 1])
        with chart_col:
            st.plotly_chart(fov.wedge_figure(point["h_aov"], f"{focal}mm"),
                            width="stretch")
        with info_col:
            st.metric("환산 화각", f"{point['eff_focal']}mm",
                      help=f"실제 {focal}mm × {crop}")
            st.markdown(f"**분류** : {point['category']}")
            st.markdown(f"**수평** {point['h_aov']}° · **수직** {point['v_aov']}°")
            st.markdown(f"적합: {' · '.join(point['suited_for'])}")

    # 나의 입력 (입력값 요약)
    elif view == views[2]:
        st.markdown("#### 입력 요약")
        picked_subjects = user_input.get("subjects", [])
        rows = [
            ("내 카메라", f"{body['title']} "
                       f"({body.get('mount') or '센서 기준'} · {body['sensor']})"),
            ("촬영 주제", ", ".join(picked_subjects) or "-"),
            ("렌즈 형태", user_input.get("lens_type", "상관없음")),
            ("저조도", f"{user_input.get('low_light', 3)}/5"),
            ("예산", f"~{budget:,}원"),
            ("우선순위", user_input.get("priority", "화질")),
            ("휴대성", f"{user_input.get('portability', 3)}/5"),
        ]
        for label, value in rows:
            label_col, value_col = st.columns([1, 2])
            label_col.markdown(f"**{label}**")
            value_col.markdown(value)

    # 하단 버튼들 (다시하기 / 처음으로)
    st.write("---")
    left_btn, _, right_btn = st.columns([1, 2, 1])
    with left_btn:
        if st.button("다시하기", width="stretch"):
            state.reset_flow()
            st.switch_page("pages/2_input.py")
    with right_btn:
        if st.button("처음으로", width="stretch", type="primary"):
            st.session_state.clear()
            st.switch_page("pages/1_landing.py")
