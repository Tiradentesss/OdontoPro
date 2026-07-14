import React from 'react';
import { View, Text, StyleSheet, SafeAreaView } from 'react-native';
import { Bell } from 'lucide-react-native';
import ScheduleHeaderNoBack from '../components/ScheduleHeaderNoBack';
import BottomNavBar from '../components/BottomNavBar';

export default function NotificationsScreen({ navigation, showBottomNav = true }) {
  return (
    // Removido o ImageBackground e colocado um View com estilo container
    <View style={styles.pageContainer}>
      <SafeAreaView style={styles.container}>
        <ScheduleHeaderNoBack title="Notificações" />

        <View style={styles.content}>
          <View style={styles.emptyContainer}>
            <Bell size={48} color="#cbd5e1" strokeWidth={1.5} style={styles.icon} />
            <Text style={styles.emptyText}>Não há notificações no momento</Text>
          </View>
        </View>

        {showBottomNav && (
          <BottomNavBar
            activeTab="notifications"
            onTabPress={(tab) => navigation.navigate(tab.charAt(0).toUpperCase() + tab.slice(1))}
          />
        )}
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  pageContainer: {
    flex: 1,
    backgroundColor: '#f8fafc', // Cor de fundo limpa (ajuste conforme a sua Home)
  },
  container: { 
    flex: 1, 
  },
  content: { 
    flex: 1, 
    justifyContent: 'center', 
    alignItems: 'center',
    paddingHorizontal: 30
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  icon: {
    marginBottom: 16,
    opacity: 0.8,
  },
  emptyText: {
    fontSize: 16,
    color: '#94a3b8',
    fontWeight: '500',
    textAlign: 'center',
  },
});