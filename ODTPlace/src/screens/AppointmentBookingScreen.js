import React, { useState } from 'react';
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
} from 'react-native';
import ScheduleHeader from '../components/ScheduleHeader';
import BottomNavBar from '../components/BottomNavBar';
import { createAppointment } from '../services/api';
import { useAuth } from '../context/AuthContext';

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
      resizeMode="cover"
    >
      <SafeAreaView style={styles.container}>
        <ScheduleHeader title="Agendamento" onBack={() => navigation.goBack()} />

        <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
          <View style={styles.headerCard}>
            <Text style={styles.headerLabel}>Profissional</Text>
            <Text style={styles.headerTitle}>{professional.nome ?? professional.name ?? 'Dr. Nome Sobrenome'}</Text>
            <Text style={styles.headerSubtitle}>{professional.specialty ?? professional.especialidades?.[0] ?? 'Especialidade'}</Text>
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.fieldLabel}>Nome Completo</Text>
            <TextInput
              style={styles.input}
              placeholder="Seu nome completo"
              placeholderTextColor="#9ca3af"
              value={nomeCompleto}
              onChangeText={setNomeCompleto}
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.fieldLabel}>Email</Text>
            <TextInput
              keyboardType="email-address"
              autoCapitalize="none"
              style={styles.input}
              placeholder="Digite seu E-mail"
              placeholderTextColor="#9ca3af"
              value={email}
              onChangeText={setEmail}
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.fieldLabel}>Número de telefone</Text>
            <TextInput
              keyboardType="phone-pad"
              style={styles.input}
              placeholder="+55 (00) 0000-0000"
              placeholderTextColor="#9ca3af"
              value={phone}
              onChangeText={setPhone}
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.fieldLabel}>Escolha a data e Horário</Text>
            <TouchableOpacity style={styles.slotInput} activeOpacity={0.85} onPress={handleSlotPress}>
              <Text style={styles.slotText}>{selectedSlot}</Text>
              <Text style={styles.slotArrow}>⌄</Text>
            </TouchableOpacity>
            <Text style={styles.slotHelp}>Toque para escolher o dia e o horário.</Text>
          </View>

          {/* Seleção de Especialidade */}
          {doctorSpecialties.length > 0 && (
            <View style={styles.formGroup}>
              <Text style={styles.fieldLabel}>Especialidade</Text>
              <TouchableOpacity 
                style={styles.slotInput} 
                activeOpacity={0.85} 
                onPress={() => setSpecialtyPickerVisible(true)}
              >
                <Text style={styles.slotText}>{selectedSpecialtyName}</Text>
                <Text style={styles.slotArrow}>⌄</Text>
              </TouchableOpacity>
              {doctorSpecialties.length > 1 && (
                <Text style={styles.slotHelp}>Toque para escolher uma especialidade.</Text>
              )}
            </View>
          )}

          {/* Preço da Consulta */}
          <View style={styles.priceCard}>
            <Text style={styles.priceLabel}>Valor da Consulta</Text>
            <Text style={styles.priceValue}>R$ {consultationPrice.toFixed(2).replace('.', ',')}</Text>
          </View>

          <Modal visible={specialtyPickerVisible} transparent animationType="fade">
            <View style={styles.pickerOverlay}>
              <View style={styles.pickerCard}>
                <View style={styles.pickerHeader}>
                  <Text style={styles.pickerTitle}>Selecione a Especialidade</Text>
                  <TouchableOpacity 
                    style={styles.pickerCloseButton} 
                    onPress={() => setSpecialtyPickerVisible(false)}
                    activeOpacity={0.8}
                  >
                    <Text style={styles.pickerCloseText}>✕</Text>
                  </TouchableOpacity>
                </View>
                <ScrollView style={styles.specialtyList}>
                  {doctorSpecialties.map((specialty) => (
                    <TouchableOpacity
                      key={specialty.id}
                      style={[
                        styles.specialtyOption,
                        selectedSpecialtyId === specialty.id && styles.specialtyOptionActive
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
                          selectedSpecialtyId === specialty.id && styles.specialtyOptionTextActive
                        ]}>{specialty.nome}</Text>
                        {selectedSpecialtyId === specialty.id && (
                          <Text style={styles.specialtyCheckmark}>✓</Text>
                        )}
                      </View>
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              </View>
            </View>
          </Modal>

          <Modal visible={pickerVisible} transparent animationType="fade">
            <View style={styles.pickerOverlay}>
              <View style={styles.pickerCard}>
                <View style={styles.pickerHeader}>
                  <Text style={styles.pickerTitle}>{monthLabel}</Text>
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
                        style={[styles.dayCell, isSelected && styles.dayCellSelected]}
                        activeOpacity={0.85}
                        onPress={() => setSelectedDate(day.id)}
                      >
                        <Text style={[styles.dayNumber, isSelected && styles.dayNumberSelected]}>{day.day}</Text>
                      </TouchableOpacity>
                    );
                  })}
                </View>

                <Text style={styles.timeSectionTitle}>Horário</Text>
                <View style={styles.timeRow}>
                  {['09:00', '09:30', '12:00', '12:30', '15:00', '16:30'].map((time) => {
                    const isActive = selectedTime === time;
                    return (
                      <TouchableOpacity
                        key={time}
                        style={[styles.timeChip, isActive && styles.timeChipActive]}
                        activeOpacity={0.85}
                        onPress={() => setSelectedTime(time)}
                      >
                        <Text style={[styles.timeChipText, isActive && styles.timeChipTextActive]}>{time}</Text>
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
            <Text style={styles.fieldLabel}>Motivo da consulta (Opcional)</Text>
            <TextInput
              style={[styles.input, styles.reasonInput]}
              placeholder="O que você está sentindo ou precisa? Por exemplo: 'Estou muito ansioso e com dificuldade para dormir'."
              placeholderTextColor="#cbd5e1"
              value={reason}
              onChangeText={setReason}
              multiline
              numberOfLines={4}
              textAlignVertical="top"
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

              <Text style={styles.confirmationTitle}>Agendamento Confirmado</Text>
              <Text style={styles.confirmationSubtitle}>Seu agendamento foi feito com sucesso</Text>

              <View style={styles.confirmationProfileCard}>
                <View style={styles.confirmationProfileImage}>
                  <Text style={styles.confirmationProfileInitial}>{(professional.nome ?? professional.name)?.charAt(0) ?? 'P'}</Text>
                </View>
                <Text style={styles.confirmationProfileName}>{professional.nome ?? professional.name ?? 'Dr. Nome Sobrenome'}</Text>
                <Text style={styles.confirmationProfileSpecialty}>{professional.specialty ?? professional.especialidades?.[0] ?? 'Especialidade'}</Text>
              </View>

              <View style={styles.confirmationDetailsRow}>
                <Text style={styles.confirmationDetailText}>{selectedSlot}</Text>
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
    paddingTop: 120,
  },
  content: {
    paddingHorizontal: 20,
    paddingBottom: 160,
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
