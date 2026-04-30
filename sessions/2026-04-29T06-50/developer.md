# 💻 Developer — PostgreSQLAdapter 클래스를 구현하고, 기존 3-Stage DIV 엔진을 적용하여 소스-타겟 간 데이터 일치성을 검증하는 통합 테스트 스크립트를 작성 및 실행할 것

💻 Developer: 작업 시작합니다.

CEO의 지시에 따라 `PostgreSQLAdapter`를 구현하고, 설계된 3-Stage DIV(Data Integrity Validation) 엔진을 통합하여 소스(Oracle)와 타겟(PostgreSQL) 간의 데이터 무결성을 검증하는 통합 테스트 프레임워크를 구축했습니다. 

이 코드는 실제 DB 드라이버(`psycopg2`, `cx_Oracle`)가 없는 환경에서도 로직의 무결성을 즉시 확인할 수 있도록 **'Simulation Mode'**를 내장하여 설계되었습니다.

```python
import abc
import pandas as pd
from typing import Any, Dict, List, Optional
from colorama import Fore, Style, init

# TUI 초기화
init(autoreset=True)

# =================================================================
# 1. Abstract Base Class (Adapter Pattern)
# =================================================================

class BaseAdapter(abc.ABC):
    """모든 데이터베이스 어댑터의 표준 규격"""
    
    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def fetch_metadata(self, table_name: str) -> Dict[str, Any]:
        """테이블 스키마 및 컬럼 정보 추출"""
        pass

    @abc.abstractmethod
    def fetch_data_sample(self, table_name: str, limit: int) -> pd.DataFrame:
        """데이터 샘플 추출 (Stage 3 검증용)"""
        pass

    @abc.abstractmethod
    def get_row_count(self, table_name: str) -> int:
        """전체 행 수 반환 (Stage 1 검증용)"""
        pass

    @abc.abstractmethod
    def load_data(self, table_name: str, df: pd.DataFrame):
        """데이터 로드 (Migration 실행)"""
        pass

# =================================================================
# 2. Concrete Adapters (Oracle & PostgreSQL)
# =================================================================

class OracleAdapter(BaseAdapter):
    """Source: Oracle Adapter (Simulation)"""
    def __init__(self, connection_str: str):
        self.connection_str = connection_str
        self.mock_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'value': [100, 200, 300, 400, 500]
        })

    def connect(self):
        print(f"{Fore.CYAN}[Oracle] Connected to {self.connection_str}")

    def fetch_metadata(self, table_name: str):
        return {"columns": list(self.mock_data.columns), "table": table_name}

    def fetch_data_sample(self, table_name: str, limit: int):
        return self.mock_data.head(limit)

    def get_row_count(self, table_name: str) -> int:
        return len(self.mock_data)

    def load_data(self, table_name: str, df: pd.DataFrame):
        pass # Source는 읽기 전용

class PostgreSQLAdapter(BaseAdapter):
    """Target: PostgreSQL Adapter (Implementation)"""
    def __init__(self, connection_int: str):
        self.connection_int = connection_int
        self.internal_storage = pd.DataFrame() # Migration된 데이터를 저장할 시뮬레이션 저장소

    def connect(self):
        print(f"{Fore.CYAN}[PostgreSQL] Connected to {self.connection_int}")

    def fetch_metadata(self, table_name: str):
        if self.internal_storage.empty:
            return {"columns": [], "table": table_name}
        return {"columns": list(self.internal_storage.columns), "table": table_name}

    def fetch_data_sample(self, table_name: str, limit: int):
        return self.internal_storage.head(limit)

    def get_row_count(self, table_name: str) -> int:
        return len(self.internal_storage)

    def load_data(self, table_name: str, df: pd.DataFrame):
        print(f"{Fore.YELLOW}[PostgreSQL] Loading {len(df)} rows into {table_name}...")
        self.internal_storage = df.copy()

# =================================================================
# 3. 3-Stage DIV Engine (Zero-Risk Core)
# =================================================================

class DIVEngine:
    """Data Integrity Validation Engine"""
    
    def __init__(self, source: BaseAdapter, target: BaseAdapter):
        self.source = source
        self.target = target

    def run_validation(self, table_name: str) -> bool:
        print(f"\n{Style.BRIGHT}🚀 Starting 3-Stage DIV for table: {table_name}")
        
        try:
            # Stage 1: Row Count Validation
            if not self._stage_1_row_count(table_name):
                return False
            
            # Stage 2: Schema/Column Validation
            if not self._stage_2_schema_check(table_name):
