# 🎨 Designer — 분석 결과의 가독성을 극대화할 수 있도록 데이터 시각화(표, 차트, 텍스트 스타일) 및 웹 페이지 레이아웃 디자인 가이드를 작성하세요.

🎨 Designer: 작업 시작합니다.

# 📊 데이터 시각화 및 웹 레이아웃 디자인 가이드 (v1.0)

본 가이드는 분석된 데이터의 가독성을 극대화하고, 사용자에게 신뢰감 있는 인사이트를 전달하기 위해 설계되었습니다. 코드 수정 없이 CSS 및 레이아웃 구조 설계에 즉시 적용 가능한 가이드라인입니다.

## 1. 디자인 컨셉 (Design Concept)
- **Concept Name:** "Clarity & Insight"
- **Core Value:** 데이터의 계층 구조(Hierarchy) 명확화, 인지 부하(Cognational Load) 최소화, 즉각적인 의사결정 지원.
- **Visual Tone:** Professional, Clean, Data-driven.

## 2. 비주얼 시스템 (Visual System)

### 🎨 컬러 팔레트 (Color Palette)
| 용도 | Hex Code | 설명 |
| :--- | :--- | :--- |
| **Primary (Brand)** | `#0052FF` | 핵심 지표 및 강조 텍스트 (신뢰감) |
| **Background** | `#F8F9FA` | 전체 페이지 배경 (눈의 피로도 감소) |
| **Surface (Card)** | `#FFFFFF` | 데이터 카드 및 컨테이너 배경 |
| **Success** | `#28A745` | 긍정적 지표, 정상 상태, 완료 |
| **Danger** | `#DC3545` | 부정적 지표, 에러, 위험 상태 |
| **Warning** | `#FFC107` | 주의 필요, 진행 중, 경고 |
| **Text (Primary)** | `#212529` | 주요 타이틀 및 본문 |
| **Text (Secondary)** | `#6C757D` | 부가 설명, 캡션, 메타 데이터 |

### 🔡 타이포그래피 (Typography)
- **Font Family:** `Pretendard`, `Inter`, `sans-serif` (가독성 중심의 Sans-serif 권장)
- **Hierarchy:**
    - **H1 (Page Title):** `32px / Bold / #212529` (페이지의 주제)
    - **H2 (Section Title):** `24px / Semi-bold / #212529` (데이터 섹션 구분)
    - **H3 (Card Title):** `18px / Medium / #212529` (개별 차트/표 제목)
    - **Body (Main):** `16px / Regular / #212529` (분석 내용 본문)
    - **Caption/Small:** `14px / Regular / #6C757D` (날짜, 단위, 부가 설명)

## 3. 레이아웃 가이드 (Layout Guide)

### 🏗️ 페이지 구조 (Modular Dashboard Structure)
1.  **Header Section:** 분석 대상 명칭, 분석 일시, 전체 요약(Summary) Score.
2.  **KPI Hero Cards:** 가장 중요한 핵심 지표 3~4개를 상단에 가로로 배치 (Large Font 적용).
3.  **Main Content Grid (2-Column):**
    - **Left (Large):** 상세 트렌드 차트 (Line/Area Chart) - 시간 흐름에 따른 변화.
    *   **Right (Small):** 구성비 차트 (Donut/Pie Chart) - 현재 상태의 비중.
4.  **Detailed Data Section:** 상세 수치 데이터 테이블 (Full Width).
5.  **Action/Insight Footer:** 분석 결과에 따른 권장 조치(Next Step) 및 CTA 버튼.

## 4. 컴포넌트 디자인 상세 (Component Detail)

### 📋 데이터 테이블 (Data Table)
- **Header:** `Background: #F1F3F5`, `Font-weight: Bold`, `Sticky Header` 적용.
- **Row:** `Border-bottom: 1px solid #E9ECEF`.
- **Alignment:** 
    - 텍스트 데이터: `Left-aligned`
    - 숫자/수치 데이터: `Right-aligned` (자릿수 맞춤을 통해 비교 용이성 확보)
    - 상태(Status) 태그: `Center-aligned`
- **Zebra Striping:** 행 간 구분을 위해 `nth-child(even)`에 아주 연한 회색 적용.

### 📊 차트 스타일 (Chart Styling)
- **Line Chart:** `Stroke-width: 3px`, `Area Fill: Primary Color (Opacity 10%)`.
- **Bar Chart:** `Border-radius: 4px`, `Gap: 8px`.
- **Tooltips:** 마우스 오버 시 `Background: #212529`, `Text: #FFFFFF`, `Padding: 8px 12px`.

### 🃏 데이터 카드 (Data Card)
- **Shadow:** `box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05)`.
- **Border:** `1px solid #E9ECEF`.
- **Padding:** `24px` (내부 여백을 충분히 확보하여 정보 밀도 조절).

📝 다음 단계 제안: 위 가이드를 바탕으로 실제 웹 페이지에 적용할 CSS 스타일시트(CSS Variables 포함) 작성을 요청하세요.
