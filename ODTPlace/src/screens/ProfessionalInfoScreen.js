import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, SafeAreaView, TouchableOpacity, ImageBackground, ScrollView } from 'react-native';
import ScheduleHeader from '../components/ScheduleHeader';
import BottomNavBar from '../components/BottomNavBar';
import { getDoctorById, getDoctorStats, getProfessionalAppointments } from '../services/api';

export default function ProfessionalInfoScreen({ route, navigation }) {
  const professional = route?.params?.professional ?? {};
  const clinic = route?.params?.clinic ?? {};
  const user = route?.params?.user;
  const [showFullDescription, setShowFullDescription] = useState(false);
  const [completedConsultations, setCompletedConsultations] = useState(null);
  const [doctorProfile, setDoctorProfile] = useState(null);

  useEffect(() => {
    const loadStats = async () => {
      try {
        if (professional?.id) {
          try {
            const doctorData = await getDoctorById(professional.id);
            setDoctorProfile(doctorData || null);
          } catch (profileErr) {
            console.log('Failed to load doctor profile:', profileErr);
            setDoctorProfile(null);
          }

          const stats = await getDoctorStats(professional.id);
          const completed = stats.completed_consultations ?? 0;
          setCompletedConsultations(completed);

          // If stats are zero (or missing), try to fetch appointments and count completed ones as fallback
          if ((completed === 0) && professional?.id) {
            try {
              const appts = await getProfessionalAppointments({ medico_id: professional.id });
              const completedCount = Array.isArray(appts)
                ? appts.filter(a => {
                    const st = (a.status || '').toString().toLowerCase();
                    return ['realizada', 'completa', 'confirmada', 'confirmado'].includes(st);
                  }).length
                : 0;
              if (completedCount > 0) setCompletedConsultations(completedCount);
            } catch (err) {
              // ignore fallback errors — keep zeros
            }
          }
        }
      } catch (err) {
        console.log('Failed to load doctor stats:', err);
      }
    };
    loadStats();
  }, [professional?.id]);

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
            <Text style={styles.professionalName}>{professional.nome ?? professional.name ?? 'Nome do Profissional'}</Text>
            <Text style={styles.professionalSpecialty}>{professional.specialty ?? professional.especialidades?.[0] ?? 'Especialidade'}</Text>
          </View>

          <View style={styles.metricRow}>
            <View style={styles.metricCard}>
              <Text style={styles.metricValue}>{completedConsultations ?? professional.patients ?? 0}</Text>
              <Text style={styles.metricLabel}>Pacientes</Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricValue}>{doctorProfile?.avaliacao ?? professional?.avaliacao ?? professional?.rating ?? '—'} ★</Text>
              <Text style={styles.metricLabel}>{(doctorProfile?.num_avaliacoes ?? professional?.num_avaliacoes ?? professional?.avaliacoes ?? professional?.reviews ?? 0)} avaliações</Text>
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
            <Text style={styles.sectionTitle}>Horários de Atendimento</Text>
            <Text style={styles.sectionText}>{(clinic.horarios && clinic.horarios.join ? clinic.horarios.join(' • ') : (clinic.horarios || clinic.horario || professional.hours || 'Seg - Sab (08:00 - 18:30)'))}</Text>
          </View>

          <TouchableOpacity
            style={styles.bookButton}
            activeOpacity={0.85}
            onPress={() => navigation.navigate('AppointmentBooking', { professional, clinic, user, selectedSpecialty: route?.params?.selectedSpecialty })}
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