import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, TouchableOpacity, Image, ImageBackground } from 'react-native';
import ScheduleHeaderNoBack from '../components/ScheduleHeaderNoBack';
import BottomNavBar from '../components/BottomNavBar';

export default function SettingsScreen({ navigation, showBottomNav = true }) {
  return (
    <ImageBackground
      source={require('../../assets/imagem background.png')}
      style={styles.pageBackground}
      resizeMode="cover"
    >
      <SafeAreaView style={styles.container}>
        <ScheduleHeaderNoBack title="Configurações" />

        <View style={styles.content}>
          <View style={styles.topCard}>
            <View style={styles.iconWrapper} />
            <Text style={styles.profileName}>Nome da Conta</Text>
          </View>

          <View style={styles.optionCard}>
            <TouchableOpacity style={styles.optionRow} activeOpacity={0.8} onPress={() => navigation.navigate('PersonalInfo')}>
              <Image source={require('../../assets/IconHome.png')} style={styles.optionIcon} resizeMode="contain" />
              <View style={styles.optionText}>
                <Text style={styles.optionTitle}>Informações Pessoais</Text>
                <Text style={styles.optionSubtitle}>Atualize seus dados</Text>
              </View>
            </TouchableOpacity>
            <TouchableOpacity style={styles.optionRow} activeOpacity={0.8} onPress={() => navigation.navigate('System')}>
              <Image source={require('../../assets/IconClipboard.png')} style={styles.optionIcon} resizeMode="contain" />
              <View style={styles.optionText}>
                <Text style={styles.optionTitle}>Sistema</Text>
                <Text style={styles.optionSubtitle}>Configurações do aplicativo</Text>
              </View>
            </TouchableOpacity>
            <TouchableOpacity style={styles.optionRow} activeOpacity={0.8} onPress={() => navigation.navigate('NotificationSettings')}>
              <Image source={require('../../assets/IconNotificacao.png')} style={styles.optionIcon} resizeMode="contain" />
              <View style={styles.optionText}>
                <Text style={styles.optionTitle}>Notificações</Text>
                <Text style={styles.optionSubtitle}>Gerencie alertas e sons</Text>
              </View>
            </TouchableOpacity>
            <TouchableOpacity style={styles.optionRow} activeOpacity={0.8} onPress={() => navigation.navigate('Login')}>
              <Image source={require('../../assets/IconConfiguracao.png')} style={styles.optionIcon} resizeMode="contain" />
              <View style={styles.optionText}>
                <Text style={styles.optionTitle}>Sair</Text>
                <Text style={styles.optionSubtitle}>Encerrar sessão</Text>
              </View>
            </TouchableOpacity>
          </View>
        </View>
        {showBottomNav && (
          <BottomNavBar
            activeTab="settings"
            onTabPress={(tab) => {
              if (tab === 'home') {
                navigation.navigate('Home');
              } else if (tab === 'schedule') {
                navigation.navigate('Schedule');
              } else if (tab === 'notifications') {
                navigation.navigate('Notifications');
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
  topCard: {
    alignItems: 'center',
    marginBottom: 24,
  },
  iconWrapper: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#e0f2fe',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 18,
  },
  icon: {
    width: 0,
    height: 0,
  },
  screenTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 6,
  },
  screenSubtitle: {
    fontSize: 14,
    color: '#64748b',
    textAlign: 'center',
    lineHeight: 20,
  },
  optionCard: {
    backgroundColor: '#ffffff',
    borderRadius: 24,
    paddingVertical: 12,
    paddingHorizontal: 14,
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowOffset: { width: 0, height: 10 },
    shadowRadius: 18,
    elevation: 10,
  },
  optionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  optionIcon: {
    width: 28,
    height: 28,
    tintColor: '#0ea5e9',
    marginRight: 12,
  },
  optionText: {
    flex: 1,
  },
  profileName: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0f172a',
    marginTop: -8,
    marginBottom: 16,
  },
  optionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 4,
  },
  optionSubtitle: {
    fontSize: 13,
    color: '#64748b',
  },
});