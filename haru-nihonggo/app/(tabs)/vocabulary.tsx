import React, { useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, ScrollView, Image, TextInput } from 'react-native';
import { useWordStore } from '../../store/useWordStore';
import { getWordImage } from '../../data/wordImages';
import { Ionicons } from '@expo/vector-icons';
import { playJapaneseTTS } from '../../utils/tts';

export default function VocabularyScreen() {
  const words = useWordStore((state) => state.words);
  const [filter, setFilter] = useState<'all' | 'learning' | 'mastered'>('all');
  const [search, setSearch] = useState('');

  const query = search.trim().toLowerCase();
  const filteredWords = words.filter(w => {
    // 상태 필터
    if (filter === 'learning' && !(w.status === 'new' || w.interval < 6)) return false;
    if (filter === 'mastered' && !(w.interval >= 6 || w.status === 'mastered')) return false;
    // 검색(한자/히라가나/한국어/발음)
    if (query) {
      const haystack = `${w.kanji} ${w.hiragana} ${w.korean} ${w.pronunciation ?? ''} ${w.english}`.toLowerCase();
      if (!haystack.includes(query)) return false;
    }
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
    const itemImage = getWordImage(item);
    return (
      <View className="bg-white rounded-2xl p-4 mb-3 shadow-sm border border-gray-100 flex-row justify-between items-center">
        <View className="w-16 h-16 bg-[#F0F4F1] rounded-xl mr-4 overflow-hidden items-center justify-center">
          {itemImage ? (
            <Image source={itemImage} className="w-full h-full" resizeMode="cover" />
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
      {/* 검색 바 */}
      <View className="flex-row items-center bg-white rounded-2xl px-4 mb-3 border border-gray-100">
        <Ionicons name="search" size={18} color="#9CA3AF" />
        <TextInput
          className="flex-1 py-3 px-2 text-gray-800"
          placeholder="단어·뜻·발음으로 검색"
          placeholderTextColor="#9CA3AF"
          value={search}
          onChangeText={setSearch}
          autoCorrect={false}
        />
        {search.length > 0 && (
          <TouchableOpacity onPress={() => setSearch('')} className="p-1">
            <Ionicons name="close-circle" size={18} color="#CBD5E1" />
          </TouchableOpacity>
        )}
      </View>

      <View className="flex-row items-center mb-4">
        <ScrollView horizontal showsHorizontalScrollIndicator={false} className="flex-1">
          <FilterButton title="전체보기" value="all" />
          <FilterButton title="몰라요" value="learning" />
          <FilterButton title="알아요" value="mastered" />
        </ScrollView>
        <Text className="text-gray-400 text-sm ml-2">{filteredWords.length}개</Text>
      </View>

      <FlatList
        data={filteredWords}
        keyExtractor={(item) => item.id}
        renderItem={renderWord}
        showsVerticalScrollIndicator={false}
        initialNumToRender={12}
        maxToRenderPerBatch={12}
        windowSize={7}
        removeClippedSubviews
        ListEmptyComponent={
          <View className="items-center mt-20">
            <Ionicons name="search-outline" size={48} color="#D1D5DB" />
            <Text className="text-gray-400 mt-3">검색 결과가 없어요</Text>
          </View>
        }
      />
    </View>
  );
}
