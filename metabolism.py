def estimate_vo2(age, sex, hr):
    """Estimate oxygen uptake from a worker profile and heart rate."""
    if age <= 0 or age > 120:
        raise ValueError("나이는 1~120 범위여야 합니다.")

    if hr <= 0 or hr > 220:
        raise ValueError("심박수는 1~220 범위여야 합니다.")

    normalized_sex = sex.lower()
    hr_max = 220 - age
    if hr > hr_max + 20:
        raise ValueError("심박수가 비정상적으로 높습니다.")

    if normalized_sex == "male":
        vo2_max = 45
    elif normalized_sex == "female":
        vo2_max = 35
    else:
        raise ValueError("성별은 male 또는 female 이어야 합니다.")

    intensity = min(hr / hr_max, 1)
    return vo2_max * intensity


def calculate_calories(vo2, weight):
    """Convert estimated oxygen uptake to kcal burned per minute."""
    if weight <= 0 or weight > 300:
        raise ValueError("체중은 1~300kg 범위여야 합니다.")

    oxygen_consumption = (vo2 * weight) / 1000
    return oxygen_consumption * 5
