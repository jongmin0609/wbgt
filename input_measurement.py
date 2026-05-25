import argparse

from measurement_store import CURRENT_MEASUREMENT_PATH, read_measurement, write_measurement


def prompt_value(label):
    return input(f"{label}: ").strip()


def parse_args():
    parser = argparse.ArgumentParser(
        description="PC에서 온열 위험도 대시보드 측정값을 갱신합니다.",
    )
    parser.add_argument("--heart-rate", help="현재 심박수(bpm)")
    parser.add_argument("--wbgt", help="온열지수(WBGT)")
    parser.add_argument("--age", help="나이")
    parser.add_argument("--weight", help="체중(kg)")
    parser.add_argument("--sex", choices=("male", "female"), help="성별")
    return parser.parse_args()


def main():
    args = parse_args()
    current = read_measurement()
    heart_rate = args.heart_rate or prompt_value("현재 심박수(bpm)")
    wbgt = args.wbgt or prompt_value("온열지수(WBGT)")
    age = args.age or current["age"]
    weight = args.weight or current["weight"]
    sex = args.sex or current["sex"]

    try:
        payload = write_measurement(heart_rate, wbgt, age=age, weight=weight, sex=sex)
    except ValueError as error:
        raise SystemExit(f"입력 오류: {error}") from error

    print("측정값을 저장했습니다.")
    print(f"심박수: {payload['heart_rate']} bpm")
    print(f"온열지수(WBGT): {payload['wbgt']:.1f}")
    print(f"프로필: {payload['age']}세 / {payload['weight']:g}kg / {payload['sex']}")
    print(f"저장 위치: {CURRENT_MEASUREMENT_PATH}")


if __name__ == "__main__":
    main()
