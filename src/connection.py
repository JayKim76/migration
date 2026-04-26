"""
Step 1: Oracle Database 접속 관리

Source / Target DB에 oracledb(python-oracledb) 드라이버로 접속한다.
Thin 모드(Oracle Client 불필요)를 기본으로 사용하며,
필요 시 Thick 모드(Oracle Client 설치 필요)로 전환 가능하다.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

import oracledb
import paramiko

from src.utils import (
    build_dsn,
    get_password,
    logger,
    print_header,
    print_info,
    print_ok,
    print_fail,
    print_table,
)


# ── DB 정보 컨테이너 ───────────────────────────────────────────────────────────

@dataclass
class DBInfo:
    label: str                          # "SOURCE" 또는 "TARGET"
    # Server Info
    server_host: str = ""
    ssh_user: str = ""
    # Oracle DB Info
    host: str = ""
    port: int = 1521
    service_name: str = ""
    username: str = ""
    version: str = ""
    instance_name: str = ""
    db_name: str = ""
    charset: str = ""
    nls_params: dict = field(default_factory=dict)
    default_tablespace: str = ""
    temp_tablespace: str = ""
    connected: bool = False


# ── 접속 클래스 ────────────────────────────────────────────────────────────────

class OracleConnection:
    """
    Oracle DB 접속을 관리하는 클래스.

    사용 예::

        with OracleConnection(cfg["source"], label="SOURCE") as conn:
            info = conn.get_db_info()
    """

    def __init__(self, cfg_section: dict, label: str = "DB", thick_mode: bool = False):
        self.cfg = cfg_section
        self.label = label.upper()
        self.thick_mode = thick_mode
        self._conn: Optional[oracledb.Connection] = None
        self.db_info = DBInfo(
            label=self.label,
            server_host=cfg_section.get("server_host", cfg_section.get("host", "")),
            ssh_user=cfg_section.get("ssh_user", ""),
            host=cfg_section.get("host", ""),
            port=int(cfg_section.get("port", 1521)),
            service_name=cfg_section.get("service_name", ""),
            username=cfg_section.get("username", ""),
        )

    # ── 컨텍스트 매니저 ─────────────────────────────────────────────────────────

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    # ── 접속 ────────────────────────────────────────────────────────────────────

    def connect(self) -> oracledb.Connection:
        """DB에 접속하고 Connection 객체를 반환한다."""
        if self._conn:
            return self._conn

        if self.thick_mode:
            oracle_home = self.cfg.get("oracle_home") or os.environ.get("ORACLE_HOME")
            oracledb.init_oracle_client(lib_dir=oracle_home)
            logger.debug(f"[{self.label}] Thick 모드 (Oracle Home: {oracle_home})")
        else:
            logger.debug(f"[{self.label}] Thin 모드 (Oracle Client 불필요)")

        password = get_password(self.cfg, self.label)
        dsn = build_dsn(self.cfg)

        logger.info(f"[{self.label}] 접속 시도: {self.cfg['username']}@{dsn}")
        try:
            self._conn = oracledb.connect(
                user=self.cfg["username"],
                password=password,
                dsn=dsn,
            )
            self.db_info.connected = True
            logger.info(f"[{self.label}] 접속 성공")
        except oracledb.DatabaseError as e:
            logger.error(f"[{self.label}] 접속 실패: {e}")
            raise
        return self._conn

    def close(self):
        if self._conn:
            try:
                self._conn.close()
                logger.debug(f"[{self.label}] 접속 종료")
            except Exception:
                pass
            self._conn = None
            self.db_info.connected = False

    @property
    def connection(self) -> oracledb.Connection:
        if not self._conn:
            raise RuntimeError(f"[{self.label}] 아직 접속되지 않았습니다. connect()를 먼저 호출하세요.")
        return self._conn

    # ── 쿼리 헬퍼 ───────────────────────────────────────────────────────────────

    def execute_query(self, sql: str, params: dict = None) -> list[dict]:
        """SQL을 실행하고 dict 리스트로 반환한다."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params or {})
            columns = [col[0].lower() for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def execute_scalar(self, sql: str, params: dict = None):
        """단일 값을 반환하는 쿼리 실행."""
        rows = self.execute_query(sql, params)
        if rows:
            return list(rows[0].values())[0]
        return None

    # ── DB 정보 조회 ─────────────────────────────────────────────────────────────

    def get_db_info(self) -> DBInfo:
        """DB 버전, 인스턴스, 캐릭터셋 등 주요 정보를 조회한다."""
        # 버전
        ver_rows = self.execute_query("SELECT banner FROM v$version WHERE rownum = 1")
        self.db_info.version = ver_rows[0]["banner"] if ver_rows else "Unknown"

        # 인스턴스
        inst_rows = self.execute_query(
            "SELECT instance_name, db_name, status FROM v$instance"
        )
        if inst_rows:
            self.db_info.instance_name = inst_rows[0].get("instance_name", "")
            self.db_info.db_name = inst_rows[0].get("db_name", "")

        # 캐릭터셋
        nls_rows = self.execute_query(
            "SELECT parameter, value FROM nls_database_parameters "
            "WHERE parameter IN ('NLS_CHARACTERSET','NLS_NCHAR_CHARACTERSET',"
            "'NLS_LANGUAGE','NLS_TERRITORY','NLS_DATE_FORMAT')"
        )
        for r in nls_rows:
            param = r["parameter"]
            val = r["value"]
            self.db_info.nls_params[param] = val
            if param == "NLS_CHARACTERSET":
                self.db_info.charset = val

        # 기본 Tablespace
        ts_rows = self.execute_query(
            "SELECT property_value FROM database_properties "
            "WHERE property_name IN "
            "('DEFAULT_PERMANENT_TABLESPACE','DEFAULT_TEMP_TABLESPACE')"
        )
        for i, r in enumerate(ts_rows):
            if i == 0:
                self.db_info.default_tablespace = r["property_value"]
            else:
                self.db_info.temp_tablespace = r["property_value"]

        return self.db_info

    # ── 접속 테스트 ─────────────────────────────────────────────────────────────

    def test_ssh_connection(self) -> bool:
        """서버 OS(SSH) 접속 상태를 확인한다."""
        if not self.db_info.server_host:
            logger.debug(f"[{self.label}] server_host 미설정. SSH 테스트 생략.")
            return True

        logger.info(f"[{self.label}] SSH 접속 시도: {self.db_info.ssh_user}@{self.db_info.server_host}")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_pwd = self.cfg.get("ssh_password", "")
            if ssh_pwd:
                client.connect(hostname=self.db_info.server_host, username=self.db_info.ssh_user, password=ssh_pwd, timeout=5)
            else:
                client.connect(hostname=self.db_info.server_host, username=self.db_info.ssh_user, timeout=5)
            logger.info(f"[{self.label}] SSH 접속 성공")
            return True
        except Exception as e:
            logger.error(f"[{self.label}] SSH 접속 실패: {e}")
            return False
        finally:
            client.close()

    def test_connection(self) -> bool:
        """서버 및 DB 접속 상태를 확인하고 결과를 출력한다."""
        print_header(f"{self.label} Environment (Server & DB) 접속 테스트")
        
        # 1. SSH 접속 테스트
        if self.db_info.server_host:
            if self.test_ssh_connection():
                print_ok(f"[{self.label}] Linux Server (SSH) 접속 성공: {self.db_info.server_host}")
            else:
                print_fail(f"[{self.label}] Linux Server (SSH) 접속 실패: {self.db_info.server_host}")
                return False

        # 2. Oracle DB 접속 테스트
        try:
            self.connect()
            info = self.get_db_info()

            rows = [
                ["DB Version", info.version],
                ["Instance", info.instance_name],
                ["DB Name", info.db_name],
                ["Character Set", info.charset],
                ["Default Tablespace", info.default_tablespace],
                ["Temp Tablespace", info.temp_tablespace],
            ]
            for k, v in info.nls_params.items():
                if k not in ("NLS_CHARACTERSET",):
                    rows.append([k, v])

            print_table(["항목", "값"], rows)
            print_ok(f"[{self.label}] Oracle Database 접속 성공: {self.db_info.host}:{self.db_info.port}")
            return True

        except Exception as e:
            print_fail(f"[{self.label}] Oracle Database 접속 실패: {e}")
            return False


# ── 편의 함수 ─────────────────────────────────────────────────────────────────

def connect_source(cfg: dict, thick_mode: bool = False) -> OracleConnection:
    """Source DB OracleConnection 객체를 생성하고 반환한다 (접속 포함)."""
    conn = OracleConnection(cfg["source"], label="SOURCE", thick_mode=thick_mode)
    conn.connect()
    return conn


def connect_target(cfg: dict, thick_mode: bool = False) -> OracleConnection:
    """Target DB OracleConnection 객체를 생성하고 반환한다 (접속 포함)."""
    conn = OracleConnection(cfg["target"], label="TARGET", thick_mode=thick_mode)
    conn.connect()
    return conn
