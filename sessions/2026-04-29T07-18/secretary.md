# 📱 Secretary — M3 단계(MySQL, MS-SQL 확장)의 세부 작업 백로그를 작성하고, 각 작업별 마일스포트와 완료 정의(DoD)를 포함한 지시서를 생성할 것

📱 Secretary: 작업 시작합니다.

# 📋 [M3 단계] MySQL & MS-SQL 확장 작업 백로그 및 지시서

본 문서는 M2(PostgreSQL) 완료 후, 데이터시스의 'Zero-Risk' 가치를 유지하며 지원 데이터베이스 범위를 MySQL 및 MS-SQL로 확장하기 위한 세부 실행 계획입니다.

## 🎯 M3 목표
- **핵심 과제:** MySQL 및 MS-SQL 전용 어댑터 개발 및 통합 검증
- **기술적 목표:** 어댑터 패턴(Adapter Pattern)을 통한 DB 확장성 확보 및 3-Stage DIV(Data Integrity Verification) 엔진의 완벽한 이식

---

## 🛠 세부 작업 백로그 (Backlog)

### 1. [M3-A] MySQL Adapter 개발 및 검증
- **작업 내용:**
    - `MySQLAdapter` 클래스 구현 (mysql-connector-python 기반)
    - MySQL 전용 데이터 타입 매핑 로직 작성
    - MySQL 환경에서의 3-Stage DIV(Schema $\rightarrow$ Row Count $\rightarrow$ Content) 테스트
- **마일스톤:** M3-A (MySQL Integration Complete)
- **완료 정의 (DoD):**
    - [ ] MySQL DB 연결 및 세션 유지 확인
    - [ ] Oracle $\rightarrow$ MySQL 마이그레이션 시 데이터 무결성(DIV) 100% 일치
    - [ ] 대용량 데이터(100k+ rows) 처리 시 메모리 누수 없음 확인

### 2. [M3-B] MS-SQL Adapter 개발 및 검증
- **작업 내용:**
    - `MSSQLAdapter` 클래스 구현 (pyodbc 또는 pymssql 기반)
    - MS-SQL 특화 데이터 타입(datetime2, nvarchar 등) 매칭 로직 구현
    - MS-SQL 환경에서의 3-Stage DIV 엔진 작동 검증
- **마일스톤:** M3-B (MS-SQL Integration Complete)
- **완료 정의 (DoD):**
    - [ ] MS-SQL DB 연결 및 인증 프로세스 정상 작동
    - [ ] Oracle $\rightarrow$ MS-SQL 마이그레이션 시 데이터 무결성(DIV) 100% 일치
    - [ ] T-SQL 특화 문법 충돌 여부 검증 완료

### 3. [M3-C] 통합 어댑터 인터페이스 및 CLI 고도화
- **작업 내용:**
    - 모든 어댑터(Oracle, PostgreSQL, MySQL, MS-SQL)가 동일한 `BaseAdapter` 인터페이스를 준수하는지 검사
    - CLI 진입점에서 `--target` 옵션에 따른 어댑터 동적 로딩 로직 최적화
    - 통합 테스트 스위트(Integration Test Suite) 작성
- **마일스톤:** M3-C (Unified Engine Finalization)
- **완료 정의 (DoD):**
    - [ ] 단일 명령어로 4종의 모든 DB 대상 마이그레이션 시뮬레이션 성공
    - [ ] 새로운 DB 추가 시 코드 수정 최소화를 위한 어댑터 패턴 구조 검증 완료
    - [ ] 에러 발생 시 'Zero-Risk' 원칙에 따른 자동 롤백(Rollback) 작동 확인

### 4. [M3-D] 운영 문서화 및 SOP 업데이트
- **작업 내용:**
    - 확장된 DB 리스트를 포함한 `Migration Tool User Guide` 업데이트
    - 신규 어댑터 개발자를 위한 `Adapter Development SOP` 작성
- **마일스톤:** M3-D (Documentation & Handover)
- **완료 정의 (DoD):**
    - [ ] 모든 지원 DB별 환경 설정(Driver, Connection String) 가이드 포함
    - [ ] 개발자용 에러 핸들링 및 로그 모니터링 매뉴얼 완료

---

## ⚠️ 리스크 관리 지침 (CEO 지시 준수)
- **데이터 무결성 최우선:** 모든 작업의 핵심 KPI는 **'DIV(Data Integrity Verification) 100%'** 임.
- **Zero-Risk 유지:** 어댑터 확장 시 기존 Oracle/PostgreSQL 로직에 사이드 이펙트가 없는지 단위 테스트 필수 수행.
- **확장성 고려:** 향후 MariaDB, SQLite 등 추가 확장이 용이하도록 인터페이스 추상화 수준을 엄격히 유지할 것.

📝 다음 단계 제안: M3-A(MySQL Adapter) 개발을 위한 초기 환경 설정 및 `BaseAdapter` 인터페이스 설계 작업 착수 여부를 결정해 주세요.
