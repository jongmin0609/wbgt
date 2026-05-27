RISK_GUIDANCE = {
    "안전": {
        "rest_time": "정기 휴식 유지",
        "action_text": (
            "현재 조건은 기준값보다 여유가 있습니다. "
            "작업을 지속하되 시원한 물을 가까이 두고 심박수, 어지러움, 두통, 과도한 발한 같은 변화를 관찰하세요."
        ),
        "action_items": [
            "정기 휴식 계획 유지",
            "시원한 물 섭취 유지",
            "심박수와 어지러움 여부 관찰",
            "WBGT 변화 추적",
        ],
        "water_text": "갈증이 나기 전부터 소량씩 자주 섭취",
        "control_text": "일반 모니터링 유지",
        "tone": "safe",
    },
    "주의": {
        "rest_time": "매시간 10분 이상 휴식 검토",
        "action_text": (
            "WBGT가 기준값에 근접했습니다. "
            "그늘 또는 시원한 장소에서 짧고 자주 쉬게 하고, 작업 속도와 작업강도를 낮추세요."
        ),
        "action_items": [
            "짧고 자주 쉬도록 안내",
            "그늘/냉방 장소 확보",
            "작업 속도 낮추기",
            "15~20분마다 수분 섭취 확인",
            "심박수와 이상 증상 재확인",
        ],
        "water_text": "15~20분마다 물 섭취 권고",
        "control_text": "작업자 상태 확인, 그늘 휴식 준비",
        "tone": "caution",
    },
    "위험": {
        "rest_time": "매시간 15분 이상 휴식 권고",
        "action_text": (
            "기준값을 초과한 상태입니다. "
            "그늘 휴식, 작업강도 저감, 인원 교대, 무더위 시간대 작업 조정을 시행하세요."
        ),
        "action_items": [
            "작업 속도와 강도 낮추기",
            "그늘/냉방 장소에서 휴식",
            "인원 교대 또는 작업시간 조정",
            "수분과 전해질 보충 확인",
            "10~15분 후 재측정",
        ],
        "water_text": "15~20분마다 물 섭취, 장시간 발한 시 전해질 보충 검토",
        "control_text": "작업-휴식 주기 조정 및 관리자 확인",
        "tone": "danger",
    },
    "매우 위험": {
        "rest_time": "작업시간 단축 및 휴식 대폭 증가",
        "action_text": (
            "기준값을 크게 초과했습니다. "
            "고강도 작업은 중단하거나 연기하고, 가능한 경우 냉방·그늘 휴식 후 재평가하세요."
        ),
        "action_items": [
            "고강도 작업 중단 또는 연기",
            "그늘/냉방 장소로 이동",
            "동료와 이상 증상 상호 확인",
            "작업시간 단축 또는 재배치",
            "재측정 후 작업 재개 판단",
        ],
        "water_text": "수분·전해질 보충, 동료 간 이상 증상 확인",
        "control_text": "작업 재배치, 기계화 보조, 작업시간 변경",
        "tone": "severe",
    },
    "즉시 작업중지": {
        "rest_time": "즉시 작업 중지",
        "action_text": (
            "작업을 즉시 멈추고 작업자를 시원한 장소로 이동시키세요. "
            "혼란, 실신, 구토, 의식 저하, 체온 이상 등 열질환 의심 증상이 있으면 즉시 응급조치를 요청하세요."
        ),
        "action_items": [
            "작업 중지 지시",
            "그늘/냉방 장소 이동",
            "이상 증상 확인 후 응급조치",
            "수분 섭취 가능 여부 확인",
            "10~15분 후 재측정",
        ],
        "water_text": "의식이 명확한 경우에만 수분 섭취",
        "control_text": "작업 재개 전 조건 재평가 필수",
        "tone": "stop",
    },
}


ALERT_RISK_LEVELS = {"위험", "매우 위험", "즉시 작업중지"}


def get_risk_guidance(
    risk,
    margin=None,
    workload=None,
    acclimatized=None,
    limit_type=None,
):
    """
    위험도에 따른 권장 행동 양식을 반환합니다.

    반영 요소:
    - 위험도 단계
    - 기준 WBGT와 실제 WBGT의 차이
    - 작업강도
    - 순화 여부
    - 적용 기준 종류
    """

    if risk not in RISK_GUIDANCE:
        raise ValueError(f"알 수 없는 위험도 단계입니다: {risk}")

    guidance = RISK_GUIDANCE[risk].copy()
    extra_notes = []

    if margin is not None:
        if margin >= 0:
            extra_notes.append(f"기준 WBGT까지 여유 {margin:.1f}℃")
        else:
            extra_notes.append(f"기준 WBGT를 {abs(margin):.1f}℃ 초과")

    if workload in ("고강도", "매우 고강도") and risk != "안전":
        extra_notes.append("고강도 작업이므로 작업 속도 저감, 인원 교대, 기계화 보조를 우선 검토")

    if acclimatized is False and risk in ("주의", "위험", "매우 위험"):
        extra_notes.append("비순화 작업자이므로 더 긴 휴식과 단계적 노출 적용")

    if limit_type:
        extra_notes.append(f"적용 기준: NIOSH {limit_type}")

    guidance["context_notes"] = extra_notes

    return guidance


def should_trigger_alert(risk):
    """
    관리자 경고 알림이 필요한 위험도인지 판단합니다.
    """

    if risk not in RISK_GUIDANCE:
        raise ValueError(f"알 수 없는 위험도 단계입니다: {risk}")

    return risk in ALERT_RISK_LEVELS
