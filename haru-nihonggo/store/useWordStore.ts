import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { seedWords } from '../data/seedWords';

export type WordStatus = 'new' | 'learning' | 'mastered';

export interface Word {
  id: string;
  kanji: string;
  hiragana: string;
  korean: string;
  pronunciation?: string;
  imageKey?: string;
  english: string;
  status: WordStatus;
  nextReviewDate: number;
  interval: number; // in days
  easeFactor: number;
  incorrectCount: number;
}

export interface Settings {
  dailyGoal: number;
  autoPlayAudio: boolean;
  startDate: number; // 학습 시작일(ms) — "함께한 날짜" 계산용
}

export const calculateWordLevel = (word: Word): number => {
  if (word.status === 'new') return 0;
  
  const now = Date.now();
  const daysOverdue = (now - word.nextReviewDate) / (1000 * 60 * 60 * 24);
  
  if (word.interval >= 6) { // Mastered or late-stage learning
    if (daysOverdue > 3) return 1; // Dynamic degradation (Level 1)
    return 2; // Strict recall (Level 2)
  }
  
  // Early learning stage
  if (daysOverdue > 2) return 0; // Degrade to full hint (Level 0)
  return 1; // Normal learning (Toggle hint Level 1)
};

interface WordState {
  words: Word[];
  settings: Settings;
  addWords: (newWords: Word[]) => void;
  updateSettings: (newSettings: Partial<Settings>) => void;
  reviewWord: (id: string, isCorrect: boolean, countIncorrect?: boolean) => void;
  getTodayReviewWords: () => Word[];
  getTodayNewWords: () => Word[];
  getIncorrectWords: () => Word[];
  generateQuiz: (count: number) => { question: Word, options: string[] }[];
  resetData: () => void;
}

// Initial seed data from external file
const INITIAL_WORDS: Word[] = seedWords as Word[];

export const useWordStore = create<WordState>()(
  persist(
    (set, get) => ({
      words: INITIAL_WORDS,
      settings: {
        dailyGoal: 10,
        autoPlayAudio: true,
        startDate: Date.now(),
      },
      
      addWords: (newWords) => set((state) => ({ words: [...state.words, ...newWords] })),
      updateSettings: (newSettings) => set((state) => ({ settings: { ...state.settings, ...newSettings } })),
      
      reviewWord: (id, isCorrect, countIncorrect = false) => set((state) => {
        const words = state.words.map(word => {
          if (word.id !== id) return word;
          
          const now = new Date();
          let newInterval = word.interval;
          let newEaseFactor = word.easeFactor;
          let newStatus = word.status;
          let newIncorrectCount = word.incorrectCount;
          
          if (isCorrect) {
            if (newInterval === 0) newInterval = 1;
            else if (newInterval === 1) newInterval = 6;
            else newInterval = Math.round(newInterval * newEaseFactor);
            
            // 상한 3.0 — 정답마다 무한 증가해 간격이 폭주하는 것을 방지
            newEaseFactor = Math.min(3.0, newEaseFactor + 0.1);
            newStatus = newInterval > 21 ? 'mastered' : 'learning';
          } else {
            newInterval = 1;
            newEaseFactor = Math.max(1.3, newEaseFactor - 0.2);
            newStatus = 'learning';
            if (countIncorrect) {
              newIncorrectCount += 1;
            }
          }
          
          const nextDate = new Date(now.getTime() + newInterval * 24 * 60 * 60 * 1000);
          
          return {
            ...word,
            interval: newInterval,
            easeFactor: newEaseFactor,
            status: newStatus,
            incorrectCount: newIncorrectCount,
            nextReviewDate: nextDate.getTime()
          };
        });
        
        return { words };
      }),
      
      getTodayReviewWords: () => {
        const { words } = get();
        const now = Date.now();
        return words.filter(w => w.status !== 'new' && w.nextReviewDate <= now);
      },
      
      getTodayNewWords: () => {
        const { words, settings } = get();
        const now = Date.now();
        const reviewCount = words.filter(w => w.status !== 'new' && w.nextReviewDate <= now).length;
        
        // 미완료 방지: 복습 카드가 목표치의 1.5배 이상 쌓였다면 새 단어를 줄이거나 중단합니다.
        let maxNew = settings.dailyGoal;
        if (reviewCount > settings.dailyGoal * 1.5) {
            maxNew = Math.max(0, settings.dailyGoal - Math.floor(reviewCount / 2));
        }
        
        if (maxNew === 0) return [];
        return words.filter(w => w.status === 'new').slice(0, maxNew);
      },
      
      getIncorrectWords: () => {
        const { words } = get();
        return words.filter(w => w.incorrectCount > 0).sort((a, b) => b.incorrectCount - a.incorrectCount);
      },
      
      generateQuiz: (count) => {
        const { words } = get();
        // Get up to `count` words that are currently learning or mastered, fallback to all words
        let candidates = words.filter(w => w.status !== 'new');
        if (candidates.length < count) {
            candidates = [...words];
        }
        
        // Shuffle candidates
        const shuffled = [...candidates].sort(() => 0.5 - Math.random());
        const selected = shuffled.slice(0, count);
        
        return selected.map(word => {
            // 정답과 겹치지 않고 서로도 중복되지 않는 오답 3개 선택
            // (한국어 뜻이 중복되는 단어가 있어 정답이 보기에 두 번 나오는 버그 방지)
            const seen = new Set<string>([word.korean]);
            const wrongOptions: string[] = [];
            const pool = words.filter(w => w.id !== word.id).sort(() => 0.5 - Math.random());
            for (const w of pool) {
                if (wrongOptions.length >= 3) break;
                if (seen.has(w.korean)) continue;
                seen.add(w.korean);
                wrongOptions.push(w.korean);
            }

            // Mix correct answer with wrong options
            const options = [...wrongOptions, word.korean].sort(() => 0.5 - Math.random());

            return {
                question: word,
                options
            };
        });
      },
      resetData: () => set({ words: INITIAL_WORDS }),
    }),
    {
      name: 'word-storage',
      storage: createJSONStorage(() => AsyncStorage),
      version: 4,
      migrate: (persistedState: any, version: number) => {
        if (version < 3) {
          // Clean up the corrupted n4_ words from previous versions (최초 1회 마이그레이션)
          const words = (persistedState.words || []).filter((w: any) => !w.id.startsWith('n4_'));
          persistedState = { ...persistedState, words };
        }
        if (version < 4) {
          // v4: 학습 시작일 필드 추가(없으면 지금 시각으로 초기화)
          persistedState = {
            ...persistedState,
            settings: {
              ...(persistedState.settings || {}),
              startDate: persistedState.settings?.startDate ?? Date.now(),
            },
          };
        }
        return persistedState;
      },
      merge: (persistedState: any, currentState: WordState) => {
        const persistedWords = persistedState.words || [];
        
        // 1. 이미 진도가 쌓인 단어의 최신 정적 데이터(뜻, 발음, 한자, 이미지키 등) 동기화 (진도 보존)
        const mergedWords = persistedWords.map((pw: Word) => {
          const cw = INITIAL_WORDS.find(w => w.id === pw.id);
          if (cw) {
            return {
              ...pw,
              kanji: cw.kanji,
              hiragana: cw.hiragana,
              pronunciation: cw.pronunciation,
              korean: cw.korean,
              english: cw.english,
              imageKey: cw.imageKey || pw.imageKey,
            };
          }
          return pw;
        });
        
        const existingIds = new Set(mergedWords.map((w: Word) => w.id));
        
        // 2. 새로 추가된 N4 정제 단어 병합
        const newWords = INITIAL_WORDS.filter(w => !existingIds.has(w.id));
        
        return {
          ...currentState,
          ...persistedState,
          // settings는 얕은 병합으로 새 필드(startDate 등) 기본값을 보존
          settings: { ...currentState.settings, ...(persistedState.settings || {}) },
          words: [...mergedWords, ...newWords]
        };
      }
    }
  )
);
