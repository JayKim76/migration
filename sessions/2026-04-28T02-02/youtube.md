# 📺 YouTube — 마이그레이션 성공 사례를 시각화한 기술 튜토리얼 영상의 스크립트를 작성하고, 개발자들의 클릭을 유도할 썸네일 브리프를 기획하라.

📺 YouTube: 작업 시작합니다.

CEO의 지시 사항에 따라, **Oracle Migration Tool**의 기술적 신뢰도를 극대화하고 엔지니어들의 'Pain Point(데이터 유실 공포)'를 공략하는 튜토리얼 영상 스크립트와 썸네일 브리프를 기획하였습니다.

---

# 🎬 1. 영상 기획안: "The Zero-Risk Migration"

**[영상 제목(안)]**
- (국문) 데이터 유실 0%, 1TB 오라클 DB를 AWS로 안전하게 옮기는 법 (Sentinel-Flow 아키텍처 공개)
- (영문) How to Migrate 1TB Oracle DB to AWS with Zero Data Loss (Sentinel-Flow Architecture)

**[핵심 타겟]**
- 클라우드 전환 프로젝트를 담당하는 DBA, 인프라 엔지니어, DevOps 엔지니어

**[영상 구조 (Total: 약 8~10분)]**

| 단계 | 시간 | 화면 구성 (Visual) | 오디오/내레이션 (Audio) |
| :--- | :--- | :--- | :--- |
| **1. Hook** | 0:00~0:45 | 어두운 배경, 에러 로그가 쏟아지는 터미널 화면, 붉은색 경고등. 'Migration Failed' 텍스트 강조. | "마이그레이션 중 발견된 데이터 불일치, 그리고 멈춰버린 서비스. 엔지니어에게 가장 끔찍한 순간입니다." |
| **2. Problem** | 0:45~2:00 | 기존 수동 방식의 복잡한 체크리스트, 엑셀 시트, 사람이 일일이 쿼리를 날리는 답답한 과정 시각화. | "기존의 방식은 너무나도 수동적입니다. 검증은 느리고, 휴먼 에치(Human Error)의 위험은 상존하죠." |
| **3. Solution** | 2:00~4:30 | **Sentinel-Flow 아키텍처 다이어그램** 등장. 데이터가 흐르는 레이어(Ingestion $\to$ Execution $\to$ DIV)를 애니메이션으로 표현. | "여기, '검증이 이동을 제어하는' 새로운 패러다임, Sentinel-Flow 아키텍처를 소개합니다." |
| **4. Deep Dive (DIV)** | 4:30~7:00 | **DIV(Data Integrity Validation) 엔진** 작동 화면. Checksum 비교 과정, 해시값이 일치하며 초록색 체크표시($\checkmark$)가 뜨는 클로즈업. | "단순히 옮기는 것이 아닙니다. MD5 해시 기반의 3단계 검증을 통해 단 1바이트의 오차도 허용하지 않습니다." |
| **5. Case Study** | 7:00~8:30 | 실제 1TB 마이그레이션 진행 로그. 에러 발생 시 **Auto-Rollback**이 작동하며 시스템이 안정 상태로 복구되는 대시보드 시각화. | "실제 1TB 규모의 프로젝트에서 발생한 예기치 못한 오류, 시스템은 스스로를 보호하기 위해 즉각 롤백을 수행했습니다." |
| **6. Outro/CTA** | 8:30~9:00 | 깔로 팔레트(Deep Navy/Blue) 기반의 깔끔한 엔딩 카드. 웹사이트 URL 및 기술 백서 다운로드 안내. | "데이터의 무결성, 이제 타협하지 마세요. 지금 바로 Sentinel-Flow를 경험해보세요." |

---

# 🖼️ 2. 썸네일 브리프 (Thumbnail Brief)

개발자들의 클릭을 유도하기 위해 **'기술적 권위(Authority)'**와 **'공포 극복(Relief)'**이라는 두 가지 심리를 공략합니다.

### **Option 1. [The Authority] 기술적 깊이 강조형 (추천)**
*   **컨셉:** 복잡하지만 정교한 아키텍처 다이어그램을 전면에 배치하여 '배울 점이 있는 영상'임을 암시.
*   **비주얼:** 
    *   배경: Designer가 정의한 `#0D1117` (Deep Navy) 기반의 다크 테마.
    *   중앙: Sentinel-Flow의 레이어 구조를 빛나는 네온 블루 라인으로 표현.
    *   텍스트: **"Oracle $\to$ AWS: 1TB Zero-Loss Architecture"** (Bold, White)
*   **기대 효과:** 전문적인 정보를 찾는 시니어 엔지니어의 클릭 유도.

### **Option 2. [The Relief] 결과 중심적 대비형**
*   **컨셉:** '실패(Red)'와 '성공(Green)'의 극명한 시각적 대비를 통해 안도감 제공.
*   **비주얼:** 
    *   좌측: 붉은색 에러 로그와 `FAILED` 텍스트 (Designer의 `#F85149`).
    *   우측: 초록색 체크표시와 `100% INTEGRITY` 텍스트 (Designer의 `#2EA043`).
    *   중앙: 화살표가 좌측에서 우측으로 강하게 이동.
*   **기대 효과:** 마이그레이션 실패 경험이 있는 엔지니어의 페인 포인트 자극.

### **Option 3. [The Minimalist] 코드/터미널 중심형**
*   **컨셉:** 실제 작동하는 터미널 화면(CLI)을 노출하여 '실제 튜토리얼'임을 증명.
*   **비주얼:** 
    *   배경: VS Code 또는 iTerm2의 고해밀도 텍스트 스크린샷.
    *   강조: `[SUCCESS] Data Integrity Verified` 부분에 형광색 하이라이트.
    *   텍스트: **"No More Manual Checks."** (Minimalist Typography)
*   **기대 효과:** 'Hands-on' 실습 영상을 선호하는 개발자 층 공략.

---

# 📝 3. 업로드 메타데이터 (Metadata)

*   **Video Title:** 1TB Oracle DB를 데이터 유실 없이 AWS로 옮기는 법 (Sentinel-Flow 아키텍처 & DIV 엔진)
*   **Description:** 
    마이그레이션의 가장 큰 공포, '데이터 유실'과 '서비스 중단'. 
    본 영상에서는 Sentinel-Flow 아키텍처를 활용하여 1TB 규모의 Oracle 데이터베이스를 AWS로 안전하게 전환한 실제 사례를 다룹니다. 
    
    [주요 내용]
    - Sentinel-Flow: 검증이 제어하는 마이그레이션 파이프라인
    - DIV(Data Integrity Validation) 엔진의 3단계 검증 로직
    - 장애 발생 시 자동 복구를 위한 Auto-Rollback 메커니즘
    
    [관련 자료]
    - 기술 백서 다운로드: [Link]
    - 프로젝트 레포지토리: [Link]
    - 공식 문서: [Link]

*   **Tags:** #OracleMigration #AWS #Database #DataIntegrity #DevOps #DBA #CloudMigration #SentinelFlow #DataEngineering

📝 다음 단계 제안: 영상 제작을 위한 상세 스토리보드(Shot-by-shot) 작성 또는 썸네일 제작을 위한 디자인 에셋(Layered PSD 구조) 설계가 필요하시면 말씀해 주세요.
