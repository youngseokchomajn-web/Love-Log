import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { useWordStore } from '../../store/useWordStore';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

export default function QuizScreen() {
  const router = useRouter();
  const words = useWordStore(state => state.words);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);

  // Simplified quiz logic for mockup
  const quizWords = words.slice(0, 10);
  
  if (quizWords.length === 0) {
    return (
      <View className="flex-1 bg-[#FAF9F6] justify-center items-center">
        <Text>단어가 부족합니다.</Text>
      </View>
    );
  }

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
          onPress={() => {
            setShowResult(false);
            setSelectedOption(null);
            if (currentIndex < quizWords.length - 1) {
              setCurrentIndex(prev => prev + 1);
            } else {
              router.back();
            }
          }}
        >
          <Text className="text-white font-bold text-lg">다음 단어</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const currentWord = quizWords[currentIndex];
  const progress = ((currentIndex + 1) / 10) * 100;
  const options = ['집', '역', '학교', '공원']; // Mock options

  return (
    <View className="flex-1 bg-[#FAF9F6] p-5 pt-10">
      {/* Header */}
      <View className="flex-row justify-between items-center mb-6">
        <TouchableOpacity onPress={() => router.back()}>
          <Ionicons name="close" size={28} color="#333" />
        </TouchableOpacity>
        <Text className="text-gray-500 font-medium text-sm">{currentIndex + 1} / 10</Text>
      </View>

      {/* Progress */}
      <View className="w-full bg-[#E5E5E5] h-2.5 rounded-full mb-10 overflow-hidden">
        <View className="bg-[#8EAAA3] h-full rounded-full" style={{ width: `${progress}%` }} />
      </View>

      <Text className="text-center text-gray-700 text-lg mb-8">다음 단어의 뜻으로 알맞은 것을 고르세요.</Text>

      <View className="items-center mb-10">
        <Text className="text-xl text-gray-500 mb-1">{currentWord.hiragana}</Text>
        <Text className="text-5xl font-medium text-gray-800">{currentWord.kanji || currentWord.hiragana}</Text>
      </View>

      <View className="flex-1">
        {options.map((opt, idx) => {
          const isSelected = selectedOption === idx;
          const isCorrect = idx === 1; // mock correct answer
          let bgColor = 'bg-white';
          let textColor = 'text-gray-700';
          let borderColor = 'border-gray-200';
          
          if (isSelected) {
            bgColor = isCorrect ? 'bg-[#E9F3EB]' : 'bg-[#FBE9E7]';
            borderColor = isCorrect ? 'border-[#8EAAA3]' : 'border-[#D96B6B]';
          }

          return (
            <TouchableOpacity
              key={idx}
              className={`${bgColor} border ${borderColor} rounded-2xl p-4 mb-4 flex-row items-center`}
              onPress={() => setSelectedOption(idx)}
            >
              <Text className={`${textColor} text-lg font-medium`}>{idx + 1}. {opt}</Text>
            </TouchableOpacity>
          );
        })}
      </View>

      <TouchableOpacity 
        className={`rounded-full py-4 items-center mb-6 ${selectedOption !== null ? 'bg-[#8EAAA3]' : 'bg-gray-300'}`}
        disabled={selectedOption === null}
        onPress={() => setShowResult(true)}
      >
        <Text className="text-white font-bold text-lg">다음 문제</Text>
      </TouchableOpacity>
    </View>
  );
}
