import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  Image, 
  TouchableOpacity, 
  SafeAreaView, 
  Platform, 
  StatusBar, 
  ScrollView
} from 'react-native';
import { Feather, Ionicons } from '@expo/vector-icons';
import { useTheme } from '../components/ThemeContext'; // 1. Importa o hook global de tema

// Base de dados simulada para busca por ID
const APPOINTMENTS_DATA = [
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
];

export default function PatientProfileScreen({ route, navigation }) {
  const params = route.params || {};
  const [isConfirmed, setIsConfirmed] = useState(false);
  
  // 2. Consome o estado do tema e a paleta de cores dinâmica
  const { isDarkMode, colors } = useTheme();
  
  const fallbackPatient = {
    name: 'Victor Araújo',
    avatar: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&q=80&w=120&h=120',
  };

  // Resolução lógica do paciente atual
  let currentPatient = fallbackPatient;
  let appointmentMotivo = "Extração de siso";

  if (params.patient) {
    currentPatient = {
      name: params.patient.name,
      avatar: params.patient.avatar
    };
  } else if (params.id) {
    const found = APPOINTMENTS_DATA.find(item => item.id === params.id);
    if (found) {
      currentPatient = {
        name: found.patientName,
        avatar: found.avatar
      };
      appointmentMotivo = found.motivo;
    }
  }

  // Lógica centralizada para abrir a tela de Detalhes do Agendamento
  const handleNavigateToDetails = () => {
    navigation?.navigate('AppointmentDetailsScreen', { 
      patientName: currentPatient?.name,
      motivo: appointmentMotivo
    });
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={colors.card} 
        translucent={false} 
      />

      {/* Header Superior Minimalista */}
      <View style={[styles.header, { backgroundColor: colors.card, borderColor: colors.border }]}>
        <TouchableOpacity 
          style={[styles.backButton, { backgroundColor: colors.backButtonBg }]} 
          onPress={() => navigation.goBack()}
          activeOpacity={0.6}
        >
          <Feather name="arrow-left" size={22} color={colors.text} />
        </TouchableOpacity>
        <Text style={[styles.headerTitle, { color: colors.text }]}>Perfil do Paciente</Text>
        <View style={styles.headerSpacer} />
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        
        {/* Bloco de Perfil Principal */}
        <View style={[styles.profileCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <View style={styles.avatarWrapper}>
            <Image source={{ uri: currentPatient?.avatar }} style={[styles.avatarBig, { borderColor: isDarkMode ? '#1E293B' : '#EFF6FF' }]} />
            <View style={[styles.activeBadge, { borderColor: colors.card }]} />
          </View>
          <Text style={[styles.patientNameText, { color: colors.text }]}>{currentPatient?.name}</Text>
          <Text style={[styles.cpfText, { color: colors.mutedText }]}>CPF: 100.000.111-90</Text>
          <Text style={[styles.subInfoText, { color: isDarkMode ? '#94A3B8' : '#475569' }]}>28 anos  •  Masculino</Text>
        </View>

        {/* Seção de Contato */}
        <Text style={[styles.sectionTitle, { color: colors.mutedText }]}>Informações de Contato</Text>
        <View style={[styles.infoContainerBox, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <View style={styles.contactRow}>
            <View style={[styles.iconBox, { backgroundColor: isDarkMode ? '#1E3A8A' : '#EFF6FF' }]}>
              <Feather name="phone" size={18} color={isDarkMode ? '#60A5FA' : '#2563EB'} />
            </View>
            <View style={styles.contactTextContainer}>
              <Text style={[styles.contactLabel, { color: colors.mutedText }]}>Telefone</Text>
              <Text style={[styles.contactValue, { color: colors.text }]}>(91) 98452-0000</Text>
            </View>
          </View>

          <View style={[styles.divider, { backgroundColor: colors.border }]} />

          <View style={styles.contactRow}>
            <View style={[styles.iconBox, { backgroundColor: isDarkMode ? '#064E3B' : '#F0FDF4' }]}>
              <Feather name="mail" size={18} color={isDarkMode ? '#34D399' : '#16A34A'} />
            </View>
            <View style={styles.contactTextContainer}>
              <Text style={[styles.contactLabel, { color: colors.mutedText }]}>E-mail</Text>
              <Text style={[styles.contactValue, { color: colors.text }]}>paciente@gmail.com</Text>
            </View>
          </View>

          <View style={[styles.divider, { backgroundColor: colors.border }]} />

          <View style={styles.contactRow}>
            <View style={[styles.iconBox, { backgroundColor: isDarkMode ? '#78350F' : '#FFF7ED' }]}>
              <Ionicons name="location-outline" size={20} color={isDarkMode ? '#FBBF24' : '#EA580C'} />
            </View>
            <View style={styles.contactTextContainer}>
              <Text style={[styles.contactLabel, { color: colors.mutedText }]}>Endereço</Text>
              <Text style={[styles.contactValue, { color: colors.text }]}>Rua 9 de Janeiro, altos — Marco</Text>
            </View>
          </View>
        </View>

        {/* Seção Próxima Consulta com Redirecionamento Unificado */}
        <Text style={[styles.sectionTitle, { color: colors.mutedText }]}>Próxima Consulta</Text>
        <View style={[
          styles.appointmentCard, 
          { backgroundColor: colors.card, borderColor: colors.border },
          isConfirmed && { 
            borderColor: '#10B981', 
            backgroundColor: isDarkMode ? '#064E3B' : '#F0FDF4' 
          }
        ]}>
          
          <View style={styles.appointmentBadgeRow}>
            <View style={[styles.dateBadgeContainer, { backgroundColor: isDarkMode ? '#1E3A8A' : '#EFF6FF' }]}>
              <Feather name="calendar" size={15} color={isDarkMode ? '#60A5FA' : '#163783'} style={{ marginRight: 6 }} />
              <Text style={[styles.dateBadgeText, { color: isDarkMode ? '#60A5FA' : '#163783' }]}>22 de Maio, 2026</Text>
            </View>
            <View style={[styles.timeBadgeContainer, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
              <Feather name="clock" size={13} color={colors.mutedText} style={{ marginRight: 4 }} />
              <Text style={[styles.timeBadgeText, { color: isDarkMode ? '#94A3B8' : '#475569' }]}>09:00</Text>
            </View>

            {/* Badge de Status */}
            <View style={[
              styles.statusBadge, 
              isConfirmed 
                ? { backgroundColor: isDarkMode ? '#064E3B' : '#D1FAE5' } 
                : { backgroundColor: isDarkMode ? '#78350F' : '#FEF3C7' }
            ]}>
              <Text style={[
                styles.statusBadgeText, 
                isConfirmed 
                  ? { color: isDarkMode ? '#34D399' : '#059669' } 
                  : { color: isDarkMode ? '#FBBF24' : '#D97706' }
              ]}>
                {isConfirmed ? 'Confirmada' : 'Pendente'}
              </Text>
            </View>
          </View>

          {/* Corpo do card clicável */}
          <TouchableOpacity 
            style={styles.appointmentCardBody}
            activeOpacity={0.7}
            onPress={handleNavigateToDetails}
          >
            <View style={{ flex: 1, paddingRight: 8 }}>
              <Text style={[styles.appointmentPurposeLabel, { color: colors.mutedText }]}>Procedimento / Motivo</Text>
              <Text style={[styles.appointmentPurposeValue, { color: colors.text }]}>{appointmentMotivo}</Text>
            </View>
            <View style={[styles.arrowCircle, { backgroundColor: isDarkMode ? '#334155' : '#EFF6FF' }]}>
              <Feather name="chevron-right" size={20} color={colors.brandBlue} />
            </View>
          </TouchableOpacity>

          {/* Linha Divisória interna elegante */}
          <View style={[styles.cardInternalDivider, { backgroundColor: colors.border }]} />

          {/* BOTÃO: Aciona diretamente os detalhes do agendamento */}
          <TouchableOpacity 
            style={[styles.detailsActionButton, { backgroundColor: isDarkMode ? '#1E3A8A' : '#EFF6FF', borderColor: isDarkMode ? '#2563EB' : '#BFDBFE' }]} 
            onPress={handleNavigateToDetails}
            activeOpacity={0.7}
          >
            <Feather name="file-text" size={15} color={isDarkMode ? '#60A5FA' : '#163783'} style={{ marginRight: 8 }} />
            <Text style={[styles.detailsActionButtonText, { color: isDarkMode ? '#60A5FA' : '#163783' }]}>Ver Detalhes do Agendamento</Text>
          </TouchableOpacity>
        </View>

      </ScrollView>
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
  scrollContent: {
    paddingHorizontal: 24,
    paddingBottom: 40,
  },
  profileCard: {
    alignItems: 'center',
    borderRadius: 20,
    padding: 24,
    marginTop: 20,
    marginBottom: 24,
    borderWidth: 1,
  },
  avatarWrapper: {
    position: 'relative',
    marginBottom: 16,
  },
  avatarBig: {
    width: 110,
    height: 110,
    borderRadius: 55,
    borderWidth: 3,
  },
  activeBadge: {
    position: 'absolute',
    bottom: 4,
    right: 4,
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: '#22C55E',
    borderWidth: 3,
  },
  patientNameText: {
    fontSize: 22,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: 4,
  },
  cpfText: {
    fontSize: 13,
    fontWeight: '600',
    letterSpacing: 0.5,
    marginBottom: 6,
  },
  subInfoText: {
    fontSize: 14,
    fontWeight: '500',
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 12,
  },
  infoContainerBox: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    marginBottom: 24,
  },
  contactRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 4,
  },
  iconBox: {
    width: 40,
    height: 40,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  contactTextContainer: {
    flex: 1,
  },
  contactLabel: {
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  contactValue: {
    fontSize: 15,
    fontWeight: '600',
  },
  divider: {
    height: 1,
    marginVertical: 12,
  },
  appointmentCard: {
    borderRadius: 16,
    padding: 16,
    borderWidth: 1.5,
    marginBottom: 20,
  },
  appointmentBadgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
  },
  dateBadgeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    marginRight: 8,
  },
  dateBadgeText: {
    fontSize: 13,
    fontWeight: '700',
  },
  timeBadgeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 6,
    borderRadius: 8,
  },
  timeBadgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  statusBadge: {
    marginLeft: 'auto',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusBadgeText: {
    fontSize: 11,
    fontWeight: '700',
  },
  appointmentCardBody: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  appointmentPurposeLabel: {
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  appointmentPurposeValue: {
    fontSize: 16,
    fontWeight: '700',
  },
  arrowCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardInternalDivider: {
    height: 1,
    marginVertical: 14,
  },
  detailsActionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 44,
    borderRadius: 12,
    borderWidth: 1,
  },
  detailsActionButtonText: {
    fontSize: 14,
    fontWeight: '700',
  },
});