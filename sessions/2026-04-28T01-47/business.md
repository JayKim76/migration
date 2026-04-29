# 💰 Business — Oracle DB 마이그레이션 전문가 입장에서, 현재 CLI 툴의 기능적 위험 요소(Risk)와 추가해야 할 핵심 가치를 분석해주세요. 특히, '롤백(Rollback)' 기능의 필요성을 제기하고, 이를 통합하는 전략적 방안을 제시해야 합니다. 또한, 마이그레이션 전후의 '데이터 무결성 검증(Data Integrity Validation)'을 KPI로 설정하고, 이를 비교 단계(compare)에 추가할 수 있는 비즈니스 로직을 정의해주세요.

💰 Business: 작업 시작합니다.

## 💡 CLI 툴 개선을 위한 전략적 비즈니스 분석 및 기능 정의

제시된 `oracle-migration` CLI는 전형적인 '선형적 데이터 파이프라인(Linear Data Pipeline)' 구조를 갖추고 있습니다. 기능적으로는 높은 완성도를 보이지만, 비즈니스 관점에서 가장 치명적인 리스크는 **'단방향성(One-Way Flow)'**과 **'트랜잭션 경계(Transaction Boundary)'**의 부재입니다.

따라서, 핵심 목표는 **'마이그레이션의 안전성(Safety)'**과 **'신뢰성(Assurance)'**을 극대화하여, 이 툴을 단순한 ETL 도구가 아닌, **'검증된 상태 전환(Validated State Transition)'** 플랫폼으로 포지셔닝하는 것입니다.

---

### 1. 기능적 위험 요소 (Functional Risks) 및 비즈니스 영향 분석

| 위험 요소 (Risk Area) | 현황 분석 (Current State) | 비즈니스 위험 (Business Impact) | 필수 개선 기능 (Mitigation) |
| :--- | :--- | :--- | :--- |
| **부분 마이그레이션** | `export` 또는 `import` 단계 중 하나라도 실패 시, Target DB는 불완전한 상태(Inconsistent State)에 머무름. | **데이터 무결성 위협 (Critical)**. 롤백을 위한 기준점(Baseline) 부재로 수동 복구 시간이 길어짐. | **`rollback` 명령** 도입 및 트랜잭션 그룹화. |
| **데이터 불일치 검증** | `compare`는 구조(Schema) 비교에 중점을 두지만, 데이터 내용(Content)의 차이점(Delta)을 깊이 있게 검증하지 못함. | **비즈니스 로직 오류 위험.** "데이터는 옮겨졌지만, 잘못된 값으로 옮겨졌을 수 있다"는 리스크. | **행 단위 데이터 비교 (Row-Level Comparison)** 로직 강화 및 KPI화. |
| **운영 환경 의존성** | 모든 단계가 순차적(Sequential)으로 진행되어, 중간 단계에서 오류가 발생하면 전체 파이프라인이 멈추고 재시도가 어려움. | **낮은 가용성(Availability)**. 실패 시 전체 프로젝트 지연 및 높은 인건비 발생. | **`dry-run` 및 `validation-only` 모드**를 도입하여 리스크를 사전에 시뮬레이션해야 함. |

---

### 2. 핵심 가치 제안 및 전략적 통합 방안

#### 2.1. 🛡️ 롤백(Rollback) 기능 통합 전략 (최우선 순위)
롤백은 단순한 명령어 추가가 아니라, **마이그레이션 프로세스 자체에 '안전망'을 구축하는 것**을 의미합니다.

*   **필요성 제기:** 마이그레이션은 **위험한 트랜잭션**입니다. 실패했을 때의 비용(Cost of Failure)을 최소화하는 것이 가장 큰 가치입니다.
*   **전략적 통합 방안:**
    1.  **Pre-Migration Artifact Capture:** `connect` 및 `extract-ddl` 단계에서 Target DB의 현재 상태를 스냅샷(Schema DDL, 주요 테이블의 체크섬)으로 저장합니다.
    2.  **`rollback` 명령 정의:** `python main.py rollback --config <path>`
    3.  **로직:** 롤백은 데이터를 삭제하는 것이 아니라, **최초 캡처된 스냅샷을 기반으로 Target DB를 원래 상태로 되돌리는 과정**을 실행해야 합니다. (예: `ALTER TABLE`을 이용한 데이터 삭제/복원, 또는 스냅샷 복구 스크립트 실행).

#### 2.2. 📈 데이터 무결성 검증 (Data Integrity Validation, DIV) KPI 정의
DIV는 이 툴의 가장 중요한 **KPI(Key Performance Indicator)**이자, 성공적인 마이그레이션의 **최종 비즈니스 증거(Proof Point)**입니다.

*   **KPI 정의:** **데이터 충실도 비율 (Data Fidelity Rate, DFR)**
    *   $$DFR = \frac{\text{검증된 레코드 수 (Validated Records)}}{\text{예상 레코드 수 (Total Source Records)}} \times 100$$
    *   **목표:** 100% (최소 99.99% 이상).
*   **비즈니스 로직 정의 (Compare 단계 확장):**
    *   기존 `compare`는 `SELECT * FROM source WHERE PK=X`와 `SELECT * FROM target WHERE PK=X`를 비교합니다.
    *   **확장 로직:** `compare` 명령에 **'checksum'** 기반 비교 로직을 추가합니다.
        1.  **Source Side:** PK를 기반으로 특정 레코드 그룹의 핵심 컬럼들에 대한 해시 값(Hash/Checksum)을 계산하여 임시 테이블에 저장합니다.
        2.  **Target Side:** 동일한 PK 그룹에 대해 해시 값을 계산하고, Source의 해시 값과 비교합니다.
        3.  **결과:** 해시 값이 불일치하거나, 레코드 수가 일치하지 않는 경우를 **'Mismatch'**로 분류하고, 이를 보고서의 최상단에 경고(Warning)로 표시합니다.

---

### 3. [Actionable] CLI 명령어 및 파이프라인 개선안

다음과 같이 CLI 명령어와 파이프라인을 확장해야 합니다.

| 단계 (Step) | 기존 명령어 | 개선/추가 명령어 | 역할 및 비즈니스 로직 |
| :--- | :--- | :--- | :--- |
| **(New)** | N/A | `connect --validate` | 연결 테스트 외에, **Source와 Target의 네트워크/접근 권한을 종합적으로 검증**하는 단계 추가. |
| **(New)** | N/A | `snapshot` | **마이그레이션 시작 전, Target DB의 현재 스키마 및 핵심 테이블의 체크섬을 캡처**하여 롤백의 기준점(Baseline)을 생성. |
| **Export** | `export` | (변경 없음) | 데이터 추출 (Source -> File). |
| **Import** | `import` | (변경 없음) | 데이터 적재 (File -> Target). |
| **Compare** | `compare` | `compare --validate-checksum` | **DIV KPI 실행.** Row-by-Row 비교를 넘어, 지정된 컬럼 그룹의 체크섬 비교를 강제 실행. |
| **(New)** | N/A | `rollback` | **최종 안전장치.** `snapshot` 단계에서 생성된 아티팩트를 이용해 Target DB를 원래 상태로 복구. |
| **Pipeline** | `migrate` | `migrate --full-cycle` | 전체 파이프라인 실행 시, **`snapshot` $\rightarrow$ (Export $\rightarrow$ Import) $\rightarrow$ `compare --validate-checksum` $\rightarrow$ (Success/Fail 시) `rollback`** 흐름을 강제하는 오케스트레이션 로직 추가. |

📝 다음 단계 제안: `rollback` 기능 구현을 위한 `snapshot` 단계의 데이터베이스 스냅샷(Schema & Checksum) 캡처 로직을 `src/metadata.py`에 구체화하고, `main.py`의 `cmd_rollback` 커맨드를 설계해야 합니다.
