# 💰 Business — AWS RDS 연동 시의 데이터 무결성 보장을 위한 검증 시나리오를 설계하고, 'Zero-Risk' 브랜드 가치를 증명할 KPI를 설정할 것

💰 Business: 작업 시작합니다.

# ☁️ AWS RDS 연동 데이터 무결성 검증 시나리오 및 Zero-Risk KPI 설계안

AWS RDS(Managed Service) 환경은 네트워크 가변성 및 인스턴스 관리 주체가 클라우드 사업자(AWS)라는 특수성이 있습니다. 따라서 단순 데이터 이관을 넘어, **'클라우드 환경의 불확실성 속에서도 데이터는 변하지 않는다'**는 것을 증명하는 것이 핵심입니다.

---

## 1. AWS RDS 특화 데이터 무결성 검증 시나리오 (3-Stage DIV)

RDS 연동 시 발생 가능한 네트워크 단절, 인스턴스 Failover, 스토리지 확장 등의 변수를 고려하여 설계합니다.

### [Stage 1] Schema & Metadata Integrity (Pre-Migration)
*   **검증 대상:** Table Structure, Data Types, Constraints (PK, FK, Unique), Indexes.
*   **시나리오:** 
    *   Oracle의 데이터 타입이 RDS(PostgreSQL/MySQL/MS-SQL)의 타입으로 변환될 때의 정밀도(Precision) 손실 여부 확인.
    *   RDS 인스턴스의 Parameter Group 설정과 소스 DB의 Collation/Character Set 일치 여부 검증.
*   **Fail-Safe:** 스키마 불일치 발견 시 즉시 프로세스 중단 및 `Schema-Mismatch-Report` 생성.

### [Stage 2] Quantitative Integrity (In-Migration)
*   **검증 대상:** Row Count, Object Count.
*   **시나리오:** 
    *   데이터 스트리밍 중 네트워크 패킷 손실로 인한 누락 확인.
    *   **Chunk-based Validation:** 대용량 데이터를 일정 단위(Chunk)로 나누어 이관할 때, 각 Chunk별로 Source와 Target의 Row Count를 실시간 비교.
*   **Fail-Safe:** Count 불일치 발생 시 해당 Chunk를 즉시 롤백하고 재시도(Retry) 로직 가동.

### [Stage 3] Qualitative Integrity (Post-Migration)
*   **검증 대상:** Data Content (Value-level), Checksum.
*   **시나리오:**
    *   **Hash-based Verification:** 주요 컬럼(PK 및 핵심 비즈니스 컬럼)의 값을 기반으로 `MD5/SHA-256` 해시값을 생성하여 Source와 Target의 해시값 일치 여부 비교.
    *   **Random Sampling Audit:** 전체 데이터 중 무작위 샘플을 추출하여 정밀 비교(Deep Dive) 수행.
*   **Fail-Safe:** Hash 불일치 시 `Data-Corruption-Alert` 발생 및 즉각적인 롤백 실행.

---

## 2. 'Zero-Risk' 브랜드 가치 증명을 위한 핵심 KPI

비즈니스 고객(Enterprise)에게 기술적 신뢰도를 숫자로 제시하여 'Zero-Risk'를 실체화합니다.

| KPI 지표 | 정의 | 목표치 (Target) | 비즈니스 의미 |
| :--- | :--- | :---: | :--- |
| **DIV Error Rate** | 전체 이관 데이터 중 무결성 오류가 발견된 비율 | **0.00%** | 'Zero-Risk' 브랜드의 핵심 근거 (데이터 무결성) |
| **Rollback Success Rate** | 장애 발생(Network/Storage) 시 자동 롤백 성공률 | **100%** | 시스템 안정성 및 데이터 오염 방지 능력 증명 |
| **Migration Drift Ratio** | 소스 데이터와 타겟 데이터 간의 미세한 값 차이 비율 | **0.00%** | 데이터 타입 변환 및 인코딩 정밀도 증명 |
| **RTO (Recovery Time Objective)** | 장애 발생 후 원상 복구(Rollback)까지 소요되는 시간 | **Minimization** | 비즈니스 연속성(BCP) 보장 능력 |

---

## 3. 비즈니스 실행 전략 (Action Plan)

1.  **Marketing Asset화:** 위 KPI 달성 수치를 'Migration Integrity Report'라는 형태의 결과물로 고객에게 제공하여, 단순 툴 사용을 넘어 '검증된 컨설팅'으로 포지셔닝함.
2.  **SaaS Pricing 연동:** 검증 단계(Stage 3)의 복잡도 및 데이터 용량에 따라 'Standard'와 'Premium(Full-Checksum)' 과금 모델로 분리하여 수익성 극대화.
3.  **Next Milestone:** M3 단계(MySQL/MS-SQL) 개발 시, 위에서 정의한 AWS RDS 전용 검증 로직을 어댑터 표준 인터페이스에 통합.

📝 다음 단계 제안: 위 검증 시나리오를 기반으로 한 `Automated Integrity Test Suite`의 요구사항 정의서(PRD) 작성 요청.
