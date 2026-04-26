"""
Step 4-5: Target Database 환경 체크 및 Tablespace 생성

- Source-Target 버전/캐릭터셋 호환성 검사
- Target 디스크 공간 확인
- DDL 경로 자동 변환 (Source → Target Datafile 경로)
- Tablespace, User 생성 DDL 실행
- Data Pump DIRECTORY 객체 생성
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from src.utils import (
    logger,
    print_header,
    print_info,
    print_ok,
    print_fail,
    print_warn,
    print_table,
)

if TYPE_CHECKING:
    from src.connection import OracleConnection, DBInfo


# ── 호환성 체크 ──────────────────────────────────────────────────────────────

def check_compatibility(src_info: "DBInfo", tgt_info: "DBInfo") -> dict:
    """
    Source-Target 버전/캐릭터셋 등 호환성을 검사하고 결과 dict를 반환한다.
    반환: {check_name: {"pass": bool, "detail": str}}
    """
    results = {}

    # 버전 비교: Target >= Source 권장
    def parse_version(banner: str) -> tuple:
        m = re.search(r"(\d+)\.(\d+)\.(\d+)\.(\d+)", banner)
        if m:
            return tuple(int(x) for x in m.groups())
        return (0,)

    src_ver = parse_version(src_info.version)
    tgt_ver = parse_version(tgt_info.version)
    ver_ok = tgt_ver >= src_ver
    results["version"] = {
        "pass": ver_ok,
        "detail": f"Source={src_info.version[:40]} / Target={tgt_info.version[:40]}",
    }

    # 캐릭터셋 일치
    cs_ok = src_info.charset == tgt_info.charset
    results["charset"] = {
        "pass": cs_ok,
        "detail": f"Source={src_info.charset} / Target={tgt_info.charset}",
    }

    return results


def print_compatibility_result(results: dict) -> bool:
    """호환성 체크 결과를 출력하고 모두 PASS면 True를 반환한다."""
    rows = []
    all_pass = True
    for name, r in results.items():
        status = "PASS" if r["pass"] else "FAIL"
        if not r["pass"]:
            all_pass = False
        rows.append([name, status, r["detail"]])
    print_table(["항목", "결과", "상세"], rows)
    return all_pass


# ── 디스크 공간 확인 ─────────────────────────────────────────────────────────

def check_target_disk_space(tgt_conn: "OracleConnection", required_mb: float) -> bool:
    """
    Target DB 서버의 Datafile 경로 가용 공간을 확인한다.
    (DBA_DATA_FILES의 실제 남은 공간 파악은 OS 레벨 명령이 필요하므로,
     여기서는 기존 Tablespace 여유 공간으로 대체 체크한다.)
    """
    sql = """
        SELECT ROUND(SUM(bytes) / 1048576, 2) AS free_mb
        FROM dba_free_space
    """
    rows = tgt_conn.execute_query(sql)
    free_mb = rows[0]["free_mb"] if rows else 0
    ok = float(free_mb or 0) >= required_mb
    print_info(f"Target 가용 공간: {free_mb} MB / 필요: {required_mb} MB")
    if ok:
        print_ok("디스크 공간 충분")
    else:
        print_warn("디스크 공간 부족 가능성 — 계속 진행하려면 확인 후 진행하세요.")
    return ok


# ── Datafile 경로 변환 ────────────────────────────────────────────────────────

def adjust_ddl_paths(ddl: str, path_mapping: dict) -> str:
    """
    DDL 문자열에서 Source Datafile 경로를 Target 경로로 치환한다.

    path_mapping 예시::

        {"/u01/oradata/ORCL": "/u02/oradata/NEWDB"}
    """
    result = ddl
    for src_path, tgt_path in path_mapping.items():
        result = result.replace(src_path, tgt_path)
    return result


# ── DDL 실행 ─────────────────────────────────────────────────────────────────

def _execute_ddl_file(conn: "OracleConnection", ddl_path: str, label: str = "DDL") -> bool:
    """
    SQL 파일을 읽어 각 DDL 문을 실행한다.
    '/' 구분자로 개별 문 분리.
    """
    path = Path(ddl_path)
    if not path.exists():
        print_fail(f"{label} 파일을 찾을 수 없습니다: {ddl_path}")
        return False

    content = path.read_text(encoding="utf-8")
    # '/' 로 구분된 DDL 블록 분리
    statements = [s.strip() for s in content.split("\n/") if s.strip()]

    ok_count = 0
    fail_count = 0
    for stmt in statements:
        # 주석 전용 블록 건너뜀
        if stmt.startswith("--") or not stmt:
            continue
        try:
            cursor = conn.connection.cursor()
            cursor.execute(stmt)
            conn.connection.commit()
            cursor.close()
            ok_count += 1
        except Exception as e:
            print_warn(f"  DDL 실행 오류 (무시): {e}")
            logger.warning(f"DDL 실행 오류: {e}\n{stmt[:200]}")
            fail_count += 1

    print_info(f"{label} 실행 완료: 성공={ok_count}, 실패={fail_count}")
    return fail_count == 0


# ── Data Pump DIRECTORY 생성 ─────────────────────────────────────────────────

def create_directory_object(
    conn: "OracleConnection",
    dir_name: str,
    dir_path: str,
    username: str,
) -> bool:
    """
    Oracle DIRECTORY 객체를 생성하고 권한을 부여한다.
    """
    try:
        cursor = conn.connection.cursor()
        # 경로가 없으면 그냥 시도 (DB가 경로 유효성 검사하지 않음)
        cursor.execute(
            f"CREATE OR REPLACE DIRECTORY {dir_name} AS '{dir_path}'"
        )
        cursor.execute(
            f"GRANT READ, WRITE ON DIRECTORY {dir_name} TO {username}"
        )
        conn.connection.commit()
        cursor.close()
        print_ok(f"DIRECTORY 생성: {dir_name} → {dir_path}")
        return True
    except Exception as e:
        print_fail(f"DIRECTORY 생성 실패: {e}")
        logger.error(f"DIRECTORY 생성 오류: {e}")
        return False


# ── Tablespace 생성 ──────────────────────────────────────────────────────────

def create_tablespaces(
    tgt_conn: "OracleConnection",
    ddl_path: str,
    path_mapping: dict = None,
) -> bool:
    """
    Step 2에서 생성한 tablespace_ddl.sql을 Target에 실행한다.
    path_mapping이 주어지면 Datafile 경로를 변환한다.
    """
    print_info("Tablespace DDL 실행 중...")
    ddl = Path(ddl_path).read_text(encoding="utf-8")
    if path_mapping:
        ddl = adjust_ddl_paths(ddl, path_mapping)
        # 변환된 DDL을 임시 파일에 저장
        adjusted_path = ddl_path.replace(".sql", "_adjusted.sql")
        Path(adjusted_path).write_text(ddl, encoding="utf-8")
        print_info(f"경로 변환된 DDL 저장: {adjusted_path}")
        ddl_path = adjusted_path

    return _execute_ddl_file(tgt_conn, ddl_path, "Tablespace DDL")


# ── User 생성 ────────────────────────────────────────────────────────────────

def create_users(tgt_conn: "OracleConnection", ddl_path: str) -> bool:
    """user_ddl.sql을 Target에 실행한다."""
    print_info("User DDL 실행 중...")
    return _execute_ddl_file(tgt_conn, ddl_path, "User DDL")


# ── 메인 함수 ─────────────────────────────────────────────────────────────────

def setup_target(
    src_conn: "OracleConnection",
    tgt_conn: "OracleConnection",
    cfg: dict,
    meta: dict,
) -> bool:
    """
    Step 4-5 전체 실행:
      1. 호환성 체크
      2. 디스크 공간 확인
      3. DIRECTORY 객체 생성
      4. Tablespace 생성
      5. User 생성
    """
    print_header("Step 4-5: Target 환경 체크 및 Tablespace 생성")

    # 4-1) 호환성 체크
    print_info("호환성 체크 중...")
    src_info = src_conn.db_info
    tgt_info = tgt_conn.db_info
    compat = check_compatibility(src_info, tgt_info)
    all_ok = print_compatibility_result(compat)
    if not all_ok:
        print_warn("호환성 체크에서 FAIL이 있습니다. 계속 진행합니까? (y/N)")
        if input().strip().lower() != "y":
            return False

    # 4-2) 디스크 공간
    ts_info = meta.get("tablespace_info", [])
    required_mb = sum(float(r.get("used_mb") or 0) for r in ts_info) * 1.5
    check_target_disk_space(tgt_conn, required_mb)

    # 4-3) DIRECTORY 객체 생성 (expdp/impdp 방식일 때)
    exp_cfg = cfg.get("export", {})
    imp_cfg = cfg.get("import", {})
    if exp_cfg.get("method", "expdp") == "expdp" or imp_cfg.get("method", "impdp") == "impdp":
        dir_name = imp_cfg.get("directory", exp_cfg.get("directory", "DATA_PUMP_DIR"))
        dir_path = exp_cfg.get("directory_path", "/tmp/datapump")
        tgt_username = cfg.get("target", {}).get("username", "system")
        create_directory_object(tgt_conn, dir_name, dir_path, tgt_username)

    # 4-4) Tablespace 생성
    ts_ddl_path = meta.get("tablespace_ddl_path", "output/ddl/tablespace_ddl.sql")
    path_mapping = cfg.get("import", {}).get("remap_tablespace_path", {})
    create_tablespaces(tgt_conn, ts_ddl_path, path_mapping or None)

    # 4-5) User 생성
    user_ddl_path = meta.get("user_ddl_path", "output/ddl/user_ddl.sql")
    create_users(tgt_conn, user_ddl_path)

    print_ok("Target 환경 설정 완료")
    return True
