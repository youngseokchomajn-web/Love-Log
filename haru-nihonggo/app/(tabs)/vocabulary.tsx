import React, { useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, ScrollView, TextInput } from 'react-native';
import { Image } from 'expo-image';
import { useWordStore } from '../../store/useWordStore';
import { getWordImage } from '../../data/wordImages';
import { Ionicons } from '@expo/vector-icons';
import { playJapaneseTTS } from '../../utils/tts';
import { FeedbackModal } from '../../components/FeedbackModal';
import { QuickFeedbackButton } from '../../components/QuickFeedbackButton';

const LEVELS = ['all', 'n5', 'n4', 'n3', 'n2', 'n1'] as const;
type LevelFilter = typeof LEVELS[number];

export default function VocabularyScreen() {
  const words = useWordStore((state) => state.words);
  const settings = useWordStore((state) => state.settings);
  const toggleBookmark = useWordStore((state) => state.toggleBookmark);
  const toggleFurigana = useWordStore((state) => state.toggleFurigana);

  const [filter, setFilter] = useState<'all' | 'learning' | 'mastered' | 'bookmarked'>('all');
  const [levelFilter, setLevelFilter] = useState<LevelFilter>('all');
  const [search, setSearch] = useState('');
  const [viewMode, setViewMode] = useState<'list' | 'card'>('list');
  const [cardIndex, setCardIndex] = useState(0);
  const [feedbackWord, setFeedbackWord] = useState<any>(null);

  const query = search.trim().toLowerCase();
  const filteredWords = words.filter(w => {
    // 레벨 필터 (레거시 등 level 미지정은 특정 레벨 선택 시 제외)
    if (levelFilter !== 'all' && w.level !== levelFilter) return false;
    // 상태 필터
    if (filter === 'learning' && !(w.status === 'new' || w.interval < 6)) return false;
    if (filter === 'mastered' && !(w.interval >= 6 || w.status === 'mastered')) return false;
    if (filter === 'bookmarked' && !w.isBookmarked) return false;
    // 검색(한자/히라가나/한국어/발음)
    if (query) {
      const haystack = `${w.kanji} ${w.hiragana} ${w.korean} ${w.pronunciation ?? ''} ${w.english}`.toLowerCase();
      if (!haystack.includes(query)) return false;
    }
    return true;
  });

  const currentCardWord = filteredWords[cardIndex] || filteredWords[0];

  const handlePrevCard = () => {
    if (cardIndex > 0) setCardIndex(cardIndex - 1);
  };

  const handleNextCard = () => {
    if (cardIndex < filteredWords.length - 1) setCardIndex(cardIndex + 1);
  };

  const FilterButton = ({ title, value }: { title: string, value: 'all' | 'learning' | 'mastered' | 'bookmarked' }) => {
    const isSelected = filter === value;
    return (
      <TouchableOpacity 
        onPress={() => {
          setFilter(value);
          setCardIndex(0);
        }}
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
            <Image source={itemImage} style={{ width: '100%', height: '100%' }} contentFit="cover" />
          ) : (
            <Text className="text-2xl text-[#8EAAA3] font-bold">{item.kanji ? item.kanji[0] : item.hiragana[0]}</Text>
          )}
        </View>
        <View className="flex-1">
          <View className="flex-row items-center">
            <Text className="text-sm text-gray-500 mb-1">{item.hiragana}</Text>
          </View>
          <Text className="text-2xl font-bold text-gray-800 mb-1">{item.kanji || item.hiragana}</Text>
          {item.pronunciation && (
            <Text className="text-sm text-gray-400 mb-1">[{item.pronunciation}]</Text>
          )}
          <Text className="text-base text-gray-700">{item.korean}</Text>
        </View>
        <View className="items-end justify-between h-full">
          <View className="flex-row items-center">
            <TouchableOpacity 
              className="p-2"
              onPress={() => toggleBookmark(item.id)}
            >
              <Ionicons name={item.isBookmarked ? "star" : "star-outline"} size={22} color={item.isBookmarked ? "#F2C94C" : "#CCC"} />
            </TouchableOpacity>
            <TouchableOpacity 
              className="p-2 ml-1"
              onPress={() => playJapaneseTTS(item.hiragana)}
            >
              <Ionicons name="volume-high" size={22} color="#8EAAA3" />
            </TouchableOpacity>
          </View>
          <View className={`px-2 py-1 rounded mt-3 ${(item.interval >= 6 || item.status === 'mastered') ? 'bg-[#E9F3EB]' : 'bg-gray-100'}`}>
            <Text className={`text-xs ${(item.interval >= 6 || item.status === 'mastered') ? 'text-green-800' : 'text-gray-500'}`}>
              {(item.interval >= 6 || item.status === 'mastered') ? '알아요' : '몰라요'}
            </Text>
          </View>
        </View>
      </View>
    );
  };

  const cardImage = currentCardWord ? getWordImage(currentCardWord) : null;

  return (
    <View className="flex-1 bg-[#FAF9F6] p-4">
      {/* 뷰 모드 토글 (리스트 뷰 vs 단어 카드 뷰) & 검색 바 */}
      <View className="flex-row justify-between items-center mb-3">
        <View className="flex-1 flex-row items-center bg-white rounded-2xl px-4 mr-2 border border-gray-100">
          <Ionicons name="search" size={18} color="#9CA3AF" />
          <TextInput
            className="flex-1 py-3 px-2 text-gray-800"
            placeholder="단어·뜻·발음으로 검색"
            placeholderTextColor="#9CA3AF"
            value={search}
            onChangeText={(text) => {
              setSearch(text);
              setCardIndex(0);
            }}
            autoCorrect={false}
          />
          {search.length > 0 && (
            <TouchableOpacity onPress={() => setSearch('')} className="p-1">
              <Ionicons name="close-circle" size={18} color="#CBD5E1" />
            </TouchableOpacity>
          )}
        </View>

        {/* 뷰 모드 전환 버튼 */}
        <View className="flex-row bg-gray-200 p-1 rounded-2xl">
          <TouchableOpacity 
            className={`px-3 py-2 rounded-xl flex-row items-center ${viewMode === 'list' ? 'bg-white shadow-sm' : ''}`}
            onPress={() => setViewMode('list')}
          >
            <Ionicons name="list-outline" size={16} color={viewMode === 'list' ? '#333' : '#777'} />
            <Text className={`text-xs ml-1 font-bold ${viewMode === 'list' ? 'text-gray-800' : 'text-gray-500'}`}>목록</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            className={`px-3 py-2 rounded-xl flex-row items-center ${viewMode === 'card' ? 'bg-white shadow-sm' : ''}`}
            onPress={() => setViewMode('card')}
          >
            <Ionicons name="albums-outline" size={16} color={viewMode === 'card' ? '#333' : '#777'} />
            <Text className={`text-xs ml-1 font-bold ${viewMode === 'card' ? 'text-gray-800' : 'text-gray-500'}`}>카드</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* 레벨 필터 */}
      <View className="mb-2">
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {LEVELS.map(lv => {
            const on = levelFilter === lv;
            return (
              <TouchableOpacity
                key={lv}
                onPress={() => {
                  setLevelFilter(lv);
                  setCardIndex(0);
                }}
                className={`px-4 py-1.5 rounded-full mr-2 ${on ? 'bg-[#4A725D]' : 'bg-gray-100'}`}
              >
                <Text className={`font-bold text-xs ${on ? 'text-white' : 'text-gray-500'}`}>
                  {lv === 'all' ? '전체' : lv.toUpperCase()}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {/* 상태 필터 */}
      <View className="flex-row items-center mb-4">
        <ScrollView horizontal showsHorizontalScrollIndicator={false} className="flex-1">
          <FilterButton title="전체보기" value="all" />
          <FilterButton title="⭐ 즐겨찾기" value="bookmarked" />
          <FilterButton title="몰라요" value="learning" />
          <FilterButton title="알아요" value="mastered" />
        </ScrollView>
        <Text className="text-gray-400 text-sm ml-2">{filteredWords.length}개</Text>
      </View>

      {/* 뷰 모드 1: 리스트 뷰 */}
      {viewMode === 'list' ? (
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
      ) : (
        /* 뷰 모드 2: 카드 슬라이드 뷰 (이미지 + 한자 + 가나 + 오디오 + 예문) */
        currentCardWord ? (
          <View className="flex-1 bg-white rounded-3xl p-5 shadow-sm border border-gray-100 items-center justify-between">
            {/* 카드 상단 컨트롤 (북마크 & TTS) */}
            <View className="w-full flex-row justify-between items-center mb-2">
              <TouchableOpacity 
                className="px-3 py-1.5 rounded-full bg-[#F0F4F1] flex-row items-center"
                onPress={toggleFurigana}
              >
                <Ionicons name={settings.showFurigana ? "eye-outline" : "eye-off-outline"} size={16} color="#4A725D" />
                <Text className="text-xs ml-1 font-bold text-[#4A725D]">
                  {settings.showFurigana ? '가나 켜짐' : '가나 숨김'}
                </Text>
              </TouchableOpacity>

              <View className="flex-row items-center">
                <TouchableOpacity 
                  className="p-2 rounded-full bg-gray-100 mr-2"
                  onPress={() => playJapaneseTTS(currentCardWord.hiragana)}
                >
                  <Ionicons name="volume-high" size={20} color="#4A725D" />
                </TouchableOpacity>
                <TouchableOpacity 
                  className="p-2 rounded-full bg-gray-100 mr-2"
                  onPress={() => toggleBookmark(currentCardWord.id)}
                >
                  <Ionicons name={currentCardWord.isBookmarked ? "star" : "star-outline"} size={20} color={currentCardWord.isBookmarked ? "#F2C94C" : "#999"} />
                </TouchableOpacity>

                {/* 1-Tap 즉시 제보 버튼 */}
                <QuickFeedbackButton word={currentCardWord} />
              </View>
            </View>

            {/* 카드 이미지 영역 (정사각형 1:1 이미지 100% 원본 손실없이 표출) */}
            <View className="w-full aspect-square max-h-72 bg-[#F0F4F1] rounded-2xl mb-4 overflow-hidden items-center justify-center border border-gray-100 p-2">
              {cardImage ? (
                <Image source={cardImage} style={{ width: '100%', height: '100%' }} contentFit="contain" />
              ) : (
                <Ionicons name="image-outline" size={70} color="#8EAAA3" />
              )}
            </View>

            {/* 단어 메인 정보 */}
            <View className="items-center w-full my-1">
              {currentCardWord.kanji && currentCardWord.kanji !== currentCardWord.hiragana && (
                <Text className={`text-base font-medium mb-0.5 ${settings.showFurigana ? 'text-gray-500' : 'text-transparent'}`}>
                  {currentCardWord.hiragana}
                </Text>
              )}
              <Text className="text-4xl font-bold text-gray-800 mb-1">{currentCardWord.kanji || currentCardWord.hiragana}</Text>
              <Text className="text-2xl font-bold text-[#4A725D] mb-1">{currentCardWord.korean}</Text>
              {currentCardWord.pronunciation && (
                <Text className="text-sm text-gray-400">[{currentCardWord.pronunciation}]</Text>
              )}
            </View>

            {/* 예문 박스 (터치 시 예문 TTS 재생) */}
            {currentCardWord.exampleJp && (
              <TouchableOpacity 
                className="w-full bg-[#FAF9F6] p-3 rounded-2xl border border-gray-100 my-1 items-center"
                onPress={() => playJapaneseTTS(currentCardWord.exampleReading || currentCardWord.exampleJp || '')}
              >
                <Text className="text-sm font-bold text-gray-700 mb-0.5 text-center">
                  {currentCardWord.exampleJp} <Ionicons name="volume-medium" size={14} color="#4A725D" />
                </Text>
                {currentCardWord.exampleKo && (
                  <Text className="text-xs text-gray-500 text-center">{currentCardWord.exampleKo}</Text>
                )}
              </TouchableOpacity>
            )}

            {/* 카드 슬라이드 하단 탐색 버튼 (이전 / 카드 번호 / 다음) */}
            <View className="w-full flex-row justify-between items-center mt-2 pt-2 border-t border-gray-100">
              <TouchableOpacity 
                className={`px-4 py-2.5 rounded-full flex-row items-center ${cardIndex > 0 ? 'bg-[#7EA48F]' : 'bg-gray-200'}`}
                disabled={cardIndex === 0}
                onPress={handlePrevCard}
              >
                <Ionicons name="chevron-back" size={18} color={cardIndex > 0 ? '#FFF' : '#AAA'} />
                <Text className={`font-bold text-xs ml-1 ${cardIndex > 0 ? 'text-white' : 'text-gray-400'}`}>이전</Text>
              </TouchableOpacity>

              <Text className="text-gray-600 font-bold text-sm">
                {cardIndex + 1} / {filteredWords.length}
              </Text>

              <TouchableOpacity 
                className={`px-4 py-2.5 rounded-full flex-row items-center ${cardIndex < filteredWords.length - 1 ? 'bg-[#7EA48F]' : 'bg-gray-200'}`}
                disabled={cardIndex >= filteredWords.length - 1}
                onPress={handleNextCard}
              >
                <Text className={`font-bold text-xs mr-1 ${cardIndex < filteredWords.length - 1 ? 'text-white' : 'text-gray-400'}`}>다음</Text>
                <Ionicons name="chevron-forward" size={18} color={cardIndex < filteredWords.length - 1 ? '#FFF' : '#AAA'} />
              </TouchableOpacity>
            </View>
          </View>
        ) : (
          <View className="items-center mt-20">
            <Ionicons name="search-outline" size={48} color="#D1D5DB" />
            <Text className="text-gray-400 mt-3">검색 결과가 없어요</Text>
          </View>
        )
      )}

      <FeedbackModal
        visible={feedbackWord !== null}
        onClose={() => setFeedbackWord(null)}
        word={feedbackWord}
      />
    </View>
  );
}
