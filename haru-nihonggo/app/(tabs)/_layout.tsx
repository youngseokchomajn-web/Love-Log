import React from 'react';
import { Tabs } from 'expo-router';
import { useColorScheme } from '@/components/useColorScheme';
import { Ionicons } from '@expo/vector-icons';

export default function TabLayout() {
  const colorScheme = useColorScheme();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#333333',
        tabBarInactiveTintColor: '#A0A0A0',
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopColor: '#F0F0F0',
          elevation: 0,
          shadowOpacity: 0,
          height: 65,
          paddingBottom: 10,
          paddingTop: 5,
        },
        headerStyle: {
          backgroundColor: '#FAF9F6',
          elevation: 0,
          shadowOpacity: 0,
        },
        headerTitleStyle: {
          fontWeight: 'bold',
          color: '#333',
        },
        headerTitleAlign: 'left',
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: '홈',
          tabBarIcon: ({ color }) => <Ionicons name="home" size={24} color={color} />,
          headerTitle: 'Haru Voca',
          headerRight: () => <Ionicons name="notifications-outline" size={24} color="#333" style={{ marginRight: 20 }} />,
        }}
      />
      <Tabs.Screen
        name="vocabulary"
        options={{
          title: '단어장',
          tabBarIcon: ({ color }) => <Ionicons name="book" size={24} color={color} />,
        }}
      />
      <Tabs.Screen
        name="quiz"
        options={{
          title: '모의고사',
          tabBarIcon: ({ color }) => <Ionicons name="create-outline" size={24} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: '내 정보',
          tabBarIcon: ({ color }) => <Ionicons name="person-outline" size={24} color={color} />,
        }}
      />
      {/* Hide srs and incorrect from tabs, make them hidden or push them manually */}
      <Tabs.Screen name="srs" options={{ href: null, headerShown: false }} />
      <Tabs.Screen name="incorrect" options={{ href: null, title: '오답노트' }} />
    </Tabs>
  );
}
