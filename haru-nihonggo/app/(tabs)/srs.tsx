import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useWordStore } from '../../store/useWordStore';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function SRSScreen() {
  const router = useRouter();
  const getTodayReviewWords = useWordStore(state => state.getTodayReviewWords);
  const getTodayNewWords = useWordStore(state => state.getTodayNewWords);
  const reviewWord = useWordStore(state => state.reviewWord);

  const [queue, setQueue] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);

  useEffect(() => {
    const reviews = getTodayReviewWords();
    const news = getTodayNewWords();
    setQueue([...reviews, ...news]);
  }, []);

  const handleReview = (isCorrect: boolean) => {
    if (queue.length === 0) return;
    
    const currentWord = queue[currentIndex];
    reviewWord(currentWord.id, isCorrect);

    if (currentIndex < queue.length - 1) {
      setFlipped(false);
      setCurrentIndex(prev => prev + 1);
    } else {
      router.back();
    }
  };

  if (queue.length === 0) {
    return (
      <View className="flex-1 bg-[#FAF9F6] justify-center items-center p-4 pt-12">
        <Ionicons name="happy" size={80} color="#E9F3EB" />
        <Text className="text-2xl font-bold text-gray-800 mt-6 mb-2">세션 완료!</Text>
        <Text className="text-gray-500 text-center mb-8">오늘 복습할 단어를 모두 마쳤습니다. 대단해요! 🎉</Text>
        <TouchableOpacity 
          className="bg-[#7EA48F] px-8 py-3 rounded-full w-full items-center"
          onPress={() => router.back()}
        >
          <Text className="text-white font-bold text-lg">홈으로 돌아가기</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const currentWord = queue[currentIndex];
  const progress = ((currentIndex + 1) / queue.length) * 100;

  return (
    <View className="flex-1 bg-[#FAF9F6] p-5 pt-10">
      {/* Header */}
      <View className="flex-row justify-between items-center mb-6">
        <TouchableOpacity onPress={() => router.back()}>
          <Ionicons name="close" size={28} color="#333" />
        </TouchableOpacity>
        <Text className="text-gray-500 font-medium text-sm">{currentIndex + 1} / {queue.length}</Text>
      </View>

      {/* Progress Bar */}
      <View className="w-full bg-[#E5E5E5] h-2.5 rounded-full mb-8 overflow-hidden">
        <View className="bg-[#8EAAA3] h-full rounded-full" style={{ width: `${progress}%` }} />
      </View>

      {/* Flashcard */}
      <TouchableOpacity 
        className="flex-1 bg-white rounded-3xl p-6 shadow-sm border border-gray-100 items-center mb-10 overflow-hidden"
        activeOpacity={0.9}
        onPress={() => setFlipped(true)}
      >
        <View className="w-full h-48 bg-[#F0F4F1] rounded-2xl mb-6 items-center justify-center">
          {/* Placeholder for train station illustration */}
          <Ionicons name="train-outline" size={64} color="#8EAAA3" />
        </View>

        <Text className="text-xl text-gray-500 mb-2">{currentWord.hiragana}</Text>
        <Text className="text-5xl font-medium text-gray-800 mb-6">{currentWord.kanji || currentWord.hiragana}</Text>
        
        {flipped ? (
          <View className="items-center mt-auto w-full">
            <Text className="text-3xl font-bold text-gray-800">{currentWord.korean}</Text>
          </View>
        ) : (
          <View className="items-center mt-auto">
            <Text className="text-gray-400">탭해서 뜻 보기 ↺</Text>
          </View>
        )}
      </TouchableOpacity>

      {/* Action Buttons */}
      <View className="flex-row justify-between h-14 mb-4">
        <TouchableOpacity 
          className={`flex-1 rounded-full items-center justify-center mr-2 ${flipped ? 'bg-[#FBE9E7]' : 'bg-[#F0F0F0]'}`}
          disabled={!flipped}
          onPress={() => handleReview(false)}
        >
          <Text className={`text-lg font-medium ${flipped ? 'text-[#D96B6B]' : 'text-gray-400'}`}>몰라요</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          className={`flex-1 rounded-full items-center justify-center ml-2 ${flipped ? 'bg-[#E9F3EB]' : 'bg-[#F0F0F0]'}`}
          disabled={!flipped}
          onPress={() => handleReview(true)}
        >
          <Text className={`text-lg font-medium ${flipped ? 'text-[#7EA48F]' : 'text-gray-400'}`}>알아요</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
