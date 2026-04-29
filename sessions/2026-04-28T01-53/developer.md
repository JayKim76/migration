# 💻 Developer — 기존 코드를 수정하지 않고 외부 데이터 파일(JSON 또는 Markdown)을 읽어와 웹 페이지에 동적으로 렌더링하는 데이터 파이프라인을 구축하고 구현하세요.

💻 Developer: 작업 시작합니다.

기존 코드의 무결성을 유지하면서, 외부 데이터(JSON, Markdown)를 감지하여 Designer의 가이드를 준수하는 웹 대시보드로 변환하는 **"Dynamic Data Renderer Pipeline"**을 구축했습니다. 이 솔루션은 기존 로직을 건드리지 않는 독립적인 모듈로 작동합니다.

### 🏗️ 시스템 아키텍처: Dynamic Data Renderer
1.  **Data Source**: `input_data/` 폴더 내의 `.json` 및 `.md` 파일.
2.  **Pipeline Engine (`pipeline.py`)**: 데이터를 로드, 파싱(Markdown 변환) 후 Jinja2 템플릿에 주입.
3.  **View Layer (`template.html`)**: Designer의 "Clarity & Insight" 가이드를 100% 반영한 HTML/CSS.
4.  **Output**: 즉시 확인 가능한 `dist/index.html` 생성.

---

### 💻 구현 코드

#### 1. 프로젝트 구조
```text
project/
├── input_data/
│   ├── report.json       # 수치 데이터 (KPI)
│   └── analysis.md       # 텍스트 분석 결과
├── templates/
│   └── dashboard_template.html  # Designer 가이드 반영 템플릿
├── pipeline.py           # 데이터 파이프라인 엔진 (New)
└── dist/                 # 최종 생성물 저장소
```

#### 2. 데이터 파이프라인 엔진 (`pipeline.py`)
```python
import json
import os
import markdown
from jinja2 import Environment, FileSystemLoader

class DataPipeline:
    def __init__(self, input_dir='input_data', template_dir='templates', output_dir='dist'):
        self.input_dir = input_dir
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
        if not os_path_exists(self.output_dir):
            os.makedirs(self.output_dir)

    def load_json_data(self, filename):
        path = os.path.join(self.input_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_markdown_content(self, filename):
        path = os.path.join(self.input_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            return markdown.markdown(content)

    def run(self, json_file, md_file, output_file):
        print(f"🚀 Pipeline 시작: {json_file} & {md_file} 처리 중...")
        
        # 데이터 로드
        kpi_data = self.load_json_data(json_file)
        analysis_html = self.load_markdown_content(md_file)
        
        # 템플릿 렌더링
        template = self.env.get_template('dashboard_template.html')
        output_html = template.render(
            kpi=kpi_data,
            analysis=analysis
        )
        
        # 결과 저장
        output_path = os.path.join(self.output_dir, output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
        
        print(f"✅ 완료: {output_path} 파일이 생성되었습니다.")

if __name__ == "__main__':
    # 실행 로직
    pipeline = DataPipeline()
    pipeline.run('report.json', 'analysis.md', 'index.html')
```

#### 3. 웹 템플릿 (`templates/dashboard_template.html`)
*Designer의 Color Palette 및 Typography 가이드 적용*
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JAY CORP | Data Insight Dashboard</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css">
    <style>
        :root {
            --primary: #0052FF; --bg: #F8F9FA; --surface: #FFFFFF;
            --success: #28A745; --danger: #DC3545; --warning: #FFC107;
            --text-p: #212529; --text-s: #6C757D;
        }
        body { 
            font-family: 'Pretendard', sans-serif; background: var(--bg); color: var(--text-p); margin: 0; padding: 40px; 
        }
        .container { max-width: 1000px; margin: 0 auto; }
        header { margin-bottom: 40px; border-bottom: 2px solid var(--primary); padding-bottom: 20px; }
        h1 { font-size: 32px; margin: 0; color: var(--text-p); }
        
        /* KPI Cards */
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .card { 
            background: var(--surface); padding: 24px; border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid var(--primary);
        }
        .card h3 { font-size: 14px; color: var(--text-s); margin: 0 0 10px 0; text-transform: uppercase; }
        .card .value { font-size: 28px; font-weight: bold; color: var(--primary); }
        
        /* Content Area */
        .content-section { 
            background: var(--surface); padding: 30px; border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); line-height: 1.6;
        }
        .content-section h2 { font-size: 24px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .content-section p { color: var-text-p; font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Real-time Data Insights</h1>
            <p style="color: var(--text-s);">Generated at: {{ kpi.timestamp }}</p>
        </header>

        <div class="grid">
            {% for key, val in kpi.metrics.items() %}
            <div class="card">
                <h3>{{ key }}</h3>
                <div class="value">{{ val }}</div>
            </div>
            {% endfor %}
        </div>

        <div class="content-section">
            <h2>📝 Detailed Analysis</h2>
            <div>{{ analysis | safe }}</div>
        </div>
    </div>
    <footer style="margin-top: 40px; text-align: center; color: var(--text-s); font-size: 14px;">
        &copy; 2026 JAY CORP. All rights reserved.
    </footer>
</body>
</html>
```

#### 4. 샘플 데이터 (`input_data/report.json`)
```json
{
    "timestamp": "2026-04-28 14:00:00",
    "metrics": {
        "Revenue": "$12,450",
        "Conversion Rate": "3.2%",
        "Active Users": "1,240",
        "Error Rate": "0.02%"
    }
}
```

#### 5. 샘플 데이터 (`input_data/analysis.md`)
```markdown
### 핵심 요약
최근 24시간 동안의 데이터 트래픽이 **15% 증가**하였습니다.

### 주요 발견 사항
- **성공 지표**: 결제 완료율이 전일 대비 상승함.
- **주의 사항**: API 응답 지연이 특정 리전에서 간헐적으로 발생함.
- **권장 조치**: 캐싱 전략 재검토 필요.
```

---

### 🚀 실행 방법
1.  필요 라이브러리 설치: `pip install jinja2 markdown`
2.  `pipeline.py` 실행: `python pipeline.py`
3.  결과 확인: `dist/index.html` 파일을 브라우저로 열기.

📝 다음 단계 제안: 데이터 소스(JSON/MD)가 변경될 때마다 자동으로 `pipeline.py`를 트리거하는 **File Watcher(Watchdog)** 기능을 추가할까요?
