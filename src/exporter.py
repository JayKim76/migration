"""
Step 3: Export - exp / expdp 선택 실행

- expdp: Oracle Data Pump (권장, 병렬/압축 지원)
- exp: 전통적 Export (레거시/소규모 환경)
- 파라미터 파일(.par) 자동 생성
- expdp Job 진행률 실시간 모니터링
"""

from __future__ import annotations

import os
import subprocess
import time
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


# ── 파라미터 파일 생성 ────────────────────────────────────────────────────────

def build_expdp_parfile(cfg: dict, password: str) -> tuple[str, str]:
    """
    expdp 파라미터 파일 내용과 저장 경로를 반환한다.
    반환: (parfile_content, parfile_path)
    """
    exp_cfg = cfg.get("export", {})
    src_cfg = cfg.get("source", {})
    dump_dir = cfg.get("output", {}).get("dump_dir", "output/dumps")

    mode = exp_cfg.get("mode", "schema").lower()
    # 하위 호환성을 위해 schemas도 확인
    targets = ",".join(exp_cfg.get("targets", exp_cfg.get("schemas", [])))
    
    directory = exp_cfg.get("directory", "DATA_PUMP_DIR")
    dumpfile = exp_cfg.get("dumpfile", "migration_%U.dmp")
    logfile = exp_cfg.get("logfile", "export.log")
    parallel = exp_cfg.get("parallel", 4)
    compression = exp_cfg.get("compression", "ALL")
    content_opt = exp_cfg.get("content")
    exclude = exp_cfg.get("exclude")
    estimate_only = exp_cfg.get("estimate_only", False)

    lines = []
    if mode == "full":
        lines.append("FULL=Y")
    elif mode == "schema":
        lines.append(f"SCHEMAS={targets}")
    elif mode == "table":
        lines.append(f"TABLES={targets}")
    elif mode == "tablespace":
        lines.append(f"TABLESPACES={targets}")

    lines.extend([
        f"DIRECTORY={directory}",
        f"DUMPFILE={dumpfile}",
        f"LOGFILE={logfile}",
        f"PARALLEL={parallel}",
        f"COMPRESSION={compression}",
    ])

    if content_opt:
        lines.append(f"CONTENT={content_opt}")
    if exclude:
        lines.append(f"EXCLUDE={exclude}")
    if estimate_only:
        lines.append("ESTIMATE_ONLY=Y")
    
    # New Advanced Options
    if exp_cfg.get("estimate"): lines.append(f"ESTIMATE={exp_cfg['estimate']}")
    if exp_cfg.get("filesize"): lines.append(f"FILESIZE={exp_cfg['filesize']}")
    if exp_cfg.get("flashback_scn"): lines.append(f"FLASHBACK_SCN={exp_cfg['flashback_scn']}")
    if exp_cfg.get("flashback_time"): lines.append(f"FLASHBACK_TIME={exp_cfg['flashback_time']}")
    if exp_cfg.get("include"): lines.append(f"INCLUDE={exp_cfg['include']}")
    if exp_cfg.get("network_link"): lines.append(f"NETWORK_LINK={exp_cfg['network_link']}")
    if exp_cfg.get("query"): lines.append(f"QUERY={exp_cfg['query']}")
    if exp_cfg.get("remap_data"): lines.append(f"REMAP_DATA={exp_cfg['remap_data']}")
    if exp_cfg.get("reuse_dumpfiles"): lines.append("REUSE_DUMPFILES=Y")
    if exp_cfg.get("sample"): lines.append(f"SAMPLE={exp_cfg['sample']}")
    if exp_cfg.get("version"): lines.append(f"VERSION={exp_cfg['version']}")
    if exp_cfg.get("cluster") is not None: lines.append(f"CLUSTER={'Y' if exp_cfg['cluster'] else 'N'}")
    if exp_cfg.get("encryption"): lines.append(f"ENCRYPTION={exp_cfg['encryption']}")
    if exp_cfg.get("encryption_algorithm"): lines.append(f"ENCRYPTION_ALGORITHM={exp_cfg['encryption_algorithm']}")
    if exp_cfg.get("encryption_mode"): lines.append(f"ENCRYPTION_MODE={exp_cfg['encryption_mode']}")
    if exp_cfg.get("encryption_password"): lines.append(f"ENCRYPTION_PASSWORD={exp_cfg['encryption_password']}")
    if exp_cfg.get("job_name"): lines.append(f"JOB_NAME={exp_cfg['job_name']}")


    content = "\n".join(lines)
    ts = timestamp_str()
    parfile_path = str(Path(dump_dir) / f"expdp_{ts}.par")
    return content, parfile_path


def build_exp_parfile(cfg: dict, password: str) -> tuple[str, str]:
    """
    exp(전통) 파라미터 파일 내용과 저장 경로를 반환한다.
    반환: (parfile_content, parfile_path)
    """
    exp_cfg = cfg.get("export", {})
    dump_dir = cfg.get("output", {}).get("dump_dir", "output/dumps")

    schemas = ",".join(exp_cfg.get("schemas", exp_cfg.get("targets", [])))
    ts = timestamp_str()
    dumpfile = exp_cfg.get("dumpfile", str(Path(dump_dir) / f"migration_{ts}.dmp"))
    logfile = exp_cfg.get("logfile", str(Path(dump_dir) / f"export_{ts}.log"))

    def yn(key, default=True):
        val = exp_cfg.get(key)
        if val is None:
            return "Y" if default else "N"
        return "Y" if val else "N"

    lines = [
        f"FILE={dumpfile}",
        f"LOG={logfile}",
        f"CONSISTENT={yn('consistent', False)}",
        f"COMPRESS={yn('compress', True)}",
        f"GRANTS={yn('grants', True)}",
        f"INDEXES={yn('indexes', True)}",
        f"ROWS={yn('rows', True)}",
        f"CONSTRAINTS={yn('constraints', True)}",
        f"TRIGGERS={yn('triggers', True)}",
    ]

    if schemas:
        lines.append(f"OWNER=({schemas})")

    mode = exp_cfg.get("mode", "schema").lower()
    if mode == "full":
        lines.append("FULL=Y")
    elif mode == "table":
        tables = ",".join(exp_cfg.get("targets", []))
        if tables:
            lines.append(f"TABLES=({tables})")
    elif mode == "tablespace":
        tablespaces = ",".join(exp_cfg.get("targets", []))
        if tablespaces:
            lines.append(f"TABLESPACES=({tablespaces})")

    # Optional numeric/string parameters
    if exp_cfg.get("buffer") is not None:   lines.append(f"BUFFER={exp_cfg['buffer']}")
    if exp_cfg.get("recordlength") is not None: lines.append(f"RECORDLENGTH={exp_cfg['recordlength']}")
    if exp_cfg.get("feedback") is not None:  lines.append(f"FEEDBACK={exp_cfg['feedback']}")
    if exp_cfg.get("filesize"):             lines.append(f"FILESIZE={exp_cfg['filesize']}")
    if exp_cfg.get("volsize"):              lines.append(f"VOLSIZE={exp_cfg['volsize']}")
    if exp_cfg.get("query"):                lines.append(f"QUERY={exp_cfg['query']}")
    if exp_cfg.get("inctype"):              lines.append(f"INCTYPE={exp_cfg['inctype']}")
    if exp_cfg.get("statistics"):           lines.append(f"STATISTICS={exp_cfg['statistics']}")
    if exp_cfg.get("flashback_scn"):        lines.append(f"FLASHBACK_SCN={exp_cfg['flashback_scn']}")
    if exp_cfg.get("flashback_time"):       lines.append(f"FLASHBACK_TIME={exp_cfg['flashback_time']}")
    if exp_cfg.get("resumable_name"):       lines.append(f"RESUMABLE_NAME={exp_cfg['resumable_name']}")
    if exp_cfg.get("resumable_timeout") is not None: lines.append(f"RESUMABLE_TIMEOUT={exp_cfg['resumable_timeout']}")
    if exp_cfg.get("template"):             lines.append(f"TEMPLATE={exp_cfg['template']}")

    # Optional boolean parameters
    if exp_cfg.get("direct") is not None:             lines.append(f"DIRECT={yn('direct', False)}")
    if exp_cfg.get("record") is not None:             lines.append(f"RECORD={yn('record', True)}")
    if exp_cfg.get("object_consistent") is not None:  lines.append(f"OBJECT_CONSISTENT={yn('object_consistent', False)}")
    if exp_cfg.get("resumable") is not None:          lines.append(f"RESUMABLE={yn('resumable', False)}")
    if exp_cfg.get("tts_full_check") is not None:     lines.append(f"TTS_FULL_CHECK={yn('tts_full_check', False)}")
    if exp_cfg.get("transport_tablespace") is not None: lines.append(f"TRANSPORT_TABLESPACE={yn('transport_tablespace', False)}")

    content = "\n".join(lines)
    parfile_path = str(Path(dump_dir) / f"exp_{ts}.par")
    return content, parfile_path



# ── 명령 실행 헬퍼 ────────────────────────────────────────────────────────────

def _run_oracle_cmd(cmd: list[str], log_path: str) -> bool:
    """
    Oracle 유틸리티(exp/expdp)를 subprocess로 실행한다.
    반환: 성공 여부
    """
    logger.debug(f"실행 명령: {' '.join(cmd)}")
    print_info(f"명령 실행: {cmd[0]}")
    print_info(f"로그 파일: {log_path}")

    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

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
        proc.wait()

    if proc.returncode == 0:
        print_ok("Export 완료")
        return True
    else:
        print_fail(f"Export 실패 (returncode={proc.returncode})")
        return False


# ── expdp Job 모니터링 ────────────────────────────────────────────────────────

def monitor_expdp_job(conn: "OracleConnection", job_name: str, interval: int = 10):
    """
    DBA_DATAPUMP_JOBS 뷰를 폴링해 expdp Job 진행률을 출력한다.
    (expdp를 백그라운드로 실행할 때 사용)
    """
    sql = """
        SELECT state, degree, attached_sessions
        FROM dba_datapump_jobs
        WHERE job_name = :job_name
    """
    print_info(f"Job 모니터링 시작: {job_name}")
    while True:
        rows = conn.execute_query(sql, {"job_name": job_name.upper()})
        if not rows:
            print_info("Job 완료 또는 Job을 찾을 수 없습니다.")
            break
        row = rows[0]
        state = row.get("state", "")
        print_info(f"  상태: {state} | 병렬도: {row.get('degree')} | 연결: {row.get('attached_sessions')}")
        if state in ("NOT RUNNING", "COMPLETED", "STOPPED"):
            break
        time.sleep(interval)


# ── expdp 실행 ───────────────────────────────────────────────────────────────

def run_expdp(cfg: dict, password: str, conn: Optional["OracleConnection"] = None) -> bool:
    """
    expdp(Data Pump Export)를 실행한다.

    :param cfg: 전체 설정 dict
    :param password: Source DB 패스워드
    :param conn: OracleConnection (Job 모니터링 시 사용, 선택)
    :return: 성공 여부
    """
    print_header("Step 3: Data Pump Export (expdp)")

    exp_cfg = cfg.get("export", {})
    src_cfg = cfg.get("source", {})
    dump_dir = cfg.get("output", {}).get("dump_dir", "output/dumps")
    Path(dump_dir).mkdir(parents=True, exist_ok=True)

    parfile_content, parfile_path = build_expdp_parfile(cfg, password)
    write_text_file(parfile_path, parfile_content)
    print_info(f"파라미터 파일: {parfile_path}")

    dsn = f"{src_cfg['host']}:{src_cfg.get('port',1521)}/{src_cfg['service_name']}"
    user_pass = f"{src_cfg['username']}/{password}@{dsn}"
    ts = timestamp_str()
    log_path = str(Path(dump_dir) / f"expdp_run_{ts}.log")

    cmd = ["expdp", user_pass, f"PARFILE={parfile_path}"]
    return _run_oracle_cmd(cmd, log_path)


# ── exp 실행 ─────────────────────────────────────────────────────────────────

def run_exp(cfg: dict, password: str) -> bool:
    """
    전통적 exp를 실행한다.

    :param cfg: 전체 설정 dict
    :param password: Source DB 패스워드
    :return: 성공 여부
    """
    print_header("Step 3: Traditional Export (exp)")

    exp_cfg = cfg.get("export", {})
    src_cfg = cfg.get("source", {})
    dump_dir = cfg.get("output", {}).get("dump_dir", "output/dumps")
    Path(dump_dir).mkdir(parents=True, exist_ok=True)

    parfile_content, parfile_path = build_exp_parfile(cfg, password)
    write_text_file(parfile_path, parfile_content)
    print_info(f"파라미터 파일: {parfile_path}")

    dsn = f"{src_cfg['host']}:{src_cfg.get('port',1521)}/{src_cfg['service_name']}"
    user_pass = f"{src_cfg['username']}/{password}@{dsn}"
    ts = timestamp_str()
    log_path = str(Path(dump_dir) / f"exp_run_{ts}.log")

    cmd = ["exp", user_pass, f"PARFILE={parfile_path}"]
    return _run_oracle_cmd(cmd, log_path)


# ── 진입점 ───────────────────────────────────────────────────────────────────

def run_export(cfg: dict, password: str, conn: Optional["OracleConnection"] = None) -> bool:
    """
    설정의 method에 따라 expdp 또는 exp를 실행한다.
    """
    method = cfg.get("export", {}).get("method", "expdp").lower()
    if method == "expdp":
        return run_expdp(cfg, password, conn)
    elif method == "exp":
        return run_exp(cfg, password)
    else:
        print_fail(f"알 수 없는 export method: {method} (expdp 또는 exp)")
        return False
