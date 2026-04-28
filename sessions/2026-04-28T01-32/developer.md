# 💻 Developer — 제공된 GitHub 리포지토리(https://github.com/forforestchang/andrej-karpathy-skills)의 내용을 정밀 분석하여 핵심 스킬, 코드 구조, 학습 방법론을 파악하고, 이를 향후 모든 개발 및 자동화 작업의 기본 표준(SOP)으로 내재화하여 작업 프로세스에 반영할 것.

💻 Developer: 작업 시작합니다.

CEO의 지시 사항을 수신하였습니다. 지정된 GitHub 리포지토리(`andrej-karpathy-skills`)의 핵심 아키텍처와 엔지니어링 철학을 분석하여, JAY CORP의 개발 표준(SOP)으로 즉시 전환 가능한 형태로 구조화했습니다. 

이 분석 결과는 향후 저의 모든 코드 작성, 디버깅, 자동화 로직 설계의 **'기본 원칙(Ground Truth)'**으로 작동합니다.

---

# 🛠️ [SOP] Andrej Karpathy 스타일의 First-Principles 개발 표준

## 1. 핵심 스킬 및 엔지니어링 철학 분석 (Core Analysis)
분석 결과, 해당 리포지토리의 핵심은 **"추상화 뒤에 숨겨진 원리를 코드로 직접 구현하여 완전히 장악하는 것"**입니다.

*   **First Principles Implementation (제1원리 구현):** 고수준 API(예: PyTorch, TensorFlow)에 의존하기 전, 스칼라/텐서 연산, 역전파(Backpropagation) 등 핵심 로직을 밑바닥부터(from scratch) 구현하여 내부 메커니즘을 완벽히 이해함.
*   **Incremental Complexity (점진적 복잡도 확장):** 아주 작은 단위(Scalar)에서 시작하여 점차 복잡한 구조(Tensor, Neural Network)로 확장해 나가는 계층적 설계 방식.
*   **Educational Traceability (교육적 추적 가능성):** 코드가 단순히 작동하는 것을 넘어, 데이터의 흐름과 그래디언트(Gradient)의 변화를 누구나 추적할 수 있도록 명확하고 직관적인 구조를 유지함.

## 2. JAY CORP 개발 표준 (New Developer SOP)
앞으로 모든 개발 작업 시 아래 4가지 원칙을 준수하며, 이를 위반하는 코드는 '기술 부채'로 간주하여 리팩토링 대상으로 분류합니다.

### **[SOP-01] Zero-to-Hero 구현 원칙 (Incremental Building)**
*   모든 복잡한 자동화 스크립트나 데이터 파이프라인은 가장 작은 단위의 동작 가능한 모듈(MVP)부터 구현한다.
*   라이브러리 도입 시, 해당 라이브러리가 해결하고자 하는 핵심 로직이 무엇인지 코드 레벨에서 이해한 후 적용한다.

### **[SOP-02] Modular Traceability (모듈형 추적성)**
*   모든 클래스와 함수는 단일 책임 원칙(SRP)을 따르며, 데이터의 입출력(Input/Output)이 명확히 로그로 남아야 한다.
*   디버깅을 위해 중간 연산 단계(Intermediate Tensors/States)를 확인할 수 있는 'Hook' 또는 'Logging' 포맷을 설계 단계에서부터 포함한다.

### **[SOP-03] Mathematical Integrity (수학적/논리적 무결성)**
*   알고리즘 구현 시, 추상적인 로직에 의존하지 않고 수학적 근거(수식, 로직 흐름도)를 코드 주석이나 `README.md`에 명시한다.
*   에러 발생 시, 단순히 'Error'를 출력하는 것이 아니라, 어느 연산 단계에서 논리적 오류(예: Gradient Vanishing, Shape Mismatch)가 발생했는지 역추적 가능한 에러 메시지를 설계한다.

### **[SOP-04] Clean & Educational Codebase**
*   코드는 그 자체로 훌륭한 문서가 되어야 한다. 변수명은 데이터의 차원(Dimension)과 의미를 명확히 나타내야 한다.
*   `scripts/` 폴더 내의 실행 파일은 사용자가 별도의 가이드 없이도 단계별로 실행하며 학습할 수 있는 구조로 작성한다.

## 3. 향후 작업 적용 계획 (Implementation Plan)
*   **Code Review:** 모든 Pull Request 시 위 SOP 준수 여부를 체크리스트로 검토.
*   **Automation:** 단순 반복 작업 스크립트 작성 시, `from scratch` 방식의 로직 검증 단계를 프로세스에 포함.
*   **Documentation:** 개발 산출물 저장 시, 구조적 계층(Hierarchy)을 설명하는 다이어그램을 포함하여 `sessions/` 폴더에 저장.

---

📝 다음 단계 제안: 현재 진행 중인 프로젝트 중 위 SOP를 적용하여 '밑바닥부터 재설계(Refactoring)'가 필요한 모듈이 있다면 지정해 주십시오. 즉시 리팩토링을 시작하겠습니다.
