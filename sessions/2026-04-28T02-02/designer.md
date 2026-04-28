# 🎨 Designer — 도구의 전문성과 기술적 신뢰도를 전달할 수 있는 다크 모드 기반의 브랜드 아이덴티티(BI)와 대시보드 UI 디자인 가이드를 제작하라.

🎨 Designer: 작업 시작합니다.

# 🛡️ Oracle Migration Tool: Brand Identity & Dashboard UI Design Guide

본 가이드는 **'Sentinel-Flow'** 아키텍처의 기술적 정밀함과 **'Zero-Risk'**라는 비즈니스 가치를 시각화하기 위해 설계되었습니다. 신뢰를 상징하는 Deep Navy와 데이터의 무결성을 강조하는 High-Contrast Accent 컬러를 사용하여, 엔터프라이즈급 솔루션의 전문성을 전달합니다.

---

## 1. Brand Identity (BI) Concept: "The Sentinel Essence"
- **Core Concept:** **"Precision in Motion"** (움직임 속의 정밀함)
- **Visual Metaphor:** 데이터 흐름(Flow)을 감시하는 파수꾼(Sentinel)의 눈, 완벽하게 맞물린 데이터의 격자(Grid), 끊김 없는 연결(Seamless Connection).
- **Tone & Manner:** 
    - **Technical:** 정교한 수치와 상태를 명확히 전달하는 고해밀도 레이아웃.
    - **Trustworthy:** 무게감 있는 다크 테마와 안정적인 타이포그래피.
    - **Advanced:** 최첨단 클라우드 네이티브 기술력을 상징하는 네온 액센트.

---

## 2. Color Palette (Dark Mode Optimized)
데이터의 상태(Success, Failure, Progress)를 즉각적으로 인지할 수 있도록 **'Semantic Color'** 체계를 구축합니다.

| 구분 | Hex Code | 용도 | 시각적 의미 |
| :--- | :--- | :--- | :--- |
| **Base Background** | `#0D1117` | 메인 화면 배경 | 깊이감 있는 공간감 형성 |
| **Surface/Card** | `#161B22` | 카드, 사이드바, 모달 | 레이어 분리 및 계층 구조 형성 |
| **Primary (Accent)** | `#58A6FF` | 핵심 CTA, 진행 중인 Flow | 기술적 진보, 활성 상태(Active) |
| **Success (DIV)** | `#2EA043` | 데이터 무결성 검증 완료 | 무결성(Integrity), 안전, 완료 |
| **Error (Rollback)** | `#F85149` | 오류 발생, 롤백 트리거 | 위험, 중단, 즉각적 조치 필요 |
| **Warning** | `#D29922` | 데이터 불일치 주의, 재시도 | 주의 깊은 모니터링 필요 |
| **Text (Primary)** | `#C9D1D9` | 주요 텍스트, 헤더 | 높은 가독성 확보 |
| **Text (Muted)** | `#8B949E` | 부가 설명, 메타 데이터 | 시각적 위계(Hierarchy) 조절 |

---

## 3. Typography System
데이터의 가독성과 기술적 전문성을 동시에 확보하기 위해 **'Sans-serif'**와 **'Monospace'**를 혼용합니다.

- **UI/Interface (Sans-serif):** `Inter` 또는 `SF Pro Display`
    - 용도: 헤더, 메뉴, 레이블, 설명 문구.
    - 특징: 현대적이고 깔끔한 가독성.
- **Data/Code (Monospace):** `JetBrains Mono` 또는 `Fira Code`
    - 용도: 데이터 수치(Row Count, Size), SQL 쿼리, 로그, 진단 코드(Diagnostic Code).
    - 특징: 글자 간 간격이 일정하여 수치 비교 및 코드 분석에 최적화.

---

## 4. Dashboard UI Design System (Components)

### 4.1. Migration Progress Card (The Pulse)
- **Visual:** Circular Progress Bar + Real-time Percentage.
- **Element:** `Source DB` $\rightarrow$ `Target DB` 화살표 애니메이션.
- **Feature:** 현재 처리 중인 Chunk의 상태를 실시간으로 표시.

### 4.2. DIV Status Indicator (The Integrity Check)
- **Visual:** 하이라이트된 체크리스트 형태.
- **Element:** `Metadata Check [OK]`, `Row Count Check [OK]`, `Checksum [VERIFYING...]`.
- **Feature:** 검증 단계별로 색상 변화(Gray $\rightarrow$ Blue $\rightarrow$ Green).

### 4.3. Sentinel-Flow Pipeline Map (The Architecture)
- **Visual:** Node-based Flow Diagram.
- **Element:** Ingestion $\rightarrow$ Execution $\rightarrow$ DIV $\rightarrow$ Completion 단계를 노드로 표현.
- **Feature:** 특정 노드 클릭 시 해당 단계의 상세 로그 및 Error Log 팝업 연동.

### 4.4. Error & Rollback Alert (The Safety Net)
- **Visual:** 고대비(High-Contrast) 배너 및 글로우(Glow) 효과.
- **Element:** `[CRITICAL] Data Mismatch Detected! Initiating Auto-Rollback...`
- **Feature:** 에러 발생 시 배경에 붉은색 미세한 글로우 효과를 주어 긴급성 전달.

---

## 5. Dashboard Layout Concept
**"Modular Grid System"**을 채택하여 정보의 밀도를 조절합니다.

1.  **Sidebar (Navigation):** 프로젝트 목록, Pipeline 관리, History, Settings.
2.  **Global Header:** 시스템 전체 건강 상태(System Health), 현재 활성 마이그레이션 수, 알림 아이콘.
3.  **Main Content Area:**
    - **Top Row (Summary):** Total Migrated, Success Rate, Active Errors (Small KPI Cards).
    - **Middle Row (Visual Flow):** Sentinel-Flow Pipeline Map (Large Interactive Diagram).
    - **Bottom Row (Detail):** Real-time Log Stream (Monospace) & Data Integrity Table.

📝 다음 단계 제안: 위 디자인 가이드를 바탕으로 실제 대시보드의 **'High-Fidelity Prototype(Figma)'** 또는 **'React/Tailwind 기반 UI 컴포넌트 코드'** 작성을 진행할까요?
