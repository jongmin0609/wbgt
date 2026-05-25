from datetime import datetime

import streamlit as st

from measurement_store import read_measurement, write_measurement


SEX_LABELS = {
    "male": "남성",
    "female": "여성",
}


def format_updated_at(updated_at):
    if not updated_at:
        return "아직 저장된 시각이 없습니다."

    try:
        return datetime.fromisoformat(updated_at).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return str(updated_at)


st.set_page_config(
    page_title="PC 측정값 입력",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        :root {
            --ink: #101828;
            --muted: #526070;
            --line: #d7dee7;
            --surface: #ffffff;
            --canvas: #f4f7f9;
        }
        .stApp {
            background: var(--canvas);
            color: var(--ink);
        }
        .block-container {
            max-width: 720px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        h1, h2, h3, p {
            letter-spacing: 0;
        }
        .input-head {
            border-bottom: 1px solid var(--line);
            margin-bottom: 1rem;
            padding-bottom: 1rem;
        }
        .input-head p {
            color: var(--muted);
            font-size: 0.95rem;
            margin: 0 0 0.28rem;
        }
        .input-head h1 {
            color: var(--ink);
            font-size: 1.9rem;
            line-height: 1.2;
            margin: 0;
        }
        .current-status {
            align-items: center;
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: space-between;
            margin-bottom: 1rem;
            padding: 0.72rem 0.9rem;
        }
        .current-status strong {
            color: var(--ink);
            font-size: 0.98rem;
        }
        .current-status span {
            color: var(--muted);
            font-size: 0.9rem;
        }
        [data-testid="stForm"] {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1rem;
        }
        div[data-testid="stNumberInput"] input {
            background: var(--surface);
        }
        div[data-testid="stFormSubmitButton"] button {
            min-height: 2.8rem;
            width: 100%;
        }
        @media (max-width: 640px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1.2rem;
            }
            .input-head h1 {
                font-size: 1.55rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

current = read_measurement()
sex_options = list(SEX_LABELS)

st.markdown(
    f"""
    <header class="input-head">
        <p>PC 입력 페이지</p>
        <h1>측정값 전송</h1>
    </header>
    <section class="current-status" data-testid="input-status">
        <strong>최근 저장</strong>
        <span>{format_updated_at(current.get("updated_at"))}</span>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.form("measurement-form"):
    st.subheader("측정값")
    measurement_columns = st.columns(2)
    with measurement_columns[0]:
        heart_rate = st.number_input(
            "현재 심박수",
            min_value=1,
            max_value=220,
            value=current["heart_rate"],
            step=1,
            help="단위: bpm",
        )
    with measurement_columns[1]:
        wbgt = st.number_input(
            "온열지수 (WBGT)",
            min_value=0.0,
            max_value=60.0,
            value=current["wbgt"],
            step=0.1,
            format="%.1f",
        )

    st.subheader("프로필")
    profile_columns = st.columns(3)
    with profile_columns[0]:
        age = st.number_input(
            "나이",
            min_value=1,
            max_value=120,
            value=current["age"],
            step=1,
        )
    with profile_columns[1]:
        weight = st.number_input(
            "체중",
            min_value=1.0,
            max_value=300.0,
            value=current["weight"],
            step=0.5,
            format="%.1f",
            help="단위: kg",
        )
    with profile_columns[2]:
        sex = st.selectbox(
            "성별",
            options=sex_options,
            index=sex_options.index(current["sex"]),
            format_func=SEX_LABELS.get,
        )

    submitted = st.form_submit_button("대시보드로 전송", type="primary")

if submitted:
    try:
        payload = write_measurement(
            heart_rate=heart_rate,
            wbgt=wbgt,
            age=age,
            weight=weight,
            sex=sex,
        )
    except ValueError as error:
        st.error(str(error))
    else:
        st.success(
            f"저장 완료: {payload['heart_rate']} bpm / WBGT {payload['wbgt']:.1f} / "
            f"{payload['age']}세 / {payload['weight']:g}kg / {SEX_LABELS[payload['sex']]}"
        )
