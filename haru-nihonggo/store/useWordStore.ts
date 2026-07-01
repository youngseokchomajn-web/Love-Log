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
}

interface WordState {
  words: Word[];
  settings: Settings;
  addWords: (newWords: Word[]) => void;
  updateSettings: (newSettings: Partial<Settings>) => void;
  reviewWord: (id: string, isCorrect: boolean) => void;
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
      },
      
      addWords: (newWords) => set((state) => ({ words: [...state.words, ...newWords] })),
      updateSettings: (newSettings) => set((state) => ({ settings: { ...state.settings, ...newSettings } })),
      
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
        return words.filter(w => w.status === 'new').slice(0, settings.dailyGoal);
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
            // Pick 3 random wrong answers (korean meanings)
            const otherWords = words.filter(w => w.id !== word.id);
            const wrongOptions = [...otherWords].sort(() => 0.5 - Math.random()).slice(0, 3).map(w => w.korean);
            
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
    }
  )
);
