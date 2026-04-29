"""
Oracle Migration Tool - CLI 진입점

사용법:
  python main.py migrate                           # 전체 마이그레이션
  python main.py connect --type source             # Step 1: Source 접속 테스트
  python main.py connect --type target             # Step 1: Target 접속 테스트
  python main.py extract-ddl                       # Step 2: DDL 추출
  python main.py export [--method exp|expdp]       # Step 3: Export
  python main.py setup-target                      # Step 4-5: Target 환경 설정
  python main.py import [--method imp|impdp]       # Step 6-7: Import
  python main.py compare [--format md|html|both]   # Step 8: 비교 리포트
"""

import sys
import getpass

import click

from src.utils import load_config, ensure_dirs, get_password, print_header, print_step, print_ok, print_fail, logger
from src.connection import OracleConnection, connect_source, connect_target
from src.metadata import extract_metadata
from src.exporter import run_export
from src.target_setup import setup_target
from src.importer import run_import
from src.comparator import run_comparison


# ── 공통 옵션 ─────────────────────────────────────────────────────────────────

CONFIG_OPT = click.option(
    "--config", "-c",
    default="config/migration_config.yaml",
    show_default=True,
    help="설정 파일 경로",
)

THICK_OPT = click.option(
    "--thick",
    is_flag=True,
    default=False,
    help="Oracle Thick 모드 (Oracle Client 설치 필요)",
)


# ── CLI 그룹 ─────────────────────────────────────────────────────────────────

@click.group()
@click.version_option("1.0.0", prog_name="oracle-migration")
def cli():
    """Oracle Database Migration Tool"""


# ── connect ──────────────────────────────────────────────────────────────────

@cli.command("connect")
@CONFIG_OPT
@THICK_OPT
@click.option("--type", "db_type", type=click.Choice(["source", "target"]), default="source", show_default=True)
@click.option("--server-host", help="Server OS Host")
@click.option("--ssh-user", help="SSH Username")
@click.option("--ssh-password", help="SSH Password")
@click.option("--host", help="DB Host")
@click.option("--port", type=int, help="DB Port")
@click.option("--service-name", help="Service Name / SID")
@click.option("--username", help="DB Username")
@click.option("--password", help="DB Password")
def cmd_connect(config, thick, db_type, server_host, ssh_user, ssh_password, host, port, service_name, username, password):
    """Step 1: DB 접속 테스트."""
    cfg = load_config(config)
    ensure_dirs(cfg)
    section = cfg[db_type]
    
    # Override from CLI
    if server_host: section["server_host"] = server_host
    if ssh_user: section["ssh_user"] = ssh_user
    if ssh_password: section["ssh_password"] = ssh_password
    if host: section["host"] = host
    if port: section["port"] = port
    if service_name: section["service_name"] = service_name
    if username: section["username"] = username
    if password: section["password"] = password

    conn = OracleConnection(section, label=db_type.upper(), thick_mode=thick)
    ok = conn.test_connection()
    conn.close()
    sys.exit(0 if ok else 1)


# ── extract-ddl ──────────────────────────────────────────────────────────────

@cli.command("extract-ddl")
@CONFIG_OPT
@THICK_OPT
@click.option("--ddl-dir", help="DDL 파일 저장 디렉토리")
def cmd_extract_ddl(config, thick, ddl_dir):
    """Step 2: Source DB 메타정보 조회 및 DDL 추출."""
    cfg = load_config(config)
    if ddl_dir:
        cfg.setdefault("output", {})["ddl_dir"] = ddl_dir
        
    ensure_dirs(cfg)
    src_conn = OracleConnection(cfg["source"], label="SOURCE", thick_mode=thick)
    src_conn.connect()
    src_conn.get_db_info()
    try:
        extract_metadata(src_conn, cfg)
    finally:
        src_conn.close()


# ── export ───────────────────────────────────────────────────────────────────

@cli.command("export")
@CONFIG_OPT
@THICK_OPT
@click.option("--method", type=click.Choice(["exp", "expdp"]), default=None, help="exp 또는 expdp (설정 파일 우선)")
@click.option("--mode", type=click.Choice(["full", "schema", "table", "tablespace"]), default=None, help="Export 모드")
@click.option("--targets", default=None, help="선택한 모드에 따른 대상 (콤마 구분)")
@click.option("--directory", default=None, help="Oracle DIRECTORY 객체명")
@click.option("--dumpfile", default=None, help="덤프 파일명")
@click.option("--logfile", default=None, help="로그 파일명")
@click.option("--parallel", type=int, default=None, help="expdp 병렬도")
@click.option("--compression", type=click.Choice(["ALL", "METADATA_ONLY", "DATA_ONLY", "NONE"]), default=None, help="expdp 압축 옵션")
@click.option("--schemas", default=None, help="하위 호환용 스키마 목록")
@click.option("--consistent/--no-consistent", default=None, help="exp consistent 옵션")
# ── exp-only options ──────────────────────────────────────────────────────────
@click.option("--grants/--no-grants", default=None, help="exp: 권한 익스포트 (Y)")
@click.option("--indexes/--no-indexes", default=None, help="exp: 인덱스 익스포트 (Y)")
@click.option("--rows/--no-rows", default=None, help="exp: 데이터 행 익스포트 (Y)")
@click.option("--constraints/--no-constraints", default=None, help="exp: 제약조건 익스포트 (Y)")
@click.option("--triggers/--no-triggers", default=None, help="exp: 트리거 익스포트 (Y)")
@click.option("--direct/--no-direct", default=None, help="exp: Direct Path 사용 (N)")
@click.option("--buffer", type=int, default=None, help="exp: 데이터 버퍼 크기")
@click.option("--recordlength", type=int, default=None, help="exp: IO 레코드 길이")
@click.option("--inctype", default=None, help="exp: 증분 익스포트 타입")
@click.option("--record/--no-record", default=None, help="exp: 증분 익스포트 추적 (Y)")
@click.option("--statistics", type=click.Choice(["ESTIMATE", "COMPUTE", "NONE"]), default=None, help="exp: 통계 분석 (ESTIMATE)")
@click.option("--object-consistent/--no-object-consistent", default=None, help="exp: 객체 익스포트 중 read-only 트랜잭션")
@click.option("--feedback", type=int, default=None, help="exp: x행마다 진행률 출력 (0=비활성)")
@click.option("--resumable/--no-resumable", default=None, help="exp: 공간 오류 시 일시 중단")
@click.option("--resumable-name", default=None, help="exp: Resumable 구문 식별 문자열")
@click.option("--resumable-timeout", type=int, default=None, help="exp: Resumable 대기 시간")
@click.option("--tts-full-check/--no-tts-full-check", default=None, help="exp: TTS 전체/부분 의존성 검사")
@click.option("--volsize", default=None, help="exp: 테이프 볼륨당 바이트 수")
@click.option("--transport-tablespace/--no-transport-tablespace", default=None, help="exp: Transportable Tablespace 메타데이터 익스포트")
@click.option("--template", default=None, help="exp: iAS 모드 익스포트 템플릿명")
@click.option("--content", type=click.Choice(["ALL", "DATA_ONLY", "METADATA_ONLY"]), default=None, help="Export 내용")
@click.option("--exclude", default=None, help="제외할 객체 (예: STATISTICS)")
@click.option("--estimate-only", is_flag=True, default=False, help="실제 추출 없이 예상 크기만 확인")
@click.option("--estimate", type=click.Choice(["BLOCKS", "STATISTICS"]), default=None)
@click.option("--filesize", default=None)
@click.option("--flashback-scn", default=None)
@click.option("--flashback-time", default=None)
@click.option("--include", default=None)
@click.option("--network-link", default=None)
@click.option("--query", default=None)
@click.option("--remap-data", default=None)
@click.option("--reuse-dumpfiles", is_flag=True, default=False)
@click.option("--sample", default=None)
@click.option("--version", default=None)
@click.option("--cluster", is_flag=True, default=None)
@click.option("--encryption", type=click.Choice(["ALL", "DATA_ONLY", "ENCRYPTED_COLUMNS_ONLY", "METADATA_ONLY", "NONE"]), default=None)
@click.option("--encryption-algorithm", type=click.Choice(["AES128", "AES192", "AES256"]), default=None)
@click.option("--encryption-mode", type=click.Choice(["DUAL", "PASSWORD", "TRANSPARENT"]), default=None)
@click.option("--encryption-password", default=None)
@click.option("--job-name", default=None)
def cmd_export(config, thick, method, mode, targets, directory, dumpfile, logfile, parallel, compression, schemas, consistent, content, exclude, estimate_only,
               estimate, filesize, flashback_scn, flashback_time, include, network_link, query, remap_data, reuse_dumpfiles, sample, version, cluster,
               encryption, encryption_algorithm, encryption_mode, encryption_password, job_name,
               grants, indexes, rows, constraints, triggers, direct, buffer, recordlength, inctype, record, statistics, object_consistent,
               feedback, resumable, resumable_name, resumable_timeout, tts_full_check, volsize, transport_tablespace, template):
    """Step 3: Source DB Export (exp/expdp)."""
    cfg = load_config(config)
    ensure_dirs(cfg)
    
    exp_cfg = cfg.setdefault("export", {})
    if method: exp_cfg["method"] = method
    if mode: exp_cfg["mode"] = mode
    if targets: exp_cfg["targets"] = [t.strip() for t in targets.split(",") if t.strip()]
    if directory: exp_cfg["directory"] = directory
    if dumpfile: exp_cfg["dumpfile"] = dumpfile
    if logfile: exp_cfg["logfile"] = logfile
    if parallel is not None: exp_cfg["parallel"] = parallel
    if compression: exp_cfg["compression"] = compression
    if schemas: exp_cfg["schemas"] = [s.strip() for s in schemas.split(",") if s.strip()]
    if consistent is not None: exp_cfg["consistent"] = consistent
    if content: exp_cfg["content"] = content
    if exclude: exp_cfg["exclude"] = exclude
    if estimate_only: exp_cfg["estimate_only"] = True
    if estimate: exp_cfg["estimate"] = estimate
    if filesize: exp_cfg["filesize"] = filesize
    if flashback_scn: exp_cfg["flashback_scn"] = flashback_scn
    if flashback_time: exp_cfg["flashback_time"] = flashback_time
    if include: exp_cfg["include"] = include
    if network_link: exp_cfg["network_link"] = network_link
    if query: exp_cfg["query"] = query
    if remap_data: exp_cfg["remap_data"] = remap_data
    if reuse_dumpfiles: exp_cfg["reuse_dumpfiles"] = reuse_dumpfiles
    if sample: exp_cfg["sample"] = sample
    if version: exp_cfg["version"] = version
    if cluster is not None: exp_cfg["cluster"] = cluster
    if encryption: exp_cfg["encryption"] = encryption
    if encryption_algorithm: exp_cfg["encryption_algorithm"] = encryption_algorithm
    if encryption_mode: exp_cfg["encryption_mode"] = encryption_mode
    if encryption_password: exp_cfg["encryption_password"] = encryption_password
    if job_name: exp_cfg["job_name"] = job_name
    # exp-only
    if grants is not None: exp_cfg["grants"] = grants
    if indexes is not None: exp_cfg["indexes"] = indexes
    if rows is not None: exp_cfg["rows"] = rows
    if constraints is not None: exp_cfg["constraints"] = constraints
    if triggers is not None: exp_cfg["triggers"] = triggers
    if direct is not None: exp_cfg["direct"] = direct
    if buffer is not None: exp_cfg["buffer"] = buffer
    if recordlength is not None: exp_cfg["recordlength"] = recordlength
    if inctype: exp_cfg["inctype"] = inctype
    if record is not None: exp_cfg["record"] = record
    if statistics: exp_cfg["statistics"] = statistics
    if object_consistent is not None: exp_cfg["object_consistent"] = object_consistent
    if feedback is not None: exp_cfg["feedback"] = feedback
    if resumable is not None: exp_cfg["resumable"] = resumable
    if resumable_name: exp_cfg["resumable_name"] = resumable_name
    if resumable_timeout is not None: exp_cfg["resumable_timeout"] = resumable_timeout
    if tts_full_check is not None: exp_cfg["tts_full_check"] = tts_full_check
    if volsize: exp_cfg["volsize"] = volsize
    if transport_tablespace is not None: exp_cfg["transport_tablespace"] = transport_tablespace
    if template: exp_cfg["template"] = template


    password = get_password(cfg["source"], "SOURCE")
    src_conn = OracleConnection(cfg["source"], label="SOURCE", thick_mode=thick)
    src_conn.connect()
    try:
        ok = run_export(cfg, password, src_conn)
    finally:
        src_conn.close()
    sys.exit(0 if ok else 1)


# ── setup-target ─────────────────────────────────────────────────────────────

@cli.command("setup-target")
@CONFIG_OPT
@THICK_OPT
def cmd_setup_target(config, thick):
    """Step 4-5: Target 환경 체크 및 Tablespace/User 생성."""
    cfg = load_config(config)
    ensure_dirs(cfg)

    src_conn = OracleConnection(cfg["source"], label="SOURCE", thick_mode=thick)
    tgt_conn = OracleConnection(cfg["target"], label="TARGET", thick_mode=thick)
    src_conn.connect()
    src_conn.get_db_info()
    tgt_conn.connect()
    tgt_conn.get_db_info()

    try:
        # Step 2 결과 파일 경로를 meta dict에 설정
        ddl_dir = cfg.get("output", {}).get("ddl_dir", "output/ddl")
        meta = {
            "tablespace_ddl_path": f"{ddl_dir}/tablespace_ddl.sql",
            "user_ddl_path": f"{ddl_dir}/user_ddl.sql",
            "tablespace_info": [],
        }
        ok = setup_target(src_conn, tgt_conn, cfg, meta)
    finally:
        src_conn.close()
        tgt_conn.close()
    sys.exit(0 if ok else 1)


# ── import ───────────────────────────────────────────────────────────────────

@cli.command("import")
@CONFIG_OPT
@THICK_OPT
@click.option("--method", type=click.Choice(["imp", "impdp"]), default=None, help="imp 또는 impdp")
# ── impdp-specific options ────────────────────────────────────────────────────
@click.option("--mode", type=click.Choice(["full", "schema", "table", "tablespace"]), default=None)
@click.option("--targets", default=None, help="대상 목록 (콤마 구분)")
@click.option("--directory", default=None, help="Oracle DIRECTORY 객체명")
@click.option("--dumpfile", default=None, help="덤프 파일명")
@click.option("--logfile", default=None, help="로그 파일명")
@click.option("--parallel", type=int, default=None)
@click.option("--table-exists-action", type=click.Choice(["SKIP", "APPEND", "TRUNCATE", "REPLACE"]), default=None)
@click.option("--content", type=click.Choice(["ALL", "DATA_ONLY", "METADATA_ONLY"]), default=None)
@click.option("--exclude", default=None)
@click.option("--include", default=None)
@click.option("--query", default=None)
@click.option("--remap-schema", default=None, help="SOURCE:TARGET (콤마 구분 다중 가능)")
@click.option("--remap-tablespace", default=None, help="SOURCE:TARGET (콤마 구분 다중 가능)")
@click.option("--remap-datafile", default=None)
@click.option("--remap-data", default=None)
@click.option("--remap-table", default=None)
@click.option("--network-link", default=None)
@click.option("--flashback-scn", default=None)
@click.option("--flashback-time", default=None)
@click.option("--version", default=None)
@click.option("--job-name", default=None)
@click.option("--sqlfile", default=None, help="SQL DDL을 파일로 추출 (import 미실행)")
@click.option("--cluster", is_flag=True, default=None)
@click.option("--reuse-datafiles", is_flag=True, default=False)
@click.option("--skip-unusable-indexes", is_flag=True, default=False)
@click.option("--streams-configuration", is_flag=True, default=False)
@click.option("--transport-full-check", is_flag=True, default=False)
@click.option("--transport-tablespaces", default=None)
@click.option("--transport-datafiles", default=None)
@click.option("--encryption-password", default=None)
@click.option("--transform", default=None, help="예: SEGMENT_ATTRIBUTES:N")
@click.option("--status", type=int, default=None, help="Job 상태 모니터링 주기(초)")
def cmd_import(config, thick, method,
               mode, targets, directory, dumpfile, logfile, parallel, table_exists_action,
               content, exclude, include, query,
               remap_schema, remap_tablespace, remap_datafile, remap_data, remap_table,
               network_link, flashback_scn, flashback_time, version, job_name, sqlfile,
               cluster, reuse_datafiles, skip_unusable_indexes, streams_configuration,
               transport_full_check, transport_tablespaces, transport_datafiles,
               encryption_password, transform, status):
    """Step 6-7: Target DB Import (imp/impdp)."""
    cfg = load_config(config)
    ensure_dirs(cfg)

    imp_cfg = cfg.setdefault("import", {})
    if method:               imp_cfg["method"] = method
    if mode:                 imp_cfg["mode"] = mode
    if targets:              imp_cfg["targets"] = [t.strip() for t in targets.split(",") if t.strip()]
    if directory:            imp_cfg["directory"] = directory
    if dumpfile:             imp_cfg["dumpfile"] = dumpfile
    if logfile:              imp_cfg["logfile"] = logfile
    if parallel is not None: imp_cfg["parallel"] = parallel
    if table_exists_action:  imp_cfg["table_exists_action"] = table_exists_action
    if content:              imp_cfg["content"] = content
    if exclude:              imp_cfg["exclude"] = exclude
    if include:              imp_cfg["include"] = include
    if query:                imp_cfg["query"] = query
    if network_link:         imp_cfg["network_link"] = network_link
    if flashback_scn:        imp_cfg["flashback_scn"] = flashback_scn
    if flashback_time:       imp_cfg["flashback_time"] = flashback_time
    if version:              imp_cfg["version"] = version
    if job_name:             imp_cfg["job_name"] = job_name
    if sqlfile:              imp_cfg["sqlfile"] = sqlfile
    if cluster is not None:  imp_cfg["cluster"] = cluster
    if reuse_datafiles:      imp_cfg["reuse_datafiles"] = True
    if skip_unusable_indexes: imp_cfg["skip_unusable_indexes"] = True
    if streams_configuration: imp_cfg["streams_configuration"] = True
    if transport_full_check: imp_cfg["transport_full_check"] = True
    if transport_tablespaces: imp_cfg["transport_tablespaces"] = transport_tablespaces
    if transport_datafiles:  imp_cfg["transport_datafiles"] = transport_datafiles
    if encryption_password:  imp_cfg["encryption_password"] = encryption_password
    if transform:            imp_cfg["transform"] = transform
    if status is not None:   imp_cfg["status"] = status
    if remap_data:           imp_cfg["remap_data"] = remap_data
    if remap_table:          imp_cfg["remap_table"] = remap_table
    if remap_datafile:       imp_cfg["remap_datafile"] = remap_datafile
    # parse remap_schema / remap_tablespace as dict
    if remap_schema:
        for pair in remap_schema.split(","):
            if ":" in pair:
                src, tgt = pair.strip().split(":", 1)
                imp_cfg.setdefault("remap_schema", {})[src.strip()] = tgt.strip()
    if remap_tablespace:
        for pair in remap_tablespace.split(","):
            if ":" in pair:
                src, tgt = pair.strip().split(":", 1)
                imp_cfg.setdefault("remap_tablespace", {})[src.strip()] = tgt.strip()

    password = get_password(cfg["target"], "TARGET")
    ok = run_import(cfg, password)
    sys.exit(0 if ok else 1)



# ── compare ──────────────────────────────────────────────────────────────────

@cli.command("compare")
@CONFIG_OPT
@THICK_OPT
@click.option("--format", "fmt", type=click.Choice(["markdown", "html", "both"]), default=None)
@click.option("--output", "output_path", default=None, help="리포트 파일 저장 경로 (단일 파일)")
def cmd_compare(config, thick, fmt, output_path):
    """Step 8: Source-Target 비교 리포트 생성."""
    cfg = load_config(config)
    ensure_dirs(cfg)
    if fmt:
        cfg.setdefault("comparison", {})["output_format"] = fmt

    src_conn = OracleConnection(cfg["source"], label="SOURCE", thick_mode=thick)
    tgt_conn = OracleConnection(cfg["target"], label="TARGET", thick_mode=thick)
    src_conn.connect()
    src_conn.get_db_info()
    tgt_conn.connect()
    tgt_conn.get_db_info()

    try:
        results = run_comparison(src_conn, tgt_conn, cfg)
    finally:
        src_conn.close()
        tgt_conn.close()

    fail_cnt = sum(1 for r in results if r["status"] == "FAIL")
    sys.exit(0 if fail_cnt == 0 else 1)


# ── migrate (전체 파이프라인) ──────────────────────────────────────────────────

@cli.command("migrate")
@CONFIG_OPT
@THICK_OPT
@click.option("--skip-export", is_flag=True, help="Export 단계 건너뜀 (Dump 파일이 이미 있을 때)")
@click.option("--skip-import", is_flag=True, help="Import 단계 건너뜀")
@click.option("--skip-compare", is_flag=True, help="비교 단계 건너뜀")
def cmd_migrate(config, thick, skip_export, skip_import, skip_compare):
    """전체 마이그레이션 파이프라인 실행 (Step 1~8)."""
    cfg = load_config(config)
    ensure_dirs(cfg)

    print_header("Oracle Migration Tool — 전체 파이프라인 시작")

    # Step 1: Source 접속
    print_step(1, "Source Database 접속")
    src_conn = OracleConnection(cfg["source"], label="SOURCE", thick_mode=thick)
    if not src_conn.test_connection():
        print_fail("Source 접속 실패. 중단합니다.")
        sys.exit(1)

    # Step 2: 메타정보 조회 및 DDL 추출
    print_step(2, "Database 정보 조회 및 DDL 추출")
    src_conn.connect()
    src_conn.get_db_info()
    meta = extract_metadata(src_conn, cfg)

    # Step 3: Export
    if not skip_export:
        print_step(3, "Export (exp/expdp)")
        src_password = get_password(cfg["source"], "SOURCE")
        ok = run_export(cfg, src_password, src_conn)
        if not ok:
            print_fail("Export 실패. 중단합니다.")
            src_conn.close()
            sys.exit(1)

    src_conn.close()

    # Step 4: Target 접속
    print_step(4, "Target Database 접속")
    tgt_conn = OracleConnection(cfg["target"], label="TARGET", thick_mode=thick)
    if not tgt_conn.test_connection():
        print_fail("Target 접속 실패. 중단합니다.")
        sys.exit(1)
    tgt_conn.connect()
    tgt_conn.get_db_info()

    # Step 5: Target 환경 체크 및 Tablespace 생성
    print_step(5, "Target 환경 체크 및 Tablespace 생성")
    src_conn2 = OracleConnection(cfg["source"], label="SOURCE", thick_mode=thick)
    src_conn2.connect()
    src_conn2.get_db_info()
    setup_ok = setup_target(src_conn2, tgt_conn, cfg, meta)
    src_conn2.close()
    if not setup_ok:
        print_fail("Target 환경 설정 실패. 중단합니다.")
        tgt_conn.close()
        sys.exit(1)

    # Step 6-7: Import
    if not skip_import:
        print_step(6, "Import (imp/impdp)")
        tgt_password = get_password(cfg["target"], "TARGET")
        ok = run_import(cfg, tgt_password)
        if not ok:
            print_fail("Import 실패.")

    # Step 8: 비교
    if not skip_compare:
        print_step(8, "Source-Target 비교")
        src_conn3 = OracleConnection(cfg["source"], label="SOURCE", thick_mode=thick)
        src_conn3.connect()
        src_conn3.get_db_info()
        results = run_comparison(src_conn3, tgt_conn, cfg)
        src_conn3.close()

    tgt_conn.close()
    print_ok("전체 마이그레이션 파이프라인 완료")


# ── 엔트리포인트 ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()
