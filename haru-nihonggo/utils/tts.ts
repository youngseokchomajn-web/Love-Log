import * as Speech from 'expo-speech';
import { Platform } from 'react-native';

export const playJapaneseTTS = (text: string) => {
  if (Platform.OS === 'web') {
    // 웹 환경: expo-speech 래퍼의 버그(큐 멈춤, 보이스 할당 오류)를 우회하기 위해 네이티브 Web API 직접 호출
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      // 큐에 막혀서 소리가 안 나는 현상을 방지하기 위해 이전 음성을 취소
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'ja-JP';
      utterance.rate = 0.9;
      
      const voices = window.speechSynthesis.getVoices();
      const preferredVoices = ['Google 日本語', 'Kyoko', 'Otoya', 'Haruka'];
      
      // 고품질 일본어 원어민 우선 검색
      let jaVoice = voices.find(v => preferredVoices.some(pv => v.name.includes(pv)));
      if (!jaVoice) {
        // 차선책: lang 속성이 ja 인 아무 일본어 음성 검색
        jaVoice = voices.find(v => v.lang.toLowerCase().includes('ja'));
      }
      
      if (jaVoice) {
        utterance.voice = jaVoice;
      }
      
      window.speechSynthesis.speak(utterance);
    }
  } else {
    // 모바일(앱) 환경: OS 네이티브 TTS가 매우 안정적이므로 expo-speech 그대로 사용
    Speech.speak(text, {
      language: 'ja-JP',
      rate: 0.9,
    });
  }
};
