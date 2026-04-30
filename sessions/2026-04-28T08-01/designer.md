# 🎨 Designer — 출력되는 화면에 이전 가이드(흰색 카드 배경, 가이드 컬러 팔레트, 데이터 흐름 애니메이션)를 적용하여 시각적 일관성을 유지하십시오.

🎨 Designer: 작업 시작합니다.

CEO의 지시사항에 따라, `render_dashboard.py`의 시각적 완성도를 높이기 위한 **[Visual Identity & UI Implementation Guide]**를 전달합니다. 이 가이드는 Developer가 `render_dashboard.py` 내의 HTML/CSS(Web) 및 Rich Library(TUI) 코드를 즉시 수정할 수 있도록 구체적인 속성값과 로직을 포함합니다.

---

# 🎨 Dashboard Visual Design Guide (v1.1)

## 1. Brand Color Palette (가이드 컬러)
데이터의 상태(Integrity)를 직관적으로 인지할 수 있도록 고대비(High-Contrast) 팔레트를 적용합니다.

| Category | Hex Code | Usage |
| :--- | :--- | :--- |
| **Primary (Success)** | `#00C853` | Integrity Score 100%, Success Status, Completed Tasks |
| **Secondary (Warning)** | `#FFD600` | Data Mismatch, Warning Status, Partial Migration |
| **Tertiary (Error)** | `#FF1744` | Critical Error, Failed Migration, Data Loss |
| **Accent (Flow)** | `#2979FF` | **Data Flow Animation**, Progress Bar, Active Stream |
| **Background (Card)** | `#FFFFFF` | Web Dashboard Card Background |
| **Surface (Base)** | `#F5F5F7` | Web Dashboard Main Background |

## 2. Web Dashboard: UI Component Specification
Web 모드(`Flask`)를 위한 CSS 및 레이아웃 가이드입니다.

### 2.1 Card System (흰색 카드 배경)
- **Style**: `background: #FFFFFF; border-radius: 12px; border: 1px solid #E0E0E0; box-shadow: 0 4px 20px rgba(0,0,0,0.05);`
- **Padding**: `24px` (여백을 충분히 확보하여 데이터 가독성 증대)

### 2.2 Data Flow Animation (데이터 흐름 시각화)
- **Concept**: 테이블 간 데이터가 이동하는 듯한 'Streaming' 효과를 CSS 애니메이션으로 구현.
- **Implementation (CSS Keyframes)**:
```css
@keyframes flow-line {
  0% { stroke-dashoffset: 100; opacity: 0; }
  50% { opacity: 1; }
  100% { stroke-dashoffset: 0; opacity: 0; }
}
/* 데이터 전송 라인에 적용 */
.flow-path {
  stroke: #2979FF;
  stroke-dasharray: 10;
  animation: flow-line 2s linear infinite;
}
```

## 3. TUI (Terminal UI) Specification
`rich` 라이브ness를 극대화하여 전문적인 CLI 경험을 제공합니다.

### 3.1 Typography & Text Style
- **Header**: `bold magenta` (시스템 경계 구분)
- **Metrics**: `bold cyan` (핵심 수치 강조)
- **Status**: `bold green` (Success) / `bold yellow` (Warning) / `bold red` (Error)

### 3.2 Progress & Flow Implementation
- **Progress Bar**: `Bar` 스타일을 `color="#2979FF"`(Accent Blue)로 고정하여 데이터 흐름을 상징화.
- **Panel Structure**:
  - `rich.panel.Panel`을 사용하여 각 테이블의 상태를 독립된 'Card'처럼 보이게 구성.
  - `border_style="bright_blue"`를 사용하여 데이터 스트림의 연결성 표현.

## 4. Visual Hierarchy (시각적 계층 구조)
1.  **Level 1 (Hero)**: `Integrity Score` (가장 큰 폰트, 강조 컬러)
2.  **Level 2 (Summary)**: `Total Rows`, `Diff Count` (카드 형태의 요약 섹션)
3.  **Level 3 (Detail)**: `Table Status List` (정렬된 테이블 형태)
4.  **Level 4 (Log)**: `Migration Logs` (모노스페이스 폰트, 낮은 채도)

---

📝 다음 단계 제안: Developer는 위 가이드의 CSS 및 Rich Style 속성을 `render_dashboard.py`의 `render_template_string` 및 `Console` 객체 설정에 즉시 반영하십시오.
