import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useWordStore } from '../../store/useWordStore';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import * as Speech from 'expo-speech';

export default function QuizScreen() {
  const router = useRouter();
  const generateQuiz = useWordStore(state => state.generateQuiz);
  
  const [quizList, setQuizList] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);

  useEffect(() => {
    // Generate 10 quiz questions on mount
    const qs = generateQuiz(10);
    setQuizList(qs);
  }, []);

  if (quizList.length === 0) {
    return (
      <View className="flex-1 bg-[#FAF9F6] justify-center items-center">
        <Text>퀴즈를 불러오는 중입니다...</Text>
      </View>
    );
  }

  const currentQuiz = quizList[currentIndex];
  const progress = ((currentIndex + 1) / quizList.length) * 100;

  const handleNext = () => {
    setShowResult(false);
    setSelectedOption(null);
    if (currentIndex < quizList.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      router.back();
    }
  };

  if (showResult) {
    return (
      <View className="flex-1 bg-[#FAF9F6] items-center p-5 pt-20">
        <View className="w-32 h-32 bg-[#D1E0D7] rounded-full items-center justify-center mb-8 relative">
          <Ionicons name="happy" size={60} color="#333" />
          <Text className="absolute -top-2 right-0 text-2xl">✨</Text>
          <Text className="absolute top-1/2 -left-4 text-xl">🎉</Text>
        </View>
        <Text className="text-3xl font-bold text-gray-800 mb-4">정답이에요!</Text>
        <Text className="text-lg text-gray-600 mb-1">잘했어요! 👏</Text>
        <Text className="text-lg text-gray-600 mb-12">계속해봐요!</Text>
        
        <TouchableOpacity 
          className="bg-[#8EAAA3] rounded-full py-4 px-8 w-full items-center mt-auto mb-10"
          onPress={handleNext}
        >
          <Text className="text-white font-bold text-lg">다음 단어</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const speak = () => {
    Speech.speak(currentQuiz.question.hiragana, { language: 'ja-JP' });
  };

  return (
    <View className="flex-1 bg-[#FAF9F6] p-5 pt-10">
      <View className="flex-row justify-between items-center mb-6">
        <TouchableOpacity onPress={() => router.back()}>
          <Ionicons name="close" size={28} color="#333" />
        </TouchableOpacity>
        <Text className="text-gray-500 font-medium text-sm">{currentIndex + 1} / {quizList.length}</Text>
      </View>

      <View className="w-full bg-[#E5E5E5] h-2.5 rounded-full mb-10 overflow-hidden">
        <View className="bg-[#8EAAA3] h-full rounded-full" style={{ width: `${progress}%` }} />
      </View>

      <Text className="text-center text-gray-700 text-lg mb-8">다음 단어의 뜻으로 알맞은 것을 고르세요.</Text>

      <TouchableOpacity className="items-center mb-10" onPress={speak}>
        <Text className="text-xl text-gray-500 mb-1">{currentQuiz.question.hiragana} <Ionicons name="volume-medium" size={16} /></Text>
        <Text className="text-5xl font-medium text-gray-800">{currentQuiz.question.kanji || currentQuiz.question.hiragana}</Text>
      </TouchableOpacity>

      <View className="flex-1">
        {currentQuiz.options.map((opt: string, idx: number) => {
          const isSelected = selectedOption === idx;
          const isCorrect = opt === currentQuiz.question.korean;
          
          let bgColor = 'bg-white';
          let textColor = 'text-gray-700';
          let borderColor = 'border-gray-200';
          
          if (selectedOption !== null) {
            // Reveal answer logic
            if (isCorrect) {
               bgColor = 'bg-[#E9F3EB]';
               borderColor = 'border-[#8EAAA3]';
            } else if (isSelected && !isCorrect) {
               bgColor = 'bg-[#FBE9E7]';
               borderColor = 'border-[#D96B6B]';
            }
          } else if (isSelected) {
            bgColor = 'bg-gray-100';
          }

          return (
            <TouchableOpacity
              key={idx}
              className={`${bgColor} border ${borderColor} rounded-2xl p-4 mb-4 flex-row items-center`}
              onPress={() => setSelectedOption(idx)}
              disabled={selectedOption !== null}
            >
              <Text className={`${textColor} text-lg font-medium`}>{idx + 1}. {opt}</Text>
            </TouchableOpacity>
          );
        })}
      </View>

      <TouchableOpacity 
        className={`rounded-full py-4 items-center mb-6 ${selectedOption !== null ? 'bg-[#8EAAA3]' : 'bg-gray-300'}`}
        disabled={selectedOption === null}
        onPress={() => {
          const isCorrect = currentQuiz.options[selectedOption] === currentQuiz.question.korean;
          // 퀴즈 결과도 학습 스탯(SRS)에 반영
          useWordStore.getState().reviewWord(currentQuiz.question.id, isCorrect);

          if (isCorrect) {
            setShowResult(true);
          } else {
            handleNext();
          }
        }}
      >
        <Text className="text-white font-bold text-lg">다음 문제</Text>
      </TouchableOpacity>
    </View>
  );
}
