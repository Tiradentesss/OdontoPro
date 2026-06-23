import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Platform, StatusBar, Dimensions } from 'react-native';
import { Feather, MaterialCommunityIcons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context'; 
import { useTheme } from '../ThemeContext'; // 1. Importa o hook global de tema

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
  const insets = useSafeAreaInsets();
  
  // 2. Consome o estado do tema e a paleta de cores dinâmica
  const { isDarkMode, colors } = useTheme();

  const nextAppointment = {
    patient: "Luciana Alencar",
    procedure: "Manutenção de Aparelho",
    time: "14:30",
    date: "Hoje, 27 de Maio",
    avatarColor: isDarkMode ? '#1E3A8A' : '#EFF6FF',
    textColor: isDarkMode ? '#60A5FA' : '#163783'
  };

  return (
    <View style={[styles.container, { backgroundColor: colors.container }]}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={colors.container} 
        translucent={false} 
      />
      
      <ScrollView 
        showsVerticalScrollIndicator={false}
        contentContainerStyle={[
          styles.scrollContent, 
          { paddingTop: Platform.OS === 'android' ? insets.top + 16 : 16 }
        ]}
      >
        
        {/* Cabeçalho */}
        <View style={styles.header}>
          <View style={styles.textGroup}>
            <Text style={[styles.greeting, { color: colors.text }]}>Olá, Gabriel</Text>
            <Text style={styles.subtitle}>Veja o panorama e a agenda da sua clínica para hoje.</Text>
          </View>
          
          <TouchableOpacity 
            style={[styles.notificationBtn, { backgroundColor: colors.card, borderColor: colors.border }]} 
            activeOpacity={0.6}
            onPress={() => navigation?.navigate('NotificationsScreen')}
          >
            <Feather name="bell" size={20} color={colors.text} />
            <View style={styles.badge} />
          </TouchableOpacity>
        </View>

        {/* Grade de Ações Principais */}
        <View style={styles.actionGrid}>
          <TouchableOpacity 
            style={[styles.gridCard, { backgroundColor: colors.card, borderColor: colors.border }]}
            onPress={() => navigation?.navigate('AgendaTab')}
            activeOpacity={0.7}
          >
            <View style={[styles.gridIconBg, { backgroundColor: isDarkMode ? '#1E3A8A' : '#EFF6FF' }]}>
              <Feather name="calendar" size={20} color={isDarkMode ? '#60A5FA' : '#163783'} />
            </View>
            <Text style={[styles.gridCardTitle, { color: colors.text }]}>Agenda</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.gridCard, { backgroundColor: colors.card, borderColor: colors.border }]}
            onPress={() => navigation?.navigate('ReportsScreen')}
            activeOpacity={0.7}
          >
            <View style={[styles.gridIconBg, { backgroundColor: isDarkMode ? '#064E3B' : '#F0FDF4' }]}>
              <Feather name="bar-chart-2" size={20} color={isDarkMode ? '#34D399' : '#10B981'} />
            </View>
            <Text style={[styles.gridCardTitle, { color: colors.text }]}>Relatórios</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.gridCard, { backgroundColor: colors.card, borderColor: colors.border }]}
            onPress={() => navigation?.navigate('PatientsScreen')}
            activeOpacity={0.7}
          >
            <View style={[styles.gridIconBg, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
              <Feather name="users" size={20} color={isDarkMode ? '#94A3B8' : '#475569'} />
            </View>
            <Text style={[styles.gridCardTitle, { color: colors.text }]}>Pacientes</Text>
          </TouchableOpacity>
        </View>

        {/* Próximo Atendimento */}
        <Text style={[styles.sectionTitle, { color: colors.text }]}>Próximo Atendimento</Text>
        <TouchableOpacity 
          style={[styles.reminderCard, { backgroundColor: colors.card, borderColor: colors.border }]} 
          activeOpacity={0.8}
          onPress={() => navigation?.navigate('AgendaTab')}
        >
          <View style={styles.reminderHeader}>
            <View style={[styles.avatarPlaceholder, { backgroundColor: nextAppointment.avatarColor }]}>
              <Text style={[styles.avatarText, { color: nextAppointment.textColor }]}>
                {nextAppointment.patient.charAt(0)}
              </Text>
            </View>
            <View style={styles.reminderInfo}>
              <Text style={[styles.patientName, { color: colors.text }]}>{nextAppointment.patient}</Text>
              <Text style={styles.procedureName}>{nextAppointment.procedure}</Text>
            </View>
            <View style={[styles.timeTag, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
              <Text style={[styles.timeTagText, { color: colors.text }]}>{nextAppointment.time}</Text>
            </View>
          </View>
          
          <View style={[styles.reminderFooter, { borderColor: colors.border }]}>
            <Feather name="clock" size={12} color="#64748B" style={{ marginRight: 6 }} />
            <Text style={styles.reminderFooterText}>{nextAppointment.date}</Text>
          </View>
        </TouchableOpacity>

        {/* Destaques da Clínica */}
        <Text style={[styles.sectionTitle, { color: colors.text }]}>Destaques da Clínica</Text>
        <View style={[styles.insightsCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <View style={styles.insightRow}>
            <View style={[styles.insightIconWrapper, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
              <MaterialCommunityIcons name="account-group-outline" size={20} color={isDarkMode ? '#94A3B8' : '#475569'} />
            </View>
            <View style={styles.insightBody}>
              <Text style={[styles.insightTitle, { color: colors.text }]}>Volume de Pacientes</Text>
              <Text style={styles.insightMeta}>142 ativos em tratamento contínuo</Text>
            </View>
            <View style={[styles.statusBadge, { backgroundColor: isDarkMode ? '#064E3B' : '#F0FDF4' }]}>
              <Text style={[styles.statusText, { color: isDarkMode ? '#34D399' : '#16A34A' }]}>Estável</Text>
            </View>
          </View>

          <View style={[styles.insightDivider, { backgroundColor: colors.border }]} />

          <View style={styles.insightRow}>
            <View style={[styles.insightIconWrapper, { backgroundColor: isDarkMode ? '#0C4A6E' : '#E0F2FE' }]}>
              <MaterialCommunityIcons name="currency-usd" size={20} color={isDarkMode ? '#38BDF8' : '#0369A1'} />
            </View>
            <View style={styles.insightBody}>
              <Text style={[styles.insightTitle, { color: colors.text }]}>Balanço Estimado do Mês</Text>
              <Text style={styles.insightMeta}>Metas de fechamento alinhadas com o esperado</Text>
            </View>
            <View style={[styles.statusBadge, { backgroundColor: isDarkMode ? '#0C4A6E' : '#E0F2FE' }]}>
              <Text style={[styles.statusText, { color: isDarkMode ? '#38BDF8' : '#0369A1' }]}>+14%</Text>
            </View>
          </View>

          <View style={[styles.insightDivider, { backgroundColor: colors.border }]} />

          <View style={styles.insightRow}>
            <View style={[styles.insightIconWrapper, { backgroundColor: isDarkMode ? '#4C1D95' : '#FFF7ED' }]}>
              <MaterialCommunityIcons name="lightbulb-on-outline" size={20} color={isDarkMode ? '#C084FC' : '#EA580C'} />
            </View>
            <View style={styles.insightBody}>
              <Text style={[styles.insightTitle, { color: colors.text }]}>Oportunidade de Retenção</Text>
              <Text style={styles.insightMeta}>3 pacientes não retornam há mais de 6 meses.</Text>
            </View>
          </View>
        </View>

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 24,
    paddingBottom: 140, 
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 24,
  },
  textGroup: {
    flex: 1,
    paddingRight: 16,
  },
  greeting: {
    fontSize: 26,
    fontWeight: '800',
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 13,
    color: '#64748B', 
    marginTop: 4,
    fontWeight: '500',
    lineHeight: 18,
    letterSpacing: -0.1,
  },
  notificationBtn: {
    padding: 10,
    borderRadius: 12,
    position: 'relative',
    borderWidth: 1,
    marginTop: 2,
  },
  badge: {
    position: 'absolute',
    top: 9,
    right: 10,
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#EF4444', 
  },
  actionGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
    marginTop: 4,
  },
  gridCard: {
    width: (width - 64) / 3, 
    paddingVertical: 16,
    paddingHorizontal: 12,
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 1,
  },
  gridIconBg: {
    width: 40,
    height: 40,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  gridCardTitle: {
    fontSize: 12,
    fontWeight: '600',
    letterSpacing: -0.1,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '700',
    marginTop: 24,
    marginBottom: 12,
    letterSpacing: -0.2,
  },
  reminderCard: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
  },
  reminderHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatarPlaceholder: {
    width: 42,
    height: 42,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarText: {
    fontSize: 15,
    fontWeight: '700',
  },
  reminderInfo: {
    flex: 1,
  },
  patientName: {
    fontSize: 15,
    fontWeight: '700',
  },
  procedureName: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '500',
    marginTop: 1,
  },
  timeTag: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
  },
  timeTagText: {
    fontSize: 12,
    fontWeight: '700',
  },
  reminderFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    borderTopWidth: 1,
    marginTop: 14,
    paddingTop: 12,
  },
  reminderFooterText: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '500',
  },
  insightsCard: {
    borderRadius: 16,
    paddingHorizontal: 16,
    borderWidth: 1,
  },
  insightRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 14,
  },
  insightIconWrapper: {
    width: 36,
    height: 36,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  insightBody: {
    flex: 1,
    paddingRight: 8,
  },
  insightTitle: {
    fontSize: 13,
    fontWeight: '700',
  },
  insightMeta: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '500',
    marginTop: 2,
    lineHeight: 15,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '700',
  },
  insightDivider: {
    height: 1,
  },
});