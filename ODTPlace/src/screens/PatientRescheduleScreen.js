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
  Pressable,
  TextInput,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../components/ThemeContext';
import { getDoctorAvailability, updateAppointment } from '../services/api';
import { formatAppointmentDateTime, formatAppointmentTime, parseAppointmentDate } from '../utils/appointmentTime';

const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
const weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
const { width } = Dimensions.get('window');

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

export default function PatientRescheduleScreen({ route, navigation }) {
  const { patientName, appointment } = route.params || {};
  const today = new Date();
  const { isDarkMode, colors } = useTheme();
  const patientBlue = isDarkMode ? '#38BDF8' : '#0EA5E9';
  const headerBg = isDarkMode ? colors.container : patientBlue;
  const headerTextColor = isDarkMode ? colors.text : '#FFFFFF';
  const headerIconColor = isDarkMode ? colors.text : patientBlue;
  const headerButtonBg = isDarkMode ? colors.card : colors.backButtonBg;
  const parseDateString = (value) => {
    return parseAppointmentDate(value);
  };

  const getIsoLabel = (isoDate) => {
    const [year, month, day] = isoDate.split('-').map(Number);
    const date = new Date(year, month - 1, day);
    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' });
  };

  const [selectedDate, setSelectedDate] = useState(`${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`);
  const [selectedDateLabel, setSelectedDateLabel] = useState(getIsoLabel(`${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`));
  const [selectedTime, setSelectedTime] = useState('10:30');
  const [currentMonth, setCurrentMonth] = useState({ year: today.getFullYear(), month: today.getMonth() + 1 });
  const [calendarVisible, setCalendarVisible] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [availableDates, setAvailableDates] = useState([]);
  const [availableSlots, setAvailableSlots] = useState({});
  const [availabilityLoading, setAvailabilityLoading] = useState(false);

  useEffect(() => {
    const appointmentDate = parseDateString(appointment?.data_hora || appointment?.date);
    if (appointmentDate) {
      const isoDate = `${appointmentDate.getFullYear()}-${String(appointmentDate.getMonth() + 1).padStart(2, '0')}-${String(appointmentDate.getDate()).padStart(2, '0')}`;
      setSelectedDate(isoDate);
      setSelectedDateLabel(getIsoLabel(isoDate));
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

  const handleConfirmReschedule = async () => {
    try {
      const [year, month, day] = selectedDate.split('-').map(Number);
      const [hours, minutes] = selectedTime.split(':').map(Number);
      if (appointment?.id) {
        await updateAppointment(appointment.id, { data_hora: formatAppointmentDateTime(selectedDate, `${hours}:${minutes}`) });
      }
      setIsModalVisible(false);
      navigation.navigate('SuccessScreen', { returnRoute: 'Home' });
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível reagendar a consulta.');
    }
  };

  const handleSelectDate = (dateId) => {
    if (!availableDates.includes(dateId)) return;
    setSelectedDate(dateId);
    setSelectedDateLabel(getIsoLabel(dateId));
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
        backgroundColor={headerBg}
        translucent={false}
      />

      <View style={[styles.header, { backgroundColor: headerBg, borderColor: colors.border }]}> 
        <TouchableOpacity style={[styles.backButton, { backgroundColor: headerButtonBg }]} onPress={() => navigation.goBack()} activeOpacity={0.7}>
          <Feather name="arrow-left" size={22} color={headerIconColor} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: headerTextColor }]}>Reagendar Consulta</Text>
        <View style={styles.headerSpacer} />
      </View>

      <View style={styles.content}>
        <View style={styles.patientMetaContainer}>
          <Text style={[styles.patientLabel, { color: colors.mutedText }]}>Paciente</Text>
          <Text style={[styles.patientName, { color: colors.text }]}>{patientName || appointment?.nome || 'Paciente'}</Text>
        </View>

        <Text style={[styles.sectionTitle, { color: colors.mutedText }]}>Data</Text>
        <TouchableOpacity
          style={[styles.pickerSelector, { backgroundColor: colors.card, borderColor: colors.border }]}
          activeOpacity={0.85}
          onPress={() => setCalendarVisible((prev) => !prev)}
        >
          <View style={[styles.iconBox, { backgroundColor: isDarkMode ? '#1E293B' : '#EFF6FF' }]}>
            <Feather name="calendar" size={18} color={patientBlue} />
          </View>
          <Text style={[styles.pickerText, { color: colors.text }]}>{selectedDateLabel}</Text>
          <Feather name="chevron-down" size={18} color={colors.mutedText} />
        </TouchableOpacity>

        <Text style={[styles.selectedDateText, { color: colors.text }]}>Data selecionada: {selectedDateLabel}</Text>

        <Modal visible={calendarVisible} transparent animationType="fade" onRequestClose={() => setCalendarVisible(false)}>
          <Pressable style={[styles.modalOverlay, { backgroundColor: isDarkMode ? 'rgba(0,0,0,0.6)' : 'rgba(15,23,42,0.3)' }]} onPress={() => setCalendarVisible(false)}>
            <Pressable style={[styles.calendarModal, { backgroundColor: colors.card, borderColor: colors.border }]} onPress={() => {}}>
              <View style={styles.calendarHeader}>
                <TouchableOpacity onPress={goPreviousMonth} style={[styles.calendarNavButton, { backgroundColor: colors.backButtonBg }]} activeOpacity={0.7}>
                  <Feather name="chevron-left" size={18} color={patientBlue} />
                </TouchableOpacity>
                <Text style={[styles.calendarLabel, { color: colors.text }]}>{monthNames[currentMonth.month - 1]} {currentMonth.year}</Text>
                <TouchableOpacity onPress={goNextMonth} style={[styles.calendarNavButton, { backgroundColor: colors.backButtonBg }]} activeOpacity={0.7}>
                  <Feather name="chevron-right" size={18} color={patientBlue} />
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
                      style={[styles.dateCell, { backgroundColor: isSelectedDate ? patientBlue : 'transparent', borderColor: colors.border }, !isAvailable && styles.dateCellDisabled]}
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

        <Text style={[styles.sectionTitle, { color: colors.mutedText }]}>Horário</Text>
        <TextInput
          value={selectedTime}
          editable={false}
          keyboardType="numeric"
          placeholder="HH:MM"
          placeholderTextColor={colors.mutedText}
          style={[styles.timeInput, { backgroundColor: colors.card, borderColor: colors.border, color: colors.text }]}
        />

        <Text style={[styles.sectionTitle, { color: colors.mutedText, marginTop: 20 }]}>Sugestões de Horário</Text>
        <View style={styles.timeGrid}>
          {(availableSlots[selectedDate] || []).map((time) => {
            const isSelected = time === selectedTime;
            return (
              <TouchableOpacity
                key={time}
                style={[
                  styles.timeSlot,
                  { backgroundColor: colors.card, borderColor: colors.border },
                  isSelected && { backgroundColor: patientBlue, borderColor: patientBlue }
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
        </View>
        {!availabilityLoading && !(availableSlots[selectedDate] || []).length && (
          <Text style={[styles.noAvailabilityText, { color: colors.mutedText }]}>Nenhum horário disponível para esta data.</Text>
        )}
        {availabilityLoading && <Text style={[styles.noAvailabilityText, { color: colors.mutedText }]}>Carregando horários...</Text>}

        <View style={styles.spacer} />

        <View style={styles.actionsRow}>
          <TouchableOpacity style={[styles.saveButton, { backgroundColor: patientBlue }]} activeOpacity={0.85} onPress={handleOpenConfirmation}>
            <Feather name="calendar" size={18} color="#FFFFFF" style={{ marginRight: 8 }} />
            <Text style={[styles.saveButtonText, { color: '#FFFFFF' }]}>Reagendar Consulta</Text>
          </TouchableOpacity>
        </View>
      </View>

      <Modal visible={isModalVisible} transparent animationType="fade" onRequestClose={() => setIsModalVisible(false)}>
        <Pressable style={[styles.modalOverlay, { backgroundColor: isDarkMode ? 'rgba(0,0,0,0.6)' : 'rgba(15,23,42,0.3)' }]} onPress={() => setIsModalVisible(false)}>
          <Pressable style={[styles.confirmModal, { backgroundColor: colors.card, borderColor: colors.border }]} onPress={() => {}}>
            <Text style={[styles.confirmTitle, { color: colors.text }]}>Confirmar reagendamento</Text>
            <Text style={[styles.confirmText, { color: colors.mutedText }]}>Deseja alterar a consulta para {selectedDateLabel} às {selectedTime}?</Text>
            <View style={styles.confirmButtons}>
              <TouchableOpacity style={[styles.modalButton, { backgroundColor: colors.backButtonBg }]} activeOpacity={0.8} onPress={() => setIsModalVisible(false)}>
                <Text style={[styles.modalButtonText, { color: colors.text }]}>Voltar</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.modalButton, { backgroundColor: patientBlue }]} activeOpacity={0.8} onPress={handleConfirmReschedule}>
                <Text style={[styles.modalButtonText, { color: '#FFFFFF' }]}>Confirmar</Text>
              </TouchableOpacity>
            </View>
          </Pressable>
        </Pressable>
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
    width: 38,
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 20,
  },
  patientMetaContainer: {
    marginBottom: 24,
  },
  patientLabel: {
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  patientName: {
    fontSize: 24,
    fontWeight: '800',
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 12,
  },
  pickerSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderRadius: 18,
    borderWidth: 1,
    marginBottom: 18,
  },
  iconBox: {
    width: 38,
    height: 38,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  pickerText: {
    flex: 1,
    fontSize: 15,
    fontWeight: '700',
  },
  timeInput: {
    width: '100%',
    borderRadius: 16,
    borderWidth: 1,
    padding: 14,
    fontSize: 16,
    marginBottom: 20,
  },
  selectedDateText: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 18,
  },
  timeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
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
    fontWeight: '700',
  },
  spacer: {
    flex: 1,
  },
  actionsRow: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
  saveButton: {
    flex: 1,
    height: 56,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.12,
    shadowRadius: 14,
    elevation: 3,
  },
  saveButtonText: {
    fontSize: 15,
    fontWeight: '700',
  },
  modalOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  calendarModal: {
    width: width - 40,
    borderRadius: 20,
    padding: 18,
  },
  calendarHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 18,
  },
  calendarNavButton: {
    width: 40,
    height: 40,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  calendarLabel: {
    fontSize: 15,
    fontWeight: '700',
  },
  weekdaysRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 14,
  },
  weekdayText: {
    width: '14.28%',
    textAlign: 'center',
    fontSize: 12,
    fontWeight: '700',
  },
  calendarGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  dateCellEmpty: {
    width: '13.7%',
    height: 44,
    marginBottom: 8,
  },
  dateCell: {
    width: '13.7%',
    height: 44,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    marginBottom: 8,
  },
  dateCellDisabled: {
    opacity: 0.3,
  },
  dateCellText: {
    fontSize: 14,
    fontWeight: '700',
  },
  noAvailabilityText: {
    fontSize: 13,
    marginBottom: 16,
  },
  confirmModal: {
    width: width - 56,
    padding: 22,
    borderRadius: 20,
    borderWidth: 1,
  },
  confirmTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 14,
  },
  confirmText: {
    fontSize: 14,
    lineHeight: 22,
    marginBottom: 24,
  },
  confirmButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  modalButton: {
    flex: 1,
    height: 48,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 4,
  },
  modalButtonText: {
    fontSize: 14,
    fontWeight: '700',
  },
});
