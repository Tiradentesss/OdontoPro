import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Modal,
  ImageBackground,
  Alert,
  Platform,
  StatusBar,
} from 'react-native';
import ScheduleHeader from '../components/ScheduleHeader';
import BottomNavBar from '../components/BottomNavBar';
import { createAppointment } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../components/ThemeContext';

const statusBarHeight = Platform.OS === 'android' ? StatusBar.currentHeight || 24 : 44;

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

export default function AppointmentBookingScreen({ route, navigation }) {
  const professional = route?.params?.professional ?? {};
  const clinic = route?.params?.clinic ?? {};
  const { user } = useAuth();
  const { isDarkMode } = useTheme();
  
  // Data atual
  const today = new Date();
  
  // Converter especialidades em formato com ID e nome
  const getDoctorSpecialties = () => {
    if (Array.isArray(professional.especialidades) && professional.especialidades.length > 0) {
      // Se as especialidades já tiverem ID e nome
      return professional.especialidades.map((spec, index) => {
        if (typeof spec === 'object' && spec.id && spec.nome) {
          return { id: spec.id, nome: spec.nome };
        }
        // Se for apenas string, criar objeto com ID sequencial
        return { id: String(index + 1), nome: spec };
      });
    }
    // Fallback para specialty ou valor padrão
    const specialty = professional.specialty || 'Consulta';
    return [{ id: professional.especialidade_id || '1', nome: specialty }];
  };
  
  const doctorSpecialties = getDoctorSpecialties();
  
  const [nomeCompleto, setNomeCompleto] = useState(user?.nome ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [phone, setPhone] = useState(user?.telefone ?? '');
  const [reason, setReason] = useState('');
  const [selectedSlot, setSelectedSlot] = useState('');
  const [confirmationVisible, setConfirmationVisible] = useState(false);
  const [pickerVisible, setPickerVisible] = useState(false);
  const [specialtyPickerVisible, setSpecialtyPickerVisible] = useState(false);
  const [currentMonth, setCurrentMonth] = useState({ year: today.getFullYear(), month: today.getMonth() + 1 });
  const [selectedDate, setSelectedDate] = useState(`${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`);
  const [selectedTime, setSelectedTime] = useState('09:00');
  const [selectedSpecialtyId, setSelectedSpecialtyId] = useState(doctorSpecialties[0]?.id || '1');
  const [selectedSpecialtyName, setSelectedSpecialtyName] = useState(doctorSpecialties[0]?.nome || 'Consulta');
  const [isReasonFocused, setIsReasonFocused] = useState(false);
  
  const selectedRouteSpecialty = route?.params?.selectedSpecialty ?? null;
  const selectedRouteSpecialtyId = route?.params?.selectedSpecialtyId ?? null;
  
  useEffect(() => {
    if (selectedRouteSpecialtyId) {
      const match = doctorSpecialties.find(spec => String(spec.id) === String(selectedRouteSpecialtyId));
      if (match) {
        setSelectedSpecialtyId(match.id);
        setSelectedSpecialtyName(match.nome);
        return;
      }
    }

    if (selectedRouteSpecialty) {
      const match = doctorSpecialties.find(spec => String(spec.nome).toLowerCase() === String(selectedRouteSpecialty).toLowerCase());
      if (match) {
        setSelectedSpecialtyId(match.id);
        setSelectedSpecialtyName(match.nome);
      }
    }
  }, [doctorSpecialties, selectedRouteSpecialty, selectedRouteSpecialtyId]);
  
  // Preço da consulta (pode ser mock ou vir da API)
  const consultationPrice = professional.preco || 150.00;

  const monthDays = getMonthDays(currentMonth.year, currentMonth.month);
  const monthLabel = `${monthNames[currentMonth.month - 1]} ${currentMonth.year}`;

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

  const handleSlotPress = () => {
    setPickerVisible(true);
  };

  const confirmDateTime = () => {
    const [year, month, day] = selectedDate.split('-');
    setSelectedSlot(`${monthNames[Number(month) - 1]} - ${String(day).padStart(2, '0')} - ${currentMonth.year} ${selectedTime}`);
    setPickerVisible(false);
  };

  const formatDateTime = (date, time) => {
    // Formato: HH:MM (sem AM/PM)
    const [hourString, minuteString] = time.split(':');
    const hour = Number(hourString);
    const minute = Number(minuteString);

    return `${date} ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}:00`;
  };

  const handleConfirmBooking = async () => {
    if (!nomeCompleto || !email || !phone) {
      Alert.alert('Erro', 'Preencha todos os campos obrigatórios.');
      return;
    }
    
    if (!selectedSlot) {
      Alert.alert('Erro', 'Selecione uma data e horário para a consulta.');
      return;
    }

    try {
      const data_hora = formatDateTime(selectedDate, selectedTime);
      await createAppointment({
        nome: nomeCompleto.trim(),
        email,
        telefone: phone,
        clinica_id: clinic.id,
        medico_id: professional.id,
        especialidade_id: selectedSpecialtyId,
        data_hora,
        observacoes: reason,
        paciente_id: user.id,
      });
      setConfirmationVisible(true);
    } catch (error) {
      Alert.alert('Erro', error.response?.data?.error ?? 'Falha ao agendar consulta.');
    }
  };

  const closeConfirmation = () => {
    setConfirmationVisible(false);
  };

  const handleReturnHome = () => {
    setConfirmationVisible(false);
    navigation.navigate('Home');
  };

  return (
    <ImageBackground
      source={require('../../assets/imagem background.png')}
      style={styles.pageBackground}
      imageStyle={!isDarkMode ? { transform: [{ scale: 1.2 }] } : undefined}
      resizeMode="cover"
    >
      <SafeAreaView style={[styles.container, isDarkMode && { backgroundColor: '#020617' }]}> 
        <ScheduleHeader title="Agendamento" onBack={() => navigation.goBack()} iconName="calendar" />

        <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
          <View style={[styles.headerCard, isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155' }]}> 
            <Text style={[styles.headerLabel, { color: isDarkMode ? '#38BDF8' : '#0ea5e9' }]}>Profissional</Text>
            <Text style={[styles.headerTitle, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>{professional.nome ?? professional.name ?? 'Dr. Nome Sobrenome'}</Text>
            <Text style={[styles.headerSubtitle, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>{professional.specialty ?? professional.especialidades?.[0] ?? 'Especialidade'}</Text>
          </View>

          <View style={styles.formGroup}>
            <Text style={[styles.fieldLabel, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Nome Completo</Text>
            <TextInput
              style={[styles.input, isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155', color: '#F8FAFC' }]}
              placeholder="Seu nome completo"
              placeholderTextColor={isDarkMode ? '#94A3B8' : '#9ca3af'}
              value={nomeCompleto}
              onChangeText={setNomeCompleto}
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={[styles.fieldLabel, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Email</Text>
            <TextInput
              keyboardType="email-address"
              autoCapitalize="none"
              style={[styles.input, isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155', color: '#F8FAFC' }]}
              placeholder="Digite seu E-mail"
              placeholderTextColor={isDarkMode ? '#94A3B8' : '#9ca3af'}
              value={email}
              onChangeText={setEmail}
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={[styles.fieldLabel, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Número de telefone</Text>
            <TextInput
              keyboardType="phone-pad"
              style={[styles.input, isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155', color: '#F8FAFC' }]}
              placeholder="+55 (00) 0000-0000"
              placeholderTextColor={isDarkMode ? '#94A3B8' : '#9ca3af'}
              value={phone}
              onChangeText={setPhone}
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={[styles.fieldLabel, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Escolha a data e Horário</Text>
            <TouchableOpacity style={[styles.slotInput, isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155' }]} activeOpacity={0.85} onPress={handleSlotPress}>
              <Text style={[styles.slotText, { color: isDarkMode ? '#E2E8F0' : '#94a3b8' }]}>{selectedSlot}</Text>
              <Text style={[styles.slotArrow, { color: isDarkMode ? '#38BDF8' : '#0ea5e9' }]}>⌄</Text>
            </TouchableOpacity>
            <Text style={[styles.slotHelp, { color: isDarkMode ? '#94A3B8' : '#94a3b8' }]}>Toque para escolher o dia e o horário.</Text>
          </View>

          {/* Seleção de Especialidade */}
          {doctorSpecialties.length > 0 && (
            <View style={styles.formGroup}>
              <Text style={[styles.fieldLabel, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Especialidade</Text>
              <View style={styles.dropdownWrapper}>
                <TouchableOpacity 
                  style={[styles.slotInput, specialtyPickerVisible && styles.slotInputOpen, isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155' }]} 
                  activeOpacity={0.85} 
                  onPress={() => setSpecialtyPickerVisible((prev) => !prev)}
                >
                  <Text style={[styles.slotText, { color: isDarkMode ? '#E2E8F0' : '#94a3b8' }]}>{selectedSpecialtyName}</Text>
                  <Text style={[styles.slotArrow, { color: isDarkMode ? '#38BDF8' : '#0ea5e9' }]}>{specialtyPickerVisible ? '⌃' : '⌄'}</Text>
                </TouchableOpacity>

                {specialtyPickerVisible && (
                  <View style={styles.inlinePickerContainer}>
                    <View style={styles.inlinePickerCard}>
                      <Text style={[styles.pickerTitle, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Selecione a Especialidade</Text>
                      <ScrollView style={styles.specialtyList}>
                        {doctorSpecialties.map((specialty) => (
                          <TouchableOpacity
                            key={specialty.id}
                            style={[
                              styles.specialtyOption,
                              selectedSpecialtyId === specialty.id && styles.specialtyOptionActive,
                              isDarkMode && { backgroundColor: '#0F172A', borderBottomColor: '#334155' },
                              isDarkMode && selectedSpecialtyId === specialty.id && { backgroundColor: '#1E293B' }
                            ]}
                            onPress={() => {
                              setSelectedSpecialtyId(specialty.id);
                              setSelectedSpecialtyName(specialty.nome);
                              setSpecialtyPickerVisible(false);
                            }}
                            activeOpacity={0.85}
                          >
                            <View style={styles.specialtyOptionContent}>
                              <Text style={[
                                styles.specialtyOptionText,
                                selectedSpecialtyId === specialty.id && styles.specialtyOptionTextActive,
                                isDarkMode && { color: '#E2E8F0' },
                                isDarkMode && selectedSpecialtyId === specialty.id && { color: '#38BDF8' }
                              ]}>{specialty.nome}</Text>
                              {selectedSpecialtyId === specialty.id && (
                                <Text style={[styles.specialtyCheckmark, { color: isDarkMode ? '#38BDF8' : '#0284c7' }]}>✓</Text>
                              )}
                            </View>
                          </TouchableOpacity>
                        ))}
                      </ScrollView>
                    </View>
                  </View>
                )}
              </View>

              {doctorSpecialties.length > 1 && (
                <Text style={[styles.slotHelp, { color: isDarkMode ? '#94A3B8' : '#94a3b8' }]}>Toque para escolher uma especialidade.</Text>
              )}
            </View>
          )}

          {/* Preço da Consulta */}
          <View style={[styles.priceCard, isDarkMode && { backgroundColor: '#0F172A', borderColor: '#334155' }]}> 
            <Text style={[styles.priceLabel, { color: isDarkMode ? '#86EFAC' : '#166534' }]}>Valor da Consulta</Text>
            <Text style={[styles.priceValue, { color: isDarkMode ? '#4ADE80' : '#16a34a' }]}>R$ {consultationPrice.toFixed(2).replace('.', ',')}</Text>
          </View>

          <Modal visible={pickerVisible} transparent animationType="fade">
            <View style={styles.pickerOverlay}>
              <View style={[styles.pickerCard, isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155' }]}> 
                <View style={styles.pickerHeader}>
                  <Text style={[styles.pickerTitle, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>{monthLabel}</Text>
                  <View style={styles.pickerNavButtons}>
                    <TouchableOpacity style={styles.pickerNavButton} onPress={goPreviousMonth} activeOpacity={0.8}>
                      <Text style={styles.pickerNavText}>‹</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.pickerNavButton} onPress={goNextMonth} activeOpacity={0.8}>
                      <Text style={styles.pickerNavText}>›</Text>
                    </TouchableOpacity>
                  </View>
                </View>

                <View style={styles.weekdaysRow}>
                  {weekdays.map((weekday) => (
                    <Text key={weekday} style={styles.weekdayLabel}>{weekday}</Text>
                  ))}
                </View>

                <View style={styles.daysGrid}>
                  {Array.from({ length: new Date(currentMonth.year, currentMonth.month - 1, 1).getDay() }, (_, index) => (
                    <View key={`empty-${index}`} style={styles.dayCellEmpty} />
                  ))}
                  {monthDays.map((day) => {
                    const isSelected = selectedDate === day.id;
                    return (
                      <TouchableOpacity
                        key={day.id}
                        style={[styles.dayCell, isSelected && styles.dayCellSelected, isDarkMode && !isSelected && { backgroundColor: '#1E293B' }, isDarkMode && isSelected && { backgroundColor: '#38BDF8' }]}
                        activeOpacity={0.85}
                        onPress={() => setSelectedDate(day.id)}
                      >
                        <Text style={[styles.dayNumber, isSelected && styles.dayNumberSelected, isDarkMode && !isSelected && { color: '#F8FAFC' }, isDarkMode && isSelected && { color: '#0F172A' }]}>{day.day}</Text>
                      </TouchableOpacity>
                    );
                  })}
                </View>

                <Text style={[styles.timeSectionTitle, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Horário</Text>
                <View style={styles.timeRow}>
                  {['09:00', '09:30', '12:00', '12:30', '15:00', '16:30'].map((time) => {
                    const isActive = selectedTime === time;
                    return (
                      <TouchableOpacity
                        key={time}
                        style={[styles.timeChip, isActive && styles.timeChipActive, isDarkMode && !isActive && { backgroundColor: '#1E293B', borderWidth: 1, borderColor: '#334155' }, isDarkMode && isActive && { backgroundColor: '#38BDF8' }]}
                        activeOpacity={0.85}
                        onPress={() => setSelectedTime(time)}
                      >
                        <Text style={[styles.timeChipText, isActive && styles.timeChipTextActive, isDarkMode && !isActive && { color: '#E2E8F0' }, isDarkMode && isActive && { color: '#0F172A' }]}>{time}</Text>
                      </TouchableOpacity>
                    );
                  })}
                </View>

                <View style={styles.pickerActionsRow}>
                  <TouchableOpacity style={styles.pickerCancelButton} onPress={() => setPickerVisible(false)} activeOpacity={0.85}>
                    <Text style={styles.pickerCancelText}>Cancelar</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.pickerConfirmButton} onPress={confirmDateTime} activeOpacity={0.85}>
                    <Text style={styles.pickerConfirmText}>Confirmar</Text>
                  </TouchableOpacity>
                </View>
              </View>
            </View>
          </Modal>

          <View style={styles.formGroup}>
            <Text style={[styles.fieldLabel, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Motivo da consulta (Opcional)</Text>
            <TextInput
              style={[
                styles.input,
                styles.reasonInput,
                isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155', color: '#F8FAFC' },
                isReasonFocused && isDarkMode && styles.reasonInputFocusedDark
              ]}
              placeholder="O que você está sentindo ou precisa? Por exemplo: 'Estou muito ansioso e com dificuldade para dormir'."
              placeholderTextColor={isDarkMode ? '#E2E8F0' : '#64748B'}
              value={reason}
              onChangeText={setReason}
              multiline
              numberOfLines={4}
              textAlignVertical="top"
              selectionColor={isDarkMode ? '#38BDF8' : '#0EA5E9'}
              cursorColor={isDarkMode ? '#38BDF8' : '#0EA5E9'}
              onFocus={() => setIsReasonFocused(true)}
              onBlur={() => setIsReasonFocused(false)}
            />
          </View>

          <TouchableOpacity style={styles.submitButton} activeOpacity={0.85} onPress={handleConfirmBooking}>
            <Text style={styles.submitButtonText}>Confirmar agendamento</Text>
          </TouchableOpacity>
        </ScrollView>

        <Modal visible={confirmationVisible} transparent animationType="fade">
          <View style={styles.modalOverlay}>
            <View style={styles.confirmationCard}>
              <View style={styles.confirmationIconWrapper}>
                <View style={styles.confirmationIcon}>
                  <Text style={styles.confirmationCheck}>✓</Text>
                </View>
              </View>

              <Text style={[styles.confirmationTitle, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Agendamento Confirmado</Text>
              <Text style={[styles.confirmationSubtitle, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>Seu agendamento foi feito com sucesso</Text>

              <View style={[styles.confirmationProfileCard, isDarkMode && { backgroundColor: '#1E293B' }]}> 
                <View style={styles.confirmationProfileImage}>
                  <Text style={styles.confirmationProfileInitial}>{(professional.nome ?? professional.name)?.charAt(0) ?? 'P'}</Text>
                </View>
                <Text style={[styles.confirmationProfileName, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>{professional.nome ?? professional.name ?? 'Dr. Nome Sobrenome'}</Text>
                <Text style={[styles.confirmationProfileSpecialty, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>{professional.specialty ?? professional.especialidades?.[0] ?? 'Especialidade'}</Text>
              </View>

              <View style={styles.confirmationDetailsRow}>
                <Text style={[styles.confirmationDetailText, { color: isDarkMode ? '#E2E8F0' : '#334155' }]}>{selectedSlot}</Text>
              </View>

              <TouchableOpacity style={styles.changeLink} activeOpacity={0.85} onPress={closeConfirmation}>
                <Text style={styles.changeLinkText}>Alterar data ou horário</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.returnButton} activeOpacity={0.85} onPress={handleReturnHome}>
                <Text style={styles.returnButtonText}>Voltar ao Início</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>

        <BottomNavBar
          activeTab="schedule"
          onTabPress={(tab) => {
            if (tab === 'home') {
              navigation.navigate('Home');
            } else if (tab === 'schedule') {
              navigation.navigate('Schedule');
            } else if (tab === 'notifications') {
              navigation.navigate('Notifications');
            } else if (tab === 'settings') {
              navigation.navigate('Settings');
            }
          }}
        />
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
    paddingTop: statusBarHeight + 120,
  },
  content: {
    paddingHorizontal: 20,
    paddingBottom: 200,
  },
  headerCard: {
    backgroundColor: '#ffffff',
    borderRadius: 28,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 6 },
    shadowRadius: 14,
    elevation: 6,
  },
  headerLabel: {
    fontSize: 12,
    color: '#0ea5e9',
    fontWeight: '700',
    marginBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#64748b',
  },
  formGroup: {
    marginBottom: 16,
  },
  fieldLabel: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 10,
  },
  input: {
    backgroundColor: '#ffffff',
    borderRadius: 18,
    paddingVertical: 16,
    paddingHorizontal: 18,
    fontSize: 14,
    color: '#0f172a',
    shadowColor: '#000',
    shadowOpacity: 0.04,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 10,
    elevation: 4,
  },
  slotInput: {
    backgroundColor: '#ffffff',
    borderRadius: 18,
    paddingVertical: 16,
    paddingHorizontal: 18,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.04,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 10,
    elevation: 4,
  },
  slotInputOpen: {
    borderBottomLeftRadius: 0,
    borderBottomRightRadius: 0,
    shadowOpacity: 0,
    elevation: 0,
  },
  slotText: {
    color: '#94a3b8',
    fontSize: 14,
  },
  slotArrow: {
    color: '#0ea5e9',
    fontSize: 18,
  },
  slotHelp: {
    marginTop: 8,
    color: '#94a3b8',
    fontSize: 12,
  },
  priceCard: {
    backgroundColor: '#f0fdf4',
    borderRadius: 18,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#bbf7d0',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  priceLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#166534',
  },
  priceValue: {
    fontSize: 24,
    fontWeight: '800',
    color: '#16a34a',
  },
  specialtyList: {
    maxHeight: 300,
  },

  dropdownWrapper: {
    position: 'relative',
  },
  inlinePickerContainer: {
    position: 'absolute',
    top: 56,
    left: 0,
    right: 0,
    zIndex: 10,
    elevation: 10,
  },
  inlinePickerCard: {
    width: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 18,
    borderTopLeftRadius: 0,
    borderTopRightRadius: 0,
    paddingVertical: 8,
    paddingHorizontal: 4,
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 16,
    elevation: 8,
  },
  specialtyOption: {
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  specialtyOptionActive: {
    backgroundColor: '#f0f9ff',
  },
  specialtyOptionContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  specialtyOptionText: {
    fontSize: 16,
    color: '#334155',
    flex: 1,
  },
  specialtyOptionTextActive: {
    color: '#0284c7',
    fontWeight: '700',
  },
  specialtyCheckmark: {
    fontSize: 18,
    color: '#0284c7',
    fontWeight: '700',
    marginLeft: 12,
  },
  pickerCloseButton: {
    padding: 8,
  },
  pickerCloseText: {
    fontSize: 20,
    color: '#64748b',
  },
  reasonInput: {
    minHeight: 120,
    paddingTop: 18,
  },
  reasonInputFocusedDark: {
    borderColor: '#38BDF8',
    shadowColor: '#38BDF8',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.45,
    shadowRadius: 8,
    elevation: 4,
  },
  submitButton: {
    marginTop: 14,
    backgroundColor: '#10b981',
    borderRadius: 24,
    paddingVertical: 16,
    alignItems: 'center',
  },
  submitButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.55)',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  pickerCard: {
    width: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 28,
    padding: 20,
  },
  pickerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  pickerTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0f172a',
  },
  pickerNavButtons: {
    flexDirection: 'row',
  },
  pickerNavButton: {
    width: 34,
    height: 34,
    borderRadius: 12,
    backgroundColor: '#e2e8f0',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  pickerNavText: {
    fontSize: 18,
    color: '#0f172a',
  },
  weekdaysRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  weekdayLabel: {
    fontSize: 12,
    color: '#64748b',
    width: '14.28%',
    textAlign: 'center',
  },
  daysGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 18,
  },
  dayCellEmpty: {
    width: '14.28%',
    height: 44,
  },
  dayCell: {
    width: '14.28%',
    height: 44,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 16,
    marginBottom: 6,
  },
  dayCellSelected: {
    backgroundColor: '#0ea5e9',
  },
  dayNumber: {
    fontSize: 14,
    color: '#0f172a',
  },
  dayNumberSelected: {
    color: '#ffffff',
    fontWeight: '800',
  },
  timeSectionTitle: {
    fontSize: 14,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 12,
  },
  timeRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  timeChip: {
    width: '48%',
    backgroundColor: '#f8fafc',
    borderRadius: 16,
    paddingVertical: 14,
    alignItems: 'center',
    marginBottom: 10,
  },
  timeChipActive: {
    backgroundColor: '#0ea5e9',
  },
  timeChipText: {
    fontSize: 14,
    color: '#0f172a',
    fontWeight: '700',
  },
  timeChipTextActive: {
    color: '#ffffff',
  },
  pickerActionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  pickerCancelButton: {
    flex: 1,
    backgroundColor: '#e2e8f0',
    borderRadius: 20,
    paddingVertical: 14,
    alignItems: 'center',
    marginRight: 10,
  },
  pickerCancelText: {
    color: '#0f172a',
    fontWeight: '700',
  },
  pickerConfirmButton: {
    flex: 1,
    backgroundColor: '#0ea5e9',
    borderRadius: 20,
    paddingVertical: 14,
    alignItems: 'center',
  },
  pickerConfirmText: {
    color: '#ffffff',
    fontWeight: '700',
  },
  confirmationCard: {
    width: '100%',
    backgroundColor: '#f8fafc',
    borderRadius: 28,
    paddingVertical: 28,
    paddingHorizontal: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.12,
    shadowOffset: { width: 0, height: 10 },
    shadowRadius: 18,
    elevation: 20,
  },
  confirmationIconWrapper: {
    marginBottom: 20,
  },
  confirmationIcon: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: '#0ea5e9',
    justifyContent: 'center',
    alignItems: 'center',
  },
  confirmationCheck: {
    fontSize: 38,
    color: '#ffffff',
    fontWeight: '800',
  },
  confirmationTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 8,
    textAlign: 'center',
  },
  confirmationSubtitle: {
    fontSize: 14,
    color: '#64748b',
    marginBottom: 20,
    textAlign: 'center',
  },
  confirmationProfileCard: {
    width: '100%',
    alignItems: 'center',
    paddingVertical: 18,
    backgroundColor: '#ffffff',
    borderRadius: 24,
    marginBottom: 18,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowOffset: { width: 0, height: 6 },
    shadowRadius: 14,
    elevation: 8,
  },
  confirmationProfileImage: {
    width: 92,
    height: 92,
    borderRadius: 46,
    backgroundColor: '#e2e8f0',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  confirmationProfileInitial: {
    fontSize: 32,
    fontWeight: '800',
    color: '#0ea5e9',
  },
  confirmationProfileName: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 2,
  },
  confirmationProfileSpecialty: {
    fontSize: 14,
    color: '#64748b',
  },
  confirmationDetailsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 18,
  },
  confirmationDetailText: {
    fontSize: 14,
    color: '#334155',
  },
  confirmationSeparator: {
    width: 1,
    height: 16,
    backgroundColor: '#cbd5e1',
    marginHorizontal: 12,
  },
  changeLink: {
    marginBottom: 16,
  },
  changeLinkText: {
    color: '#0ea5e9',
    fontSize: 14,
    fontWeight: '700',
  },
  returnButton: {
    width: '100%',
    backgroundColor: '#0ea5e9',
    borderRadius: 24,
    paddingVertical: 16,
    alignItems: 'center',
  },
  returnButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
});
