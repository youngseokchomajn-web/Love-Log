import React from 'react';
import { View, Text, FlatList, TouchableOpacity } from 'react-native';
import { useWordStore } from '../../store/useWordStore';
import { Ionicons } from '@expo/vector-icons';

export default function IncorrectScreen() {
  const incorrectWords = useWordStore((state) => state.getIncorrectWords());

  if (incorrectWords.length === 0) {
    return (
      <View className="flex-1 bg-background justify-center items-center p-4">
        <Ionicons name="happy-outline" size={64} color="#8EAAA3" />
        <Text className="text-xl font-bold text-text mt-4">오답이 없어요!</Text>
        <Text className="text-subtext mt-2 text-center">완벽하게 학습하고 계시네요.{'\n'}앞으로도 화이팅!</Text>
      </View>
    );
  }

  const renderWord = ({ item }: { item: any }) => (
    <View className="bg-white rounded-2xl p-4 mb-3 shadow-sm border border-gray-100">
      <View className="flex-row justify-between items-start mb-2">
        <View>
          <Text className="text-sm text-subtext mb-1">{item.hiragana}</Text>
          <Text className="text-2xl font-bold text-text">{item.kanji || item.hiragana}</Text>
        </View>
        <View className="bg-pink px-2 py-1 rounded">
          <Text className="text-xs text-red-500 font-bold">{item.incorrectCount}번 틀림</Text>
        </View>
      </View>
      <View className="bg-gray-50 rounded-xl p-3 mt-2 flex-row justify-between items-center">
        <Text className="text-base text-gray-700">{item.korean}</Text>
        <TouchableOpacity>
          <Text className="text-sm text-subtext font-medium text-green-700">집중 학습 ></Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <View className="flex-1 bg-background p-4">
      <View className="mb-4">
        <Text className="text-subtext">총 <Text className="font-bold text-red-400">{incorrectWords.length}</Text>개의 틀린 단어가 있습니다.</Text>
      </View>
      <FlatList
        data={incorrectWords}
        keyExtractor={(item) => item.id}
        renderItem={renderWord}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}
