import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  FlatList, 
  TouchableOpacity, 
  SafeAreaView, 
  Platform, 
  StatusBar,
  Alert
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../ThemeContext'; // 1. Importa o hook global de tema

const mockNotifications = [
  {
    id: '1',
    title: 'Novo Agendamento',
    description: 'Victor Araújo solicitou uma consulta para 22 de Dezembro às 9h00.',
    time: 'Há 5 min',
    unread: true,
    type: 'calendar'
  },
  {
    id: '2',
    title: 'Consulta Reagendada',
    description: 'Hugo Pontes alterou o horário da consulta para as 14h00.',
    time: 'Há 1 hora',
    unread: false,
    type: 'clock'
  }
];

export default function NotificationsScreen({ navigation }) {
  const [notifications, setNotifications] = useState(mockNotifications);

  // 2. Consome o estado do tema e a paleta de cores dinâmica
  const { isDarkMode, colors } = useTheme();

  const handleSelectNotification = (id) => {
    setNotifications(prev =>
      prev.map(item => item.id === id ? { ...item, unread: false } : item)
    );
  };

  // Função para excluir uma notificação específica
  const handleDeleteNotification = (id) => {
    setNotifications(prev => prev.filter(item => item.id !== id));
  };

  const handleClearAll = () => {
    Alert.alert(
      'Limpar histórico',
      'Deseja apagar todas as notificações da sua lista?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Apagar Todas', style: 'destructive', onPress: () => setNotifications([]) }
      ]
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={colors.container} 
        translucent={false} 
      />

      {/* Cabeçalho Premium Sincronizado */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={[styles.backButton, { backgroundColor: colors.backButtonBg }]} 
          onPress={() => navigation?.goBack()}
          activeOpacity={0.6}
        >
          <Feather name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        
        <View style={styles.headerTitleContainer}>
          <Text style={[styles.headerTitle, { color: colors.text }]}>Notificações</Text>
        </View>

        {notifications.length > 0 ? (
          <TouchableOpacity 
            onPress={handleClearAll} 
            activeOpacity={0.6} 
            style={[styles.clearButton, { backgroundColor: colors.backButtonBg }]}
          >
            <Feather name="trash-2" size={18} color={colors.mutedText} />
          </TouchableOpacity>
        ) : (
          <View style={styles.headerSpacer} />
        )}
      </View>

      {/* Lista ou Estado Vazio Controlado */}
      {notifications.length === 0 ? (
        <View style={styles.emptyContainer}>
          <View style={[styles.emptyIconCircle, { backgroundColor: isDarkMode ? '#1E293B' : '#E2E8F0' }]}>
            <Feather name="bell-off" size={32} color={isDarkMode ? '#64748B' : '#94A3B8'} />
          </View>
          <Text style={[styles.emptyTitle, { color: colors.text }]}>Tudo limpo por aqui</Text>
          <Text style={[styles.emptySubtitle, { color: colors.mutedText }]}>
            Você não possui novas notificações ou alertas pendentes no painel.
          </Text>
        </View>
      ) : (
        <FlatList
          data={notifications}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          renderItem={({ item }) => (
            <TouchableOpacity 
              style={[
                styles.notificationCard, 
                { backgroundColor: colors.card, borderColor: colors.border },
                item.unread && { 
                  borderColor: isDarkMode ? '#3B82F6' : '#CBD5E1', 
                  backgroundColor: isDarkMode ? '#1E293B' : '#FFFFFF' 
                }
              ]}
              onPress={() => handleSelectNotification(item.id)}
              activeOpacity={0.85}
            >
              {/* Topo do Card: Ícone, Tempo e Ação de Excluir */}
              <View style={styles.cardHeader}>
                <View style={styles.headerLeftRow}>
                  <View style={[styles.iconBadgeWrapper, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
                    <Feather 
                      name={item.type === 'calendar' ? 'calendar' : 'clock'} 
                      size={16} 
                      color={isDarkMode ? '#94A3B8' : colors.text} 
                    />
                  </View>
                  
                  <View style={styles.timeBadgeContainer}>
                    {item.unread && <View style={[styles.unreadDot, { backgroundColor: colors.brandBlue }]} />}
                    <Text style={[styles.timeText, { color: colors.mutedText }]}>{item.time}</Text>
                  </View>
                </View>

                {/* Botão Excluir Individual */}
                <TouchableOpacity 
                  onPress={() => handleDeleteNotification(item.id)}
                  style={[styles.deleteButton, { backgroundColor: colors.card, borderColor: colors.border }]}
                  hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                  activeOpacity={0.6}
                >
                  <Feather name="x" size={16} color={colors.mutedText} />
                </TouchableOpacity>
              </View>

              {/* Conteúdo de Texto Dinâmico */}
              <Text style={[
                styles.notificationTitle, 
                { color: colors.text },
                item.unread && styles.unreadTitleText
              ]}>
                {item.title}
              </Text>
              <Text style={[styles.notificationDescription, { color: colors.mutedText }]} numberOfLines={3}>
                {item.description}
              </Text>
            </TouchableOpacity>
          )}
        />
      )}
    </SafeAreaView>
  );
}

// =========================================================================
// DESIGN SYSTEM & ESTILOS PREMIUM
// =========================================================================
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight + 16 : 16,
    paddingBottom: 16,
  },
  backButton: {
    padding: 10,
    borderRadius: 14,
  },
  headerTitleContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: '700',
    letterSpacing: -0.5,
    textAlign: 'center',
    marginLeft: 8,
  },
  clearButton: {
    padding: 10,
    borderRadius: 14,
  },
  headerSpacer: {
    width: 44, 
  },
  listContent: {
    paddingHorizontal: 24,
    paddingTop: 12,
    paddingBottom: 40,
  },
  notificationCard: {
    borderRadius: 20,
    padding: 18,
    marginBottom: 14,
    borderWidth: 1,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.02,
    shadowRadius: 8,
    elevation: 1,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  headerLeftRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconBadgeWrapper: {
    padding: 8,
    borderRadius: 10,
  },
  timeBadgeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 10,
  },
  unreadDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 6,
  },
  timeText: {
    fontSize: 12,
    fontWeight: '500',
  },
  deleteButton: {
    padding: 4,
    borderRadius: 8,
    borderWidth: 1,
  },
  notificationTitle: {
    fontSize: 15,
    fontWeight: '600',
    letterSpacing: -0.2,
    marginBottom: 4,
  },
  unreadTitleText: {
    fontWeight: '700',
  },
  notificationDescription: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: '400',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 44,
    marginBottom: 80,
  },
  emptyIconCircle: {
    padding: 20,
    borderRadius: 24,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 6,
    letterSpacing: -0.2,
  },
  emptySubtitle: {
    fontSize: 13,
    textAlign: 'center',
    lineHeight: 19,
    fontWeight: '400',
  },
});