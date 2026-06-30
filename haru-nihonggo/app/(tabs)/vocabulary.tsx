import React, { useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, ScrollView } from 'react-native';
import { useWordStore } from '../../store/useWordStore';
import { Ionicons } from '@expo/vector-icons';
import * as Speech from 'expo-speech';

export default function VocabularyScreen() {
  const words = useWordStore((state) => state.words);
  const [filter, setFilter] = useState<'all' | 'learning' | 'mastered'>('all');

  const filteredWords = words.filter(w => {
    if (filter === 'all') return true;
    if (filter === 'learning') return w.status === 'learning' || w.status === 'new';
    if (filter === 'mastered') return w.status === 'mastered';
    return true;
  });

  const FilterButton = ({ title, value }: { title: string, value: 'all' | 'learning' | 'mastered' }) => {
    const isSelected = filter === value;
    return (
      <TouchableOpacity 
        onPress={() => setFilter(value)}
        className={`px-4 py-2 rounded-full mr-2 ${isSelected ? 'bg-[#8EAAA3]' : 'bg-gray-200'}`}
      >
        <Text className={`font-medium ${isSelected ? 'text-white' : 'text-gray-600'}`}>{title}</Text>
      </TouchableOpacity>
    );
  };

  const renderWord = ({ item }: { item: any }) => {
    return (
      <View className="bg-white rounded-2xl p-4 mb-3 shadow-sm border border-gray-100 flex-row justify-between items-center">
        <View className="flex-1">
          <Text className="text-sm text-gray-500 mb-1">{item.hiragana}</Text>
          <Text className="text-2xl font-bold text-gray-800 mb-2">{item.kanji || item.hiragana}</Text>
          <Text className="text-base text-gray-700">{item.korean}</Text>
        </View>
        <View className="items-end justify-between h-full">
          <TouchableOpacity 
            className="p-2 bg-gray-50 rounded-full"
            onPress={() => Speech.speak(item.hiragana, { language: 'ja-JP' })}
          >
            <Ionicons name="volume-medium" size={20} color="#888" />
          </TouchableOpacity>
          <View className={`px-2 py-1 rounded mt-4 ${item.status === 'mastered' ? 'bg-[#E9F3EB]' : 'bg-gray-100'}`}>
            <Text className={`text-xs ${item.status === 'mastered' ? 'text-green-800' : 'text-gray-500'}`}>
              {item.status === 'mastered' ? '마스터' : '학습중'}
            </Text>
          </View>
        </View>
      </View>
    );
  };

  return (
    <View className="flex-1 bg-[#FAF9F6] p-4">
      <View className="flex-row mb-4">
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <FilterButton title="전체보기" value="all" />
          <FilterButton title="학습중" value="learning" />
          <FilterButton title="마스터" value="mastered" />
        </ScrollView>
      </View>
      
      <FlatList
        data={filteredWords}
        keyExtractor={(item) => item.id}
        renderItem={renderWord}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

function FilterBtn({ label, active, onPress }: { label: string, active: boolean, onPress: () => void }) {
  return (
    <TouchableOpacity 
      className={`flex-1 py-2 items-center rounded-lg ${active ? 'bg-mint shadow-sm' : 'bg-transparent'}`}
      onPress={onPress}
    >
      <Text className={`font-medium ${active ? 'text-green-800' : 'text-subtext'}`}>{label}</Text>
    </TouchableOpacity>
  );
}
