import React, { useState, useMemo } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  FlatList, 
  TouchableOpacity, 
  Image, 
  SafeAreaView, 
  Platform, 
  StatusBar,
  TextInput,
  ScrollView
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../components/ThemeContext'; // 1. Importa o hook global de tema

// Mapeamento dinâmico de Especialidades para manter contraste Premium em ambos os modos
const getSegmentStyle = (segment, isDarkMode) => {
  const stylesMap = {
    'Estética': { bg: '#FAE8FF', text: '#A21CAF', darkBg: '#4A1D4E', darkText: '#F472B6' },
    'Ortodontia': { bg: '#EFF6FF', text: '#1D4ED8', darkBg: '#1E3A8A', darkText: '#60A5FA' },
    'Implante': { bg: '#FEF3C7', text: '#B45309', darkBg: '#78350F', darkText: '#FBBF24' },
    'Clínico Geral': { bg: '#E1F5FE', text: '#0288D1', darkBg: '#01579B', darkText: '#29B6F6' },
    'Cirurgia': { bg: '#FEE2E2', text: '#B91C1C', darkBg: '#7F1D1D', darkText: '#F87171' },
  };

  const current = stylesMap[segment] || { bg: '#F1F5F9', text: '#475569', darkBg: '#334155', darkText: '#94A3B8' };
  return {
    backgroundColor: isDarkMode ? current.darkBg : current.bg,
    color: isDarkMode ? current.darkText : current.text
  };
};

// Mapeamento de Cores para as Tags de Status
const getStatusColor = (status, isDarkMode) => {
  const statusMap = {
    'Concluído': { light: '#10B981', dark: '#34D399' },
    'Em Revisão': { light: '#3B82F6', dark: '#60A5FA' },
  };
  return statusMap[status]?.[isDarkMode ? 'dark' : 'light'] || '#64748B';
};

const mockHistory = [
  { id: '1', name: 'Alex Batista', segment: 'Estética', recordStatus: 'Concluído', lastProcedure: 'Clareamento a Laser', time: '14:30', dateLabel: 'Hoje', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=120&h=120' },
  { id: '2', name: 'Eduarda Maria', segment: 'Ortodontia', recordStatus: 'Concluído', lastProcedure: 'Manutenção de Aparelho', time: '10:15', dateLabel: 'Hoje', avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&q=80&w=120&h=120' },
  { id: '3', name: 'Hugo Pontes', segment: 'Implante', recordStatus: 'Em Revisão', lastProcedure: 'Instalação de Prótese', time: '16:00', dateLabel: 'Ontem', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=120&h=120' },
  { id: '4', name: 'João Claudio', segment: 'Clínico Geral', recordStatus: 'Concluído', lastProcedure: 'Limpeza e Profilaxia', time: '11:00', dateLabel: 'Ontem', avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=120&h=120' },
  { id: '5', name: 'José Alves', segment: 'Cirurgia', recordStatus: 'Concluído', lastProcedure: 'Extração de Siso (38)', time: '09:30', dateLabel: '28 de Maio', avatar: 'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&q=80&w=120&h=120' },
];

export default function PatientsHistoryScreen({ navigation }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('Todos'); 

  // 2. Consome o estado do tema e a paleta de cores dinâmica
  const { isDarkMode, colors } = useTheme();

  // Filtra os dados crus ANTES de montar o esqueleto de grupos da listagem
  const groupedHistory = useMemo(() => {
    const formattedQuery = searchQuery.trim().toLowerCase();
    
    const filteredRawData = mockHistory.filter(item => {
      const matchesSearch = !formattedQuery || 
        item.name.toLowerCase().includes(formattedQuery) || 
        item.lastProcedure.toLowerCase().includes(formattedQuery) ||
        item.segment.toLowerCase().includes(formattedQuery);

      if (!matchesSearch) return false;

      if (activeFilter === 'Hoje') return item.dateLabel === 'Hoje';
      if (activeFilter === 'Esta Semana') return item.dateLabel === 'Hoje' || item.dateLabel === 'Ontem';
      return true; 
    });

    const groups = filteredRawData.reduce((acc, item) => {
      const key = item.dateLabel;
      if (!acc[key]) acc[key] = [];
      acc[key].push(item);
      return acc;
    }, {});

    return Object.keys(groups).map(date => ({
      date,
      data: groups[date]
    }));
  }, [searchQuery, activeFilter]);

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={colors.container} 
        translucent={false} 
      />
      
      {/* Cabeçalho */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={[styles.backButton, { backgroundColor: colors.backButtonBg }]} 
          onPress={() => navigation?.goBack()}
          activeOpacity={0.6}
        >
          <Feather name="arrow-left" size={22} color={colors.text} />
        </TouchableOpacity>
        <View style={styles.headerTitleContainer}>
          <Text style={[styles.headerTitle, { color: colors.text }]}>Histórico Clínico</Text>
        </View>
        <View style={styles.headerSpacer} />
      </View>

      {/* Barra de Pesquisa */}
      <View style={styles.searchSection}>
        <View style={[styles.searchContainer, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <Feather name="search" size={18} color={colors.mutedText} style={styles.searchIcon} />
          <TextInput
            style={[styles.searchInput, { color: colors.text }]}
            placeholder="Buscar por nome ou procedimento..."
            placeholderTextColor={colors.mutedText}
            value={searchQuery}
            onChangeText={setSearchQuery}
            autoCorrect={false}
            autoCapitalize="none"
          />
          {searchQuery.trim().length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')} style={styles.clearButton} activeOpacity={0.5}>
              <Feather name="x" size={16} color={colors.mutedText} />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Filtros Horizontais Dinâmicos */}
      <View style={styles.filterSection}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filterScroll}>
          <Text style={[styles.filterLabelText, { color: colors.mutedText }]}>Filtrar:</Text>
          
          {['Todos', 'Hoje', 'Esta Semana', 'Este Mês'].map((filter) => {
            const isSelected = activeFilter === filter;
            return (
              <TouchableOpacity
                key={filter}
                activeOpacity={0.8}
                onPress={() => setActiveFilter(filter)}
                style={[
                  styles.filterChip,
                  { 
                    backgroundColor: isSelected 
                      ? colors.brandBlue 
                      : (isDarkMode ? '#1E293B' : '#F4F7FC') 
                  }
                ]}
              >
                <Text style={[
                  styles.filterChipText, 
                  { color: isSelected ? '#FFFFFF' : colors.mutedText }
                ]}>
                  {filter}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {/* Lista Principal Dinâmica */}
      <FlatList
        data={groupedHistory}
        keyExtractor={item => item.date}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={() => (
          <View style={styles.emptyContainer}>
            <Feather name="search" size={40} color={colors.mutedText} style={{ marginBottom: 12 }} />
            <Text style={[styles.emptyText, { color: colors.mutedText }]}>
              Nenhum resultado para a busca realizada.
            </Text>
          </View>
        )}
        renderItem={({ item: group }) => (
          <View style={styles.timelineGroup}>
            <View style={styles.timelineHeader}>
              <Text style={[styles.timelineDateText, { color: colors.mutedText }]}>{group.date}</Text>
              <View style={[styles.timelineLine, { backgroundColor: colors.border }]} />
            </View>

            {group.data.map((item) => {
              const badgeStyle = getSegmentStyle(item.segment, isDarkMode);
              const statusColor = getStatusColor(item.recordStatus, isDarkMode);

              return (
                <View key={item.id} style={[styles.patientCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
                  <Image source={{ uri: item.avatar }} style={[styles.avatar, { borderColor: colors.border }]} />
                  
                  <View style={styles.infoContainer}>
                    <View style={styles.nameRow}>
                      <Text style={[styles.patientName, { color: colors.text }]} numberOfLines={1}>
                        {item.name}
                      </Text>
                      <Text style={[styles.timeText, { color: isDarkMode ? '#64748B' : '#94A3B8' }]}>{item.time}</Text>
                    </View>
                    
                    <View style={styles.metaRow}>
                      <View style={[styles.badge, { backgroundColor: badgeStyle.backgroundColor }]}>
                        <Text style={[styles.badgeText, { color: badgeStyle.color }]}>
                          {item.segment}
                        </Text>
                      </View>

                      <View style={styles.procedureContainer}>
                        <Feather name="check-circle" size={12} color={colors.mutedText} style={styles.metaIcon} />
                        <Text style={[styles.procedureText, { color: colors.mutedText }]} numberOfLines={1}>
                          {item.lastProcedure}
                        </Text>
                      </View>
                    </View>
                  </View>
                  
                  <View style={styles.statusRightContainer}>
                    <View style={[styles.statusIndicatorTag, { backgroundColor: statusColor + '15' }]}>
                      <Text style={[styles.statusIndicatorText, { color: statusColor }]}>{item.recordStatus}</Text>
                    </View>
                  </View>
                </View>
              );
            })}
          </View>
        )}
      />
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
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight + 12 : 12,
    paddingBottom: 4,
  },
  backButton: {
    padding: 10,
    borderRadius: 12,
  },
  headerTitleContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: { 
    fontSize: 20, 
    fontWeight: '700', 
    letterSpacing: -0.4,
    textAlign: 'center',
    marginLeft: 8,
  },
  headerSpacer: {
    width: 42, 
  },
  searchSection: {
    paddingHorizontal: 24,
    marginTop: 16,
    marginBottom: 16,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: 14,
    paddingHorizontal: 14,
    height: 46,
  },
  searchIcon: {
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    fontSize: 14,
    fontWeight: '500',
    height: '100%',
  },
  clearButton: {
    padding: 4,
  },
  filterSection: {
    marginBottom: 20,
  },
  filterScroll: {
    paddingHorizontal: 24,
    alignItems: 'center',
    gap: 10,
  },
  filterLabelText: {
    fontSize: 15,
    fontWeight: '700',
    marginRight: 4,
  },
  filterChip: {
    paddingHorizontal: 18,
    paddingVertical: 10,
    borderRadius: 30, 
    justifyContent: 'center',
    alignItems: 'center',
  },
  filterChipText: {
    fontSize: 14,
    fontWeight: '600',
    letterSpacing: -0.2,
  },
  listContent: {
    paddingHorizontal: 24,
    paddingBottom: 32,
  },
  timelineGroup: {
    marginBottom: 16,
  },
  timelineHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  timelineDateText: {
    fontSize: 13,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginRight: 10,
  },
  timelineLine: {
    flex: 1,
    height: 1,
  },
  patientCard: {
    padding: 12,
    borderRadius: 16,
    marginBottom: 10,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.02,
    shadowRadius: 4,
    elevation: 0.5,
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 10,
    borderWidth: 1,
  },
  infoContainer: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'center',
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
    paddingRight: 4,
  },
  patientName: { 
    fontSize: 15, 
    fontWeight: '600', 
    letterSpacing: -0.1,
    flex: 1,
    marginRight: 8,
  },
  timeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  badge: {
    paddingHorizontal: 6,
    paddingVertical: 2.5,
    borderRadius: 6,
    marginRight: 8,
  },
  badgeText: {
    fontSize: 11,
    fontWeight: '600',
  },
  procedureContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    paddingRight: 6,
  },
  metaIcon: {
    marginRight: 4,
  },
  procedureText: {
    fontSize: 12,
    fontWeight: '400',
  },
  statusRightContainer: {
    justifyContent: 'center',
    alignItems: 'flex-end',
    marginLeft: 4,
  },
  statusIndicatorTag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statusIndicatorText: {
    fontSize: 11,
    fontWeight: '700',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 48,
  },
  emptyText: {
    fontSize: 14,
    fontWeight: '500',
  }
});