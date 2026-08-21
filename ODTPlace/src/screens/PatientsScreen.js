import React, { useEffect, useMemo, useState } from 'react';
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
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../components/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { getProfessionalAppointments } from '../services/api';
import { formatAppointmentDateKey, formatAppointmentTime, parseAppointmentDate } from '../utils/appointmentTime';

const normalizeStatus = (status) => (status || '').toString().toLowerCase();

const getStatusColor = (status, isDarkMode) => {
  const normalized = normalizeStatus(status);
  const statusMap = {
    confirmada: { light: '#10B981', dark: '#34D399' },
    reagendada: { light: '#38BDF8', dark: '#7DD3FC' },
    pendente: { light: '#F59E0B', dark: '#FBBF24' },
    cancelada: { light: '#EF4444', dark: '#F87171' },
    realizada: { light: '#10B981', dark: '#34D399' },
    completa: { light: '#10B981', dark: '#34D399' },
  };
  return statusMap[normalized] || { light: '#64748B', dark: '#94A3B8' };
};

const formatDateLabel = (dateValue) => {
  if (!dateValue) return 'Data não definida';
  const date = typeof dateValue === 'string' ? new Date(dateValue) : dateValue;
  if (Number.isNaN(date.getTime())) return 'Data não definida';
  return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' });
};

const isSameDay = (date1, date2) => {
  return (
    date1.getDate() === date2.getDate() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getFullYear() === date2.getFullYear()
  );
};

const isSameMonth = (date1, date2) => {
  return (
    date1.getMonth() === date2.getMonth() &&
    date1.getFullYear() === date2.getFullYear()
  );
};

const isWithinCurrentWeek = (referenceDate, targetDate) => {
  const startOfWeek = new Date(referenceDate);
  startOfWeek.setDate(referenceDate.getDate() - referenceDate.getDay());
  startOfWeek.setHours(0, 0, 0, 0);
  const endOfWeek = new Date(startOfWeek);
  endOfWeek.setDate(startOfWeek.getDate() + 6);
  endOfWeek.setHours(23, 59, 59, 999);
  return targetDate >= startOfWeek && targetDate <= endOfWeek;
};

const getRelativeLabel = (date) => {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);

  if (isSameDay(today, date)) return 'Hoje';
  if (isSameDay(yesterday, date)) return 'Ontem';
  return formatDateLabel(date);
};

const getAvatarUrl = (name) => {
  const encodedName = encodeURIComponent(name || 'Paciente');
  return `https://ui-avatars.com/api/?name=${encodedName}&background=0D8ABC&color=fff&size=120`;
};

export default function PatientsScreen({ navigation }) {
  const { isDarkMode, colors } = useTheme();
  const { user } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('Todos');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadAppointments = async () => {
      if (!user?.id) {
        setAppointments([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await getProfessionalAppointments({ medico_id: user.id });
        setAppointments(Array.isArray(data) ? data : []);
      } catch (fetchError) {
        console.error('Error loading professional appointments:', fetchError);
        setError('Não foi possível carregar os pacientes. Verifique sua conexão e tente novamente.');
      } finally {
        setLoading(false);
      }
    };

    loadAppointments();
  }, [user?.id]);

  const filteredAppointments = useMemo(() => {
    const normalizedQuery = searchQuery.trim().toLowerCase();
    const now = new Date();

    return appointments.filter((item) => {
      if (!item) return false;

      const appointmentDate = item.data_hora ? parseAppointmentDate(item.data_hora) : null;
      const matchesQuery = !normalizedQuery || [
        item.nome,
        item.observacoes,
        item.especialidade_nome,
        item.clinica_nome,
      ].some((value) => value?.toString().toLowerCase().includes(normalizedQuery));

      if (!matchesQuery) return false;

      if (activeFilter === 'Hoje') {
        return appointmentDate ? isSameDay(now, appointmentDate) : false;
      }

      if (activeFilter === 'Esta Semana') {
        return appointmentDate ? isWithinCurrentWeek(now, appointmentDate) : false;
      }

      if (activeFilter === 'Este Mês') {
        return appointmentDate ? isSameMonth(now, appointmentDate) : false;
      }

      return true;
    });
  }, [appointments, searchQuery, activeFilter]);

  const groupedAppointments = useMemo(() => {
    const groups = filteredAppointments.reduce((acc, item) => {
      const appointmentDate = item.data_hora ? parseAppointmentDate(item.data_hora) : null;
      const groupKey = appointmentDate ? formatAppointmentDateKey(appointmentDate) : 'sem-data';

      if (!acc[groupKey]) {
        acc[groupKey] = {
          id: groupKey,
          label: appointmentDate ? getRelativeLabel(appointmentDate) : 'Sem data',
          date: appointmentDate,
          data: [],
        };
      }

      acc[groupKey].data.push(item);
      return acc;
    }, {});

    return Object.values(groups).sort((a, b) => {
      if (!a.date) return 1;
      if (!b.date) return -1;
      return b.date - a.date;
    });
  }, [filteredAppointments]);

  const renderPatientCard = (item) => {
    const appointmentDate = item.data_hora ? parseAppointmentDate(item.data_hora) : null;
    const timeText = appointmentDate
      ? formatAppointmentTime(appointmentDate)
      : '--:--';
    const status = item.status || 'pendente';
    const statusColor = getStatusColor(status, isDarkMode);

    return (
      <TouchableOpacity
        activeOpacity={0.85}
        onPress={() => navigation?.navigate('PatientProfileScreen', {
          id: item.id,
          appointment: item,
          fromPatientsHistory: true,
        })}
        style={[styles.patientCard, { backgroundColor: colors.card, borderColor: colors.border }]}
      >
        <Image
          source={{ uri: getAvatarUrl(item.nome) }}
          style={[styles.avatar, { borderColor: colors.border }]}
        />

        <View style={styles.infoContainer}>
          <View style={styles.nameRow}>
            <Text style={[styles.patientName, { color: colors.text }]} numberOfLines={1}>
              {item.nome}
            </Text>
            <Text style={[styles.timeText, { color: isDarkMode ? '#94A3B8' : '#64748B' }]}>{timeText}</Text>
          </View>

          <View style={styles.metaRow}>
            <View style={[styles.badge, { backgroundColor: isDarkMode ? '#1E293B' : '#EFF6FF' }]}>
              <Text style={[styles.badgeText, { color: isDarkMode ? '#60A5FA' : '#2563EB' }]}> 
                {item.especialidade_nome || 'Geral'}
              </Text>
            </View>
            <View style={styles.procedureContainer}>
              <Feather name="file-text" size={12} color={colors.mutedText} style={styles.metaIcon} />
              <Text style={[styles.procedureText, { color: colors.mutedText }]} numberOfLines={1}>
                {item.observacoes || 'Consulta agendada'}
              </Text>
            </View>
          </View>

          <Text style={[styles.clinicText, { color: colors.mutedText }]} numberOfLines={1}>
            {item.clinica_nome || 'Clínica não informada'}
          </Text>
        </View>

        <View style={styles.statusRightContainer}>
          <View style={[styles.statusIndicatorTag, { backgroundColor: `${statusColor.light}20` }]}> 
            <Text style={[styles.statusIndicatorText, { color: statusColor.light }]}>
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}> 
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={colors.container}
        translucent={false}
      />
      <View style={styles.header}>
        <TouchableOpacity
          style={[styles.backButton, { backgroundColor: colors.backButtonBg }]}
          onPress={() => navigation?.goBack()}
          activeOpacity={0.7}
        >
          <Feather name="arrow-left" size={22} color={colors.text} />
        </TouchableOpacity>
        <View style={styles.headerTitleContainer}>
          <Text style={[styles.headerTitle, { color: colors.text }]}>Pacientes</Text>
        </View>
        <View style={styles.headerSpacer} />
      </View>

      <View style={styles.searchSection}>
        <View style={[styles.searchContainer, { backgroundColor: colors.card, borderColor: colors.border }]}> 
          <Feather name="search" size={18} color={colors.mutedText} style={styles.searchIcon} />
          <TextInput
            style={[styles.searchInput, { color: colors.text }]}
            placeholder="Buscar por paciente, procedimento ou especialidade"
            placeholderTextColor={colors.mutedText}
            value={searchQuery}
            onChangeText={setSearchQuery}
            autoCorrect={false}
            autoCapitalize="none"
          />
          {searchQuery.trim().length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')} style={styles.clearButton} activeOpacity={0.6}>
              <Feather name="x" size={16} color={colors.mutedText} />
            </TouchableOpacity>
          )}
        </View>
      </View>

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
                    backgroundColor: isSelected ? colors.brandBlue : isDarkMode ? '#1E293B' : '#F4F7FC',
                  },
                ]}
              >
                <Text style={[styles.filterChipText, { color: isSelected ? '#FFFFFF' : colors.mutedText }]}>
                  {filter}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.brandBlue} />
          <Text style={[styles.loadingText, { color: colors.mutedText }]}>Carregando pacientes...</Text>
        </View>
      ) : error ? (
        <View style={styles.emptyContainer}>
          <Feather name="alert-circle" size={40} color={colors.mutedText} style={{ marginBottom: 12 }} />
          <Text style={[styles.emptyText, { color: colors.mutedText, textAlign: 'center' }]}>{error}</Text>
        </View>
      ) : (
        <FlatList
          key="patients-flatlist"
          data={groupedAppointments}
          keyExtractor={(item) => item.id}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={() => (
            <View style={styles.emptyContainer}>
              <Feather name="search" size={40} color={colors.mutedText} style={{ marginBottom: 12 }} />
              <Text style={[styles.emptyText, { color: colors.mutedText }]}>Nenhum paciente encontrado.</Text>
            </View>
          )}
          renderItem={({ item: group }) => (
            <View style={styles.timelineGroup}>
              <View style={styles.timelineHeader}>
                <Text style={[styles.timelineDateText, { color: colors.mutedText }]}>{group.label}</Text>
                <View style={[styles.timelineLine, { backgroundColor: colors.border }]} />
              </View>
              {group.data.map((appointment) => (
                <View key={appointment.id}>{renderPatientCard(appointment)}</View>
              ))}
            </View>
          )}
        />
      )}
    </SafeAreaView>
  );
}

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
    paddingBottom: 10,
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
  },
  headerSpacer: {
    width: 42,
  },
  searchSection: {
    paddingHorizontal: 24,
    marginTop: 16,
    marginBottom: 12,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: 14,
    paddingHorizontal: 14,
    height: 48,
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
    marginBottom: 16,
  },
  filterScroll: {
    paddingHorizontal: 24,
    alignItems: 'center',
    gap: 10,
  },
  filterLabelText: {
    fontSize: 15,
    fontWeight: '700',
    marginRight: 8,
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
    marginBottom: 18,
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
    elevation: 1,
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 12,
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
    marginBottom: 6,
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
    marginBottom: 4,
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
  clinicText: {
    fontSize: 12,
    fontWeight: '500',
  },
  statusRightContainer: {
    justifyContent: 'center',
    alignItems: 'flex-end',
    marginLeft: 8,
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
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 40,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    fontWeight: '500',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 48,
    paddingHorizontal: 24,
  },
  emptyText: {
    fontSize: 14,
    fontWeight: '500',
  },
});