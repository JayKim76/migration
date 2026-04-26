"""
Oracle Migration Tool - 공통 유틸리티
"""

import os
import sys
import logging
import getpass
from datetime import datetime
from pathlib import Path

import yaml
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)


# ── 로거 설정 ──────────────────────────────────────────────────────────────────

def setup_logger(name: str = "migration", log_dir: str = "output/logs") -> logging.Logger:
    """파일 + 콘솔 핸들러가 붙은 로거를 반환한다."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(log_dir) / f"{name}_{timestamp}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 콘솔 핸들러 (INFO 이상)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))

    # 파일 핸들러 (DEBUG 이상)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger


logger = setup_logger()


# ── 설정 로드 ──────────────────────────────────────────────────────────────────

def load_config(config_path: str = "config/migration_config.yaml") -> dict:
    """YAML 설정 파일을 로드하고 dict로 반환한다."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


def get_password(cfg_section: dict, label: str) -> str:
    """
    설정에 password가 없거나 빈 문자열이면 콘솔에서 입력받는다.
    """
    pw = cfg_section.get("password", "")
    if not pw:
        pw = getpass.getpass(f"[{label}] password: ")
    return pw


def ensure_dirs(cfg: dict):
    """output 하위 디렉토리를 모두 생성한다."""
    for key in ("base_dir", "ddl_dir", "dump_dir", "report_dir", "log_dir"):
        path = cfg.get("output", {}).get(key, f"output/{key}")
        Path(path).mkdir(parents=True, exist_ok=True)


# ── 출력 헬퍼 ──────────────────────────────────────────────────────────────────

def print_header(title: str):
    line = "=" * 60
    print(f"\n{Fore.CYAN}{line}")
    print(f"  {title}")
    print(f"{line}{Style.RESET_ALL}\n")


def print_step(step: int, title: str):
    print(f"\n{Fore.YELLOW}[STEP {step}] {title}{Style.RESET_ALL}")


def print_ok(msg: str):
    print(f"  {Fore.GREEN}[PASS]{Style.RESET_ALL} {msg}")


def print_fail(msg: str):
    print(f"  {Fore.RED}[FAIL]{Style.RESET_ALL} {msg}")


def print_warn(msg: str):
    print(f"  {Fore.YELLOW}[WARN]{Style.RESET_ALL} {msg}")


def print_info(msg: str):
    print(f"  {Fore.BLUE}[INFO]{Style.RESET_ALL} {msg}")


def print_table(headers: list, rows: list):
    """간단한 텍스트 테이블 출력."""
    try:
        from tabulate import tabulate
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    except ImportError:
        # tabulate 없을 경우 간단 출력
        print("  " + " | ".join(str(h) for h in headers))
        print("  " + "-" * 60)
        for row in rows:
            print("  " + " | ".join(str(c) for c in row))


# ── DSN 빌더 ──────────────────────────────────────────────────────────────────

def build_dsn(cfg_section: dict) -> str:
    """Easy Connect 형식의 DSN 문자열을 생성한다."""
    host = cfg_section["host"]
    port = cfg_section.get("port", 1521)
    service = cfg_section["service_name"]
    return f"{host}:{port}/{service}"


# ── 파일 유틸 ─────────────────────────────────────────────────────────────────

def write_text_file(path: str, content: str):
    """텍스트 파일을 UTF-8로 저장한다."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print_info(f"파일 저장: {p}")


def timestamp_str() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")
