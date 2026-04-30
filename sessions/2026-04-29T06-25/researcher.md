# 🔍 Researcher — 3단계 DIV(Structural, Content, Statistical)의 세부 검증 알고리즘과 신규 어댑터(PostgreSQL 등) 구현을 위한 인터페이스 표준 규격을 정의하라.

🔍 Researcher: 작업 시작합니다.

# 📋 3단계 DIV 알고리즘 및 어댑터 표준 규격 정의서

본 문서는 'Zero-Risk' 브랜드 가치를 기술적으로 뒷받연하기 위한 **데이터 무결성 검증(DIV) 상세 로직**과 확장성을 위한 **어댑터 인터페이스 규격**을 정의합니다.

---

## 1. 3단계 DIV(Data Integrity Verification) 세부 알고리즘

모든 검증은 **Fail-Fast** 원칙을 따르며, 하위 단계에서 오류 발생 시 즉시 중단하고 롤백 프로세스를 트리거합니다.

### 1단계: Structural Validation (구조 검증)
*목표: Source와 Target의 스키마(Metadata) 일치 여부 확인*
- **[Algorithm 1.1] Schema Mapping Check**: 
    - 대상: Table Name, Column Name, Data Type, Nullable, Primary Key, Foreign Key.
    - 로직: Source의 메타데이터를 추출하여 Target의 메타데이터와 `Set` 비교 연산 수행.
- **[Algorithm 1.2] Constraint Integrity Check**:
    - 대상: Unique Constraints, Check Constraints.
    - 로직: 제약 조건의 누락 여부를 확인하여 데이터 유실 및 부정합 방지.

### 2단계: Content Validation (내용 검증)
*목표: 실제 데이터 레코드의 일치 여부 확인 (샘플링 및 해시 기반)*
- **[Algorithm 2.1] Row Count Verification**:
    - 로직: `SELECT COUNT(*)`를 통해 양측의 총 레코드 수 비교. (가장 기본적이며 필수적인 단계)
- **[Algorithm 2.2] Data Sampling Hash Check**:
    - 로직: 전체 데이터를 비교하기 어려운 대용량의 경우, 특정 컬럼(PK 기반)의 샘플을 추출하여 `SHA-256` 해시값 비교.
    - 방식: `Hash(Column_A + Column_B + ...)` → Source Hash vs Target Hash.
- **[Algorithm 2.3] Null/Empty Value Check**:
    - 로직: 특정 컬럼의 Null 발생 빈도 및 빈 문자열(`''`) 분포 비교.

### 3단계: Statistical Validation (통계 검증)
*목표: 수치 데이터의 집계값 일치 여부 확인 (대량 데이터의 최종 검증)*
- **[Algorithm 3.1] Numeric Aggregation Check**:
    - 대상: Numeric, Float, Decimal 타입 컬럼.
    - 로직: `SUM()`, `AVG()`, `MIN()`, `MAX()` 연산 결과값의 오차 범위(Epsilon) 내 일치 여부 확인.
- **[Algorithm 3.2] Distinct Value Distribution**:
    - 대상: Categorical(String, Enum) 타입 컬럼.
    - 로직: `COUNT(DISTINCT column_name)`를 통해 범주형 데이터의 분포 일치 여부 확인.

---

## 2. 신규 어댑터(PostgreSQL 등) 인터페이스 표준 규격

모든 신규 어댑터는 `BaseAdapter` 추상 클래스를 상속받아 동일한 메서드 시그니처를 유지해야 합니다.

### [Interface: `BaseAdapter` (Abstract Base Class)]

| 메서드명 | 반환 타입 | 설명 | 필수 구현 사항 |
| :---            | :---        | :--- | :--- |
| `connect()` | `bool` | 데이터베이스 연결 수행 | Connection Pool 관리 및 에러 핸들링 |
| `get_schema()` | `Dict[str, Any]` | 테이블/컬럼 메타데이터 반환 | `{'tables': [{'name': '...', 'columns': [...]}]}` |
| `get_row_count(table_name)` | `int` | 특정 테이블의 전체 행 수 반환 | `SELECT COUNT(*)` 쿼리 실행 |
| `get_aggregate_stats(table_name, columns)` | `Dict[str, float]` | 지정된 컬럼의 통계값(SUM, AVG 등) 반환 | `SUM`, `AVG` 등 집계 쿼리 실행 |
| `get_sample_hash(table_name, sample_size)` | `str` | 샘플링된 데이터의 해시값 반환 | 샘플링 쿼리 + 해시 연산 |
| `execute_query(query)` | `List[Dict]` | 임의의 SQL 실행 및 결과 반환 | 쿼리 실행 및 결과의 Dictionary 변환 |
| `close()` | `None` | 연결 종료 및 리소스 해제 | `connection.close()` 호출 보장 |

### [Standardized Output Format (JSON/Dict)]
모든 어댑터의 `get_schema` 결과는 아래 형식을 준수합니다.
```json
{
  "metadata": {
    "database_type": "postgresql",
    "timestamp": "2026-04-29T10:00:00Z"
  },
  "tables": [
    {
      "table_name": "users",
      "columns": [
        {"name": "id", "type": "integer", "nullable": false, "is_pk": true},
        {"name": "email", "type": "varchar", "nullable": false, "is_pk": false}
      ]
    }
  ]
}
```

---

## 3. 구현 가이드라인 (Developer Note)

1.  **Error Handling**: 모든 어댑터는 `MigrationError` 커스텀 예외를 던져야 하며, 에러 발생 시 반드시 `close()`가 호출되도록 `try-finally` 또는 `contextmanager`를 사용한다.
2.  **Scalability**: `PostgreSQLAdapter`, `MySQLAdapter
