import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, ImageBackground } from 'react-native';
import ScheduleHeaderNoBack from '../components/ScheduleHeaderNoBack';
import BottomNavBar from '../components/BottomNavBar';

export default function NotificationsScreen({ navigation, showBottomNav = true }) {
  return (
    <ImageBackground
      source={require('../../assets/imagem background.png')}
      style={styles.pageBackground}
      resizeMode="cover"
    >
      <SafeAreaView style={styles.container}>
        <ScheduleHeaderNoBack title="Notificações" />
        <View style={styles.content}>
          <View style={styles.messageCard}>
            <Text style={styles.title}>Ainda não há notificações</Text>
            <Text style={styles.subtitle}>Assim que houver novidades, você verá aqui.</Text>
          </View>
        </View>
        {showBottomNav && (
          <BottomNavBar
            activeTab="notifications"
            onTabPress={(tab) => {
              if (tab === 'home') {
                navigation.navigate('Home');
              } else if (tab === 'schedule') {
                navigation.navigate('Schedule');
              } else if (tab === 'settings') {
                navigation.navigate('Settings');
              }
            }}
          />
        )}
      </SafeAreaView>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  pageBackground: {
    flex: 1,
  },
  container: {
    flex: 1,
    backgroundColor: 'transparent',
    paddingTop: 120,
  },
  content: {
    paddingHorizontal: 20,
    paddingTop: 24,
  },
  messageCard: {
    backgroundColor: '#ffffff',
    borderRadius: 28,
    padding: 24,
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowOffset: { width: 0, height: 10 },
    shadowRadius: 18,
    elevation: 10,
  },
  title: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 14,
    color: '#64748b',
    lineHeight: 20,
  },
});