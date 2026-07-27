import React, { useState, useCallback } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Image } from 'expo-image';
import { useWordStore, calculateWordLevel } from '../../store/useWordStore';
import { getWordImage } from '../../data/wordImages';
import { useRouter, useLocalSearchParams, useFocusEffect } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { playJapaneseTTS } from '../../utils/tts';
import { FeedbackModal } from '../../components/FeedbackModal';
import { QuickFeedbackButton } from '../../components/QuickFeedbackButton';

export default function SRSScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const isWarmup = params.mode === 'warmup';
  const isIncorrectReview = params.mode === 'incorrect';

  const getTodayReviewWords = useWordStore(state => state.getTodayReviewWords);
  const getTodayNewWords = useWordStore(state => state.getTodayNewWords);
  const getIncorrectWords = useWordStore(state => state.getIncorrectWords);
  const reviewWord = useWordStore(state => state.reviewWord);
  const toggleBookmark = useWordStore(state => state.toggleBookmark);
  const toggleFurigana = useWordStore(state => state.toggleFurigana);
  const recordDailyStudy = useWordStore(state => state.recordDailyStudy);

  const settings = useWordStore(state => state.settings);
  const words = useWordStore(state => state.words);
  const [queue, setQueue] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [feedbackVisible, setFeedbackVisible] = useState(false);

  // 탭 화면은 언마운트되지 않으므로, 포커스될 때마다 모드에 맞춰 큐를 재구성한다.
  useFocusEffect(
    useCallback(() => {
      setCurrentIndex(0);
      setFlipped(false);
      setShowHint(false);

      if (isIncorrectReview) {
        setQueue([...getIncorrectWords()]);
        return;
      }

      const reviews = getTodayReviewWords();
      const news = getTodayNewWords();

      if (isWarmup) {
        setQueue([...reviews].sort(() => 0.5 - Math.random()).slice(0, 20));
      } else {
        setQueue([...reviews, ...news]);
      }
    }, [params.mode])
  );

  const handleReview = (isCorrect: boolean) => {
    if (queue.length === 0) return;
    
    const currentWord = queue[currentIndex];
    reviewWord(currentWord.id, isCorrect, !isCorrect);
    recordDailyStudy(); // 🔥 스트릭 기록

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

  const rawWord = queue[currentIndex];
  // 최신 북마크 상태를 스토어에서 직접 조회
  const currentWord = words.find(w => w.id === rawWord.id) || rawWord;
  const cardImage = getWordImage(currentWord);
  const progress = ((currentIndex + 1) / queue.length) * 100;
  
  let level = calculateWordLevel(currentWord);
  if (isWarmup) level = 0; // 웜업 모드에서는 무조건 힌트 제공
  
  const shouldShowImage = level === 0 || (level === 1 && showHint) || flipped;
  const showFuriganaText = settings.showFurigana || flipped;

  return (
    <View className="flex-1 bg-[#FAF9F6] p-5 pt-10">
      {/* Header */}
      <View className="flex-row justify-between items-center mb-6">
        <TouchableOpacity onPress={() => router.back()}>
          <Ionicons name="close" size={28} color="#333" />
        </TouchableOpacity>

        <View className="flex-row items-center">
          {/* 👁️ 후리가나 ON/OFF 토글 */}
          <TouchableOpacity 
            className="px-3 py-1.5 rounded-full bg-white border border-gray-200 mr-2 flex-row items-center"
            onPress={toggleFurigana}
          >
            <Ionicons name={settings.showFurigana ? "eye-outline" : "eye-off-outline"} size={16} color={settings.showFurigana ? "#4A725D" : "#999"} />
            <Text className={`text-xs ml-1 font-bold ${settings.showFurigana ? 'text-[#4A725D]' : 'text-gray-400'}`}>
              {settings.showFurigana ? '가나 켜짐' : '가나 숨김'}
            </Text>
          </TouchableOpacity>

          {/* ⭐ 즐겨찾기 북마크 */}
          <TouchableOpacity 
            className="p-1.5 rounded-full bg-white border border-gray-200 mr-2"
            onPress={() => toggleBookmark(currentWord.id)}
          >
            <Ionicons name={currentWord.isBookmarked ? "star" : "star-outline"} size={20} color={currentWord.isBookmarked ? "#F2C94C" : "#999"} />
          </TouchableOpacity>

          {/* 🚩 1-Tap 즉시 오류/불만족 제보 버튼 */}
          <QuickFeedbackButton word={currentWord} />
        </View>

        <Text className="text-gray-500 font-medium text-sm">{isWarmup ? '웜업 🚀 ' : ''}{currentIndex + 1} / {queue.length}</Text>
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
        <View className={`w-full ${flipped ? 'h-36' : 'aspect-square max-h-72'} bg-[#F0F4F1] rounded-2xl mb-4 items-center justify-center overflow-hidden border border-gray-100 p-2`}>
          {shouldShowImage ? (
            cardImage ? (
              <Image
                source={cardImage}
                style={{ width: '100%', height: '100%' }}
                contentFit="contain"
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

        {currentWord.kanji && currentWord.kanji !== currentWord.hiragana && (
          <Text className={`text-lg mb-1 ${showFuriganaText ? 'text-gray-500' : 'text-transparent'}`}>
            {currentWord.hiragana}
          </Text>
        )}
        <Text className={`font-medium text-gray-800 ${flipped ? 'text-4xl mb-3' : 'text-5xl mb-6'}`}>{currentWord.kanji || currentWord.hiragana}</Text>

        {flipped ? (
          <View className="items-center w-full">
            <Text className="text-3xl font-bold text-gray-800 mb-2">{currentWord.korean}</Text>
            {currentWord.pronunciation && (
              <Text className="text-lg text-gray-500 mb-2">[{currentWord.pronunciation}]</Text>
            )}
            {currentWord.exampleJp && (
              <TouchableOpacity 
                className="mt-2 w-full bg-[#F7F9F7] rounded-2xl p-4 border border-[#E5EDE7] relative"
                activeOpacity={0.7}
                onPress={(e) => {
                  e.stopPropagation();
                  playJapaneseTTS(currentWord.exampleJp);
                }}
              >
                <View className="flex-row justify-between items-center mb-1">
                  <Text className="text-base text-gray-800 font-medium flex-1 mr-2">{currentWord.exampleJp}</Text>
                  <Ionicons name="volume-high" size={20} color="#8EAAA3" />
                </View>
                {currentWord.exampleReading && (
                  <Text className="text-sm text-[#8EAAA3] mb-1">{currentWord.exampleReading}</Text>
                )}
                {currentWord.exampleKo && (
                  <Text className="text-sm text-gray-500">{currentWord.exampleKo}</Text>
                )}
              </TouchableOpacity>
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

      <FeedbackModal
        visible={feedbackVisible}
        onClose={() => setFeedbackVisible(false)}
        word={currentWord}
      />
    </View>
  );
}
