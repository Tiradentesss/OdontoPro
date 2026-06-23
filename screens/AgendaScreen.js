import React, { useState } from "react";
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
} from "react-native";
import { Feather } from "@expo/vector-icons";
import DateTimePicker from "@react-native-community/datetimepicker";
import { useTheme } from "../ThemeContext"; // 1. Importa o hook global de tema

// =========================================================================
// CONFIGURAÇÕES E DADOS CONSTANTES
// =========================================================================

// Configuração adaptável para os badges de status baseada no modo escuro
const getStatusConfig = (isDarkMode) => ({
  "Novo Agendamento": {
    borderColor: "#3B82F6",
    backgroundColor: isDarkMode ? "#1E3A8A" : "#EFF6FF",
    textColor: isDarkMode ? "#60A5FA" : "#2563EB",
    badgeText: "Novo",
  },
  Reagendado: {
    borderColor: "#F59E0B",
    backgroundColor: isDarkMode ? "#78350F" : "#FFFBEB",
    textColor: isDarkMode ? "#FBBF24" : "#D97706",
    badgeText: "Reagendado",
  },
  Confirmado: {
    borderColor: "#10B981",
    backgroundColor: isDarkMode ? "#064E3B" : "#ECFDF5",
    textColor: isDarkMode ? "#34D399" : "#059669",
    badgeText: "Confirmado",
  },
  "Não Confirmado": {
    borderColor: "#94A3B8",
    backgroundColor: isDarkMode ? "#334155" : "#F1F5F9",
    textColor: isDarkMode ? "#94A3B8" : "#475569",
    badgeText: "Pendente",
  },
});

const FILTER_OPTIONS = ["Todos", "Confirmado", "Pendente", "Reagendado"];

const daysOfWeek = [
  { id: "19", dayName: "D", dayNum: "19" },
  { id: "20", dayName: "S", dayNum: "20" },
  { id: "21", dayName: "T", dayNum: "21" },
  { id: "22", dayName: "Q", dayNum: "22" },
  { id: "23", dayName: "Q", dayNum: "23" },
  { id: "24", dayName: "S", dayNum: "24" },
  { id: "25", dayName: "S", dayNum: "25" },
];

const appointmentsByDay = {
  22: [
    {
      id: "1",
      patientNumber: "PAC-001",
      timeStart: "09:00",
      timeEnd: "09:30",
      status: "Novo Agendamento",
      patientName: "Gabriel Gomes",
      motivo: "Extração de siso",
      avatar: "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&q=80&w=120&h=120",
    },
    {
      id: "2",
      patientNumber: "PAC-002",
      timeStart: "10:30",
      timeEnd: "11:15",
      status: "Não Confirmado",
      patientName: "Mariana Costa",
      motivo: "Dor de dente aguda",
      avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&q=80&w=120&h=120",
    },
    {
      id: "3",
      patientNumber: "PAC-003",
      timeStart: "12:00",
      timeEnd: "12:30",
      status: "Confirmado",
      patientName: "Hugo Pontes",
      motivo: "Ajuste de Prótese",
      avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=120&h=120",
    },
    {
      id: "4",
      patientNumber: "PAC-004",
      timeStart: "14:00",
      timeEnd: "14:30",
      status: "Reagendado",
      patientName: "Natália Silva",
      motivo: "Clareamento Dental",
      avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=120&h=120",
    },
  ],
};

// =========================================================================
// COMPONENTE PRINCIPAL
// =========================================================================

export default function AgendaScreen({ navigation }) {
  const [selectedDay, setSelectedDay] = useState("22");
  const [filter, setFilter] = useState("Todos");
  const [date, setDate] = useState(new Date(2026, 4, 22));
  const [showCalendar, setShowCalendar] = useState(false);

  // 2. Consome o estado do tema e a paleta de cores dinâmica
  const { isDarkMode, colors } = useTheme();
  const STATUS_CONFIG = getStatusConfig(isDarkMode);

  // Filtragem dos cards de agendamento
  const rawAppointments = appointmentsByDay[selectedDay] || [];
  const displayedAppointments = rawAppointments.filter((item) => {
    if (filter === "Todos") return true;
    if (filter === "Confirmado") return item.status === "Confirmado";
    if (filter === "Pendente") return item.status === "Não Confirmado";
    if (filter === "Reagendado") return item.status === "Reagendado";
    return true;
  });

  // Renderizador isolado de cada item da lista (Timeline)
  const renderAppointmentItem = ({ item }) => {
    const config = STATUS_CONFIG[item.status] || STATUS_CONFIG["Novo Agendamento"];
    
    return (
      <View style={styles.timelineRow}>
        {/* Bloco de Horários */}
        <View style={styles.timeBlock}>
          <Text style={[styles.timeStartText, { color: colors.text }]}>{item.timeStart}</Text>
          <Text style={styles.timeEndText}>{item.timeEnd}</Text>
        </View>

        {/* Card do Paciente */}
        <TouchableOpacity
          style={[styles.appointmentCard, { backgroundColor: colors.card, borderColor: colors.border }]}
          onPress={() => navigation?.navigate("PatientProfileScreen", { id: item.id })}
        >
          {/* Header do Card (Badge de Status e Número do Prontuário) */}
          <View style={styles.cardHeaderRow}>
            <View style={[styles.statusBadge, { backgroundColor: config.backgroundColor, borderColor: config.borderColor, borderWidth: isDarkMode ? 1 : 0 }]}>
              <Text style={[styles.statusBadgeText, { color: config.textColor }]}>
                {config.badgeText}
              </Text>
            </View>
            <Text style={styles.appointmentTitle}>{item.patientNumber}</Text>
          </View>

          {/* Detalhes do Paciente */}
          <View style={styles.patientInfoContainer}>
            <Image source={{ uri: item.avatar }} style={styles.avatar} />
            <View style={styles.patientTextColumn}>
              <Text style={[styles.patientName, { color: colors.text }]}>{item.patientName}</Text>
              <Text style={styles.patientMotivo}>{item.motivo}</Text>
            </View>
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

      {/* Header Superior */}
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

      {/* Seletor de Mês / Calendário */}
      <TouchableOpacity style={styles.monthSelector} onPress={() => setShowCalendar(true)}>
        <Text style={[styles.monthText, { color: colors.brandBlue }]}>Maio, 2026</Text>
        <Feather name="calendar" size={20} color={colors.brandBlue} style={{ marginLeft: 8 }} />
      </TouchableOpacity>

      {showCalendar && (
        <DateTimePicker
          value={date}
          mode="date"
          display="inline"
          onChange={(e, d) => {
            setShowCalendar(false);
            if (d) setDate(d);
          }}
        />
      )}

      {/* Faixa Horizontal de Dias da Semana */}
      <View style={styles.calendarStrip}>
        {daysOfWeek.map((item) => {
          const isActive = item.dayNum === selectedDay;
          return (
            <TouchableOpacity
              key={item.id}
              style={[
                styles.dayCard, 
                { backgroundColor: colors.card },
                isActive && { backgroundColor: colors.brandBlue }
              ]}
              onPress={() => setSelectedDay(item.dayNum)}
            >
              <Text style={[
                styles.dayNameLabel, 
                { color: colors.mutedText },
                isActive && { color: "#FFFFFF" }
              ]}>
                {item.dayName}
              </Text>
              <Text style={[
                styles.dayNumLabel, 
                { color: colors.text },
                isActive && { color: "#FFFFFF" }
              ]}>
                {item.dayNum}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Seção de Filtros */}
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
                  isFilterActive && { color: "#FFFFFF" }
                ]}>
                  {f}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>

      {/* Lista de Compromissos */}
      <FlatList
        data={displayedAppointments}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        renderItem={renderAppointmentItem}
        showsVerticalScrollIndicator={false}
      />
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
    paddingTop: 16,
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
    marginVertical: 16,
  },
  monthText: { 
    fontSize: 24, 
    fontWeight: "800", 
  },
  calendarStrip: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingHorizontal: 24,
    marginBottom: 20,
  },
  dayCard: {
    width: 44,
    height: 74,
    borderRadius: 14,
    justifyContent: "center",
    alignItems: "center",
  },
  dayNameLabel: { 
    fontSize: 12, 
  },
  dayNumLabel: { 
    fontSize: 16, 
    fontWeight: "700",
  },
  listHeaderSection: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 24,
    marginBottom: 16,
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
    borderRadius: 18,
    padding: 14,
    marginLeft: 12,
    borderWidth: 1.5,
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