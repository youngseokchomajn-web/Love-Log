# Haru Nihonggo (하루 일본어)

하루 일본어 앱 프로젝트입니다. Expo와 React Native 기반으로 작성되었습니다.

## 🎯 개발 목적 (Project Purpose)
일본어 학습자(특히 JLPT N4 등급 중심)를 위해 제작된 어휘 및 단어 학습 앱입니다. 사용자가 매일 꾸준히 일본어 단어를 학습하고 플래시카드(Word Card) 형태로 익힐 수 있도록 돕는 것을 목표로 합니다.

## 📈 현재 진행 상황 (Current Status)
- **UI/UX 디자인 및 기초 세팅:** Expo v56, NativeWind를 통한 기본 테마(따뜻하고 감성적인 디자인) 및 라우팅 구조(Expo Router) 셋업 완료
- **데이터 파이프라인:** JLPT N4 단어 데이터 파싱 및 정제 스크립트(`parse_n4.py`, `update_n4.py`) 작업 진행 중
- **에셋 생성:** 단어별 이미지 자동 생성 파이프라인(`word_card_generator/`, `utils/`) 구축 및 에셋(`assets/images/words/`) 확보 중
- **상태 관리:** Zustand를 이용한 전역 상태 관리 기본 구조 세팅

## 🛠 Tech Stack
- **Framework:** React Native, Expo (v56.0.0)
- **Routing:** Expo Router
- **Styling:** NativeWind (Tailwind CSS)
- **State Management:** Zustand
- **Storage:** AsyncStorage

## 📦 Prerequisites
- Node.js (v18 이상 권장)
- npm 
- iOS Simulator 또는 Android Emulator (선택)
- Expo Go 앱 (실기기 테스트용)

## 🚀 Getting Started

1. **의존성 설치**
   ```bash
   npm install
   ```

2. **개발 서버 실행**
   ```bash
   npm start
   ```

3. **플랫폼별 실행**
   - iOS: `npm run ios`
   - Android: `npm run android`
   - Web: `npm run web`

## 🤖 AI / 봇 가이드 (중요)
프로젝트 내에 AI 어시스턴트(Cursor, Claude, Gemini 등)를 사용할 때 다음 규칙을 준수해야 합니다 (`AGENTS.md` 참고):
- **Expo 버전 주의**: 현재 **Expo v56.0.0**을 사용 중입니다. 코드를 작성하거나 수정하기 전에 반드시 [Expo v56.0.0 공식 문서](https://docs.expo.dev/versions/v56.0.0/)를 기준으로 해야 합니다. 구버전 코드가 삽입되지 않도록 주의하세요.

## 📂 Project Structure
- `app/`: Expo Router 기반의 페이지 및 라우팅 디렉토리
- `components/`: 재사용 가능한 UI 컴포넌트
- `constants/`: 컬러, 테마 등 앱 전반에서 사용하는 상수
- `store/`: Zustand 상태 관리 스토어
- `assets/`: 이미지, 폰트 등 정적 리소스
- `utils/`: 유틸리티 및 헬퍼 함수들
- `data/` & `word_card_generator/`: 데이터 및 단어 카드 생성 관련 파일
