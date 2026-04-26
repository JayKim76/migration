# Oracle Migration Tool Maintenance Guide

이 문서는 Oracle Migration Tool의 각 단계별 동작 원리와 유지보수를 위한 기술 정보를 담고 있습니다.

## 📂 프로젝트 구조 및 핵심 파일

- `main.py`: CLI 진입점 및 전체 파이프라인 제어
- `config/migration_config.yaml`: 모든 설정의 중심 (DB 접속, 옵션 등)
- `src/`: 각 단계별 로직 모듈
- `dashboard/`: 시각화 대시보드 (Frontend)

---

## 🛠 단계별 상세 기술 설명

### Step 1: Connectivity (접속 테스트)
- **목적**: Source 및 Target DB와의 물리적(Server) 및 논리적(Database) 연결 확인.
- **관련 파일**: `src/connection.py`, `main.py` (cmd_connect), `dashboard/index.html`, `config/migration_config.yaml`
- **동작 원리**: 
    - **Server Info**: Linux 서버 IP (`server_host`) 및 SSH 계정 (`ssh_user`) 정보를 통해 OS 레벨 접근성 확인.
    - **Oracle DB Info**: Service Name, Port, User 정보를 통해 DB 레벨 접속 테스트.
    - `python-oracledb` 라이브러리를 사용하여 접속 시도.
- **유지보수 포인트**:
    - 새로운 DB 버전 대응 시 접속 파라미터(Easy Connect Plus 등) 업데이트.
    - 보안 정책에 따른 Wallet 접속 기능 추가 필요 시 `OracleConnection` 클래스 수정.

### Step 2: DDL Extraction (메타데이터 추출)
- **목적**: 데이터 마이그레이션 전 필요한 객체(Tablespace, User)의 DDL 추출.
- **관련 파일**: `src/metadata.py`
- **동작 원리**:
    - `DBMS_METADATA.GET_DDL` 패키지를 호출하여 SQL 스크립트 생성.
    - `output/ddl/` 폴더에 `tablespace_ddl.sql`, `user_ddl.sql` 등으로 저장.
- **유지보수 포인트**:
    - 인덱스, 뷰, 프로시저 등 추가 객체 추출 필요 시 쿼리 확장.
    - 소스 DB 버전별 `GET_DDL` 파라미터 차이 확인.

### Step 3: Export (데이터 추출)
- **목적**: 데이터를 덤프 파일(.dmp) 형태로 로컬 또는 서버에 저장.
- **관련 파일**: `src/exporter.py`
- **동작 원리**:
    - 설정값에 따라 전통적인 `exp` 또는 현대적인 `expdp` 명령어 실행.
    - `expdp` 사용 시 서버 내 `DIRECTORY` 객체 권한 확인 필수.
- **유지보수 포인트**:
    - 대용량 데이터 대응을 위한 `PARALLEL` 옵션 튜닝.
    - `COMPRESSION` 옵션 적용을 통한 덤프 파일 크기 최적화.

### Step 4 & 5: Target Setup (환경 설정)
- **목적**: 추출된 DDL을 Target DB에 실행하여 구조 생성.
- **관련 파일**: `src/target_setup.py`
- **동작 원리**:
    - Step 2에서 생성된 SQL 파일을 읽어 Target DB에서 순차적 실행.
    - Tablespace 생성 -> User 생성 -> 권한 부여 순서 보장.
- **유지보수 포인트**:
    - 소스와 타겟의 경로명이 다를 경우 `REMAP_DATAFILE` 로직 확인.
    - 이미 존재하는 객체에 대한 에러 핸들링 (Ignore vs Error).

### Step 6 & 7: Import (데이터 주입)
- **목적**: 덤프 파일을 Target DB에 로드.
- **관련 파일**: `src/importer.py`
- **동작 원리**:
    - `imp` 또는 `impdp` 명령어 실행.
    - `REMAP_SCHEMA`, `REMAP_TABLESPACE` 옵션을 통한 유연한 마이그레이션 지원.
- **유지보수 포인트**:
    - 데이터 정합성을 위한 `CONSTRAINTS=N` -> `Y` 순서 제어.
    - 인덱스 재생성 시점 조절 (Import 중 vs Import 후).

### Step 8: Validation (데이터 검증)
- **목적**: 소스와 타겟 간의 객체 수 및 데이터 건수 비교.
- **관련 파일**: `src/comparator.py`
- **동작 원리**:
    - `USER_TABLES`, `USER_INDEXES` 등 딕셔너리 뷰를 조회하여 수치 비교.
    - HTML 및 Markdown 형식의 리포트 자동 생성 (`output/reports/`).
- **유지보수 포인트**:
    - 중요 테이블에 대한 Hash Checksum 비교 기능 추가.
    - 리포트 디자인 변경 시 `comparator.py` 내 HTML 템플릿 수정.

---

## 📑 대시보드 유지보수 (dashboard/)

- **UI 수정**: `dashboard/style.css`에서 `--accent-cyan` 등의 CSS 변수를 수정하여 테마 변경 가능.
- **단계 추가**: `dashboard/index.html`에 새로운 `<section>`을 추가하고 `script.js`의 `stepData` 객체를 업데이트.
- **이미지 변경**: `dashboard/assets/` 폴더의 이미지를 동일한 파일명으로 교체.

---

## ⚠️ 트러블슈팅 가이드

1. **접속 실패**: 방화벽 확인 및 `listener.ora` 설정 확인.
2. **Export 권한 부족**: `EXP_FULL_DATABASE` 롤 부여 여부 확인.
3. **Tablespace 용량 부족**: Target DB의 Datafile `AUTOEXTEND` 설정 확인.
4. **한글 깨짐**: 소스/타겟 DB의 `NLS_CHARACTERSET` 일치 여부 확인.
