import React, { useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, ScrollView, Image } from 'react-native';
import { useWordStore } from '../../store/useWordStore';
import { wordImages } from '../../data/wordImages';
import { Ionicons } from '@expo/vector-icons';
import { playJapaneseTTS } from '../../utils/tts';

export default function VocabularyScreen() {
  const words = useWordStore((state) => state.words);
  const [filter, setFilter] = useState<'all' | 'learning' | 'mastered'>('all');

  const filteredWords = words.filter(w => {
    if (filter === 'all') return true;
    if (filter === 'learning') return w.status === 'new' || w.interval < 6;
    if (filter === 'mastered') return w.interval >= 6 || w.status === 'mastered';
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
        <View className="w-16 h-16 bg-[#F0F4F1] rounded-xl mr-4 overflow-hidden items-center justify-center">
          {item.imageKey && wordImages[item.imageKey] ? (
            <Image source={wordImages[item.imageKey]} className="w-full h-full" resizeMode="cover" />
          ) : (
            <Text className="text-2xl text-[#8EAAA3] font-bold">{item.kanji ? item.kanji[0] : item.hiragana[0]}</Text>
          )}
        </View>
        <View className="flex-1">
          <Text className="text-sm text-gray-500 mb-1">{item.hiragana}</Text>
          <Text className="text-2xl font-bold text-gray-800 mb-1">{item.kanji || item.hiragana}</Text>
          {item.pronunciation && (
            <Text className="text-sm text-gray-400 mb-1">[{item.pronunciation}]</Text>
          )}
          <Text className="text-base text-gray-700">{item.korean}</Text>
        </View>
        <View className="items-end justify-between h-full">
          <TouchableOpacity 
            className="p-3 mr-1"
            onPress={() => playJapaneseTTS(item.hiragana)}
          >
            <Ionicons name="volume-high" size={24} color="#8EAAA3" />
          </TouchableOpacity>
          <View className={`px-2 py-1 rounded mt-4 ${(item.interval >= 6 || item.status === 'mastered') ? 'bg-[#E9F3EB]' : 'bg-gray-100'}`}>
            <Text className={`text-xs ${(item.interval >= 6 || item.status === 'mastered') ? 'text-green-800' : 'text-gray-500'}`}>
              {(item.interval >= 6 || item.status === 'mastered') ? '알아요' : '몰라요'}
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
          <FilterButton title="몰라요" value="learning" />
          <FilterButton title="알아요" value="mastered" />
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
