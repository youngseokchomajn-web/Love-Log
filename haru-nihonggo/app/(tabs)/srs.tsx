import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, Image } from 'react-native';
import { useWordStore, calculateWordLevel } from '../../store/useWordStore';
import { getWordImage } from '../../data/wordImages';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { playJapaneseTTS } from '../../utils/tts';

export default function SRSScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const isWarmup = params.mode === 'warmup';
  const isIncorrectReview = params.mode === 'incorrect';

  const getTodayReviewWords = useWordStore(state => state.getTodayReviewWords);
  const getTodayNewWords = useWordStore(state => state.getTodayNewWords);
  const getIncorrectWords = useWordStore(state => state.getIncorrectWords);
  const reviewWord = useWordStore(state => state.reviewWord);

  const settings = useWordStore(state => state.settings);
  const [queue, setQueue] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [showHint, setShowHint] = useState(false);

  useEffect(() => {
    if (isIncorrectReview) {
      // 오답 재복습: 틀린 단어(오답 많은 순)만 큐로 구성
      setQueue([...getIncorrectWords()]);
      return;
    }

    const reviews = getTodayReviewWords();
    const news = getTodayNewWords();

    if (isWarmup) {
      // 웜업 모드: 복습 단어만 무작위 20개로 제한하여 부담을 줄임
      setQueue([...reviews].sort(() => 0.5 - Math.random()).slice(0, 20));
    } else {
      setQueue([...reviews, ...news]);
    }
  }, []);

  const handleReview = (isCorrect: boolean) => {
    if (queue.length === 0) return;
    
    const currentWord = queue[currentIndex];
    // "몰라요"(오답)도 오답노트에 집계되도록 countIncorrect 전달
    reviewWord(currentWord.id, isCorrect, !isCorrect);

    if (currentIndex < queue.length - 1) {
      setFlipped(false);
      setShowHint(false);
      setCurrentIndex(prev => prev + 1);
    } else {
      router.back();
    }
  };

  const handleFlip = () => {
    setFlipped(true);
    if (settings.autoPlayAudio) {
      const currentWord = queue[currentIndex];
      playJapaneseTTS(currentWord.hiragana);
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
  const cardImage = getWordImage(currentWord);
  const progress = ((currentIndex + 1) / queue.length) * 100;
  
  let level = calculateWordLevel(currentWord);
  if (isWarmup) level = 0; // 웜업 모드에서는 무조건 힌트 제공
  
  const shouldShowImage = level === 0 || (level === 1 && showHint) || flipped;

  return (
    <View className="flex-1 bg-[#FAF9F6] p-5 pt-10">
      {/* Header */}
      <View className="flex-row justify-between items-center mb-6">
        <TouchableOpacity onPress={() => router.back()}>
          <Ionicons name="close" size={28} color="#333" />
        </TouchableOpacity>
        <Text className="text-gray-500 font-medium text-sm">{isWarmup ? '웜업 모드 🚀 ' : ''}{currentIndex + 1} / {queue.length}</Text>
      </View>

      {/* Progress Bar */}
      <View className="w-full bg-[#E5E5E5] h-2.5 rounded-full mb-8 overflow-hidden">
        <View className="bg-[#8EAAA3] h-full rounded-full" style={{ width: `${progress}%` }} />
      </View>

      {/* Flashcard */}
      <TouchableOpacity 
        className="flex-1 bg-white rounded-3xl p-6 shadow-sm border border-gray-100 items-center mb-10 overflow-hidden"
        activeOpacity={0.9}
        onPress={handleFlip}
      >
        <View className="w-full h-48 bg-[#F0F4F1] rounded-2xl mb-6 items-center justify-center overflow-hidden">
          {shouldShowImage ? (
            cardImage ? (
              <Image
                source={cardImage}
                className="w-full h-full"
                resizeMode="cover"
              />
            ) : (
              <Ionicons name="image-outline" size={64} color="#8EAAA3" />
            )
          ) : (
            level === 1 ? (
              <TouchableOpacity 
                className="items-center justify-center w-full h-full"
                onPress={() => setShowHint(true)}
              >
                <Ionicons name="image-outline" size={36} color="#8EAAA3" className="mb-2" />
                <Text className="text-[#8EAAA3] font-medium">터치해서 힌트 보기</Text>
              </TouchableOpacity>
            ) : (
              <View className="items-center justify-center w-full h-full">
                <Ionicons name="eye-off-outline" size={36} color="#D1E5D5" className="mb-2" />
                <Text className="text-[#A2C4B1] font-medium">스스로 떠올려보세요!</Text>
              </View>
            )
          )}
        </View>

        <Text className="text-xl text-gray-500 mb-2">{currentWord.hiragana}</Text>
        <Text className="text-5xl font-medium text-gray-800 mb-6">{currentWord.kanji || currentWord.hiragana}</Text>
        
        {flipped ? (
          <View className="items-center mt-auto w-full">
            <Text className="text-3xl font-bold text-gray-800 mb-2">{currentWord.korean}</Text>
            {currentWord.pronunciation && (
              <Text className="text-xl text-gray-500 mb-2">[{currentWord.pronunciation}]</Text>
            )}
          </View>
        ) : (
          <View className="items-center mt-auto">
            <Text className="text-gray-400">탭해서 뜻 보기 ↺</Text>
          </View>
        )}
      </TouchableOpacity>

      {/* Action Buttons */}
      <View className="flex-row justify-between h-14 mb-4 w-full">
        {!flipped ? (
          <TouchableOpacity 
            className="flex-1 rounded-full items-center justify-center bg-[#8EAAA3]"
            onPress={handleFlip}
          >
            <Text className="text-lg font-bold text-white">정답 확인하기</Text>
          </TouchableOpacity>
        ) : (
          <>
            <TouchableOpacity 
              className="flex-1 rounded-full items-center justify-center mr-2 bg-[#FBE9E7]"
              onPress={() => handleReview(false)}
            >
              <Text className="text-lg font-bold text-[#D96B6B]">몰라요</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              className="flex-1 rounded-full items-center justify-center ml-2 bg-[#E9F3EB]"
              onPress={() => handleReview(true)}
            >
              <Text className="text-lg font-bold text-[#7EA48F]">알아요</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </View>
  );
}
