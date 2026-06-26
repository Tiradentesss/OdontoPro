import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  SafeAreaView, 
  Platform, 
  StatusBar,
  Modal,
  Dimensions
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../components/ThemeContext'; // Importação do tema global

const { width } = Dimensions.get('window');

export default function RescheduleScreen({ route, navigation }) {
  const { patientName } = route.params || { patientName: 'Victor Araújo' };
  const [selectedTime, setSelectedTime] = useState('10:30');
  const [selectedDate, setSelectedDate] = useState('23 de Maio, 2026');
  const [isModalVisible, setIsModalVisible] = useState(false);

  // Consome as propriedades globais do tema
  const { isDarkMode, colors } = useTheme();

  // Abre o modal de revisão
  const handleOpenConfirmation = () => {
    setIsModalVisible(true);
  };

  // Fecha o modal e consolida o fluxo indo para a SuccessScreen
  const handleConfirmReschedule = () => {
    setIsModalVisible(false);
    navigation.navigate('SuccessScreen');
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
          activeOpacity={0.7}
        >
          <View style={[styles.iconBox, { backgroundColor: isDarkMode ? '#1E293B' : '#EFF6FF' }]}>
            <Feather name="calendar" size={18} color={colors.brandBlue} />
          </View>
          <Text style={[styles.pickerText, { color: colors.text }]}>{selectedDate}</Text>
          <Feather name="chevron-down" size={18} color={colors.mutedText} style={{ marginRight: 4 }} />
        </TouchableOpacity>

        {/* Grid de Horários */}
        <Text style={[styles.sectionTitle, { color: colors.mutedText }]}>Horários Disponíveis</Text>
        <View style={styles.timeGrid}>
          {['08:00', '09:00', '10:30', '11:30', '14:00', '15:30'].map((time) => {
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
        </View>

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
                style={styles.modalConfirmButton}
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
  timeGrid: { 
    flexDirection: 'row', 
    flexWrap: 'wrap', 
    justifyContent: 'space-between' 
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
    paddingHorizontal: 24,
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
    backgroundColor: '#10B981', // Mantido verde semântico para sucesso/confirmação
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  modalConfirmButtonText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});