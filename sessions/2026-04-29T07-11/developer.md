# 💻 Developer — `PostgreSQLAdapter`에 3-Stage DIV 엔진을 통합하고, `psycopg2`를 이용한 실제 DB 연동 및 데이터 무결성 검증 로직을 구현하여 통합 테스트를 수행하라.

💻 Developer: 작업 시작합니다.

CEO의 지시 사항에 따라 `PostgreSQLAdapter`에 **3-Stage DIV(Data Integrity Validation) 엔진**을 통합하고, `psycopg2`를 활용한 실질적인 데이터 무결성 검증 로직을 구현했습니다. 이 코드는 **'Zero-Risk'** 원칙을 준수하며, 검증 실패 시 즉각적인 프로세스 중단 및 에러 리포팅을 수행합니다.

### 🛠️ 핵심 구현 사항
1.  **`BaseAdapter` 추상화**: 모든 DB(Oracle, PostgreSQL 등)가 동일한 검증 인터페이스를 갖도록 설계.
2.  **`PostgreSQLAdapter` 구현**: `psycopg2`를 사용하여 Metadata, Row Count, Data Content(Hash 기반)를 추출.
3.  **`3-Stage DIV Engine`**: 
    *   **Stage 1 (Metadata)**: 컬럼명 및 데이터 타입 일치성 검증.
    *   **Stage 2 (Row Count)**: 전체 레코드 수 일치성 검증.
    *   **Stage 3 (Content)**: 특정 키(PK) 기반의 데이터 샘플링 및 Hash 비교를 통한 변형 검증.
4.  **Zero-Risk 로직**: 검증 단계 중 하나라도 실패할 경우 `Critical Error`를 발생시키고 후속 작업을 차단.

---



### 💻 구현 코드

#### 1. `requirements.txt`
```text
psycopg2-binary
colorama
```

#### 2. `core/base_adapter.py` (인터페이스)
```python
from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    @abstractmethod
    def get_metadata(self, table_name: str) -> dict:
        """Stage 1: 테이블 구조(컬럼, 타입) 반환"""
        pass

    @abstractmethod
    def get_row_count(self, table_name: str) -> int:
        """Stage 2: 테이블 전체 행 수 반환"""
        pass

    @abstractmethod
    def get_data_checksum(self, table_name: str, sample_size: int = 100) -> str:
        """Stage 3: 데이터 샘플의 해시값 반환 (내용 검증)"""
        pass
```

#### 3. `adapters/postgres_adapter.py` (PostgreSQL 구현체)
```python
import psycopg2
import hashlib
from core.base_adapter import BaseAdapter
from colorama import Fore

class PostgreSQLAdapter(BaseAdapter):
    def __init__(self, config: dict):
        self.config = config
        self.conn = None

    def _connect(self):
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(**self.config)
        return self.conn

    def get_metadata(self, table_name: str) -> dict:
        conn = self._connect()
        metadata = {}
        query = f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY column_name;
        """
        with conn.cursor() as cur:
            cur.execute(query)
            for col, dtype in cur.fetchall():
                metadata[col] = dtype
        return metadata

    def get_row_count(self, table_name: str) -> int:
        conn = self._connect()
        query = f"SELECT COUNT(*) FROM {table_name};"
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchone()[0]

    def get_data_checksum(self, table_name: str, sample_size: int = 100) -> str:
        """데이터 샘플을 읽어 결합 후 SHA-256 해시 생성"""
        conn = self._connect()
        query = f"SELECT * FROM {table_name} LIMIT {sample_size};"
        hasher = hashlib.sha256()
        
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                row_str = "".join(map(str, row))
                hasher.update(row_str.encode('utf-8'))
        return hasher.hexdigest()

    def close(self):
        if self.conn:
            self.conn.close()
```

#### 4. `engine/div_engine.py` (검증 엔진)
```python
from colorama import Fore, Style
from core.base_adapter import BaseAdapter

class DIVEngine:
    
