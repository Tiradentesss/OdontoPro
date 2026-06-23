import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  SafeAreaView, 
  Platform, 
  StatusBar 
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../ThemeContext'; // 1. Importa o hook global de tema

export default function AppointmentDetailsScreen({ route, navigation }) {
  // Recebe os dados do paciente para exibir o nome dinamicamente no cabeçalho
  const { patientName } = route.params || { patientName: 'Victor Araújo' };
  
  // Estado para simular o status da consulta localmente
  const [status, setStatus] = useState('Pendente');

  // 2. Consome o estado do tema e a paleta de cores dinâmica
  const { isDarkMode, colors } = useTheme();

  // Redireciona para a tela de sucesso configurada anteriormente
  const handleConfirm = () => {
    navigation.navigate('SuccessScreen');
  };

  // Abre a tela extra de reagendamento de consulta
  const handleReschedule = () => {
    navigation.navigate('RescheduleScreen', { patientName: patientName });
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={colors.card} 
        translucent={false} 
      />

      {/* Cabeçalho Consistente e Alinhado */}
      <View style={[styles.header, { backgroundColor: colors.card, borderColor: colors.border }]}>
        <TouchableOpacity 
          style={[styles.backButton, { backgroundColor: colors.backButtonBg }]} 
          onPress={() => navigation.goBack()}
          activeOpacity={0.6}
        >
          <Feather name="arrow-left" size={22} color={colors.text} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: colors.text }]}>Detalhes da Consulta</Text>
        <View style={styles.headerSpacer} />
      </View>

      <View style={styles.content}>
        
        {/* Paciente Identificado */}
        <View style={styles.patientMetaContainer}>
          <Text style={styles.patientLabel}>Paciente</Text>
          <Text style={[styles.patientName, { color: colors.text }]}>{patientName}</Text>
        </View>

        {/* Bloco Unificado: Dados da Consulta */}
        <Text style={styles.sectionTitle}>Informações Gerais</Text>
        <View style={[styles.appointmentCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          
          <View style={styles.infoRow}>
            <View style={[styles.iconBox, { backgroundColor: isDarkMode ? '#1E3A8A' : '#EFF6FF' }]}>
              <Feather name="calendar" size={18} color={isDarkMode ? '#60A5FA' : '#163783'} />
            </View>
            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>Data do Atendimento</Text>
              <Text style={[styles.infoValue, { color: colors.text }]}>22 de Maio, 2026</Text>
            </View>
          </View>

          <View style={[styles.divider, { backgroundColor: colors.border }]} />

          <View style={styles.infoRow}>
            <View style={[styles.iconBox, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
              <Feather name="clock" size={18} color={isDarkMode ? '#94A3B8' : '#475569'} />
            </View>
            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>Horário Marcado</Text>
              <Text style={[styles.infoValue, { color: colors.text }]}>09:00 — 09:30</Text>
            </View>
          </View>

          <View style={[styles.divider, { backgroundColor: colors.border }]} />

          <View style={styles.infoRow}>
            <View style={[
              styles.iconBox, 
              { 
                backgroundColor: status === 'Pendente' 
                  ? (isDarkMode ? '#78350F' : '#FEF3C7') 
                  : (isDarkMode ? '#064E3B' : '#D1FAE5') 
              }
            ]}>
              <Feather 
                name={status === 'Pendente' ? "alert-circle" : "check-circle"} 
                size={18} 
                color={status === 'Pendente' ? (isDarkMode ? '#FBBF24' : '#D97706') : (isDarkMode ? '#34D399' : '#059669')} 
              />
            </View>
            <View style={styles.infoTextContainer}>
              <Text style={styles.infoLabel}>Status da Confirmação</Text>
              <Text style={[
                styles.infoValue, 
                { color: status === 'Pendente' ? (isDarkMode ? '#FBBF24' : '#D97706') : (isDarkMode ? '#34D399' : '#059669') }
              ]}>
                {status}
              </Text>
            </View>
          </View>
        </View>

        {/* Bloco: Motivo da Consulta */}
        <Text style={styles.sectionTitle}>Motivo / Sintomas</Text>
        <View style={[styles.reasonCard, { backgroundColor: colors.card, borderColor: colors.border, borderLeftColor: colors.brandBlue }]}>
          <Text style={[styles.reasonText, { color: isDarkMode ? '#94A3B8' : '#334155' }]}>
            Paciente relatou episódios frequentes de dor aguda na região molar inferior direita ao ingerir alimentos frios. Suspeita clínica inicial de necessidade de extração de siso.
          </Text>
        </View>

        {/* Espaçador flexível para empurrar as ações para a base da tela */}
        <View style={styles.spacer} />

        {/* Botões de Ação Inferiores Premium */}
        <View style={styles.footerActions}>
          {status === 'Pendente' && (
            <TouchableOpacity 
              style={[styles.confirmButton, isDarkMode && { shadowColor: '#000000', backgroundColor: '#059669' }]} 
              activeOpacity={0.8}
              onPress={handleConfirm}
            >
              <Feather name="check" size={16} color="#FFFFFF" style={{ marginRight: 8 }} />
              <Text style={styles.confirmButtonText}>Confirmar Consulta</Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity 
            style={[
              styles.rescheduleButton, 
              { backgroundColor: colors.card, borderColor: colors.border }
            ]} 
            activeOpacity={0.7}
            onPress={handleReschedule}
          >
            <Feather name="calendar" size={16} color={colors.mutedText} style={{ marginRight: 8 }} />
            <Text style={[styles.rescheduleButtonText, { color: colors.text }]}>Reagendar ou Cancelar</Text>
          </TouchableOpacity>
        </View>

      </View>
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
    color: '#64748B',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  patientName: {
    fontSize: 24,
    fontWeight: '800',
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#475569',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 12,
  },
  appointmentCard: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    marginBottom: 24,
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
    color: '#64748B',
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 1,
  },
  infoValue: {
    fontSize: 15,
    fontWeight: '700',
  },
  divider: {
    height: 1,
    marginVertical: 12,
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
  spacer: {
    flex: 1,
  },
  footerActions: {
    paddingBottom: Platform.OS === 'ios' ? 20 : 30,
    marginTop: 20,
  },
  confirmButton: {
    flexDirection: 'row',
    backgroundColor: '#10B981', 
    borderRadius: 14,
    height: 54,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#10B981',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 2,
  },
  confirmButtonText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  rescheduleButton: {
    flexDirection: 'row',
    borderRadius: 14,
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
  },
  rescheduleButtonText: {
    fontSize: 14,
    fontWeight: '700',
  },
});