"""
Step 2: Database 정보 조회 및 Tablespace DDL 추출

- Tablespace 목록/크기/Datafile 정보 조회
- DBMS_METADATA로 CREATE TABLESPACE DDL 생성
- 스키마별 오브젝트 요약
- 사용자 정보 및 권한 조회
- DDL 파일 저장
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from src.utils import (
    logger,
    print_header,
    print_info,
    print_ok,
    print_warn,
    print_table,
    write_text_file,
    timestamp_str,
)

if TYPE_CHECKING:
    from src.connection import OracleConnection


# ── Tablespace 정보 조회 ─────────────────────────────────────────────────────

def get_tablespace_info(conn: "OracleConnection") -> list[dict]:
    """DBA_TABLESPACES + DBA_DATA_FILES 를 조인해 Tablespace 정보를 반환한다."""
    sql = """
        SELECT
            t.tablespace_name,
            t.block_size,
            t.status,
            t.contents,
            t.extent_management,
            t.segment_space_management,
            ROUND(NVL(s.used_mb, 0), 2)  AS used_mb,
            ROUND(NVL(s.total_mb, 0), 2) AS total_mb
        FROM dba_tablespaces t
        LEFT JOIN (
            SELECT tablespace_name,
                   SUM(bytes) / 1048576 AS total_mb,
                   SUM(bytes - NVL(free.bytes,0)) / 1048576 AS used_mb
            FROM dba_data_files df
            LEFT JOIN (
                SELECT tablespace_name, SUM(bytes) AS bytes
                FROM dba_free_space
                GROUP BY tablespace_name
            ) free USING (tablespace_name)
            GROUP BY tablespace_name
        ) s ON t.tablespace_name = s.tablespace_name
        ORDER BY t.tablespace_name
    """
    rows = conn.execute_query(sql)
    logger.debug(f"Tablespace 조회 결과: {len(rows)}건")
    return rows


def get_datafile_info(conn: "OracleConnection") -> list[dict]:
    """DBA_DATA_FILES 에서 Datafile 목록을 조회한다."""
    sql = """
        SELECT
            tablespace_name,
            file_id,
            file_name,
            ROUND(bytes / 1048576, 2) AS size_mb,
            autoextensible,
            ROUND(maxbytes / 1048576, 2) AS max_mb,
            ROUND(increment_by * 8192 / 1048576, 2) AS increment_mb
        FROM dba_data_files
        ORDER BY tablespace_name, file_id
    """
    return conn.execute_query(sql)


def get_tempfile_info(conn: "OracleConnection") -> list[dict]:
    """DBA_TEMP_FILES 에서 Temp 파일 목록을 조회한다."""
    sql = """
        SELECT
            tablespace_name,
            file_id,
            file_name,
            ROUND(bytes / 1048576, 2) AS size_mb,
            autoextensible,
            ROUND(maxbytes / 1048576, 2) AS max_mb
        FROM dba_temp_files
        ORDER BY tablespace_name, file_id
    """
    return conn.execute_query(sql)


# ── Tablespace DDL 생성 ──────────────────────────────────────────────────────

# 마이그레이션 대상에서 제외할 시스템 Tablespace
SYSTEM_TABLESPACES = {
    "SYSTEM", "SYSAUX", "UNDOTBS1", "UNDOTBS2",
    "TEMP", "USERS",
}


def generate_tablespace_ddl(conn: "OracleConnection", exclude: set = None) -> str:
    """
    DBMS_METADATA.GET_DDL 을 사용해 CREATE TABLESPACE DDL 스크립트를 생성한다.
    시스템 Tablespace는 기본적으로 제외된다.
    """
    if exclude is None:
        exclude = SYSTEM_TABLESPACES

    ts_rows = get_tablespace_info(conn)
    user_ts = [r["tablespace_name"] for r in ts_rows if r["tablespace_name"] not in exclude]

    lines = [
        "-- ============================================================",
        f"-- Tablespace DDL Script",
        f"-- Generated: {timestamp_str()}",
        f"-- Source: {conn.cfg.get('host')}:{conn.cfg.get('port')}/{conn.cfg.get('service_name')}",
        "-- ============================================================",
        "",
    ]

    for ts_name in user_ts:
        try:
            ddl = conn.execute_scalar(
                "SELECT DBMS_METADATA.GET_DDL('TABLESPACE', :ts_name) FROM dual",
                {"ts_name": ts_name},
            )
            if ddl:
                lines.append(f"-- Tablespace: {ts_name}")
                lines.append(str(ddl).strip())
                lines.append("/")
                lines.append("")
                print_ok(f"DDL 추출: {ts_name}")
            else:
                print_warn(f"DDL 없음: {ts_name}")
        except Exception as e:
            print_warn(f"DDL 추출 실패 ({ts_name}): {e}")
            logger.warning(f"DBMS_METADATA 오류 [{ts_name}]: {e}")

    return "\n".join(lines)


# ── 사용자 DDL 생성 ──────────────────────────────────────────────────────────

def get_user_info(conn: "OracleConnection", schemas: list[str]) -> list[dict]:
    """지정 스키마의 사용자 정보를 조회한다."""
    placeholders = ", ".join([f":u{i}" for i in range(len(schemas))])
    params = {f"u{i}": s.upper() for i, s in enumerate(schemas)}
    sql = f"""
        SELECT username, default_tablespace, temporary_tablespace,
               account_status, profile, created
        FROM dba_users
        WHERE username IN ({placeholders})
        ORDER BY username
    """
    return conn.execute_query(sql, params)


def generate_user_ddl(conn: "OracleConnection", schemas: list[str]) -> str:
    """스키마 사용자의 CREATE USER + GRANT DDL을 생성한다."""
    lines = [
        "-- ============================================================",
        "-- User & Grant DDL Script",
        f"-- Generated: {timestamp_str()}",
        "-- ============================================================",
        "",
    ]

    for schema in schemas:
        schema = schema.upper()
        try:
            user_ddl = conn.execute_scalar(
                "SELECT DBMS_METADATA.GET_DDL('USER', :u) FROM dual",
                {"u": schema},
            )
            grant_ddl = conn.execute_scalar(
                "SELECT DBMS_METADATA.GET_GRANTED_DDL('SYSTEM_GRANT', :u) FROM dual",
                {"u": schema},
            )
            role_ddl = conn.execute_scalar(
                "SELECT DBMS_METADATA.GET_GRANTED_DDL('ROLE_GRANT', :u) FROM dual",
                {"u": schema},
            )

            lines.append(f"-- User: {schema}")
            if user_ddl:
                lines.append(str(user_ddl).strip())
                lines.append("/")
            if grant_ddl:
                lines.append(str(grant_ddl).strip())
                lines.append("/")
            if role_ddl:
                lines.append(str(role_ddl).strip())
                lines.append("/")
            lines.append("")
            print_ok(f"User DDL 추출: {schema}")
        except Exception as e:
            print_warn(f"User DDL 실패 ({schema}): {e}")

    return "\n".join(lines)


# ── 스키마 오브젝트 요약 ─────────────────────────────────────────────────────

def get_schema_summary(conn: "OracleConnection", schemas: list[str]) -> list[dict]:
    """스키마별 오브젝트 타입/개수를 조회한다."""
    placeholders = ", ".join([f":s{i}" for i in range(len(schemas))])
    params = {f"s{i}": s.upper() for i, s in enumerate(schemas)}
    sql = f"""
        SELECT owner, object_type, COUNT(*) AS cnt
        FROM dba_objects
        WHERE owner IN ({placeholders})
          AND object_type NOT IN ('INDEX PARTITION','TABLE PARTITION','LOB','LOB PARTITION')
        GROUP BY owner, object_type
        ORDER BY owner, object_type
    """
    return conn.execute_query(sql, params)


# ── 메인 추출 함수 ───────────────────────────────────────────────────────────

def extract_metadata(conn: "OracleConnection", cfg: dict) -> dict:
    """
    DB 메타데이터를 전부 수집하고 DDL 파일을 저장한다.
    반환값: {tablespace_info, datafile_info, schema_summary, user_info}
    """
    schemas = cfg.get("export", {}).get("schemas", [])
    ddl_dir = cfg.get("output", {}).get("ddl_dir", "output/ddl")

    print_header("Step 2: Database 메타정보 조회 및 DDL 추출")

    # 1) Tablespace 정보
    print_info("Tablespace 정보 조회 중...")
    ts_info = get_tablespace_info(conn)
    headers = ["Tablespace", "Contents", "Status", "Used(MB)", "Total(MB)"]
    rows = [(r["tablespace_name"], r["contents"], r["status"], r["used_mb"], r["total_mb"]) for r in ts_info]
    print_table(headers, rows)

    # 2) Datafile 정보
    df_info = get_datafile_info(conn)
    tf_info = get_tempfile_info(conn)

    # 3) Tablespace DDL 저장
    print_info("\nTablespace DDL 추출 중...")
    ts_ddl = generate_tablespace_ddl(conn)
    ts_ddl_path = str(Path(ddl_dir) / "tablespace_ddl.sql")
    write_text_file(ts_ddl_path, ts_ddl)

    # 4) User DDL 저장
    print_info("\nUser DDL 추출 중...")
    user_ddl = generate_user_ddl(conn, schemas)
    user_ddl_path = str(Path(ddl_dir) / "user_ddl.sql")
    write_text_file(user_ddl_path, user_ddl)

    # 5) 스키마 오브젝트 요약
    print_info("\n스키마 오브젝트 요약 조회 중...")
    schema_summary = get_schema_summary(conn, schemas)
    headers2 = ["Owner", "Object Type", "Count"]
    rows2 = [(r["owner"], r["object_type"], r["cnt"]) for r in schema_summary]
    print_table(headers2, rows2)

    # 6) 사용자 정보
    user_info = get_user_info(conn, schemas)

    print_ok("메타정보 수집 완료")
    return {
        "tablespace_info": ts_info,
        "datafile_info": df_info,
        "tempfile_info": tf_info,
        "schema_summary": schema_summary,
        "user_info": user_info,
        "tablespace_ddl_path": ts_ddl_path,
        "user_ddl_path": user_ddl_path,
    }
