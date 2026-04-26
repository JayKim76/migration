# Oracle Migration Tool

Oracle DB를 Source에서 Target으로 마이그레이션하는 Python CLI 도구입니다.

## 기술 스택
- Python 3.10+
- python-oracledb (Thin 모드 기본, Oracle Client 설치 불필요)
- Click CLI

## 프로젝트 구조

```
migration/
├── docs/
│   └── maintenance_guide.md    # 단계별 유지보수 가이드 [NEW]
├── dashboard/
│   ├── index.html               # 시각화 대시보드 [NEW]
│   └── ...
├── src/
│   ├── connection.py            # Step 1: DB 접속
│   ├── metadata.py              # Step 2: 메타정보 & DDL 추출
│   ├── exporter.py              # Step 3: exp/expdp Export
│   ├── target_setup.py          # Step 4-5: Target 환경 설정
│   ├── importer.py              # Step 6-7: imp/impdp Import
│   ├── comparator.py            # Step 8: 비교 리포트
│   └── utils.py                 # 공통 유틸리티
├── output/
│   ├── ddl/                     # 추출된 DDL 스크립트
│   ├── dumps/                   # Dump 파일
│   ├── reports/                 # 비교 리포트 (MD + HTML)
│   └── logs/                    # 실행 로그
├── main.py                      # CLI 진입점
└── requirements.txt
```

## 설치

```bash
cd d:\AI\migration
pip install -r requirements.txt
```

## 설정

`config/migration_config.yaml` 파일을 수정합니다.

```yaml
source:
  host: "192.168.1.100"
  port: 1521
  service_name: "ORCL"
  username: "system"
  password: ""          # 비워두면 실행 시 입력 요청

target:
  host: "192.168.1.200"
  ...

export:
  method: "expdp"       # "exp" 또는 "expdp"
  schemas: ["HR", "SCOTT"]

import:
  method: "impdp"
  remap_tablespace: {}  # {SOURCE_TS: TARGET_TS}
```

## 사용법

### 전체 마이그레이션 (Step 1~8 자동 실행)

```bash
python main.py migrate
python main.py migrate --config config/my_config.yaml
python main.py migrate --skip-export   # Dump 파일이 이미 있을 때
```

### 단계별 실행

```bash
# Step 1: DB 접속 테스트
python main.py connect --type source
python main.py connect --type target

# Step 2: DDL 추출
python main.py extract-ddl

# Step 3: Export
python main.py export --method expdp
python main.py export --method exp

# Step 4-5: Target 환경 설정
python main.py setup-target

# Step 6-7: Import
python main.py import --method impdp
python main.py import --method imp

# Step 8: 비교 리포트
python main.py compare --format both
python main.py compare --format html
```

### Thick 모드 (Oracle Client 사용)

```bash
python main.py migrate --thick
```

## 출력물

| 경로 | 내용 |
|------|------|
| `output/ddl/tablespace_ddl.sql` | Tablespace 생성 DDL |
| `output/ddl/user_ddl.sql` | 사용자/권한 DDL |
| `output/dumps/*.par` | Export/Import 파라미터 파일 |
| `output/reports/comparison_*.md` | 비교 리포트 (Markdown) |
| `output/reports/comparison_*.html` | 비교 리포트 (HTML) |
| `output/logs/*.log` | 실행 로그 |

## exp vs expdp 비교

| 항목 | exp (전통) | expdp (Data Pump) |
|------|-----------|-------------------|
| 속도 | 느림 | 빠름 (병렬 지원) |
| 파일 위치 | 클라이언트 로컬 | 서버 (DIRECTORY 객체) |
| 압축 | 미지원 | 지원 (COMPRESSION=ALL) |
| 권장 환경 | 소규모/레거시 | 대규모/운영 |

## 주의 사항

- **expdp/impdp** 사용 시 Oracle DIRECTORY 객체가 Target 서버에 필요합니다.
- Target DB 버전은 Source와 같거나 높아야 합니다.
- Character Set 불일치 시 데이터 깨짐이 발생할 수 있습니다.
- DBA 권한이 있는 계정으로 실행하는 것을 권장합니다.
