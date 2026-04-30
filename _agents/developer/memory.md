# 💻 Developer (Lead Engineer) 개인 메모리

_Developer 에이전트만 읽고 쓰는 개인 노트. 학습·교훈·자주 쓰는 패턴이 누적됩니다._

## 학습 기록

- [2026-04-28] 다운로드 실패 로그를 즉시 추적하여 API 응답, 서버 파이프라인 또는 데이터 저장소의 오류 원인을 식별하고, 즉각적인 패치 및 재시도 로직을 구현하십시오. → 산출물 sessions/2026-04-28T01-10/developer.md
- [2026-04-28] 즉시 main.py 파일을 실행하십시오. 실행 전, 필요한 모든 종속성(dependencies)이 설치되어 있는지 확인하고, 실행 결과를 콘솔에 상세히 출력하여 보고하십시오. → 산출물 sessions/2026-04-28T01-16/developer.md
- [2026-04-28] 최종 디자인 시안과 구조를 바탕으로, 모바일과 데스크톱 환경 모두에서 완벽하게 반응하는 웹사이트를 구축해주세요. 필요한 기능(예: 문의 폼, 회원가입 API 연동)과 백엔드 데이터 파이프라인까지 구현해야 합니다. → 산출물 sessions/2026-04-28T01-24/developer.md
- [2026-04-28] 제공된 GitHub 리포지토리(https://github.com/forforestchang/andrej-karpathy-skills)의 내용을 정밀 분석하여 핵심 스킬, 코드 구조, 학습 방법론을 파악하고, 이를 향후 모든 개발 및 자동화 작업의 기본 표준(SOP)으로 내재화하여 작업 프로세스에 반영할 것. → 산출물 sessions/2026-04-28T01-32/developer.md
- [2026-04-28] 현재 작업 중인 소스 코드를 아무런 수정이나 리팩토링 없이 원본 그대로 화면에 출력하십시오. → 산출물 sessions/2026-04-28T01-35/developer.md
- [2026-04-28] main.py 파일을 로드하여 코드의 전체적인 구조, 주요 로직, 사용된 라이브러리 및 의존성을 분석하고 핵심 기능을 요약하여 보고하세요. → 산출물 sessions/2026-04-28T01-43/developer.md
- [2026-04-28] 현재 CLI 코드 전체를 분석하고, 시스템 신뢰도 확보를 최우선 목표로 하여 리팩토링을 진행합니다. 1. 모든 DB 연결 및 주요 단계(connect, export, import 등)에 '트랜잭션 커밋/롤백' 로직을 도입하여, 중간 실패 시 시스템이 안전하게 종료되도록 예외 처리를 강화합니다. 2. `OracleConnection` 객체를 싱글톤 패턴으로 개선하고, 모든 연결 및 자원(Resource) 관리를 `with` 구문(Context Manager)을 사용하여 자동화합니다. 3. `run_comparison` 함수에 Busi
- [2026-04-28] 기존 코드를 수정하지 않고 외부 데이터 파일(JSON 또는 Markdown)을 읽어와 웹 페이지에 동적으로 렌더링하는 데이터 파이프라인을 구축하고 구현하세요. → 산출물 sessions/2026-04-28T01-53/developer.md
- [2026-04-28] 데이터 무결성 검증(DIV) 기능이 강화된 자동화 파이프라인 아키텍처를 설계하고, 사용자 인터페이스(Web UI)를 위한 API 명세서를 작성하라. → 산출물 sessions/2026-04-28T02-02/developer.md
- [2026-04-28] 현재까지 완료된 작업의 결과물(웹 페이지, 데이터 시각화 또는 CLI 출력값)을 로컬 화면에 즉시 렌더링하고 사용자에게 출력하십시오. → 산출물 sessions/2026-04-28T07-47/developer.md
- [2026-04-28] 'colorama' 패키지를 설치(`pip install colorama`)하고, 향후 재발 방지를 위해 프로젝트의 의존성 관리 파일(requirements.txt 등)에 해당 라이브러리를 즉시 업데이트하여 환경 일관성을 확보하십시오. → 산출물 sessions/2026-04-28T07-53/developer.md
- [2026-04-28] 현재 작업 중인 데이터와 분석 로직을 로컬 웹 서버 또는 터미널 UI(TUI)로 즉시 렌더링할 수 있는 실행 스크립트를 구동하고, 결과값을 로컬 화면에 출력하십시오. → 산출물 sessions/2026-04-28T08-01/developer.md
- [2026-04-28] 확정된 마일스톤에 따라 차기 모듈(예: Data Extraction 로직)을 개발하십시오. 이때 'from scratch' 원칙과 'Zero-Risk' 가치를 준수하며, 기존에 정의된 에러 처리 및 모니터링 UI를 통합하십시오. → 산출물 sessions/2026-04-28T08-08/developer.md
- [2026-04-29] 리서치 결과를 바탕으로 'Zero-Risk'를 보장하기 위한 데이터 무결성 검증(DIV) 강화, 자동화된 에러 복구(Rollback) 로직, 성능 최적화(Multi-threading) 및 확장 가능한 모듈형 아키텍처 설계안을 작성하라. → 산출물 sessions/2026-04-29T03-20/developer.md
- [2026-04-29] 정의된 규격을 바탕으로 3단계 DIV 엔진, Checkpointing/Rollback 로직, 그리고 모듈형 Adapter 패턴 구조를 포함한 핵심 마이그레이션 프레임워크를 구현하라. → 산출물 sessions/2026-04-29T06-25/developer.md
- [2026-04-29] 기존 설계안에 따라 `BaseAdapter` 추상 클래스와 `3-Stage DIV` 엔진(데이터 무결성 검증 로직)의 핵심 파이썬 코드를 작성하세요. 롤백 기능, 에러 핸들링, 그리고 TUI 출력을 위한 구조를 포함하여 'Zero-Risk' 가치를 코드로 구현해야 합니다. → 산출물 sessions/2026-04-29T06-41/developer.md
- [2026-04-29] PostgreSQLAdapter 클래스를 구현하고, 기존 3-Stage DIV 엔진을 적용하여 소스-타겟 간 데이터 일치성을 검증하는 통합 테스트 스크립트를 작성 및 실행할 것 → 산출물 sessions/2026-04-29T06-50/developer.md
- [2026-04-29] `PostgreSQLAdapter`에 3-Stage DIV 엔진을 통합하고, `psycopg2`를 이용한 실제 DB 연동 및 데이터 무결성 검증 로직을 구현하여 통합 테스트를 수행하라. → 산출물 sessions/2026-04-29T07-11/developer.md
- [2026-04-29] 기존 어댑터 패턴을 기반으로 `MySQLAdapter` 및 `MSSQLAdapter` 개발에 착수하고, 3-Stage DIV 엔진이 통합되도록 구현할 것 → 산출물 sessions/2026-04-29T07-18/developer.md
- [2026-04-29] Researcher의 리포트를 바탕으로 MySQLAdapter 및 MSSQLAdapter의 상세 로직을 구현하고, 3-Stage DIV 엔진이 각 DB 타입의 특성에 맞춰 정확히 작동하는지 단위 테스트를 수행할 것. → 산출물 sessions/2026-04-29T07-37/developer.md
- [2026-04-29] MSSQLAdapter 구현(DATETIME2, NVARCHAR(MAX) 처리 로직 집중) 및 Business가 설계한 리스크 시나리오를 재현할 RiskSimulator 모듈 개발 착수 → 산출물 sessions/2026-04-29T09-04/developer.md
- [2026-04-30] PostgreSQLAdapter 내의 NUMBER 타입 매핑 로직을 재검토하고, 소수점(Scale) 정밀도 유실을 방지하는 로직을 우선적으로 구현하여 테스트 가능한 코드를 작성하라. → 산출물 sessions/2026-04-30T03-15/developer.md
- [2026-04-30] 개발된 RiskSimulator를 활용하여, MySQL 및 MSSQL 어댑터와 통합된 환경에서 데이터 타입 불일치, 길이 초과 등 모든 에러 케이스를 강제 발생시키고 롤백 기능의 성공 여부를 검증하는 통합 부하 테스트를 수행하라. → 산출물 sessions/2026-04-30T03-15/developer.md