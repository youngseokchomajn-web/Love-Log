import React from 'react';
import { View, Text, TouchableOpacity, ScrollView, Image } from 'react-native';
import { useRouter } from 'expo-router';
import { useWordStore } from '../../store/useWordStore';
import { Ionicons } from '@expo/vector-icons';

export default function HomeScreen() {
  const router = useRouter();
  const getTodayNewWords = useWordStore((state) => state.getTodayNewWords);
  const getTodayReviewWords = useWordStore((state) => state.getTodayReviewWords);
  const getIncorrectWords = useWordStore((state) => state.getIncorrectWords);
  const settings = useWordStore((state) => state.settings);

  const newCount = getTodayNewWords().length;
  const reviewCount = getTodayReviewWords().length;
  const incorrectCount = getIncorrectWords().length;

  return (
    <ScrollView className="flex-1 bg-[#FAF9F6] px-5 pt-4">
      <View className="mb-8">
        <Text className="text-xl font-medium text-gray-800 tracking-wide">좋은 아침이에요 ☀️</Text>
        <Text className="text-lg text-gray-600 mt-1">오늘 목표는 {settings.dailyGoal}개, 일본어를 만나봐요</Text>
      </View>

      <View className="flex-row justify-between items-center mb-4">
        <Text className="text-lg font-bold text-gray-800">오늘의 학습</Text>
        <TouchableOpacity>
          <Text className="text-gray-500 text-sm">전체 보기 &gt;</Text>
        </TouchableOpacity>
      </View>

      {/* Stats Cards */}
      <View className="flex-row justify-between mb-8">
        <View className="bg-[#EEEDF9] rounded-2xl p-4 flex-1 mr-2 items-center justify-center">
          <Text className="text-gray-600 text-xs mb-1 font-medium">새로운 단어</Text>
          <Text className="text-2xl font-bold text-gray-800">{newCount}<Text className="text-sm font-normal">개</Text></Text>
        </View>
        <View className="bg-[#E9F3EB] rounded-2xl p-4 flex-1 mx-1 items-center justify-center">
          <Text className="text-gray-600 text-xs mb-1 font-medium">복습 단어</Text>
          <Text className="text-2xl font-bold text-gray-800">{reviewCount}<Text className="text-sm font-normal">개</Text></Text>
        </View>
        <View className="bg-[#FBE9E7] rounded-2xl p-4 flex-1 ml-2 items-center justify-center">
          <Text className="text-gray-600 text-xs mb-1 font-medium">틀린 단어</Text>
          <Text className="text-2xl font-bold text-gray-800">{incorrectCount}<Text className="text-sm font-normal">개</Text></Text>
        </View>
      </View>

      {/* Warm-up Mode Banner */}
      {reviewCount >= Math.max(15, settings.dailyGoal * 1.5) && (
        <TouchableOpacity 
          className="bg-[#E9F3EB] rounded-3xl p-5 mb-6 flex-row items-center justify-between border border-[#D1E5D5]"
          activeOpacity={0.8}
          onPress={() => router.push('/srs?mode=warmup')}
        >
          <View className="flex-1">
            <Text className="text-lg font-bold text-[#4A725D] mb-1">🧠 가볍게 뇌풀기 (웜업)</Text>
            <Text className="text-[#6B8E7B] text-sm">복습이 많이 밀렸네요! 힌트와 함께 부담 없이 워밍업부터 해보세요.</Text>
          </View>
          <View className="ml-3">
            <Ionicons name="fitness" size={40} color="#7EA48F" />
          </View>
        </TouchableOpacity>
      )}

      {/* Start Button */}
      <View className="bg-[#FDF6E3] rounded-3xl p-5 mb-8 relative overflow-hidden">
        <Text className="text-lg font-bold text-gray-800 mb-2 z-10">단어 학습 시작하기</Text>
        <View className="items-center justify-center my-4 z-0">
          <Ionicons name="book" size={80} color="#E2D4A8" />
        </View>
        <View className="items-end z-10">
          <TouchableOpacity 
            className="bg-[#333333] rounded-full px-5 py-2.5"
            onPress={() => router.push('/srs')}
          >
            <Text className="text-white font-medium">시작하기</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Quick Menu */}
      <Text className="text-lg font-bold text-gray-800 mb-4">더 보기</Text>
      <View className="bg-transparent mb-10">
        <MenuRow icon="time-outline" label="복습하기" onPress={() => router.push('/srs')} />
        <MenuRow icon="book-outline" label="오답노트" onPress={() => router.push('/incorrect')} />
        <MenuRow icon="library-outline" label="JLPT N4 단어 목록" onPress={() => router.push('/vocabulary')} />
      </View>
    </ScrollView>
  );
}

function MenuRow({ icon, label, onPress }: { icon: any, label: string, onPress: () => void }) {
  return (
    <TouchableOpacity 
      className="flex-row justify-between items-center py-4 bg-transparent border-b border-gray-200"
      onPress={onPress}
    >
      <View className="flex-row items-center">
        <Ionicons name={icon} size={22} color="#555" />
        <Text className="ml-3 text-gray-700 font-medium text-base">{label}</Text>
      </View>
      <Ionicons name="chevron-forward" size={20} color="#CCC" />
    </TouchableOpacity>
  );
}
