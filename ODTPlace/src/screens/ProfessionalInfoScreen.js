import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, TouchableOpacity, ImageBackground, ScrollView } from 'react-native';
import ScheduleHeader from '../components/ScheduleHeader';
import BottomNavBar from '../components/BottomNavBar';

export default function ProfessionalInfoScreen({ route, navigation }) {
  const professional = route?.params?.professional ?? {};
  const [showFullDescription, setShowFullDescription] = useState(false);

  const description = professional.description ||
    'Profissional experiente com dedicação à qualidade do atendimento e ao conforto do paciente. Sempre em busca de atualizações para oferecer os melhores procedimentos e resultados.';
  const isLongDescription = description.length > 140;
  const displayedDescription = !showFullDescription && isLongDescription
    ? `${description.slice(0, 140).trim()}...`
    : description;

  return (
    <ImageBackground
      source={require('../../assets/imagem background.png')}
      style={styles.pageBackground}
      resizeMode="cover"
    >
      <SafeAreaView style={styles.container}>
        <ScheduleHeader title="Sobre o Profissional" onBack={() => navigation.goBack()} />

        <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
          <View style={styles.profileHeader}>
            <View style={styles.profileImage}>
              <Text style={styles.profileInitial}>{professional.name ? professional.name.charAt(0) : 'P'}</Text>
            </View>
            <Text style={styles.professionalName}>{professional.name ?? 'Nome do Profissional'}</Text>
            <Text style={styles.professionalSpecialty}>{professional.specialty ?? 'Especialidade'}</Text>
          </View>

          <View style={styles.metricRow}>
            <View style={styles.metricCard}>
              <Text style={styles.metricValue}>{professional.patients ?? 150}+</Text>
              <Text style={styles.metricLabel}>Pacientes</Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricValue}>{professional.experience ?? '3 anos'}</Text>
              <Text style={styles.metricLabel}>Experiência</Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricValue}>{professional.reviews ?? 120}</Text>
              <Text style={styles.metricLabel}>Avaliações</Text>
            </View>
          </View>

          <View style={styles.sectionBlock}>
            <Text style={styles.sectionTitle}>Sobre Dentista</Text>
            <Text style={styles.sectionText}>{displayedDescription}</Text>
            {isLongDescription ? (
              <TouchableOpacity onPress={() => setShowFullDescription(prev => !prev)}>
                <Text style={styles.moreText}>{showFullDescription ? 'Menos' : 'Mais'}</Text>
              </TouchableOpacity>
            ) : null}
          </View>

          <View style={styles.sectionBlock}>
            <Text style={styles.sectionTitle}>Horário de Trabalho</Text>
            <Text style={styles.sectionText}>{professional.hours ?? 'Seg - Sab (08:00 AM as 18:30 PM)'}</Text>
          </View>

          <TouchableOpacity
            style={styles.bookButton}
            activeOpacity={0.85}
            onPress={() => navigation.navigate('AppointmentBooking', { professional })}
          >
            <Text style={styles.bookButtonText}>Agendar</Text>
          </TouchableOpacity>
        </ScrollView>

        <BottomNavBar
          activeTab="home"
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
    paddingBottom: 140,
  },
  profileHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  profileImage: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#eef8ff',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 18,
    borderWidth: 2,
    borderColor: '#dbeafe',
  },
  profileInitial: {
    fontSize: 36,
    fontWeight: '800',
    color: '#0ea5e9',
  },
  professionalName: {
    fontSize: 22,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 6,
    textAlign: 'center',
  },
  professionalSpecialty: {
    fontSize: 16,
    color: '#0ea5e9',
    fontWeight: '700',
    textAlign: 'center',
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  metricCard: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 24,
    paddingVertical: 18,
    paddingHorizontal: 12,
    marginHorizontal: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 6 },
    shadowRadius: 16,
    elevation: 6,
  },
  metricValue: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 6,
  },
  metricLabel: {
    fontSize: 12,
    color: '#94a3b8',
    textAlign: 'center',
  },
  sectionBlock: {
    backgroundColor: '#ffffff',
    borderRadius: 28,
    padding: 20,
    marginBottom: 18,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 6 },
    shadowRadius: 14,
    elevation: 6,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: 10,
  },
  sectionText: {
    fontSize: 14,
    lineHeight: 22,
    color: '#475569',
  },
  moreText: {
    color: '#0ea5e9',
    fontWeight: '700',
    marginTop: 10,
  },
  bookButton: {
    backgroundColor: '#0ea5e9',
    borderRadius: 24,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 6,
  },
  bookButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
});