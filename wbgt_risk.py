def calculate_heat_risk(wbgt, kcal):
    """Classify workload and heat risk from WBGT and energy use."""
    if wbgt < 0 or wbgt > 60:
        raise ValueError("WBGT 값이 비정상적입니다.")

    if kcal < 0:
        raise ValueError("칼로리 값이 비정상적입니다.")

    if kcal < 3:
        workload = "저강도"
    elif kcal < 6:
        workload = "중강도"
    else:
        workload = "고강도"

    if wbgt >= 33:
        risk = "즉시 작업중지" if workload == "고강도" else "매우 위험"
    elif wbgt >= 31:
        risk = "매우 위험" if workload == "고강도" else "위험"
    elif wbgt >= 28:
        risk = "위험" if workload == "고강도" else "주의"
    else:
        risk = "안전"

    return risk, workload
