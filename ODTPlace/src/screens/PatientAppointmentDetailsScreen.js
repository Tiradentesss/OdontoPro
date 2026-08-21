import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  TextInput,
  Platform,
  StatusBar,
  Alert,
  Modal,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../components/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { submitAppointmentRating, updateAppointment } from '../services/api';
import { formatAppointmentTime, parseAppointmentDate } from '../utils/appointmentTime';

const getStatusInfo = (statusValue, isDarkMode) => {
  const normalized = (statusValue || '').toString().toLowerCase();
  if (normalized === 'cancelada') {
    return {
      label: 'CANCELADA',
      bg: isDarkMode ? '#581c1c' : '#fee2e2',
      text: isDarkMode ? '#fca5a5' : '#b91c1c',
    };
  }
  if (normalized === 'realizada' || normalized === 'completa') {
    return {
      label: 'REALIZADA',
      bg: isDarkMode ? '#064e3b' : '#dcfce7',
      text: isDarkMode ? '#86efac' : '#047857',
    };
  }
  if (normalized === 'perdida') {
    return {
      label: 'PERDIDA',
      bg: isDarkMode ? '#111827' : '#e5e7eb',
      text: isDarkMode ? '#f8fafc' : '#111827',
    };
  }
  if (normalized === 'confirmada') {
    return {
      label: 'CONFIRMADA',
      bg: isDarkMode ? '#78350f' : '#fef3c7',
      text: isDarkMode ? '#fde68a' : '#b45309',
    };
  }
  return {
    label: 'AGENDADA',
    bg: isDarkMode ? '#78350f' : '#fef3c7',
    text: isDarkMode ? '#fde68a' : '#b45309',
  };
};

export default function PatientAppointmentDetailsScreen({ route, navigation }) {
  const { patientName, allowReschedule = true, appointment: routeAppointment } = route.params || {};
  const [appointment, setAppointment] = useState(routeAppointment || null);
  const [status, setStatus] = useState(routeAppointment?.status || 'pendente');
  const [ratingOpen, setRatingOpen] = useState(false);
  const [selectedRating, setSelectedRating] = useState(routeAppointment?.avaliacao ?? routeAppointment?.avaliacao_nota ?? 0);
  const [ratingComment, setRatingComment] = useState('');
  const [submittingRating, setSubmittingRating] = useState(false);
  const { user } = useAuth();
  const { isDarkMode, colors } = useTheme();
  const patientBlue = isDarkMode ? '#38BDF8' : '#0EA5E9';
  const headerBg = isDarkMode ? colors.container : patientBlue;
  const headerTextColor = isDarkMode ? colors.text : '#FFFFFF';
  const headerIconColor = isDarkMode ? colors.text : patientBlue;
  const headerButtonBg = isDarkMode ? colors.card : colors.backButtonBg;

  const parseDateString = (value) => {
    return parseAppointmentDate(value);
  };

  const appointmentClinic = appointment?.clinica_nome || appointment?.clinic || appointment?.clinicName || 'Clínica';
  const appointmentSpecialty = appointment?.especialidade_nome || appointment?.specialty || 'Especialidade';
  const appointmentDoctor = appointment?.medico_nome || appointment?.doctor || 'Dr. Médico';
  const appointmentReason = appointment?.observacoes || appointment?.observations || route.params?.motivo || 'Consulta';
  const appointmentDate = parseDateString(appointment?.data_hora) || parseDateString(appointment?.date);
  const appointmentDateLabel = appointmentDate ? appointmentDate.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' }) : 'Data a definir';
  const appointmentTimeLabel = appointmentDate ? formatAppointmentTime(appointmentDate) : 'Horário a definir';

  const normalizedStatus = (status || '').toString().toLowerCase();
  const statusInfo = getStatusInfo(status, isDarkMode);
  const canReschedule = normalizedStatus === 'agendada';
  const canCancel = !['realizada', 'completa', 'cancelada', 'perdida'].includes(normalizedStatus);
  const isCompleted = ['realizada', 'completa'].includes(normalizedStatus);
  const ratingValue = appointment?.avaliacao ?? appointment?.avaliacao_nota;
  const hasRating = ratingValue !== null && ratingValue !== undefined && ratingValue !== '' && Number(ratingValue) > 0;

  const handleReschedule = () => {
    navigation.navigate('PatientRescheduleScreen', { patientName: patientName || 'Paciente', appointment });
  };

  const handleCancelAppointment = async () => {
    try {
      if (appointment?.id) {
        await updateAppointment(appointment.id, { status: 'cancelada' });
      }
      setStatus('cancelada');
      Alert.alert('Sucesso', 'A consulta foi cancelada.');
    } catch (error) {
      Alert.alert('Erro', 'Não foi possível cancelar a consulta.');
    }
  };

  const handleSubmitRating = async () => {
    if (!selectedRating) {
      Alert.alert('Atenção', 'Selecione uma classificação em estrelas.');
      return;
    }

    const patientId = user?.id ?? appointment?.paciente_id;
    if (!appointment?.id || !patientId) {
      Alert.alert('Erro', 'Não foi possível identificar o paciente desta consulta.');
      return;
    }

    setSubmittingRating(true);
    try {
      await submitAppointmentRating(appointment.id, {
        patient_id: patientId,
        nota: selectedRating,
        comentario: ratingComment,
      });
      setAppointment((current) => ({ ...current, avaliacao: selectedRating, avaliacao_comentario: ratingComment }));
      setRatingOpen(false);
      Alert.alert('Sucesso', 'Avaliação enviada com sucesso.');
    } catch (error) {
      Alert.alert('Erro', error.message || 'Não foi possível enviar a avaliação.');
    } finally {
      setSubmittingRating(false);
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
        <Text style={[styles.headerTitle, { color: headerTextColor }]}>Detalhes da Consulta</Text>
        <View style={styles.headerSpacer} />
      </View>

      <View style={styles.content}>
        <View style={styles.patientMetaContainer}>
          <Text style={[styles.patientLabel, { color: colors.mutedText }]}>Paciente</Text>
          <Text style={[styles.patientName, { color: colors.text }]}>{patientName || appointment?.nome || 'Paciente'}</Text>
        </View>

        <Text style={[styles.sectionTitle, { color: colors.mutedText }]}>Informações da Consulta</Text>
        <View style={[styles.appointmentCard, { backgroundColor: colors.card, borderColor: colors.border }]}> 
          <View style={styles.infoRow}>
            <View style={[styles.iconBox, { backgroundColor: isDarkMode ? '#1E3A8A' : '#EFF6FF' }]}>
              <Feather name="map-pin" size={18} color={isDarkMode ? '#60A5FA' : '#163783'} />
            </View>
            <View style={styles.infoTextContainer}>
              <Text style={[styles.infoLabel, { color: colors.text }]}>Clínica</Text>
              <Text style={[styles.infoValue, { color: colors.text }]}>{appointmentClinic}</Text>
            </View>
          </View>

          <View style={[styles.divider, { backgroundColor: colors.border }]} />

          <View style={styles.infoRow}>
            <View style={[styles.iconBox, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
              <Feather name="user" size={18} color={isDarkMode ? '#94A3B8' : '#475569'} />
            </View>
            <View style={styles.infoTextContainer}>
              <Text style={[styles.infoLabel, { color: colors.text }]}>Especialidade</Text>
              <Text style={[styles.infoValue, { color: colors.text }]}>{appointmentSpecialty}</Text>
            </View>
          </View>

          <View style={[styles.divider, { backgroundColor: colors.border }]} />

          <View style={styles.infoRow}>
            <View style={[styles.iconBox, { backgroundColor: isDarkMode ? '#047857' : '#DCFCE7' }]}>
              <Feather name="user-check" size={18} color={isDarkMode ? '#A7F3D0' : '#166534'} />
            </View>
            <View style={styles.infoTextContainer}>
              <Text style={[styles.infoLabel, { color: colors.text }]}>Profissional</Text>
              <Text style={[styles.infoValue, { color: colors.text }]}>{appointmentDoctor}</Text>
            </View>
          </View>

          <View style={[styles.divider, { backgroundColor: colors.border }]} />

          <View style={styles.infoRow}>
            <View style={[styles.iconBox, { backgroundColor: statusInfo.bg }]}>
              <Feather name="clock" size={18} color={statusInfo.text} />
            </View>
            <View style={styles.infoTextContainer}>
              <Text style={[styles.infoLabel, { color: colors.text }]}>Data e Hora</Text>
              <Text style={[styles.infoValue, { color: colors.text }]}>{`${appointmentDateLabel} • ${appointmentTimeLabel}`}</Text>
            </View>
          </View>

          <View style={[styles.divider, { backgroundColor: colors.border }]} />

          <View style={styles.infoRow}>
            <View style={[styles.statusBadge, { backgroundColor: statusInfo.bg }]}> 
              <Text style={[styles.statusBadgeText, { color: statusInfo.text }]}>{statusInfo.label}</Text>
            </View>
          </View>
        </View>

        <Text style={[styles.sectionTitle, { color: colors.mutedText }]}>Motivo da Consulta</Text>
        <View style={[styles.reasonCard, { backgroundColor: colors.card, borderColor: colors.border, borderLeftColor: patientBlue }]}>
          <Text style={[styles.reasonText, { color: colors.text }]}>{appointmentReason}</Text>
        </View>

        {isCompleted && !hasRating && (
                  <Modal visible={ratingOpen} transparent animationType="fade" onRequestClose={() => setRatingOpen(false)}>
                    <View style={styles.modalOverlay}>
                      <View style={[styles.ratingCard, { backgroundColor: colors.card, borderColor: colors.border, width: '90%' }]}>
                        <Text style={[styles.ratingTitle, { color: colors.text }]}>Avaliar Consulta</Text>
                        <View style={styles.ratingStars}>
                          {[1, 2, 3, 4, 5].map((value) => (
                            <TouchableOpacity
                              key={value}
                              onPress={() => setSelectedRating(value)}
                              accessibilityRole="button"
                              accessibilityLabel={`Selecionar ${value} estrela${value === 1 ? '' : 's'}`}
                            >
                              <Text style={[styles.ratingStar, { color: value <= selectedRating ? '#F59E0B' : colors.border }]}>★</Text>
                            </TouchableOpacity>
                          ))}
                        </View>
                        <TextInput
                          style={[styles.ratingInput, { color: colors.text, borderColor: colors.border, backgroundColor: isDarkMode ? '#0F172A' : '#F8FAFC' }]}
                          placeholder="Deixe um comentário (opcional)"
                          placeholderTextColor={isDarkMode ? '#94A3B8' : '#64748B'}
                          value={ratingComment}
                          onChangeText={setRatingComment}
                          multiline
                          maxLength={500}
                        />
                        <View style={styles.ratingActions}>
                          <TouchableOpacity style={[styles.ratingSubmitButton, { backgroundColor: patientBlue }]} onPress={handleSubmitRating} disabled={submittingRating}>
                            <Text style={styles.ratingSubmitText}>{submittingRating ? 'Enviando...' : 'Enviar Avaliação'}</Text>
                          </TouchableOpacity>
                          <TouchableOpacity style={styles.ratingCancelButton} onPress={() => setRatingOpen(false)} disabled={submittingRating}>
                            <Text style={[styles.ratingCancelText, { color: colors.mutedText }]}>Cancelar</Text>
                          </TouchableOpacity>
                        </View>
                      </View>
                    </View>
                  </Modal>
                )}

        <View style={styles.spacer} />

        <View style={styles.footerActions}>
          {isCompleted && !hasRating && !ratingOpen && (
            <TouchableOpacity style={[styles.rateButton, { backgroundColor: patientBlue }]} activeOpacity={0.85} onPress={() => setRatingOpen(true)}>
              <Feather name="star" size={16} color="#FFFFFF" style={{ marginRight: 8 }} />
              <Text style={styles.rateButtonText}>Avaliar Consulta</Text>
            </TouchableOpacity>
          )}

          {isCompleted && hasRating && (
            <View style={[styles.ratedButton, { backgroundColor: isDarkMode ? '#064E3B' : '#DCFCE7' }]}>
              <Feather name="check" size={16} color={isDarkMode ? '#86EFAC' : '#047857'} style={{ marginRight: 8 }} />
              <Text style={[styles.ratedButtonText, { color: isDarkMode ? '#86EFAC' : '#047857' }]}>Já avaliado</Text>
            </View>
          )}

          {allowReschedule && canReschedule && (
            <TouchableOpacity style={[styles.rescheduleButton, { backgroundColor: patientBlue }]} activeOpacity={0.85} onPress={handleReschedule}>
              <Feather name="calendar" size={16} color="#FFFFFF" style={{ marginRight: 8 }} />
              <Text style={[styles.rescheduleButtonText, { color: '#FFFFFF' }]}>Reagendar Consulta</Text>
            </TouchableOpacity>
          )}

          {canCancel && (
            <TouchableOpacity style={styles.cancelButton} activeOpacity={0.8} onPress={handleCancelAppointment}>
              <Feather name="x-circle" size={16} color="#FFFFFF" style={{ marginRight: 8 }} />
              <Text style={styles.cancelButtonText}>Cancelar Consulta</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
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
  appointmentCard: {
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    marginBottom: 24,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.08,
    shadowRadius: 16,
    elevation: 4,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconBox: {
    width: 38,
    height: 38,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  infoTextContainer: {
    flex: 1,
  },
  infoLabel: {
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 15,
    fontWeight: '700',
  },
  divider: {
    height: 1,
    marginVertical: 12,
  },
  statusBadge: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 999,
    alignSelf: 'flex-start',
  },
  statusBadgeText: {
    fontSize: 12,
    fontWeight: '700',
  },
  reasonCard: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderLeftWidth: 4,
  },
  reasonText: {
    fontSize: 14,
    fontWeight: '500',
    lineHeight: 22,
  },
  ratingCard: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    marginBottom: 8,
  },
  ratingTitle: {
    fontSize: 16,
    fontWeight: '700',
    marginBottom: 12,
  },
  ratingStars: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
    marginBottom: 16,
  },
  ratingStar: {
    fontSize: 34,
  },
  ratingInput: {
    minHeight: 88,
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 10,
    textAlignVertical: 'top',
    fontSize: 14,
  },
  ratingActions: {
    marginTop: 12,
    gap: 10,
  },
  ratingSubmitButton: {
    height: 48,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  ratingSubmitText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '700',
  },
  ratingCancelButton: {
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  ratingCancelText: {
    fontSize: 14,
    fontWeight: '600',
  },
  spacer: {
    flex: 1,
  },
  footerActions: {
    paddingBottom: Platform.OS === 'ios' ? 20 : 30,
    marginTop: 20,
  },
  rescheduleButton: {
    flexDirection: 'row',
    borderRadius: 14,
    height: 54,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.12,
    shadowRadius: 12,
    elevation: 3,
  },
  rescheduleButtonText: {
    fontSize: 15,
    fontWeight: '700',
  },
  rateButton: {
    flexDirection: 'row',
    borderRadius: 14,
    height: 54,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  rateButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
  },
  ratedButton: {
    flexDirection: 'row',
    borderRadius: 14,
    height: 54,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  ratedButtonText: {
    fontSize: 15,
    fontWeight: '700',
  },
  cancelButton: {
    flexDirection: 'row',
    backgroundColor: '#DC2626',
    borderRadius: 14,
    height: 54,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 2,
  },
  cancelButtonText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.45)',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
});
