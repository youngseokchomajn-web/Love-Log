import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type WordStatus = 'new' | 'learning' | 'mastered';

export interface Word {
  id: string;
  kanji: string;
  hiragana: string;
  korean: string;
  english: string;
  status: WordStatus;
  nextReviewDate: string; // ISO date string
  interval: number; // in days
  easeFactor: number;
  incorrectCount: number;
}

interface WordState {
  words: Word[];
  dailyLimit: number;
  addWords: (newWords: Word[]) => void;
  reviewWord: (id: string, isCorrect: boolean) => void;
  getTodayReviewWords: () => Word[];
  getTodayNewWords: () => Word[];
  getIncorrectWords: () => Word[];
}

// Initial mock data to show UI
const INITIAL_WORDS: Word[] = [
  { id: '1', kanji: '駅', hiragana: 'えき', korean: '역', english: 'Station', status: 'new', nextReviewDate: new Date().toISOString(), interval: 0, easeFactor: 2.5, incorrectCount: 0 },
  { id: '2', kanji: '学校', hiragana: 'がっこう', korean: '학교', english: 'School', status: 'new', nextReviewDate: new Date().toISOString(), interval: 0, easeFactor: 2.5, incorrectCount: 0 },
  { id: '3', kanji: '本', hiragana: 'ほん', korean: '책', english: 'Book', status: 'learning', nextReviewDate: new Date(Date.now() - 86400000).toISOString(), interval: 1, easeFactor: 2.5, incorrectCount: 1 },
  { id: '4', kanji: '猫', hiragana: 'ねこ', korean: '고양이', english: 'Cat', status: 'learning', nextReviewDate: new Date(Date.now() - 86400000).toISOString(), interval: 1, easeFactor: 2.3, incorrectCount: 2 },
];

export const useWordStore = create<WordState>()(
  persist(
    (set, get) => ({
      words: INITIAL_WORDS,
      dailyLimit: 10,
      
      addWords: (newWords) => set((state) => ({ words: [...state.words, ...newWords] })),
      
      reviewWord: (id, isCorrect) => set((state) => {
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
            
            newEaseFactor = newEaseFactor + 0.1;
            newStatus = newInterval > 21 ? 'mastered' : 'learning';
          } else {
            newInterval = 1;
            newEaseFactor = Math.max(1.3, newEaseFactor - 0.2);
            newStatus = 'learning';
            newIncorrectCount += 1;
          }
          
          const nextDate = new Date(now.getTime() + newInterval * 24 * 60 * 60 * 1000);
          
          return {
            ...word,
            interval: newInterval,
            easeFactor: newEaseFactor,
            status: newStatus,
            incorrectCount: newIncorrectCount,
            nextReviewDate: nextDate.toISOString()
          };
        });
        
        return { words };
      }),
      
      getTodayReviewWords: () => {
        const { words } = get();
        const now = new Date().toISOString();
        return words.filter(w => w.status !== 'new' && w.nextReviewDate <= now);
      },
      
      getTodayNewWords: () => {
        const { words, dailyLimit } = get();
        return words.filter(w => w.status === 'new').slice(0, dailyLimit);
      },
      
      getIncorrectWords: () => {
        const { words } = get();
        return words.filter(w => w.incorrectCount > 0).sort((a, b) => b.incorrectCount - a.incorrectCount);
      }
    }),
    {
      name: 'word-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
