\# Mini SOC — SSH 공격·탐지 자동화



\[!\[Detection Tests](https://github.com/kjm0320/mini-soc/actions/workflows/tests.yml/badge.svg)](https://github.com/kjm0320/mini-soc/actions/workflows/tests.yml)



로컬 Docker 환경에서 SSH 인증 실패를 재현하고,

로그 수집부터 Python 기반 탐지, 자동 테스트까지 구현한 개인 보안 프로젝트입니다.



\## 주요 기능



\- Docker 기반 SSH 실습 서버

\- 동일 IP에서 60초 이내 로그인 실패 3회 이상 탐지

\- 로그인 실패 생성 → 로그 수집 → 탐지 자동화

\- 탐지 로직 테스트 7개

\- GitHub Actions를 통한 자동 테스트



현재 버전은 기존 로그를 분석하는 방식입니다.

Wazuh 연동과 실시간 관제는 추후 확장 항목입니다.



\## 동작 흐름



1\. Paramiko가 로컬 SSH 서버에 인증 실패를 3회 발생시킵니다.

2\. OpenSSH가 인증 실패 로그를 출력합니다.

3\. 자동화 스크립트가 이번 실행에 해당하는 로그를 추출합니다.

4\. Python 탐지기가 IP별 실패 횟수를 집계합니다.

5\. 임계값 도달 시 경보를 출력하고 결과를 검증합니다.



접속 대상은 127.0.0.1:2222로 고정되어 있습니다.

서버 공개 호스트 키를 검증하며, 실제 계정 비밀번호는 필요하지 않습니다.



\## 기술 구성



| 영역 | 도구 |

|---|---|

| 작업 환경 | Windows CMD |

| 실습 환경 | Docker Desktop, WSL2, Docker Compose |

| 대상 서버 | Debian, OpenSSH |

| 탐지 및 자동화 | Python 3.12, Paramiko |

| 테스트 | unittest |

| 버전 관리 및 CI | Git, GitHub, GitHub Actions |



\## 빠른 시작



아래 명령은 Windows CMD 기준입니다.

Git, Python 3.12, Docker Desktop이 필요하며,

Docker Desktop의 Linux 컨테이너 엔진이 실행 중이어야 합니다.



\### 1. 저장소 다운로드



```bat

git clone https://github.com/kjm0320/mini-soc.git

cd mini-soc

```



이미 저장소가 있다면 기존 mini-soc 폴더에서 진행합니다.



\### 2. Python 환경 구성



```bat

python -m venv .venv

.venv\\Scripts\\python.exe -m pip install -r requirements.txt

```



\### 3. SSH 서버 실행



```bat

docker compose up -d --build

docker compose ps

```



\### 4. 자동 재현 및 탐지



```bat

.venv\\Scripts\\python.exe scripts\\run\_demo.py

```



성공 시 출력 예시:



```text

\[DEMO] Expected login failure 1/3

\[DEMO] Expected login failure 2/3

\[DEMO] Expected login failure 3/3

\[ALERT] Repeated SSH login failures ip=... count=3 window=60s time=...

\[SUMMARY] failed\_logins=3 alerts=1

\[PASS] Attack simulation -> logs -> detection

```



IP와 시각은 실행 환경에 따라 달라질 수 있습니다.



\### 5. 테스트 실행



```bat

.venv\\Scripts\\python.exe -m unittest discover -s tests -v

```



\### 6. 실습 서버 중지 및 재시작



```bat

docker compose stop

docker compose start

```



\## 탐지 기준과 검증



동일 IP의 실패 이벤트를 60초 시간 범위로 집계합니다.

실패 횟수가 3회에 도달할 때 경보를 발생시킵니다.

정상 로그인은 실패 횟수에 포함하지 않습니다.



| 검증 항목 | 확인 결과 |

|---|---|

| 실제 SSH 인증 실패 3회 | 경보 1건 |

| 실패 횟수와 시간 경계 | 자동 테스트 통과 |

| 서로 다른 IP 구분 | 자동 테스트 통과 |

| 정상 로그인 제외 | 자동 테스트 통과 |

| 연속 실패의 중복 경보 억제 | 자동 테스트 통과 |

| GitHub Actions | 탐지 로직 테스트 7개 통과 |



3회/60초는 실습용 기준이며 운영 환경에 맞춘 조정이 필요합니다.

테스트 통과가 실제 환경의 탐지율이나 낮은 오탐률을 보장하지는 않습니다.



\## 주요 파일



| 경로 | 역할 |

|---|---|

| lab/Dockerfile | SSH 서버 이미지 |

| compose.yaml | 컨테이너 실행 및 자원 제한 |

| scripts/detect\_ssh.py | 반복 인증 실패 탐지 |

| scripts/run\_demo.py | 실패 이벤트 생성과 탐지 검증 |

| tests/test\_detect\_ssh.py | 탐지 로직 테스트 7개 |

| .github/workflows/tests.yml | GitHub Actions 설정 |

| docs/ssh-detection-report.md | 분석 보고서 |



\## 분석 보고서



\[SSH 반복 로그인 실패 탐지 보고서](docs/ssh-detection-report.md)



실제 실행 결과, MITRE ATT\&CK 연관성,

오탐·미탐 가능성과 구현 한계를 정리했습니다.



\## 환경 제약과 한계



\- RAM 8GB PC에서 실습하기 위해 Docker SSH 서버와 Python으로 구성했습니다.

\- 현재 SIEM 연동과 실시간 로그 수집은 구현하지 않았습니다.

\- 시간순 로그 입력을 가정하며, 실행 간 탐지 상태를 저장하지 않습니다.

\- 느린 시도와 여러 IP로 분산된 시도는 현재 규칙을 회피할 수 있습니다.

\- 자동 재현은 해당 실행의 로그만 선택하므로 혼합 트래픽 검증은 아닙니다.



\## 향후 개선



\- \[ ] JSON 형식 경보 저장

\- \[ ] 실패 후 성공한 로그인 상관분석

\- \[ ] 실시간 로그 수집 및 중복 처리

\- \[ ] 자원 확보 후 Wazuh 연동



\## 실습 범위



본인이 소유하고 통제하는 로컬 환경에서 인증 실패를 재현합니다.

계정 탈취를 수행하는 도구가 아니며,

비밀번호·토큰·개인 키는 저장소에 포함하지 않습니다.

