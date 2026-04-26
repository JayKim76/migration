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
def cmd_connect(config, thick, db_type):
    """Step 1: DB 접속 테스트."""
    cfg = load_config(config)
    ensure_dirs(cfg)
    section = cfg[db_type]
    conn = OracleConnection(section, label=db_type.upper(), thick_mode=thick)
    ok = conn.test_connection()
    conn.close()
    sys.exit(0 if ok else 1)


# ── extract-ddl ──────────────────────────────────────────────────────────────

@cli.command("extract-ddl")
@CONFIG_OPT
@THICK_OPT
def cmd_extract_ddl(config, thick):
    """Step 2: Source DB 메타정보 조회 및 DDL 추출."""
    cfg = load_config(config)
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
def cmd_export(config, thick, method):
    """Step 3: Source DB Export (exp/expdp)."""
    cfg = load_config(config)
    ensure_dirs(cfg)
    if method:
        cfg["export"]["method"] = method

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
def cmd_import(config, thick, method):
    """Step 6-7: Target DB Import (imp/impdp)."""
    cfg = load_config(config)
    ensure_dirs(cfg)
    if method:
        cfg["import"]["method"] = method

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
