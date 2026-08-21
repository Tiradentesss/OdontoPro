import React, { useCallback, useEffect, useRef, useState } from "react";
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
  ScrollView,
  ActivityIndicator,
} from "react-native";
import DateTimePicker from '@react-native-community/datetimepicker';
import { Feather } from "@expo/vector-icons";
import { useTheme } from '../components/ThemeContext';
import { addAppointmentMinutes, formatAppointmentDateKey, formatAppointmentTime, parseAppointmentDate } from '../utils/appointmentTime';
import { useAuth } from '../context/AuthContext';
import { getProfessionalAppointments } from '../services/api';
import { getPatientAvatarSource } from '../utils/patientAvatar';

const getStatusConfig = (isDarkMode) => ({
  "Novo Agendamento": {
    borderColor: "#3B82F6",
    backgroundColor: isDarkMode ? "#1E3A8A" : "#EFF6FF",
    textColor: isDarkMode ? "#60A5FA" : "#2563EB",
    badgeText: "Novo",
  },
  Realizado: {
    borderColor: "#10B981",
    backgroundColor: isDarkMode ? "#064E3B" : "#ECFDF5",
    textColor: isDarkMode ? "#34D399" : "#059669",
    badgeText: "Realizado",
  },
  "Não Confirmado": {
    borderColor: "#94A3B8",
    backgroundColor: isDarkMode ? "#334155" : "#F1F5F9",
    textColor: isDarkMode ? "#94A3B8" : "#475569",
    badgeText: "Pendente",
  },
  Cancelado: {
    borderColor: "#EF4444",
    backgroundColor: isDarkMode ? "#7F1D1D" : "#FEF2F2",
    textColor: isDarkMode ? "#F87171" : "#DC2626",
    badgeText: "Cancelado",
  },
});

const FILTER_OPTIONS = ["Todos", "Realizado", "Pendente", "Cancelado"];
const weekdays = ["D", "S", "T", "Q", "Q", "S", "S"];

const formatDateKey = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const parseDateKey = (dateKey) => {
  const [year, month, day] = dateKey.split('-').map(Number);
  return new Date(year, month - 1, day);
};

const getDisplayStatus = (status) => {
  const normalized = (status || '').toString().toLowerCase();
  if (['realizada', 'completa'].includes(normalized)) return 'Realizado';
  if (normalized === 'cancelada') return 'Cancelado';
  return 'Pendente';
};

const buildDayStrip = (centerDate) => {
  const start = new Date(centerDate.getFullYear(), centerDate.getMonth(), 1);
  const end = new Date(centerDate.getFullYear(), centerDate.getMonth() + 1, 0);

  return Array.from({ length: end.getDate() }, (_, index) => {
    const date = new Date(start);
    date.setDate(start.getDate() + index);
    return {
      id: formatDateKey(date),
      dayName: weekdays[date.getDay()],
      dayNum: String(date.getDate()),
      fullDate: date,
    };
  });
};

export default function AgendaScreen({ navigation, route }) {
  const { user } = useAuth();
  const [selectedDate, setSelectedDate] = useState(formatDateKey(new Date()));
  const [filter, setFilter] = useState('Todos');
  const [date, setDate] = useState(new Date());
  const [showCalendar, setShowCalendar] = useState(false);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scrollWidth, setScrollWidth] = useState(0);
  const scrollViewRef = useRef(null);

  const { isDarkMode, colors } = useTheme();
  const STATUS_CONFIG = getStatusConfig(isDarkMode);
  const dayStrip = buildDayStrip(parseDateKey(selectedDate));

  const loadAppointments = useCallback(async () => {
    if (!user?.id) {
      setAppointments([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const data = await getProfessionalAppointments({ medico_id: user.id });
      setAppointments(Array.isArray(data) ? data : []);
    } catch (error) {
      console.log('Error loading professional agenda:', error);
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    loadAppointments();
  }, [loadAppointments]);

  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      loadAppointments();
    });

    return unsubscribe;
  }, [navigation, loadAppointments]);

  useEffect(() => {
    const nextDate = route?.params?.initialDate;
    const requestId = route?.params?.navigationSeed;

    if (!nextDate || !requestId) return;

    const parsed = parseDateKey(nextDate);
    if (Number.isNaN(parsed.getTime())) return;

    setSelectedDate(nextDate);
    setDate(parsed);
    navigation.setParams({ initialDate: undefined, navigationSeed: undefined });
  }, [route?.params?.initialDate, route?.params?.navigationSeed, navigation]);

  useEffect(() => {
    if (!scrollViewRef.current || !scrollWidth || !dayStrip.length) return;
    const selectedIndex = dayStrip.findIndex((item) => item.id === selectedDate);
    if (selectedIndex < 0) return;
    const itemWidth = 48 + 8;
    const x = selectedIndex * itemWidth - scrollWidth / 2 + itemWidth / 2;
    const scrollToSelectedDate = () => {
      scrollViewRef.current?.scrollTo({ x: Math.max(x, 0), animated: true });
    };
    const timeoutId = setTimeout(scrollToSelectedDate, 80);
    return () => clearTimeout(timeoutId);
  }, [selectedDate, dayStrip, scrollWidth]);

  const appointmentDates = new Set(
    appointments
      .filter((item) => item?.data_hora)
      .map((item) => formatAppointmentDateKey(item.data_hora))
  );

  const displayedAppointments = appointments
    .filter((item) => {
      const appointmentDate = item?.data_hora ? formatAppointmentDateKey(item.data_hora) : null;
      return appointmentDate === selectedDate;
    })
    .map((item) => {
      const appointmentDate = item?.data_hora ? parseAppointmentDate(item.data_hora) : null;
      const status = getDisplayStatus(item?.status);
      const config = STATUS_CONFIG[status] || STATUS_CONFIG['Não Confirmado'];
      const startTime = appointmentDate
        ? formatAppointmentTime(appointmentDate)
        : '--:--';
      const endTime = appointmentDate
        ? formatAppointmentTime(addAppointmentMinutes(appointmentDate, 30))
        : '--:--';

      return {
        id: String(item.id),
        patientNumber: `PAC-${String(item.paciente_id || item.id).padStart(3, '0')}`,
        timeStart: startTime,
        timeEnd: endTime,
        status,
        patientName: item.nome || 'Paciente',
        motivo: item.observacoes || 'Consulta',
        specialty: item.especialidade_nome || 'Especialidade',
        clinic: item.clinica_nome || 'Clínica',
        patientPhone: item.telefone || item.contato || '',
        avatarSource: getPatientAvatarSource(item),
        appointment: item,
        config,
      };
    })
    .filter((item) => {
      if (filter === 'Todos') return true;
      if (filter === 'Realizado') return item.status === 'Realizado';
      if (filter === 'Pendente') return item.status === 'Pendente';
      if (filter === 'Cancelado') return item.status === 'Cancelado';
      return true;
    });

  const renderAppointmentItem = ({ item }) => {
    const config = item.config || STATUS_CONFIG['Não Confirmado'];

    return (
      <View style={styles.timelineRow}>
        <View style={styles.timeBlock}>
          <Text style={[styles.timeStartText, { color: colors.text }]}>{item.timeStart}</Text>
          <Text style={styles.timeEndText}>{item.timeEnd}</Text>
        </View>

        <TouchableOpacity
          style={[styles.appointmentCard, { backgroundColor: colors.card, borderColor: colors.border }]}
          onPress={() => navigation?.navigate('AppointmentDetailsScreen', {
            patientName: item.patientName,
            allowReschedule: true,
            appointment: item.appointment,
            motivo: item.motivo,
          })}
        >
          <View style={styles.cardHeaderRow}>
            <View style={[styles.statusBadge, { backgroundColor: config.backgroundColor, borderColor: config.borderColor, borderWidth: isDarkMode ? 1 : 0 }]}>
              <Text style={[styles.statusBadgeText, { color: config.textColor }]}>
                {config.badgeText}
              </Text>
            </View>
            <Text style={styles.appointmentTitle}>{item.patientNumber}</Text>
          </View>

          <View style={styles.patientInfoContainer}>
            <Image source={item.avatarSource} style={styles.avatar} />
            <View style={styles.patientTextColumn}>
              <Text style={[styles.patientName, { color: colors.text }]}>{item.patientName}</Text>
              <Text style={styles.patientMotivo}>{item.motivo}</Text>
              {item.specialty ? (
                <Text style={[styles.patientMeta, { color: colors.mutedText }]}>{item.specialty}</Text>
              ) : null}
            </View>
          </View>

          <View style={styles.cardFooterRow}>
            {item.clinic ? (
              <View style={styles.footerChip}>
                <Feather name="home" size={12} color={colors.brandBlue} />
                <Text style={[styles.footerChipText, { color: colors.text }]}>{item.clinic}</Text>
              </View>
            ) : null}
            {item.patientPhone ? (
              <View style={styles.footerChip}>
                <Feather name="phone" size={12} color={colors.brandBlue} />
                <Text style={[styles.footerChipText, { color: colors.text }]}>{item.patientPhone}</Text>
              </View>
            ) : null}
          </View>
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}> 
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={colors.container}
      />

      <View style={styles.header}>
        <TouchableOpacity 
          style={[styles.backButton, { backgroundColor: colors.backButtonBg, borderColor: colors.border }]} 
          onPress={() => navigation?.goBack()}
        >
          <Feather name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={[styles.title, { color: colors.text }]}>Agenda</Text>
        <View style={styles.headerSpacer} />
      </View>

      <TouchableOpacity style={styles.monthSelector} onPress={() => setShowCalendar(true)}>
        <Text style={[styles.monthText, { color: colors.brandBlue }]}>{new Date(date).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}</Text>
        <Feather name="calendar" size={20} color={colors.brandBlue} style={{ marginLeft: 8 }} />
      </TouchableOpacity>

      {showCalendar && (
        <DateTimePicker
          value={date}
          mode="date"
          display="inline"
          onChange={(e, d) => {
            setShowCalendar(false);
            if (d) {
              setDate(d);
              setSelectedDate(formatDateKey(d));
            }
          }}
        />
      )}

      <ScrollView
        ref={scrollViewRef}
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.calendarStrip}
        onLayout={(event) => setScrollWidth(event.nativeEvent.layout.width)}
      >
        {dayStrip.map((item) => {
          const isActive = item.id === selectedDate;
          const hasAppointment = appointmentDates.has(item.id);
          return (
            <TouchableOpacity
              key={item.id}
              style={[
                styles.dayCard,
                { backgroundColor: colors.card, borderWidth: hasAppointment ? 1 : 0, borderColor: colors.brandBlue },
                isActive && { backgroundColor: colors.brandBlue, borderColor: colors.brandBlue }
              ]}
              onPress={() => setSelectedDate(item.id)}
            >
              <Text style={[
                styles.dayNameLabel,
                { color: colors.mutedText },
                isActive && { color: '#FFFFFF' }
              ]}>
                {item.dayName}
              </Text>
              <Text style={[
                styles.dayNumLabel,
                { color: colors.text },
                isActive && { color: '#FFFFFF' }
              ]}>
                {item.dayNum}
              </Text>
              {hasAppointment ? (
                <View style={[styles.dayDot, { backgroundColor: isActive ? '#FFFFFF' : colors.brandBlue }]} />
              ) : null}
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      <View style={styles.listHeaderSection}>
        <Text style={[styles.sectionTextHora, { color: colors.mutedText }]}>Filtrar:</Text>
        <View style={styles.sectionRightGroup}>
          {FILTER_OPTIONS.map((f) => {
            const isFilterActive = filter === f;
            return (
              <TouchableOpacity
                key={f}
                onPress={() => setFilter(f)}
                style={[
                  styles.filterChip,
                  { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' },
                  isFilterActive && { backgroundColor: colors.brandBlue }
                ]}
              >
                <Text style={[
                  styles.filterText,
                  { color: colors.mutedText },
                  isFilterActive && { color: '#FFFFFF' }
                ]}>
                  {f}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>

      {loading ? (
        <View style={styles.emptyState}>
          <ActivityIndicator size="large" color={colors.brandBlue} />
          <Text style={[styles.emptyText, { color: colors.mutedText }]}>Carregando agenda...</Text>
        </View>
      ) : (
        <FlatList
          key="agenda-flatlist"
          data={displayedAppointments}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          renderItem={renderAppointmentItem}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={() => (
            <View style={styles.emptyState}>
              <Feather name="calendar" size={38} color={colors.mutedText} />
              <Text style={[styles.emptyText, { color: colors.mutedText }]}>Nenhum agendamento para este dia.</Text>
            </View>
          )}
        />
      )}
    </SafeAreaView>
  );
}

// =========================================================================
// ESTILOS (STYLESHEET)
// =========================================================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: Platform.OS === "android" ? StatusBar.currentHeight : 0,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 24,
    paddingTop: 10,
  },
  backButton: {
    padding: 8,
    borderRadius: 12,
    borderWidth: 1,
  },
  title: { 
    fontSize: 20, 
    fontWeight: "800",
  },
  headerSpacer: { 
    width: 42,
  },
  monthSelector: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 24,
    marginTop: 10,
    marginBottom: 14,
  },
  monthText: { 
    fontSize: 24, 
    fontWeight: "800", 
  },
  calendarStrip: {
    flexDirection: "row",
    paddingHorizontal: 16,
    paddingVertical: 2,
    marginBottom: 6,
  },
  dayCard: {
    width: 44,
    height: 74,
    borderRadius: 14,
    justifyContent: "center",
    alignItems: "center",
    marginHorizontal: 4,
    paddingVertical: 6,
  },
  dayNameLabel: { 
    fontSize: 12, 
  },
  dayNumLabel: { 
    fontSize: 16, 
    fontWeight: "700",
  },
  dayDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginTop: 6,
  },
  listHeaderSection: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 24,
    marginTop: 8,
    marginBottom: 14,
  },
  sectionTextHora: { 
    fontSize: 14, 
    fontWeight: "700", 
  },
  sectionRightGroup: { 
    flexDirection: "row", 
    marginLeft: 10,
  },
  filterChip: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
    marginRight: 5,
  },
  filterText: { 
    fontSize: 10, 
    fontWeight: "700", 
  },
  listContent: { 
    paddingHorizontal: 24, 
    paddingBottom: 110,
  },
  timelineRow: { 
    flexDirection: "row", 
    marginBottom: 16,
  },
  timeBlock: { 
    width: 55, 
    paddingTop: 6,
  },
  timeStartText: { 
    fontSize: 15, 
    fontWeight: "700",
  },
  timeEndText: { 
    fontSize: 12, 
    color: "#94A3B8",
  },
  appointmentCard: {
    flex: 1,
    borderRadius: 22,
    paddingVertical: 16,
    paddingHorizontal: 16,
    marginLeft: 12,
    borderWidth: 1.5,
    minHeight: 150,
  },
  cardHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  appointmentTitle: {
    fontSize: 11,
    fontWeight: "800",
    color: "#94A3B8",
    textTransform: "uppercase",
  },
  patientInfoContainer: { 
    flexDirection: "row", 
    alignItems: "center", 
    flex: 1,
    marginTop: 8,
  },
  avatar: { 
    width: 38, 
    height: 38, 
    borderRadius: 12,
  },
  patientTextColumn: { 
    marginLeft: 10, 
    flex: 1,
  },
  patientName: { 
    fontSize: 15, 
    fontWeight: "700",
  },
  patientMotivo: { 
    fontSize: 12, 
    color: "#6B7280",
    marginTop: 2,
  },
  patientMeta: {
    fontSize: 11,
    marginTop: 4,
  },
  cardFooterRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginTop: 10,
    gap: 8,
  },
  footerChip: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 999,
    backgroundColor: "rgba(14, 165, 233, 0.10)",
    gap: 4,
  },
  footerChipText: {
    fontSize: 10,
    fontWeight: "700",
  },
  statusBadge: { 
    paddingHorizontal: 8, 
    paddingVertical: 4, 
    borderRadius: 6,
  },
  statusBadgeText: { 
    fontSize: 10, 
    fontWeight: "700",
  },
});