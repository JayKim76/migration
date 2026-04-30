# 💻 Developer — 기존 설계안에 따라 `BaseAdapter` 추상 클래스와 `3-Stage DIV` 엔진(데이터 무결성 검증 로직)의 핵심 파이썬 코드를 작성하세요. 롤백 기능, 에러 핸들링, 그리고 TUI 출력을 위한 구조를 포함하여 'Zero-Risk' 가치를 코드로 구현해야 합니다.

💻 Developer: 작업 시작합니다.

CEO의 지시 사항에 따라, 데이터 무결성을 보장하는 **`3-Stage DIV(Data Integrity Verification)`** 엔진과 확장 가능한 **`BaseAdapter`** 아키텍처를 구현했습니다. 이 코드는 'Zero-Risk' 가치를 달성하기 위해 데이터의 구조, 수량, 그리고 실제 값의 해시를 단계별로 검증하며, 실패 시 즉각적인 롤백 프로세스를 트리거하도록 설계되었습니다.

```python
import abc
import logging
import hashlib
from typing import Any, Dict, List, Optional
from colorama import Fore, Style, init

# TUI 초기화
init(autoreset=True)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MigrationEngine")

# -------------------------------------------------------------------------
# [1] BaseAdapter: 확장 가능한 어댑터 인터페이스
# -------------------------------------------------------------------------
class BaseAdapter(abc.ABC):
    """
    모든 데이터베이스 소스/타겟을 위한 추상 클래스.
    'from scratch' 원칙에 따라 핵심 인터페이스를 정의함.
    """
    @abc.abstractmethod
    def extract_data(self, query: str) -> List[Dict[str, Any]]:
        """데이터 추출 로직"""
        pass

    @abc.abstractmethod
    def load_data(self, data: List[Dict[str, Any]], table_name: str) -> bool:
        """데이터 로드 로직"""
        pass

    @abc.abstractmethod
    def get_metadata(self, table_name: str) -> Dict[str, Any]:
        """Stage 1: 스키마 및 컬럼 정보 추출"""
        pass

    @abc.abstractmethod
    def get_aggregate_stats(self, table_name: str) -> Dict[str, Any]:
        """Stage 2: Row Count, Sum 등 집계 데이터 추출"""
        pass

    @abc.abstractmethod
    def get_content_hash(self, table_name: str, sample_size: int = 100) -> str:
        """Stage 3: 데이터 샘플링 기반 해시 생성"""
        pass

    @abc.abstractmethod
    def rollback(self, table_name: str):
        """실패 시 롤백 로직"""
        pass

# -------------------------------------------------------------------------
# [2] MigrationEngine: 3-Stage DIV 및 롤백 제어 엔진
# -------------------------------------------------------------------------
class MigrationEngine:
    def __init__(self, source: BaseAdapter, target: BaseAdapter):
        self.source = source
        self.target = target
        self.is_success = False

    def _print_tui(self, stage: str, status: str, color: str = Fore.WHITE):
        """TUI 출력을 위한 헬퍼 메서드"""
        print(f"{Style.BRIGHT}{Fore.CYAN}[STAGING] {stage:<20} | {color}{status}{Style.RESET_ALL}")

    def run_migration(self, table_name: str, query: str):
        print(f"\n{Fore.YELLOW}{'='*60}")
        print(f"{Fore.YELLOW}🚀 Starting Zero-Risk Migration: {table_name}")
        print(f"{Fore.YELLOW}{'='*60}\n")

        try:
            # --- STEP 0: Data Extraction & Loading ---
            self._print_tui("Data Extraction", "Processing...", Fore.BLUE)
            data = self.source.extract_data(query)
            
            self._print_tui("Data Loading", "Writing to Target...", Fore.BLUE)
            load_success = self.target.load_data(data, table_name)
            
            if not load_success:
                raise Exception("Target Load Failed: Integrity Breach detected during write.")

            # --- STEP 1: 3-Stage DIV (Data Integrity Verification) ---
            self._print_tui("3-Stage DIV", "Initializing Verification...", Fore.MAGENTA)
            
            # Stage 1: Metadata/Schema Verification
            self._verify_stage_1(table_name)
            
            # Stage 2: Aggregate/Quantity Verification
            self._verify_stage_2(table_name)
            
            # Stage 3: Deep Content/Hash Verification
            self._verify_stage_3(table_name)

            self.is_success = True
            print(f"\n{Fore.GREEN}✅ MIGRATION COMPLETED SUCCESSFULLY: {table_name}")
            print(f"{Fore.GREEN}{'='*60}\n")

        except Exception as e:
            self.is_success = False
            print(f"\n{Fore.RED}❌ CRITICAL ERROR: {str(e)}")
            self._print_tui("Rollback", "Executing Rollback...", Fore.RED)
            self.target.rollback(table_name)
            print(f"{Fore.RED}⚠️  SYSTEM RESTORED TO PREVIOUS STATE.")
            print(f"{Fore.RED}{'='*60}\n")

    def _verify_stage_1(self, table_name: str):
        """
