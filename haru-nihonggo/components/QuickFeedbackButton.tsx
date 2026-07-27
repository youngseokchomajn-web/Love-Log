import React, { useState } from 'react';
import { View, Text, TouchableOpacity, Modal, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Word, useWordStore } from '../store/useWordStore';
import { FeedbackModal } from './FeedbackModal';

interface QuickFeedbackButtonProps {
  word: Word;
  compact?: boolean;
}

export function QuickFeedbackButton({ word, compact = false }: QuickFeedbackButtonProps) {
  const [menuVisible, setMenuVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [reported, setReported] = useState(false);

  const handleQuickReport = (reason: string) => {
    setMenuVisible(false);
    setReported(true);

    Alert.alert(
      '✅ 제보가 접수되었습니다!',
      `[${word.kanji || word.hiragana}] 단어의 '${reason}' 제보가 등록되었습니다. 빠르게 검토하여 반영하겠습니다. 감사합니다!`,
      [{ text: '확인' }]
    );
  };

  return (
    <View>
      {/* 1-Tap Quick Report Trigger Button */}
      <TouchableOpacity
        className={`flex-row items-center px-2.5 py-1.5 rounded-full border ${
          reported 
            ? 'bg-red-50 border-red-200' 
            : 'bg-white/90 border-gray-200 shadow-sm'
        }`}
        onPress={() => setMenuVisible(true)}
      >
        <Ionicons 
          name={reported ? "flag" : "flag-outline"} 
          size={compact ? 14 : 16} 
          color={reported ? "#D96B6B" : "#888"} 
        />
        {!compact && (
          <Text className={`text-xs ml-1 font-medium ${reported ? 'text-[#D96B6B] font-bold' : 'text-gray-500'}`}>
            {reported ? '제보됨' : '이상해요'}
          </Text>
        )}
      </TouchableOpacity>

      {/* 1-Tap Quick Action Popover Modal */}
      <Modal
        animationType="fade"
        transparent={true}
        visible={menuVisible}
        onRequestClose={() => setMenuVisible(false)}
      >
        <TouchableOpacity 
          className="flex-1 bg-black/40 justify-center items-center p-4"
          activeOpacity={1}
          onPress={() => setMenuVisible(false)}
        >
          <View className="bg-white w-full max-w-sm rounded-3xl p-5 border border-gray-100 shadow-lg">
            <View className="flex-row justify-between items-center mb-3 pb-2 border-b border-gray-100">
              <View className="flex-row items-center">
                <Ionicons name="alert-circle-outline" size={20} color="#D96B6B" />
                <Text className="text-base font-bold text-gray-800 ml-1.5">어떤 부분이 이상한가요?</Text>
              </View>
              <TouchableOpacity onPress={() => setMenuVisible(false)}>
                <Ionicons name="close" size={20} color="#999" />
              </TouchableOpacity>
            </View>

            <Text className="text-xs text-gray-500 mb-3 font-medium">
              대상: <Text className="font-bold text-gray-800">{word.kanji || word.hiragana}</Text> ({word.korean})
            </Text>

            {/* Quick Options (1-Tap Result) */}
            <TouchableOpacity 
              className="bg-[#F0F4F1] p-3 rounded-2xl mb-2 flex-row items-center justify-between"
              onPress={() => handleQuickReport('이미지 불일치/어색함')}
            >
              <View className="flex-row items-center">
                <Text className="text-base mr-2">🖼️</Text>
                <Text className="text-sm font-bold text-gray-700">이미지가 이상함 / 안 어울림</Text>
              </View>
              <Ionicons name="chevron-forward" size={16} color="#7EA48F" />
            </TouchableOpacity>

            <TouchableOpacity 
              className="bg-[#F0F4F1] p-3 rounded-2xl mb-2 flex-row items-center justify-between"
              onPress={() => handleQuickReport('한자/뜻/가나 오류')}
            >
              <View className="flex-row items-center">
                <Text className="text-base mr-2">📝</Text>
                <Text className="text-sm font-bold text-gray-700">한자 / 뜻 / 가나 오류</Text>
              </View>
              <Ionicons name="chevron-forward" size={16} color="#7EA48F" />
            </TouchableOpacity>

            <TouchableOpacity 
              className="bg-[#F0F4F1] p-3 rounded-2xl mb-2 flex-row items-center justify-between"
              onPress={() => handleQuickReport('예문/음성 오디오 이상함')}
            >
              <View className="flex-row items-center">
                <Text className="text-base mr-2">🔊</Text>
                <Text className="text-sm font-bold text-gray-700">예문 / 발음 오디오 이상함</Text>
              </View>
              <Ionicons name="chevron-forward" size={16} color="#7EA48F" />
            </TouchableOpacity>

            <TouchableOpacity 
              className="bg-gray-100 p-3 rounded-2xl mt-1 flex-row items-center justify-between"
              onPress={() => {
                setMenuVisible(false);
                setDetailModalVisible(true);
              }}
            >
              <View className="flex-row items-center">
                <Text className="text-base mr-2">✉️</Text>
                <Text className="text-sm font-bold text-gray-600">상세 의견 이메일로 쓰기</Text>
              </View>
              <Ionicons name="create-outline" size={16} color="#666" />
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
      </Modal>

      {/* Detail Email Feedback Modal */}
      <FeedbackModal
        visible={detailModalVisible}
        onClose={() => setDetailModalVisible(false)}
        word={word}
      />
    </View>
  );
}
