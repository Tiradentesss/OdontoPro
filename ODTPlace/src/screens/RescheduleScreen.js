import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  Platform,
  StatusBar,
  Modal,
  Dimensions,
  Alert,
  TextInput,
  Pressable,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../components/ThemeContext'; // Importação do tema global
import { getDoctorAvailability, updateAppointment } from '../services/api';
import { formatAppointmentDateTime, formatAppointmentTime, parseAppointmentDate } from '../utils/appointmentTime';

const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
const weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

const getMonthDays = (year, month) => {
  const daysInMonth = new Date(year, month, 0).getDate();
  return Array.from({ length: daysInMonth }, (_, index) => {
    const day = index + 1;
    const date = new Date(year, month - 1, day);
    return {
      id: `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`,
      day,
      weekday: weekdays[date.getDay()],
    };
  });
};

const { width } = Dimensions.get('window');

export default function RescheduleScreen({ route, navigation }) {
  const { patientName, appointment } = route.params || { patientName: 'Victor Araújo' };
  const today = new Date();

  const formatDateLabel = (isoDate) => {
    const [year, month, day] = isoDate.split('-').map(Number);
    const date = new Date(year, month - 1, day);
    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' });
  };

  const [selectedTime, setSelectedTime] = useState('10:30');
  const [selectedDate, setSelectedDate] = useState(`${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`);
  const [selectedDateLabel, setSelectedDateLabel] = useState(formatDateLabel(`${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`));
  const [currentMonth, setCurrentMonth] = useState({ year: today.getFullYear(), month: today.getMonth() + 1 });
  const [calendarVisible, setCalendarVisible] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [availableDates, setAvailableDates] = useState([]);
  const [availableSlots, setAvailableSlots] = useState({});
  const [availabilityLoading, setAvailabilityLoading] = useState(false);

  // Consome as propriedades globais do tema
  const { isDarkMode, colors } = useTheme();

  useEffect(() => {
    if (appointment?.data_hora) {
      const appointmentDate = parseAppointmentDate(appointment.data_hora);
      const isoDate = `${appointmentDate.getFullYear()}-${String(appointmentDate.getMonth() + 1).padStart(2, '0')}-${String(appointmentDate.getDate()).padStart(2, '0')}`;
      setSelectedDate(isoDate);
      setSelectedDateLabel(formatDateLabel(isoDate));
      setCurrentMonth({ year: appointmentDate.getFullYear(), month: appointmentDate.getMonth() + 1 });
      setSelectedTime(formatAppointmentTime(appointmentDate));
    }
  }, [appointment]);

  useEffect(() => {
    const clinicId = appointment?.clinica_id;
    const doctorId = appointment?.medico_id;
    if (!clinicId || !doctorId) return;

    const monthStart = `${currentMonth.year}-${String(currentMonth.month).padStart(2, '0')}-01`;
    const monthEndDate = new Date(currentMonth.year, currentMonth.month, 0);
    const monthEnd = `${currentMonth.year}-${String(currentMonth.month).padStart(2, '0')}-${String(monthEndDate.getDate()).padStart(2, '0')}`;
    let active = true;

    setAvailabilityLoading(true);
    setAvailableDates([]);
    setAvailableSlots({});
    setSelectedTime('');
    getDoctorAvailability(clinicId, doctorId, { start_date: monthStart, end_date: monthEnd, appointment_id: appointment?.id })
      .then((availability) => {
        if (!active) return;
        const dates = Array.isArray(availability?.dates) ? availability.dates : [];
        const slots = availability?.slots && typeof availability.slots === 'object' ? availability.slots : {};
        setAvailableDates(dates);
        setAvailableSlots(slots);
        if (slots[selectedDate]?.length) setSelectedTime(slots[selectedDate][0]);
      })
      .catch(() => {
        if (active) {
          setAvailableDates([]);
          setAvailableSlots({});
        }
      })
      .finally(() => {
        if (active) setAvailabilityLoading(false);
      });

    return () => { active = false; };
  }, [appointment, currentMonth.year, currentMonth.month]);

  // Abre o modal de revisão
  const handleOpenConfirmation = () => {
    if (!availableSlots[selectedDate]?.includes(selectedTime)) {
      Alert.alert('Horário indisponível', 'Selecione um horário disponível para esta data.');
      return;
    }
    const [year, month, day] = selectedDate.split('-').map(Number);
    const selectedDay = new Date(year, month - 1, day);
    selectedDay.setHours(0, 0, 0, 0);

    const todayDate = new Date();
    todayDate.setHours(0, 0, 0, 0);

    if (selectedDay <= todayDate) {
      Alert.alert('Data inválida', 'Escolha uma data futura para reagendar a consulta.');
      return;
    }

    setIsModalVisible(true);
  };

  // Fecha o modal e consolida o fluxo indo para a SuccessScreen
  const handleConfirmReschedule = async () => {
    try {
      const [year, month, day] = selectedDate.split('-').map(Number);
      const [hours, minutes] = selectedTime.split(':').map((value) => Number(value));
      if (appointment?.id) {
        await updateAppointment(appointment.id, { data_hora: formatAppointmentDateTime(selectedDate, `${hours}:${minutes}`) });
      }

      setIsModalVisible(false);
      navigation.navigate('SuccessScreen');
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível reagendar a consulta.');
    }
  };

  const handleSelectDate = (dateId) => {
    if (!availableDates.includes(dateId)) return;
    setSelectedDate(dateId);
    setSelectedDateLabel(formatDateLabel(dateId));
    setSelectedTime(availableSlots[dateId]?.[0] || '');
    setCalendarVisible(false);
  };

  const handleTimeChange = (text) => {
    const digits = text.replace(/[^0-9]/g, '');
    let formatted = digits;
    if (digits.length >= 3) {
      formatted = `${digits.slice(0, 2)}:${digits.slice(2, 4)}`;
    }
    if (formatted.length > 5) {
      formatted = formatted.slice(0, 5);
    }
    setSelectedTime(formatted);
  };

  const goPreviousMonth = () => {
    if (currentMonth.month === 1) {
      setCurrentMonth({ year: currentMonth.year - 1, month: 12 });
    } else {
      setCurrentMonth({ year: currentMonth.year, month: currentMonth.month - 1 });
    }
  };

  const goNextMonth = () => {
    if (currentMonth.month === 12) {
      setCurrentMonth({ year: currentMonth.year + 1, month: 1 });
    } else {
      setCurrentMonth({ year: currentMonth.year, month: currentMonth.month + 1 });
    }
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={colors.container} 
        translucent={false} 
      />

      {/* Cabeçalho Premium Consistente */}
      <View style={[styles.header, { backgroundColor: colors.container, borderColor: colors.border }]}>
        <TouchableOpacity 
          style={[styles.backButton, { backgroundColor: colors.backButtonBg }]} 
          onPress={() => navigation.goBack()}
          activeOpacity={0.6}
        >
          <Feather name="arrow-left" size={22} color={colors.brandBlue} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: colors.text }]}>Reagendar Consulta</Text>
        <View style={styles.headerSpacer} />
      </View>

      <View style={styles.content}>
        
        {/* Contexto do Paciente */}
        <View style={styles.patientMetaContainer}>
          <Text style={[styles.patientLabel, { color: colors.mutedText }]}>Paciente selecionado</Text>
          <Text style={[styles.patientName, { color: colors.text }]}>{patientName}</Text>
        </View>

        {/* Seletor de Data */}
        <Text style={[styles.sectionTitle, { color: colors.mutedText }]}>Selecione a Nova Data</Text>
        <TouchableOpacity
          style={[styles.pickerSelector, { backgroundColor: colors.card, borderColor: colors.border }]}
          activeOpacity={0.8}
          onPress={() => setCalendarVisible((prev) => !prev)}
        >
          <View style={[styles.iconBox, { backgroundColor: isDarkMode ? '#1E293B' : '#EFF6FF' }]}> 
            <Feather name="calendar" size={18} color={colors.brandBlue} />
          </View>
          <Text style={[styles.pickerText, { color: colors.text }]}>{selectedDateLabel}</Text>
          <Feather name="chevron-down" size={18} color={colors.mutedText} style={{ marginRight: 4 }} />
        </TouchableOpacity>

        <Modal
          visible={calendarVisible}
          transparent={true}
          animationType="fade"
          onRequestClose={() => setCalendarVisible(false)}
        >
          <Pressable
            style={[styles.modalOverlay, { backgroundColor: isDarkMode ? 'rgba(0, 0, 0, 0.6)' : 'rgba(15, 23, 42, 0.4)' }]}
            onPress={() => setCalendarVisible(false)}
          >
            <Pressable
              style={[styles.calendarModal, { backgroundColor: colors.card, borderColor: colors.border }]}
              onPress={() => {}}
            >
              <View style={styles.calendarHeader}>
                <TouchableOpacity onPress={goPreviousMonth} style={[styles.calendarNavButton, { backgroundColor: colors.backButtonBg }]} activeOpacity={0.7}>
                  <Feather name="chevron-left" size={18} color={colors.brandBlue} />
                </TouchableOpacity>
                <Text style={[styles.calendarLabel, { color: colors.text }]}>{monthNames[currentMonth.month - 1]} {currentMonth.year}</Text>
                <TouchableOpacity onPress={goNextMonth} style={[styles.calendarNavButton, { backgroundColor: colors.backButtonBg }]} activeOpacity={0.7}>
                  <Feather name="chevron-right" size={18} color={colors.brandBlue} />
                </TouchableOpacity>
              </View>

              <View style={styles.weekdaysRow}>
                {weekdays.map((weekday) => (
                  <Text key={weekday} style={[styles.weekdayText, { color: colors.mutedText }]}>{weekday}</Text>
                ))}
              </View>

              <View style={styles.calendarGrid}>
                {Array.from({ length: new Date(currentMonth.year, currentMonth.month - 1, 1).getDay() }).map((_, index) => (
                  <View key={`empty-${index}`} style={styles.dateCellEmpty} />
                ))}
                {getMonthDays(currentMonth.year, currentMonth.month).map((date) => {
                  const isSelectedDate = date.id === selectedDate;
                  const isAvailable = availableDates.includes(date.id);
                  return (
                    <TouchableOpacity
                      key={date.id}
                      style={[
                        styles.dateCell,
                        { backgroundColor: isSelectedDate ? colors.brandBlue : 'transparent', borderColor: colors.border },
                        !isAvailable && styles.dateCellDisabled,
                        isSelectedDate && { borderWidth: 0 }
                      ]}
                      onPress={() => handleSelectDate(date.id)}
                      disabled={!isAvailable}
                      activeOpacity={0.7}
                    >
                      <Text style={[styles.dateCellText, { color: isSelectedDate ? '#FFFFFF' : colors.text }]}>{date.day}</Text>
                    </TouchableOpacity>
                  );
                })}
              </View>

            </Pressable>
          </Pressable>
        </Modal>

        <Text style={[styles.selectedDateText, { color: colors.text }]}>Data selecionada: {selectedDateLabel}</Text>

        {/* Seletor de Horário */}
        <Text style={[styles.sectionTitle, { color: colors.mutedText }]}>Horário</Text>
        <TextInput
          style={[styles.timeInput, { backgroundColor: colors.card, borderColor: colors.border, color: colors.text }]}
          value={selectedTime}
          editable={false}
          keyboardType="numeric"
          placeholder="HH:MM"
          placeholderTextColor={isDarkMode ? '#94A3B8' : '#94A3B8'}
          maxLength={5}
        />

        <Text style={[styles.sectionTitle, { color: colors.mutedText, marginTop: 20 }]}>Sugestões de Horário</Text>
        <ScrollView style={styles.timeGridScroll} contentContainerStyle={styles.timeGrid} nestedScrollEnabled showsVerticalScrollIndicator>
          {(availableSlots[selectedDate] || []).map((time) => {
            const isSelected = time === selectedTime;
            return (
              <TouchableOpacity
                key={time}
                style={[
                  styles.timeSlot, 
                  { backgroundColor: colors.card, borderColor: colors.border },
                  isSelected && { backgroundColor: colors.brandBlue, borderColor: colors.brandBlue }
                ]}
                onPress={() => setSelectedTime(time)}
                activeOpacity={0.7}
              >
                <Text style={[
                  styles.timeSlotText, 
                  { color: colors.text },
                  isSelected && styles.timeSlotTextActive
                ]}>
                  {time}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
        {(availableSlots[selectedDate] || []).length > 6 && (
          <Text style={[styles.moreSlotsText, { color: colors.brandBlue }]}>Role para ver mais horários</Text>
        )}
        {!availabilityLoading && !(availableSlots[selectedDate] || []).length && (
          <Text style={[styles.noAvailabilityText, { color: colors.mutedText }]}>Nenhum horário disponível para esta data.</Text>
        )}
        {availabilityLoading && <Text style={[styles.noAvailabilityText, { color: colors.mutedText }]}>Carregando horários...</Text>}

        <View style={styles.spacer} />

        {/* Botão de Disparo */}
        <TouchableOpacity 
          style={[styles.saveButton, { backgroundColor: colors.brandBlue }]} 
          onPress={handleOpenConfirmation} 
          activeOpacity={0.8}
        >
          <Feather name="calendar" size={18} color="#FFFFFF" style={{ marginRight: 8 }} />
          <Text style={styles.saveButtonText}>Reagendar Consulta</Text>
        </TouchableOpacity>
      </View>

      {/* =========================================================================
          MODAL PREMIUM DE CONFIRMAÇÃO (TOTALMENTE ADAPTADO)
          ========================================================================= */}
      <Modal
        visible={isModalVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setIsModalVisible(false)}
      >
        <View style={[styles.modalOverlay, { backgroundColor: isDarkMode ? 'rgba(0, 0, 0, 0.6)' : 'rgba(15, 23, 42, 0.4)' }]}>
          <View style={[styles.modalContainer, { backgroundColor: colors.card, shadowColor: isDarkMode ? '#000000' : '#0F172A' }]}>
            
            {/* Ícone de Alerta Sutil */}
            <View style={[styles.modalIconWrapper, { backgroundColor: isDarkMode ? '#1E293B' : '#EFF6FF' }]}>
              <Feather name="alert-circle" size={28} color={colors.brandBlue} />
            </View>

            {/* Textos Informativos */}
            <Text style={[styles.modalTitle, { color: colors.text }]}>Confirmar Alteração?</Text>
            <Text style={[styles.modalDescription, { color: colors.mutedText }]}>
              Você está prestes a alterar o horário do atendimento de <Text style={[styles.modalHighlight, { color: colors.text }]}>{patientName}</Text>.
            </Text>

            {/* Resumo do Novo Agendamento */}
            <View style={[styles.modalSummaryBox, { backgroundColor: isDarkMode ? '#1E293B' : '#F8FAFC', borderColor: colors.border }]}>
              <View style={styles.modalSummaryRow}>
                <Feather name="calendar" size={14} color={colors.mutedText} style={{ marginRight: 8 }} />
                <Text style={[styles.modalSummaryText, { color: colors.text }]}>{selectedDate}</Text>
              </View>
              <View style={[styles.modalSummaryRow, { marginTop: 8 }]}>
                <Feather name="clock" size={14} color={colors.mutedText} style={{ marginRight: 8 }} />
                <Text style={[styles.modalSummaryText, { color: colors.text }]}>às {selectedTime} horas</Text>
              </View>
            </View>

            {/* Ações do Modal */}
            <View style={styles.modalActionsRow}>
              <TouchableOpacity 
                style={[styles.modalCancelButton, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}
                activeOpacity={0.7}
                onPress={() => setIsModalVisible(false)}
              >
                <Text style={[styles.modalCancelButtonText, { color: isDarkMode ? '#E2E8F0' : '#475569' }]}>Voltar</Text>
              </TouchableOpacity>

              <TouchableOpacity 
                style={[styles.modalConfirmButton, { backgroundColor: colors.brandBlue }]}
                activeOpacity={0.8}
                onPress={handleConfirmReschedule}
              >
                <Text style={styles.modalConfirmButtonText}>Confirmar</Text>
              </TouchableOpacity>
            </View>

          </View>
        </View>
      </Modal>

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
    paddingBottom: 16,
    borderBottomWidth: 1,
  },
  backButton: { 
    padding: 8,
    borderRadius: 12,
  },
  headerTitle: { 
    fontSize: 16, 
    fontWeight: '700', 
  },
  headerSpacer: { 
    width: 38 
  },
  content: { 
    flex: 1, 
    paddingHorizontal: 24, 
    paddingTop: 20 
  },
  patientMetaContainer: {
    marginBottom: 28,
  },
  patientLabel: {
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  patientName: { 
    fontSize: 22,
    fontWeight: '800', 
  },
  sectionTitle: { 
    fontSize: 13, 
    fontWeight: '700', 
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 12 
  },
  pickerSelector: {
    flexDirection: 'row',
    height: 56,
    borderRadius: 14,
    alignItems: 'center',
    paddingHorizontal: 12,
    borderWidth: 1,
    marginBottom: 28,
  },
  iconBox: {
    width: 36,
    height: 36,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  pickerText: { 
    flex: 1, 
    fontSize: 15, 
    fontWeight: '600' 
  },
  timeInput: {
    height: 56,
    borderRadius: 14,
    paddingHorizontal: 16,
    borderWidth: 1,
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 16,
  },
  calendarContainer: {
    borderWidth: 1,
    borderRadius: 18,
    padding: 16,
    marginBottom: 20,
  },
  calendarHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  calendarNavButton: {
    width: 38,
    height: 38,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  calendarLabel: {
    fontSize: 13,
    fontWeight: '700',
  },
  weekdaysRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  weekdayText: {
    width: '14.28%',
    textAlign: 'center',
    fontSize: 11,
    fontWeight: '700',
  },
  calendarGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  dateCellEmpty: {
    width: '13.7%',
    height: 38,
  },
  dateCell: {
    width: '13.7%',
    height: 38,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 8,
  },
  dateCellDisabled: {
    opacity: 0.3,
  },
  dateCellText: {
    fontSize: 12,
    fontWeight: '700',
  },
  selectedDateText: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 18,
  },
  timeGrid: { 
    flexDirection: 'row', 
    flexWrap: 'wrap', 
    justifyContent: 'space-between' 
  },
  timeGridScroll: {
    maxHeight: 188,
    marginBottom: 8,
  },
  noAvailabilityText: {
    fontSize: 13,
    marginBottom: 16,
  },
  moreSlotsText: {
    fontSize: 12,
    textAlign: 'center',
    marginBottom: 12,
  },
  timeSlot: {
    width: '48%',
    height: 52,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 1,
  },
  timeSlotText: { 
    fontSize: 15, 
    fontWeight: '600', 
  },
  timeSlotTextActive: { 
    color: '#FFFFFF',
    fontWeight: '700' 
  },
  spacer: { 
    flex: 1 
  },
  saveButton: {
    flexDirection: 'row',
    height: 54,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: Platform.OS === 'ios' ? 20 : 30,
  },
  saveButtonText: { 
    color: '#FFFFFF', 
    fontSize: 15, 
    fontWeight: '700' 
  },
  modalOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 16,
  },
  modalContainer: {
    width: width - 48,
    borderRadius: 24,
    padding: 24,
    alignItems: 'center',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
    elevation: 8,
  },
  calendarModal: {
    width: width - 32,
    maxHeight: 360,
    borderRadius: 22,
    padding: 16,
    alignItems: 'center',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.18,
    shadowRadius: 18,
    elevation: 12,
  },
  modalIconWrapper: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '800',
    marginBottom: 8,
    textAlign: 'center',
  },
  modalDescription: {
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 20,
    marginBottom: 20,
  },
  modalHighlight: {
    fontWeight: '700',
  },
  modalSummaryBox: {
    width: '100%',
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    marginBottom: 24,
  },
  modalSummaryRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  modalSummaryText: {
    fontSize: 14,
    fontWeight: '700',
  },
  modalActionsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
  },
  modalCancelButton: {
    flex: 1,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  modalCancelButtonText: {
    fontSize: 14,
    fontWeight: '700',
  },
  modalConfirmButton: {
    flex: 1,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalConfirmButtonText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});