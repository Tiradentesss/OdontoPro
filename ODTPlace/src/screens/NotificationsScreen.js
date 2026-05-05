import React, { useState, useEffect, useMemo } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ImageBackground, FlatList, TouchableOpacity } from 'react-native';
import ScheduleHeaderNoBack from '../components/ScheduleHeaderNoBack';
import BottomNavBar from '../components/BottomNavBar';
import { getPatientAppointments } from '../services/api';
import { useAuth } from '../context/AuthContext';

const NOTIFICATION_TYPES = {
  UPCOMING: 'upcoming',       // 1 dia antes
  TODAY: 'today',            // mesmo dia
  MISSED: 'missed',          // passou do horário e não foi finalizada
};

export default function NotificationsScreen({ navigation, showBottomNav = true }) {
  const { user } = useAuth();
  const [appointmentsData, setAppointmentsData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAppointments = async () => {
      if (!user?.id && !user?.email) {
        setLoading(false);
        return;
      }
      
      try {
        const patientId = user.id;
        let data;
        if (patientId) {
          data = await getPatientAppointments(String(patientId));
        } else if (user.email) {
          data = await getPatientAppointments(user.email);
        }
        setAppointmentsData(data || []);
      } catch (error) {
        console.log('Error loading appointments:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAppointments();
  }, [user?.id, user?.email]);

  // Gerar notificações baseadas nos agendamentos
  const notifications = useMemo(() => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const result = [];

    appointmentsData.forEach((apt) => {
      const aptDate = new Date(apt.data_hora);
      const aptDay = new Date(aptDate.getFullYear(), aptDate.getMonth(), aptDate.getDate());
      const aptTimeStr = aptDate.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
      
      // Converter hora da consulta para minutos desde meia-noite
      const aptMinutes = aptDate.getHours() * 60 + aptDate.getMinutes();
      const nowMinutes = now.getHours() * 60 + now.getMinutes();
      
      const isConfirmed = apt.status === 'confirmada' || apt.status === 'realizada';
      const isPast = aptDay < today;
      const isToday = aptDay.getTime() === today.getTime();
      const isTomorrow = aptDay.getTime() === tomorrow.getTime();
      const isUpcoming = aptDay > today;
      
      // Consulta perdida: passou do horário hoje e não foi confirmada
      if (isToday && !isConfirmed && aptMinutes < nowMinutes) {
        result.push({
          id: `missed-${apt.id}`,
          type: NOTIFICATION_TYPES.MISSED,
          title: 'Consulta Perdida',
          message: `Você perdeu sua consulta das ${aptTimeStr} com ${apt.medico_nome || 'o médico'} na ${apt.clinica_nome || 'clínica'}.`,
          time: 'Agora',
          icon: '⚠️',
          aptData: apt,
        });
      }
      
      // Consulta hoje (próximas ou em andamento)
      if (isToday && isConfirmed) {
        if (aptMinutes >= nowMinutes - 30) { // 30 min antes ou depois
          result.push({
            id: `today-${apt.id}`,
            type: NOTIFICATION_TYPES.TODAY,
            title: 'Consulta Hoje',
            message: `Sua consulta com ${apt.medico_nome || 'o médico'} é às ${aptTimeStr} na ${apt.clinica_nome || 'clínica'}.`,
            time: aptTimeStr,
            icon: '',
            aptData: apt,
          });
        }
      }
      
      // Consulta amanhã
      if (isTomorrow && isConfirmed) {
        result.push({
          id: `upcoming-${apt.id}`,
          type: NOTIFICATION_TYPES.UPCOMING,
          title: 'Consulta Amanhã',
          message: `Você tem uma consulta amanhã às ${aptTimeStr} com ${apt.medico_nome || 'o médico'} na ${apt.clinica_nome || 'clínica'}.`,
          time: 'Amanhã',
          icon: '⏰',
          aptData: apt,
        });
      }
    });

    // Ordenar: perdidas primeiro, depois hoje, depois amanhã
    const priority = { [NOTIFICATION_TYPES.MISSED]: 0, [NOTIFICATION_TYPES.TODAY]: 1, [NOTIFICATION_TYPES.UPCOMING]: 2 };
    result.sort((a, b) => priority[a.type] - priority[b.type]);

    return result;
  }, [appointmentsData]);

  const renderNotification = ({ item }) => {
    const getTypeStyle = () => {
      switch (item.type) {
        case NOTIFICATION_TYPES.MISSED:
          return { bg: '#fef2f2', border: '#fecaca', text: '#dc2626' };
        case NOTIFICATION_TYPES.TODAY:
          return { bg: '#f0f9ff', border: '#bae6fd', text: '#0284c7' };
        case NOTIFICATION_TYPES.UPCOMING:
          return { bg: '#f0fdf4', border: '#bbf7d0', text: '#16a34a' };
        default:
          return { bg: '#f8fafc', border: '#e2e8f0', text: '#64748b' };
      }
    };
    
    const typeStyle = getTypeStyle();
    
    return (
      <TouchableOpacity 
        style={[styles.notificationCard, { backgroundColor: typeStyle.bg, borderColor: typeStyle.border }]}
        activeOpacity={0.85}
      >
        <View style={styles.notificationHeader}>
          <Text style={styles.notificationIcon}>{item.icon}</Text>
          <View style={styles.notificationTitleRow}>
            <Text style={[styles.notificationTitle, { color: typeStyle.text }]}>{item.title}</Text>
            <Text style={styles.notificationTime}>{item.time}</Text>
          </View>
        </View>
        <Text style={styles.notificationMessage}>{item.message}</Text>
      </TouchableOpacity>
    );
  };

  return (
    <ImageBackground
      source={require('../../assets/imagem background.png')}
      style={styles.pageBackground}
      resizeMode="cover"
    >
      <SafeAreaView style={styles.container}>
        <ScheduleHeaderNoBack title="Notificações" />
        <View style={styles.content}>
          {loading ? (
            <View style={styles.messageCard}>
              <Text style={styles.title}>Carregando...</Text>
            </View>
          ) : notifications.length === 0 ? (
            <View style={styles.messageCard}>
              <Text style={styles.title}>Ainda não há notificações</Text>
              <Text style={styles.subtitle}>Assim que houver novidades, você verá aqui.</Text>
            </View>
          ) : (
            <FlatList
              data={notifications}
              keyExtractor={(item) => item.id}
              renderItem={renderNotification}
              showsVerticalScrollIndicator={false}
              contentContainerStyle={styles.listContent}
            />
          )}
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
  listContent: {
    paddingBottom: 100,
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
  notificationCard: {
    borderRadius: 20,
    padding: 18,
    marginBottom: 14,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 8,
    elevation: 4,
  },
  notificationHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  notificationIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  notificationTitleRow: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  notificationTitle: {
    fontSize: 16,
    fontWeight: '800',
  },
  notificationTime: {
    fontSize: 12,
    color: '#64748b',
    fontWeight: '600',
  },
  notificationMessage: {
    fontSize: 14,
    color: '#334155',
    lineHeight: 20,
  },
});