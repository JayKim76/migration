# 💰 Business — PostgreSQL DIV(Data Integrity Validation) 자동 검증을 위한 3단계(Metadata, Row Count, Data Content) 상세 검증 시나리오 및 성공/실패 판정 기준 초안을 작성하라.

💰 Business: 작업 시작합니다.

# 📊 PostgreSQL DIV(Data Integrity Validation) 3단계 검증 시/실패 시나리오 초안

본 시나리오는 데이터시스의 **'Zero-Risk'** 브랜드 가치를 실현하기 위한 핵심 기술 규격입니다. 모든 단계의 실패는 즉각적인 **Rollback** 및 **Critical Alert**를 발생시키며, 단계별 통과(Pass)가 선행되어야만 다음 단계로 진입합니다.

## 1단계: Metadata Validation (구조 무결성 검증)
**목적:** 소스(Oracle)와 타겟(PostgreSQL) 간의 스키마 일치성 확인 (Schema Drift 방지)

| 검증 항목 | 상세 검증 내용 | 성공(Pass) 기준 | 실패(Fail) 시 조치 |
| :--- | :--- | :--- | :--- |
| **Table Structure** | 테이블 명, 컬럼 명, 데이터 타입(Type) 일치 여부 | 100% 일치 | 즉시 중단 및 Schema Migration 에러 로그 생성 |
| **Constraints** | PK(Primary Key), FK(Foreign Key), Unique 제약 조건 확인 | 모든 제약 조건 전이 확인 | 제약 조건 누락 시 Rollback 및 구조 재설계 지시 |
| **Nullability** | 각 컬럼의 NULL 허용 여부 일치 확인 | Source/Target 동일 | 데이터 정합성 오류로 판단, 프로세스 중단 |
| **Precision/Scale** | Numeric, Decimal 등 소수점 정밀도 일치 여부 | 오차 범위 0 (Exact Match) | 데이터 손실(Truncation) 위험으로 판단, 중단 |

## 2단계: Row Count Validation (수량 무결성 검증)
**목적:** 데이터 누락(Data Loss) 여부의 정량적 확인

| 검증 항목 | 상세 검증 내용 | 성공(Pass) 기준 | 실패(Row Count Mismatch) 시 조치 |
| :--- | :--- | :--- | :--- |
| **Total Row Count** | 소스 테이블과 타겟 테이블의 전체 레코드 수 비교 | `Source Count == Target Count` | 즉시 중단 및 누락된 범위(Range) 식별 로직 가동 |
| **Partition/Index Count** | (Partition 테이블의 경우) 파티션별 레코드 수 비교 | 모든 파티션 합계 일치 | 특정 파티션 누락 여부 전수 조사 및 재전송 |
| **Zero-Record Check** | 데이터가 존재해야 할 테이블의 0건 여부 확인 | 0건인 테이블이 없어야 함 | 마이그레이션 실패로 간주, 즉각 Rollback |

## 3단계: Data Content Validation (내용 무결성 검증)
**목적:** 데이터 값의 실제 일치성 및 변형(Transformation) 여부 확인

| 검증 항목 | 상세 검증 내용 | 성공(Pass) 기준 | 실패(Data Mismatch) 시 조치 |
| :--- | :--- | :--- | :--- |
| **Checksum/Hash Verification** | 주요 컬럼(PK, Key Value) 기반의 MD5/SHA-256 해시값 비교 | `Source Hash == Target Hash` | 불일치 레코드 ID 추출 및 정밀 비교(Deep Dive) 모드 전환 |
| **Sample-based Deep Dive** | 무작위 샘플링(예: 5%)을 통한 전체 컬럼 값 전수 비교 | 샘플링 데이터 100% 일치 | 데이터 변형(Type Conversion Error) 원인 분석 및 재검증 |
| **Boundary Value Check** | 날짜(Date), 숫자(Numeric)의 경계값/최대/최소값 비교 | 소스/타겟 경계값 일치 | 데이터 잘림(Truncation) 또는 타입 변환 오류로 판단, 중단 |

---

## 🚀 비즈니스 임팩트 및 운영 전략

1.  **Zero-Risk 보증:** 1, 2단계 실패 시 3단계로 진입하지 않는 **'Fail-Fast'** 구조를 채택하여 리소스 낭비를 방지하고 데이터 오염을 원천 차단합니다.
2.  **SLA(Service Level Agreement) 기반:** 위 검증 결과는 고객사에게 **'Validation Report'** 형태로 자동 생성되어 제공되며, 이는 마이그레이션 성공의 법적/기술적 증거로 활용됩니다.
3.  **비용 최적화:** 대용량 테이블의 경우 3단계 전체 검증 대신 'Hash-based Sampling' 전략을 사용하여 검증 시간(Time-to-Verify)과 컴퓨팅 비용을 최적화합니다.

📝 다음 단계 제안: 위 시나리오를 기반으로 실제 Python 코드로 구현할 **'Validation Engine'의 에러 핸들링 및 Rollback 로직 설계**를 진행할까요?
