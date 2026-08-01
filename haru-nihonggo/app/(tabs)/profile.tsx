import React from 'react';
import { View, Text, TouchableOpacity, ScrollView, Switch } from 'react-native';
import { useWordStore } from '../../store/useWordStore';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { FeedbackModal } from '../../components/FeedbackModal';

export default function ProfileScreen() {
  const words = useWordStore((state) => state.words);
  const settings = useWordStore((state) => state.settings);
  const updateSettings = useWordStore((state) => state.updateSettings);
  const resetData = useWordStore((state) => state.resetData);
  const router = useRouter();
  const [feedbackVisible, setFeedbackVisible] = React.useState(false);

  const totalWords = words.length;
  const masteredWords = words.filter(w => w.status === 'mastered').length;
  const learningWords = words.filter(w => w.status === 'learning').length;
  const newWords = words.filter(w => w.status === 'new').length;
  const totalIncorrect = words.reduce((sum, w) => sum + w.incorrectCount, 0);

  // 학습 시작일로부터 며칠째인지 (달력 기준, 첫날 = 1일째)
  const dayStart = (ms: number) => {
    const d = new Date(ms);
    return new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
  };
  const daysTogether = Math.max(
    1,
    Math.round((dayStart(Date.now()) - dayStart(settings.startDate ?? Date.now())) / 86400000) + 1
  );

  const LEVEL_CYCLE: Array<'all' | 'n5' | 'n4' | 'n3' | 'n2' | 'n1'> = ['all', 'n5', 'n4', 'n3', 'n2', 'n1'];
  const cycleStudyLevel = () => {
    const i = LEVEL_CYCLE.indexOf(settings.studyLevel);
    updateSettings({ studyLevel: LEVEL_CYCLE[(i + 1) % LEVEL_CYCLE.length] });
  };

  const handleReset = () => {
    resetData();
    setTimeout(() => {
        alert('데이터가 초기화되었습니다. (JLPT N4 시드 데이터 재로딩)');
        router.replace('/');
    }, 100);
  };

  const cycleDailyGoal = () => {
    const goals = [5, 10, 20, 30];
    const currentIndex = goals.indexOf(settings.dailyGoal);
    const nextGoal = goals[(currentIndex + 1) % goals.length];
    updateSettings({ dailyGoal: nextGoal });
  };

  return (
    <ScrollView className="flex-1 bg-[#FAF9F6] p-5 pt-8">
      {/* Profile Header */}
      <View className="items-center mb-10">
        <View className="w-24 h-24 bg-[#E9F3EB] rounded-full items-center justify-center mb-4">
          <Ionicons name="person" size={48} color="#8EAAA3" />
        </View>
        <Text className="text-2xl font-bold text-gray-800">학습자 님</Text>
        <Text className="text-gray-500 mt-1">Haru Voca와 함께한지 {daysTogether}일째</Text>
      </View>

      {/* Stats Dashboard */}
      <Text className="text-lg font-bold text-gray-800 mb-4">나의 학습 통계</Text>
      <View className="bg-white rounded-3xl p-5 shadow-sm border border-gray-100 mb-8">
        <View className="flex-row justify-between mb-6">
          <View className="items-center flex-1">
            <Text className="text-3xl font-bold text-[#8EAAA3]">{masteredWords}</Text>
            <Text className="text-gray-500 text-xs mt-1">마스터 단어</Text>
          </View>
          <View className="w-[1px] bg-gray-100"></View>
          <View className="items-center flex-1">
            <Text className="text-3xl font-bold text-[#F2C94C]">{learningWords}</Text>
            <Text className="text-gray-500 text-xs mt-1">학습중</Text>
          </View>
          <View className="w-[1px] bg-gray-100"></View>
          <View className="items-center flex-1">
            <Text className="text-3xl font-bold text-gray-400">{newWords}</Text>
            <Text className="text-gray-500 text-xs mt-1">새로운 단어</Text>
          </View>
        </View>
        
        <View className="bg-[#F0F4F1] rounded-2xl p-4 flex-row justify-between items-center">
          <Text className="text-gray-700 font-medium">전체 누적 오답 횟수</Text>
          <Text className="text-xl font-bold text-[#D96B6B]">{totalIncorrect}회</Text>
        </View>
      </View>

      {/* Settings Area */}
      <Text className="text-lg font-bold text-gray-800 mb-4">학습 설정</Text>
      <View className="bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-100 mb-6">
        
        {/* Study Level */}
        <TouchableOpacity
          className="flex-row justify-between items-center p-5 border-b border-gray-100"
          onPress={cycleStudyLevel}
        >
          <View className="flex-row items-center">
            <Ionicons name="layers-outline" size={22} color="#555" />
            <View className="ml-3">
              <Text className="text-gray-700 font-medium">학습 레벨</Text>
              <Text className="text-gray-400 text-xs mt-1">오늘의 학습에 사용할 레벨</Text>
            </View>
          </View>
          <View className="bg-[#F0F4F1] px-3 py-1 rounded-full">
            <Text className="text-[#8EAAA3] font-bold">{settings.studyLevel === 'all' ? '전체' : settings.studyLevel.toUpperCase()}</Text>
          </View>
        </TouchableOpacity>

        {/* Daily Goal */}
        <TouchableOpacity
          className="flex-row justify-between items-center p-5 border-b border-gray-100"
          onPress={cycleDailyGoal}
        >
          <View className="flex-row items-center">
            <Ionicons name="flag-outline" size={22} color="#555" />
            <View className="ml-3">
              <Text className="text-gray-700 font-medium">하루 목표 학습량</Text>
              <Text className="text-gray-400 text-xs mt-1">터치하여 변경</Text>
            </View>
          </View>
          <View className="bg-[#F0F4F1] px-3 py-1 rounded-full">
            <Text className="text-[#8EAAA3] font-bold">{settings.dailyGoal}개</Text>
          </View>
        </TouchableOpacity>

        {/* Furigana Toggle */}
        <View className="flex-row justify-between items-center p-5 border-b border-gray-100">
          <View className="flex-row items-center">
            <Ionicons name="eye-outline" size={22} color="#555" />
            <View className="ml-3">
              <Text className="text-gray-700 font-medium">후리가나(가나) 기본 표시</Text>
              <Text className="text-gray-400 text-xs mt-1">카드 앞면에서 히라가나 읽기 표시</Text>
            </View>
          </View>
          <Switch
            trackColor={{ false: '#E5E5E5', true: '#8EAAA3' }}
            thumbColor={'#FFFFFF'}
            onValueChange={(val) => updateSettings({ showFurigana: val })}
            value={settings.showFurigana}
          />
        </View>

        {/* Auto TTS */}
        <View className="flex-row justify-between items-center p-5">
          <View className="flex-row items-center">
            <Ionicons name="volume-high-outline" size={22} color="#555" />
            <View className="ml-3">
              <Text className="text-gray-700 font-medium">발음 자동 듣기</Text>
              <Text className="text-gray-400 text-xs mt-1">카드 뒤집을 때 자동 재생</Text>
            </View>
          </View>
          <Switch
            trackColor={{ false: '#E5E5E5', true: '#8EAAA3' }}
            thumbColor={'#FFFFFF'}
            onValueChange={(val) => updateSettings({ autoPlayAudio: val })}
            value={settings.autoPlayAudio}
          />
        </View>
      </View>

      {/* Settings / Danger Zone */}
      <Text className="text-lg font-bold text-gray-800 mb-4">설정</Text>
      <View className="bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-100 mb-10">
        <TouchableOpacity 
          className="flex-row justify-between items-center p-5 border-b border-gray-100"
          onPress={() => alert('알림 권한을 요청합니다.\n매일 정해진 시간에 단어 학습 리마인더를 보내드릴게요!')}
        >
          <View className="flex-row items-center">
            <Ionicons name="notifications-outline" size={22} color="#555" />
            <Text className="ml-3 text-gray-700 font-medium">알림 설정</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#CCC" />
        </TouchableOpacity>
        <TouchableOpacity 
          className="flex-row justify-between items-center p-5 border-b border-gray-100"
          onPress={() => setFeedbackVisible(true)}
        >
          <View className="flex-row items-center">
            <Ionicons name="chatbubble-ellipses-outline" size={22} color="#4A725D" />
            <Text className="ml-3 text-gray-700 font-medium">의견 보내기 / 단어 오류 제보</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#CCC" />
        </TouchableOpacity>

        <TouchableOpacity 
          className="flex-row justify-between items-center p-5"
          onPress={handleReset}
        >
          <View className="flex-row items-center">
            <Ionicons name="trash-outline" size={22} color="#D96B6B" />
            <Text className="ml-3 text-[#D96B6B] font-medium">학습 데이터 초기화</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color="#CCC" />
        </TouchableOpacity>
      </View>

      <FeedbackModal
        visible={feedbackVisible}
        onClose={() => setFeedbackVisible(false)}
      />
    </ScrollView>
  );
}
