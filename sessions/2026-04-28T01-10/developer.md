# 💻 Developer — 다운로드 실패 로그를 즉시 추적하여 API 응답, 서버 파이프라인 또는 데이터 저장소의 오류 원인을 식별하고, 즉각적인 패치 및 재시도 로직을 구현하십시오.

💻 Developer: 작업 시작합니다.

현재 발생한 다운로드 실패의 원인을 파악하기 위한 **긴급 디버깅 프로토콜**과, 향후 동일 문제 방지를 위한 **Exponential Backoff 기반 재시도 로직(Patch)**을 즉시 적용합니다.

### 1. 긴급 디버깅 프로토콜 (Root Cause Analysis)
로그 추적을 위해 다음 3개 레이어를 즉시 전수 조사합니다.

| 레이어 | 체크포인트 | 확인 방법 |
| :--- | :--- | :--- |
| **API Layer** | HTTP Status Code (4xx, 5xx), Timeout, Payload Size | `Access Log`에서 `status_code` 및 `request_duration` 추출 |
| **Pipeline Layer** | Memory Overflow, Stream Interruption, Transformation Error | `Worker Node`의 `OOM(Out of Memory)` 기록 및 `Buffer` 크기 검증 |
| **Storage Layer** | Disk Full, Permission Denied, S3/DB Connection Timeout | `I/O Error` 로그 및 `Storage Quota` 잔여 용량 확인 |

---

### 2. 긴급 패치: 재시도 및 에러 핸들링 로직 (Python/Tenacity 기반)
단순 실패 시 즉시 종료되지 않고, 지수 백오프(Exponential Backoff)를 적용하여 서버 부하를 최소화하면서 재시도하도록 로직을 업데이트합니다.

```python
import logging
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# 로깅 설정: 에러 발생 시 즉시 추적 가능하도록 상세 기록
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [TraceID: %(name)s] - %(message)s'
)
logger = logging.getLogger("DownloadService")

class RetriableError(Exception):
    """재시도가 가능한 에러 (5xx, Timeout 등)"""
    pass

class PermanentError(Exception):
    """재시도가 불필요한 에러 (4xx, Permission 등)"""
    pass

@retry(
    stop=stop_after_attempt(5),  # 최대 5회 시도
    wait=wait_exponential(multiplier=1, min=2, max=10),  # 2s, 4s, 8s... 식으로 대기 시간 증가
    retry=retry_if_exception_type(RetriableError),
    before_sleep=lambda retry_state: logger.warning(
        f"⚠️ 재시도 중... (시도 횟수: {retry_state.attempt_number}) - 원인: {retry_state.outcome.exception()}"
    )
)
def robust_download(url, save_path):
    try:
        logger.info(f"🚀 다운로드 시작: {url}")
        response = requests.get(url, timeout=30, stream=True)
        
        # 1. API Layer 체크
        if response.status_code >= 500:
            raise RetriableError(f"Server Error: {response.status_code}")
        if 400 <= response.status_code < 500:
            raise PermanentError(f"Client Error: {response.status_code}")
        
        # 2. Pipeline & Storage Layer 체크
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        logger.info(f"✅ 다운로드 완료: {save_path}")
        return True

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise RetriableError(f"Network Issue: {str(e)}")
    except IOError as e:
        # 디스크 용량 부족이나 권한 문제는 재시도해도 실패할 확률이 높으므로 Permanent로 분류
        raise PermanentError(f"Storage/IO Error: {str(e)}")
    except Exception as e:
        logger.error(f"❌ 알 수 없는 치명적 오류: {str(e)}")
        raise e

# 실행 예시
if __name__ == "__main__':
    target_url = "https://example.com/data.zip"
    destination = "./downloads/data.zip"
    
    try:
        robust_download(target_url, destination)
    except PermanentError as e:
        logger.critical(f"🚨 즉시 조치 필요 (수동 개입): {e}")
    except Exception as e:
        logger.critical(f"🚨 시스템 중단 (최종 실패): {e}")
```

---

### 3. 사후 조치 및 모니터링 계획
1.  **Alerting 연동:** `PermanentError` 발생 시 즉시 Slack/PagerDuty로 `Critical` 알림 전송하도록 Webhook 연동.
2.  **Dead Letter Queue (DLQ) 도입:** 재시도 5회 실패 시, 해당 작업의 메타데이터를 별도 DB(DLQ)에 저장하여 실패 리스트를 관리하고 자동 재처리 스케줄러 구축.
3.  **Disk Monitoring:** Storage Layer 에러 방지를 위해 Disk Usage 80% 도달 시 경고 알림 설정.

📝 다음 단계 제안: 현재 서버의 `Error Log` 파일(또는 CloudWatch/Sentry 로그)을 전달해 주시면, 위 로직의 `RetriableError`와 `PermanentError` 분류를 더 정교하게 튜닝하겠습니다.
