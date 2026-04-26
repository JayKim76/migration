"""
Step 6-7: Dump File Restore - imp / impdp 선택 실행

- impdp: Oracle Data Pump Import (권장)
- imp: 전통적 Import (레거시)
- 파라미터 파일 자동 생성
- REMAP_TABLESPACE / REMAP_SCHEMA 지원
- 오류 분류 및 로그 요약
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from src.utils import (
    logger,
    print_header,
    print_info,
    print_ok,
    print_fail,
    print_warn,
    write_text_file,
    timestamp_str,
)

if TYPE_CHECKING:
    from src.connection import OracleConnection


# ── Dump 파일 목록 확인 ───────────────────────────────────────────────────────

def list_dumpfiles(dump_dir: str, pattern: str = "*.dmp") -> list[str]:
    """dump_dir 에서 .dmp 파일 목록을 반환한다."""
    files = sorted(Path(dump_dir).glob(pattern))
    return [str(f) for f in files]


# ── 파라미터 파일 생성 ────────────────────────────────────────────────────────

def build_impdp_parfile(cfg: dict, password: str) -> tuple[str, str]:
    """
    impdp 파라미터 파일 내용과 저장 경로를 반환한다.
    반환: (parfile_content, parfile_path)
    """
    imp_cfg = cfg.get("import", {})
    exp_cfg = cfg.get("export", {})
    dump_dir = cfg.get("output", {}).get("dump_dir", "output/dumps")

    schemas = ",".join(exp_cfg.get("schemas", []))
    directory = imp_cfg.get("directory", exp_cfg.get("directory", "DATA_PUMP_DIR"))
    dumpfile = imp_cfg.get("dumpfile", exp_cfg.get("dumpfile", "migration_%U.dmp"))
    logfile = imp_cfg.get("logfile", "import.log")
    parallel = imp_cfg.get("parallel", 4)
    table_exists = imp_cfg.get("table_exists_action", "REPLACE")

    lines = [
        f"SCHEMAS={schemas}",
        f"DIRECTORY={directory}",
        f"DUMPFILE={dumpfile}",
        f"LOGFILE={logfile}",
        f"PARALLEL={parallel}",
        f"TABLE_EXISTS_ACTION={table_exists}",
    ]

    # REMAP_TABLESPACE
    remap_ts = imp_cfg.get("remap_tablespace", {})
    for src_ts, tgt_ts in remap_ts.items():
        lines.append(f"REMAP_TABLESPACE={src_ts}:{tgt_ts}")

    # REMAP_SCHEMA
    remap_sc = imp_cfg.get("remap_schema", {})
    for src_sc, tgt_sc in remap_sc.items():
        lines.append(f"REMAP_SCHEMA={src_sc}:{tgt_sc}")

    content = "\n".join(lines)
    ts = timestamp_str()
    parfile_path = str(Path(dump_dir) / f"impdp_{ts}.par")
    return content, parfile_path


def build_imp_parfile(cfg: dict, password: str) -> tuple[str, str]:
    """
    imp(전통) 파라미터 파일 내용과 저장 경로를 반환한다.
    반환: (parfile_content, parfile_path)
    """
    imp_cfg = cfg.get("import", {})
    exp_cfg = cfg.get("export", {})
    dump_dir = cfg.get("output", {}).get("dump_dir", "output/dumps")

    schemas = exp_cfg.get("schemas", [])
    fromuser = ",".join(schemas)

    # remap_schema 없으면 fromuser = touser
    remap_sc = imp_cfg.get("remap_schema", {})
    touser = ",".join(remap_sc.get(s, s) for s in schemas)

    # 가장 최근 .dmp 파일 사용
    dmp_files = list_dumpfiles(dump_dir)
    dumpfile = dmp_files[-1] if dmp_files else str(Path(dump_dir) / "migration.dmp")

    ts = timestamp_str()
    logfile = str(Path(dump_dir) / f"import_{ts}.log")

    lines = [
        f"FROMUSER={fromuser}",
        f"TOUSER={touser}",
        f"FILE={dumpfile}",
        f"LOG={logfile}",
        "IGNORE=Y",
        "GRANTS=Y",
        "INDEXES=Y",
        "ROWS=Y",
        "CONSTRAINTS=Y",
    ]

    content = "\n".join(lines)
    parfile_path = str(Path(dump_dir) / f"imp_{ts}.par")
    return content, parfile_path


# ── 명령 실행 헬퍼 ────────────────────────────────────────────────────────────

def _run_oracle_cmd(cmd: list[str], log_path: str) -> tuple[bool, list[str]]:
    """
    Oracle 유틸리티를 실행하고 (성공여부, 오류라인목록)을 반환한다.
    """
    logger.debug(f"실행 명령: {' '.join(cmd)}")
    print_info(f"명령 실행: {cmd[0]}")
    print_info(f"로그 파일: {log_path}")

    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    error_lines = []

    with open(log_path, "w", encoding="utf-8") as log_f:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        for line in proc.stdout:
            line = line.rstrip()
            log_f.write(line + "\n")
            log_f.flush()
            if line:
                print(f"    {line}")
            # 오류 라인 수집
            low = line.lower()
            if any(kw in low for kw in ("ora-", "imp-", "imp:", "error", "failed")):
                error_lines.append(line)
        proc.wait()

    success = proc.returncode == 0
    return success, error_lines


# ── 오류 요약 ────────────────────────────────────────────────────────────────

def summarize_errors(error_lines: list[str], log_path: str):
    """
    Import 오류 라인을 분류하고 요약 출력한다.
    """
    if not error_lines:
        print_ok("오류 없음")
        return

    from collections import Counter
    # ORA-XXXXX 코드별 집계
    codes = Counter()
    for line in error_lines:
        import re
        m = re.search(r"(ORA-\d+|IMP-\d+)", line.upper())
        if m:
            codes[m.group(1)] += 1

    print_warn(f"오류 라인 {len(error_lines)}건 발견:")
    for code, cnt in codes.most_common(10):
        print_warn(f"  {code}: {cnt}건")
    print_info(f"전체 오류 상세: {log_path}")


# ── impdp 실행 ───────────────────────────────────────────────────────────────

def run_impdp(cfg: dict, password: str) -> bool:
    """impdp(Data Pump Import)를 실행한다."""
    print_header("Step 6-7: Data Pump Import (impdp)")

    imp_cfg = cfg.get("import", {})
    tgt_cfg = cfg.get("target", {})
    dump_dir = cfg.get("output", {}).get("dump_dir", "output/dumps")
    Path(dump_dir).mkdir(parents=True, exist_ok=True)

    parfile_content, parfile_path = build_impdp_parfile(cfg, password)
    write_text_file(parfile_path, parfile_content)
    print_info(f"파라미터 파일: {parfile_path}")

    dsn = f"{tgt_cfg['host']}:{tgt_cfg.get('port',1521)}/{tgt_cfg['service_name']}"
    user_pass = f"{tgt_cfg['username']}/{password}@{dsn}"
    ts = timestamp_str()
    log_path = str(Path(dump_dir) / f"impdp_run_{ts}.log")

    cmd = ["impdp", user_pass, f"PARFILE={parfile_path}"]
    success, error_lines = _run_oracle_cmd(cmd, log_path)
    summarize_errors(error_lines, log_path)

    if success:
        print_ok("Import 완료")
    else:
        print_fail(f"Import 실패 — 로그 확인: {log_path}")
    return success


# ── imp 실행 ─────────────────────────────────────────────────────────────────

def run_imp(cfg: dict, password: str) -> bool:
    """전통적 imp를 실행한다."""
    print_header("Step 6-7: Traditional Import (imp)")

    tgt_cfg = cfg.get("target", {})
    dump_dir = cfg.get("output", {}).get("dump_dir", "output/dumps")
    Path(dump_dir).mkdir(parents=True, exist_ok=True)

    parfile_content, parfile_path = build_imp_parfile(cfg, password)
    write_text_file(parfile_path, parfile_content)
    print_info(f"파라미터 파일: {parfile_path}")

    dsn = f"{tgt_cfg['host']}:{tgt_cfg.get('port',1521)}/{tgt_cfg['service_name']}"
    user_pass = f"{tgt_cfg['username']}/{password}@{dsn}"
    ts = timestamp_str()
    log_path = str(Path(dump_dir) / f"imp_run_{ts}.log")

    cmd = ["imp", user_pass, f"PARFILE={parfile_path}"]
    success, error_lines = _run_oracle_cmd(cmd, log_path)
    summarize_errors(error_lines, log_path)

    if success:
        print_ok("Import 완료")
    else:
        print_fail(f"Import 실패 — 로그 확인: {log_path}")
    return success


# ── 진입점 ───────────────────────────────────────────────────────────────────

def run_import(cfg: dict, password: str) -> bool:
    """설정의 method에 따라 impdp 또는 imp를 실행한다."""
    method = cfg.get("import", {}).get("method", "impdp").lower()
    if method == "impdp":
        return run_impdp(cfg, password)
    elif method == "imp":
        return run_imp(cfg, password)
    else:
        print_fail(f"알 수 없는 import method: {method} (impdp 또는 imp)")
        return False
