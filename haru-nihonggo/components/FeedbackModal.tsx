import React, { useState } from 'react';
import { View, Text, Modal, TouchableOpacity, TextInput, Alert, Linking, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Word } from '../store/useWordStore';

interface FeedbackModalProps {
  visible: boolean;
  onClose: () => void;
  word?: Word | null;
}

const REPORT_TYPES = [
  { id: 'image', label: '🖼️ 이미지 이상함 / 어색함' },
  { id: 'meaning', label: '📝 한자 / 가나 / 뜻 오류' },
  { id: 'audio', label: '🔊 예문 / 발음 오디오 이상함' },
  { id: 'suggestion', label: '💡 기타 의견 및 기능 건의' },
];

export function FeedbackModal({ visible, onClose, word }: FeedbackModalProps) {
  const [selectedType, setSelectedType] = useState('image');
  const [comment, setComment] = useState('');

  const handleSendEmail = () => {
    const typeObj = REPORT_TYPES.find(t => t.id === selectedType);
    const typeLabel = typeObj ? typeObj.label : '기타';

    const subject = encodeURIComponent(
      word 
        ? `[하루일본어 오류제보] ${word.level?.toUpperCase() || 'N4'} - ${word.kanji || word.hiragana} (${word.korean})` 
        : '[하루일본어 앱 의견 보내기]'
    );

    const bodyText = `
----------------------------------
📌 제보 항목: ${typeLabel}
${word ? `📌 대상 단어: ${word.kanji || word.hiragana} (${word.hiragana})` : ''}
${word ? `📌 한국어 뜻: ${word.korean}` : ''}
${word ? `📌 단어 ID: ${word.id}` : ''}
----------------------------------

💬 상세 내용:
${comment.trim() || '내용 없음'}

----------------------------------
하루일본어 서비스 개선에 참여해 주셔서 감사합니다!
`.trim();

    const emailUrl = `mailto:support@harunihonggo.com?subject=${subject}&body=${encodeURIComponent(bodyText)}`;

    Linking.canOpenURL(emailUrl).then(supported => {
      if (supported) {
        Linking.openURL(emailUrl);
        onClose();
        setComment('');
      } else {
        Alert.alert(
          '감사합니다!',
          '제보 내용이 정리되었습니다. 메일 앱이 없는 경우 아래 내용을 전송해주세요.\n\n' + bodyText
        );
        onClose();
      }
    });
  };

  return (
    <Modal
      animationType="slide"
      transparent={true}
      visible={visible}
      onRequestClose={onClose}
    >
      <View className="flex-1 justify-end bg-black/50">
        <View className="bg-white rounded-t-3xl p-5 border-t border-gray-100 max-h-[85%]">
          {/* Modal Header */}
          <View className="flex-row justify-between items-center mb-4 border-b border-gray-100 pb-3">
            <View className="flex-row items-center">
              <Ionicons name="flag-outline" size={22} color="#D96B6B" />
              <Text className="text-lg font-bold text-gray-800 ml-2">의견 남기기 / 오류 제보</Text>
            </View>
            <TouchableOpacity onPress={onClose} className="p-1">
              <Ionicons name="close" size={24} color="#666" />
            </TouchableOpacity>
          </View>

          <ScrollView showsVerticalScrollIndicator={false}>
            {/* Target Word Summary Card (If opened from a card) */}
            {word && (
              <View className="bg-[#FAF9F6] p-3 rounded-2xl border border-gray-100 mb-4 flex-row items-center justify-between">
                <View>
                  <Text className="text-xs text-[#4A725D] font-bold">
                    {word.level?.toUpperCase() || 'N4'} · {word.hiragana}
                  </Text>
                  <Text className="text-xl font-bold text-gray-800">{word.kanji || word.hiragana}</Text>
                  <Text className="text-sm text-gray-600">{word.korean}</Text>
                </View>
                <View className="bg-white px-3 py-1.5 rounded-full border border-gray-200">
                  <Text className="text-xs font-bold text-gray-500">ID: {word.id}</Text>
                </View>
              </View>
            )}

            {/* Category Selector */}
            <Text className="text-sm font-bold text-gray-700 mb-2">제보 유형 선택</Text>
            <View className="mb-4">
              {REPORT_TYPES.map(type => {
                const isSelected = selectedType === type.id;
                return (
                  <TouchableOpacity
                    key={type.id}
                    className={`p-3.5 rounded-2xl mb-2 flex-row items-center border ${isSelected ? 'bg-[#E9F3EB] border-[#7EA48F]' : 'bg-gray-50 border-gray-100'}`}
                    onPress={() => setSelectedType(type.id)}
                  >
                    <Ionicons 
                      name={isSelected ? "checkmark-circle" : "ellipse-outline"} 
                      size={20} 
                      color={isSelected ? "#4A725D" : "#999"} 
                    />
                    <Text className={`ml-2 text-sm font-medium ${isSelected ? 'text-[#4A725D] font-bold' : 'text-gray-700'}`}>
                      {type.label}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>

            {/* Input Comment */}
            <Text className="text-sm font-bold text-gray-700 mb-2">상세 의견 (선택 사항)</Text>
            <TextInput
              className="bg-gray-50 border border-gray-200 rounded-2xl p-3.5 text-gray-800 mb-6 h-24"
              placeholder="어떤 부분이 어색하거나 이상했는지 알려주시면 빠르게 보완하겠습니다."
              placeholderTextColor="#9CA3AF"
              multiline={true}
              textAlignVertical="top"
              value={comment}
              onChangeText={setComment}
            />

            {/* Submit Button */}
            <TouchableOpacity
              className="bg-[#4A725D] rounded-full py-4 items-center mb-4 flex-row justify-center"
              onPress={handleSendEmail}
            >
              <Ionicons name="mail" size={20} color="#FFF" className="mr-2" />
              <Text className="text-white font-bold text-base ml-2">의견 보내기 (이메일)</Text>
            </TouchableOpacity>
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}
