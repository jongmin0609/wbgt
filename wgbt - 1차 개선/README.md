# 온열 위험도 대시보드

`코드 예시.txt`의 WBGT 계산 흐름을 단일 작업자용 Streamlit 화면으로 옮긴
로컬 대시보드입니다. PC 입력 페이지가 프로필, 현재 심박수, 온열지수(WBGT)를
저장하면 휴대폰 대시보드가 그 값을 읽어 위험도, 휴식 권고, 작업강도,
계산 근거를 표시합니다.
위험도 단계가 `위험` 이상이면 대시보드에 작업관리자 알람 배너가 표시됩니다.
휴대폰에서 `알림 활성화`를 누르면 위험 이상 단계에서 브라우저 알림, 소리, 진동을 시도합니다.

## 대시보드 실행

```powershell
python -m pip install -r requirements.txt
python -m streamlit run main.py
```

`.streamlit/config.toml`이 서버를 `0.0.0.0`에 바인딩하므로 같은 네트워크의
휴대폰에서는 PC의 로컬 IP와 Streamlit 포트로 접속할 수 있습니다.
대시보드는 PC에서 저장한 측정값을 약 2초마다 다시 읽습니다. PC 입력값이
없으면 `data/sample.csv`의 최신 샘플 값으로 시작합니다.

대시보드와 PC 입력 페이지를 한 번에 실행하려면 다음 스크립트를 사용할 수 있습니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\start_servers.ps1
```

휴대폰에서 IP 주소가 바뀌는 문제가 있으면 `http://컴퓨터이름:8501` 형태의
링크를 먼저 사용해 보세요. 이 프로젝트 PC의 컴퓨터 이름은 실행 스크립트가
자동으로 출력합니다.

## PC 입력 페이지

다른 PowerShell 창에서 PC 입력 페이지를 실행합니다.

```powershell
python -m streamlit run pc_input_page.py --server.port 8502
```

PC 브라우저에서 Streamlit이 표시한 `localhost:8502` 페이지를 열고 측정값과
프로필을 입력한 뒤 `대시보드로 전송` 버튼을 누릅니다. 입력 페이지에서 바꾼
나이, 체중, 성별은 VO2와 칼로리 소모량 계산에 사용됩니다.

## 휴대폰 알림

대시보드를 휴대폰에서 열고 `알림 활성화` 버튼을 한 번 누릅니다. 이후 위험도
단계가 `위험`, `매우 위험`, `즉시 작업중지` 중 하나가 되면 대시보드가
브라우저 알림, 소리, 진동을 시도합니다.

휴대폰 OS 푸시 알림은 브라우저 보안 정책상 HTTPS 주소에서만 정상 지원되는
경우가 많습니다. 로컬 `http://IP주소:8501` 접속에서는 소리와 진동은 가능해도
OS 알림 권한이 제한될 수 있습니다.

## PC 명령 입력

프롬프트에 값을 직접 입력합니다.

```powershell
python input_measurement.py
```

한 줄 명령으로도 갱신할 수 있습니다.

```powershell
python input_measurement.py --heart-rate 144 --wbgt 32.4
```

명령으로 프로필까지 같이 바꿀 수도 있습니다.

```powershell
python input_measurement.py --heart-rate 144 --wbgt 32.4 --age 38 --weight 82.5 --sex female
```

현재 입력값은 `data/current_measurement.json`에 저장됩니다. 실제 센서 입력을
붙일 때는 PC 입력 페이지와 같은 저장 함수를 호출하거나 같은 저장 형식으로
값을 갱신하면 됩니다.

위험도 계산은 제공된 WBGT 예시 로직을 유지합니다. 화면의 휴식 시간과 행동
양식은 현장 판단을 돕는 참고 권고이며 작업 조건, 증상, 공식 폭염 안내와 함께
확인해야 합니다.

## HTTPS 배포

어디서나 접속 가능한 HTTPS 주소가 필요하면 `cloud_app.py`를 배포합니다.
Render 배포 설정은 `render.yaml`에 들어 있고, 자세한 절차는
`DEPLOY_RENDER.md`를 참고하세요.
