RISK_GUIDANCE = {
    "안전": {
        "rest_time": "정기 휴식 유지",
        "action_text": "시원한 물을 가까이 두고 작업 중 상태 변화를 계속 확인하세요.",
        "tone": "safe",
    },
    "주의": {
        "rest_time": "매시간 10분 참고",
        "action_text": "짧고 자주 쉬며 심박수 상승이나 어지러움 같은 변화를 살피세요.",
        "tone": "caution",
    },
    "위험": {
        "rest_time": "매시간 15분 참고",
        "action_text": "그늘 휴식을 확보하고 작업 속도와 강도를 낮추세요.",
        "tone": "danger",
    },
    "매우 위험": {
        "rest_time": "매시간 15분 이상",
        "action_text": "충분히 쉬도록 배치하고 무더위 시간대 작업을 최소화하세요.",
        "tone": "severe",
    },
    "즉시 작업중지": {
        "rest_time": "즉시 작업 중지",
        "action_text": "작업을 멈추고 시원한 장소로 이동해 상태를 확인하세요.",
        "tone": "stop",
    },
}

ALERT_RISK_LEVELS = {"위험", "매우 위험", "즉시 작업중지"}


def get_risk_guidance(risk):
    """Return dashboard guidance for a calculated heat-risk label."""
    try:
        return RISK_GUIDANCE[risk].copy()
    except KeyError as error:
        raise ValueError(f"알 수 없는 위험도 단계입니다: {risk}") from error


def should_trigger_alert(risk):
    """Return whether the dashboard should show a manager alert."""
    if risk not in RISK_GUIDANCE:
        raise ValueError(f"알 수 없는 위험도 단계입니다: {risk}")
    return risk in ALERT_RISK_LEVELS
