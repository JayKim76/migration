# 💻 Developer — 최종 디자인 시안과 구조를 바탕으로, 모바일과 데스크톱 환경 모두에서 완벽하게 반응하는 웹사이트를 구축해주세요. 필요한 기능(예: 문의 폼, 회원가입 API 연동)과 백엔드 데이터 파이프라인까지 구현해야 합니다.

💻 Developer: 작업 시작합니다.

CEO 지시와 디자인 시스템을 종합하여, 랜딩 페이지를 구성하는 **프론트엔드 구조(React/Next.js 기반)**와 필요한 **백엔드 API 및 데이터 파이프라인 스캐폴딩**을 구현합니다.

요구사항이 단순히 '페이지 보여주기'를 넘어 '완벽하게 작동하는 웹사이트 구축'이므로, 저는 컴포넌트 기반의 아키텍처와 명확한 데이터 흐름을 중심으로 코드를 작성하겠습니다.

---

## 🚀 1. 프론트엔드 구현 (React/Next.js Scaffold)

랜딩 페이지는 컴포넌트 단위로 분리하여 관리하는 것이 효율적입니다. 이 구조는 반응형 디자인을 기본으로 하며, 각 단계별 설득 스토리라인(Hooking $\rightarrow$ Solution $\rightarrow$ Proof $\rightarrow$ CTA)을 반영합니다.

### 📂 프로젝트 구조 (Conceptual)

```
/pages
├── index.jsx       // 메인 페이지 (랜딩 페이지)
/components
├── Header.jsx      // 네비게이션 바
├── HeroSection.jsx // 1. 후킹 (Pain Point)
├── SolutionSection.jsx // 2. 해결책 제시 (JAY CORP Methodology)
├── ProofSection.jsx // 3. 신뢰 구축 (Case Study/Data Viz)
├── CtaForm.jsx     // 4. 행동 유도 (가입/문의 폼)
```

### 📄 `components/index.jsx` (핵심 구조 코드)

```jsx
// React/Next.js 기반 랜딩 페이지 메인 파일
import Header from './Header';
import HeroSection from './HeroSection';
import SolutionSection from './SolutionSection';
import ProofSection from './ProofSection';
import CtaForm from './CtaForm';

export default function LandingPage() {
  return (
    <div className="landing-page">
      {/* 1. 헤더: 항상 최상단에 고정되어 CTA 버튼을 노출 */}
      <Header /> 

      <main>
        {/* 1. 후킹 (Hooking): Pain Point 인식 */}
        <HeroSection /> 

        {/* 2. 해결책 제시 (Solution): 우리의 차별화된 방법론 */}
        <SolutionSection /> 

        {/* 3. 신뢰 구축 (Proof): 데이터 기반의 증거 제시 */}
        <ProofSection /> 

        {/* 4. 행동 유도 (CTA): 최종 목표 달성 지점 */}
        <CtaForm /> 
      </main>

      <footer /> 
    </div>
  );
}

// =====================================================================
// 🎨 CSS/Tailwind CSS 기반 반응형 스타일링 가이드 (CSS Module)
/* 
   핵심 원칙: 
   1. Primary: #004A99, Accent: #FF6B3D (CTA)
   2. 모바일 우선(Mobile-First)으로 설계하고, 
      @media queries를 사용하여 데스크톱(min-width: 1024px)에서 레이아웃 확장.
*/
```

### 📝 `components/CtaForm.jsx` (핵심 기능 구현)

가장 중요한 **회원가입/문의 폼** 컴포넌트입니다. 이 폼은 전방의 백엔드 API와 연동됩니다.

```jsx
import React, { useState } from 'react';

function CtaForm() {
  const [formData, setFormData] = useState({ name: '', email: '', type: 'signup', message: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // *** 핵심 로직: 백엔드 API 호출 ***
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // ⚠️ API 연동 지점: 백엔드 엔드포인트 호출
    try {
      const response = await fetch('/api/v1/process-form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, type: formData.type }),
      });

      const result = await response.json();

      if (response.ok) {
        alert('성공적으로 접수되었습니다! 담당자가 곧 연락드리겠습니다.');
        setFormData({ name: '', email: '', type: 'signup', message: '' });
      } else {
        setError(result.message || '처리 중 오류가 발생했습니다. 다시 시도해주세요.');
      }
    } catch (err) {
      setError('네트워크 연결을 확인해주세요.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="cta" className="cta-section">
      <h2 className="text-4xl font-bold text-[#004A99]">지금, 문제 해결을 시작하세요.</h2>
      <p className="text-xl mb-8 text-gray-600">가장 빠르고 정확하게 컨설팅을 받으세요.</p>
      
      <form onSubmit={handleSubmit} className="max-w-xl p-8 bg-white shadow-2xl rounded-lg">
        {/* 폼 타입 선택 (회원가입 vs. 문의) */}
        <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700">문의 유형</label>
            <select 
                name="type" 
                value={formData.type} 
                onChange={handleChange} 
                className="mt-1 block w-full p-3 border border-gray-300 rounded-md focus:ring-[#FF6B3D] focus:border-[#FF6B3D]"
            >
                <option value="signup">✅ 무료 트라이얼 가입 (주요 KPI)</option>
                <option value="inquiry">💬 비즈니스 문의 (세부 상담)</option>
            </select>
        </div>

        {/* 일반 입력 필드 */}
        <input type="text" name="name" placeholder="이름 (필수)" onChange={handleChange} className="form-input" required />
        <input type="email" name="email" placeholder="이메일 주소 (필수)" onChange={handleChange} className="form-input" required />
        
        {/* 문의 메시지 필드 (문의 유형일 때만 활성화 고려) */}
        {formData.type === 'inquiry' && (
            <textarea 
                name="message" 
                placeholder="궁금한 점을 구체적으로 작성해주세요." 
                onChange={handleChange} 
                className="form-input mt-4" 
                rows="4" 
                required
            />
        )}

        {/* 에러 메시지 표시 */}
        {error && <p className="text-red-600 mt-3">{error}</p>}

        {/* CTA 버튼 (가장 중요) */}
        <button 
          type="submit" 
          disabled={loading}
          className="w-full mt-8 py-3 text-lg font-bold text-white bg-[#FF6B3D] hover:bg-[#e65c3a] transition duration-200 disabled:opacity-50"
        >
          {loading ? '처리 중...' : `제출하기 (${formData.type === 'signup' ? '무료 가입' : '문의 상담'})`}
        </button>
      </form>
    </section>
  );
}

export default CtaForm;
```

---

## ⚙️ 2. 백엔드 API 및 데이터 파이프라인 구현 (Node.js/Python)

프론트엔드의 `CtaForm.jsx`가 데이터를 전송할 백엔드 엔드포인트와 데이터 처리 로직을 정의합니다.

### 🌐 API 명세 (Endpoint Definition)

| 엔드포인트 | 메서드 | 기능 | 요청 바디 (JSON) | 응답 (Success) |
| :--- | :--- | :--- | :--- | :--- |
| `/api/v1/process-form` | `POST` | 폼 데이터 수집 및 검증 (가입/문의 통합) | `{ name, email, type, message }` | `{ success: true, message: "접수 완료" }` |
| `/api/v1/signup` | `POST` | (Fallback) 회원가입 처리 (실제 DB 연동) | `{ name, email, password }` | `{ success: true, user_id: 123 }` |

### 💾 데이터 파이프라인 로직 (Pseudo-code: Node.js/Express)

```javascript
// server/api/v1/process-form.js

const express = require('express');
const router = express.Router();
const { sendEmail } = require('../utils/emailService');
const { saveToCRM } = require('../services/crmService');

// POST /api/v1/process-form
router.post('/', async (req, res) => {
    const { name, email, type, message } = req.body;

    // 1. 입력 유효성 검증 (Validation)
    if (!name || !email || !type) {
        return res.status(400).json({ success: false, message: "필수 항목이 누락되었습니다." });
    }

    try {
        // 2. 데이터 저장 (Persistence)
        if (type === 'signup') {
            // 가입 요청은 DB를 거쳐야 하므로 별도 API로 분리하거나, 여기서 회원가입 로직 실행
            await saveToCRM({ name, email, source: 'LandingPage' });
            
            // 가입 성공 시, 사용자에게 환영 메일 발송
            await sendEmail(email, "JAY CORP에 오신 것을 환영합니다!");

        } else if (type === 'inquiry') {
            // 문의 요청은 CRM에 기록하고, 담당자에게 알림 이메일 발송
            await saveToCRM({ name, email, message, source: 'LandingPage' });
            
            // 담당자(Admin)에게 신규 문의 알림 발송
            await sendEmail('admin@jaycorp.com', `[신규 문의] ${name}님으로부터 접수됨: ${message}`);
        }

        // 3. 성공 응답
        res.status(200).json({ success: true, message: "접수가 성공적으로 완료되었습니다." });

    } catch (error) {
        console.error("API 처리 오류:", error);
        res.status(500).json({ success: false, message: "서버 처리 중 예상치 못한 오류가 발생했습니다." });
    }
});

module.exports = router;
```

---

📝 다음 단계 제안:
1. **디자인 확정 및 컴포넌트 세분화:** `HeroSection.jsx`와 `ProofSection.jsx`에 들어갈 실제 데이터 시각화(Data Viz)의 구체적인 예시와 스토리보드를 확정해야 합니다.
2. **API 키 관리 및 테스트:** 백엔드 로직을 테스트하기 위해, 가상의 `emailService`와 `crmService`를 실제 환경에 맞게 초기화(Mocking)하는 작업을 진행해야 합니다.
3. **기술 스택 확정:** (Next.js/React, Node.js/Express, MongoDB/PostgreSQL) 중 최종 스택을 확정하고 개발 환경을 세팅합니다.
