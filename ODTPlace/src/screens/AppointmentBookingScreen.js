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
} from 'react-native';
import ScheduleHeader from '../components/ScheduleHeader';
import BottomNavBar from '../components/BottomNavBar';

export default function AppointmentBookingScreen({ route, navigation }) {
  const professional = route?.params?.professional ?? {};
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [reason, setReason] = useState('');
  const [selectedSlot, setSelectedSlot] = useState('Janeiro - 02 - 2024 - 09:00AM');
  const [confirmationVisible, setConfirmationVisible] = useState(false);

  const handleSlotPress = () => {
    const options = [
      'Janeiro - 02 - 2024 - 09:00AM',
      'Janeiro - 02 - 2024 - 10:30AM',
      'Janeiro - 02 - 2024 - 14:00PM',
    ];
    const currentIndex = options.indexOf(selectedSlot);
    const nextIndex = (currentIndex + 1) % options.length;
    setSelectedSlot(options[nextIndex]);
  };

  const handleConfirmBooking = () => {
    setConfirmationVisible(true);
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
            <Text style={styles.headerTitle}>{professional.name ?? 'Dr. Nome Sobrenome'}</Text>
            <Text style={styles.headerSubtitle}>{professional.specialty ?? 'Especialidade'}</Text>
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.fieldLabel}>Primeiro Nome</Text>
            <TextInput
              style={styles.input}
              placeholder="Primeiro Nome"
              placeholderTextColor="#9ca3af"
              value={firstName}
              onChangeText={setFirstName}
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.fieldLabel}>Sobrenome</Text>
            <TextInput
              style={styles.input}
              placeholder="Sobrenome"
              placeholderTextColor="#9ca3af"
              value={lastName}
              onChangeText={setLastName}
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
            <Text style={styles.slotHelp}>Toque para alternar entre os horários disponíveis.</Text>
          </View>

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
                  <Text style={styles.confirmationProfileInitial}>{professional.name ? professional.name.charAt(0) : 'P'}</Text>
                </View>
                <Text style={styles.confirmationProfileName}>{professional.name ?? 'Dr. Nome Sobrenome'}</Text>
                <Text style={styles.confirmationProfileSpecialty}>{professional.specialty ?? 'Especialidade'}</Text>
              </View>

              <View style={styles.confirmationDetailsRow}>
                <Text style={styles.confirmationDetailText}>Terça, 14 de Dezembro</Text>
                <View style={styles.confirmationSeparator} />
                <Text style={styles.confirmationDetailText}>9:00 AM</Text>
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
