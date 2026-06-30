import React, { useState } from 'react';
import { View, Text, FlatList, TouchableOpacity } from 'react-native';
import { useWordStore } from '../../store/useWordStore';
import { Ionicons } from '@expo/vector-icons';

export default function VocabularyScreen() {
  const words = useWordStore((state) => state.words);
  const [filter, setFilter] = useState<'all' | 'learning' | 'mastered'>('all');

  const filteredWords = words.filter(w => {
    if (filter === 'all') return true;
    if (filter === 'learning') return w.status === 'learning' || w.status === 'new';
    if (filter === 'mastered') return w.status === 'mastered';
    return true;
  });

  const renderWord = ({ item }: { item: any }) => {
    return (
      <View className="bg-white rounded-2xl p-4 mb-3 shadow-sm border border-gray-100 flex-row justify-between items-center">
        <View className="flex-1">
          <Text className="text-sm text-subtext mb-1">{item.hiragana}</Text>
          <Text className="text-2xl font-bold text-text mb-2">{item.kanji || item.hiragana}</Text>
          <Text className="text-base text-gray-700">{item.korean}</Text>
        </View>
        <View className="items-end justify-between h-full">
          <TouchableOpacity className="p-2 bg-gray-50 rounded-full">
            <Ionicons name="volume-medium" size={20} color="#888" />
          </TouchableOpacity>
          <View className={`px-2 py-1 rounded mt-4 ${item.status === 'mastered' ? 'bg-mint' : 'bg-gray-100'}`}>
            <Text className={`text-xs ${item.status === 'mastered' ? 'text-green-800' : 'text-gray-500'}`}>
              {item.status === 'mastered' ? '마스터' : '학습중'}
            </Text>
          </View>
        </View>
      </View>
    );
  };

  return (
    <View className="flex-1 bg-background p-4">
      <View className="flex-row mb-4 bg-white rounded-xl p-1 shadow-sm">
        <FilterBtn label="전체" active={filter === 'all'} onPress={() => setFilter('all')} />
        <FilterBtn label="학습중" active={filter === 'learning'} onPress={() => setFilter('learning')} />
        <FilterBtn label="마스터" active={filter === 'mastered'} onPress={() => setFilter('mastered')} />
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
