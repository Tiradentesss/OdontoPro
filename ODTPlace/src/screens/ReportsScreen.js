import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { useTheme } from '../components/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { getDoctorById, getDoctorStats, getProfessionalAppointments } from '../services/api';

export default function ReportsScreen() {
  const { colors } = useTheme();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ completed_consultations: 0, positive_reviews: 0 });
  const [doctorProfile, setDoctorProfile] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [period, setPeriod] = useState('all');

  const loadData = useCallback(async () => {
    if (!user?.id) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const doctorStatsResult = await getDoctorStats(user.id);
      setStats(doctorStatsResult || { completed_consultations: 0, positive_reviews: 0 });

      try {
        const doctorProfileResult = await getDoctorById(user.id);
        setDoctorProfile(doctorProfileResult || null);
      } catch (profileErr) {
        console.log('Reports profile load error:', profileErr);
        setDoctorProfile(null);
      }

      const appointmentsResult = await getProfessionalAppointments({ medico_id: user.id });
      setAppointments(Array.isArray(appointmentsResult) ? appointmentsResult : []);
    } catch (err) {
      console.log('Reports load error:', err);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const filteredAppointments = useMemo(() => {
    if (period === 'all') return appointments;

    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - (period === 'week' ? 7 : 30));

    return appointments.filter((appointment) => {
      if (!appointment?.data_hora) return false;
      return new Date(appointment.data_hora) >= cutoff;
    });
  }, [appointments, period]);

  const upcomingCount = filteredAppointments.filter((appointment) => new Date(appointment.data_hora) > new Date()).length;
  const cancelledCount = filteredAppointments.filter((appointment) =>
    (appointment.status || '').toString().toLowerCase().includes('cancel')
  ).length;
  const completedCount = filteredAppointments.filter((appointment) => {
    const status = (appointment.status || '').toString().toLowerCase();
    return ['confirmada', 'confirmado', 'realizada', 'completa', 'done'].includes(status);
  }).length;

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}> 
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <Text style={[styles.title, { color: colors.text }]}>Relatórios</Text>

        <View style={styles.periodRow}>
          {['all', 'month', 'week'].map((item) => {
            const label = item === 'all' ? 'Todos' : item === 'month' ? 'Mês' : 'Semana';
            const active = period === item;
            return (
              <TouchableOpacity
                key={item}
                onPress={() => setPeriod(item)}
                style={[styles.periodChip, { backgroundColor: active ? colors.brandBlue : colors.card }]}
              >
                <Text style={{ color: active ? '#fff' : colors.text, fontWeight: '700' }}>{label}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.brandBlue} />
          </View>
        ) : (
          <>
            <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}> 
              <Text style={[styles.cardTitle, { color: colors.text }]}>Consultas concluídas</Text>
              <Text style={[styles.cardValue, { color: colors.text }]}>{completedCount}</Text>
            </View>

            <View style={styles.row}>
              <View style={[styles.smallCard, { backgroundColor: colors.card, borderColor: colors.border }]}> 
                <Text style={[styles.smallTitle, { color: colors.text }]}>Avaliação geral</Text>
                <Text style={[styles.smallValue, { color: colors.text }]}>
                  {doctorProfile?.avaliacao || stats.positive_reviews ? Number(doctorProfile?.avaliacao ?? stats.positive_reviews).toFixed(1) : '0.0'}
                </Text>
              </View>

              <View style={[styles.smallCard, styles.smallCardLast, { backgroundColor: colors.card, borderColor: colors.border }]}> 
                <Text style={[styles.smallTitle, { color: colors.text }]}>Próximas consultas</Text>
                <Text style={[styles.smallValue, { color: colors.text }]}>{upcomingCount}</Text>
              </View>
            </View>

            <View style={[styles.section, { backgroundColor: colors.card, borderColor: colors.border }]}> 
              <Text style={[styles.sectionTitle, { color: colors.text }]}>Resumo de status</Text>
              <View style={styles.statusRow}>
                <Text style={[styles.statusLabel, { color: colors.text }]}>Canceladas</Text>
                <Text style={[styles.statusValue, { color: colors.text }]}>{cancelledCount}</Text>
              </View>
            </View>

            <TouchableOpacity
              style={[styles.refreshButton, { backgroundColor: colors.brandBlue }]}
              onPress={() => loadData()}
            >
              <Text style={styles.refreshText}>Atualizar</Text>
            </TouchableOpacity>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 20, paddingBottom: 120 },
  title: { fontSize: 22, fontWeight: '800', marginBottom: 12 },
  periodRow: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 12 },
  periodChip: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    marginRight: 8,
    marginBottom: 8,
  },
  center: { padding: 40, alignItems: 'center' },
  card: { borderRadius: 16, padding: 18, borderWidth: 1, marginBottom: 12 },
  cardTitle: { fontSize: 13, fontWeight: '700', marginBottom: 8 },
  cardValue: { fontSize: 28, fontWeight: '800' },
  row: { flexDirection: 'row', justifyContent: 'space-between', flexWrap: 'wrap', marginTop: 8 },
  smallCard: {
    flexBasis: '48%',
    flexGrow: 1,
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    marginRight: 8,
    marginBottom: 8,
    minWidth: 0,
  },
  smallCardLast: { marginRight: 0 },
  smallTitle: { fontSize: 12, fontWeight: '700', marginBottom: 6 },
  smallValue: { fontSize: 20, fontWeight: '800' },
  section: { borderRadius: 12, padding: 12, borderWidth: 1, marginTop: 10 },
  sectionTitle: { fontSize: 14, fontWeight: '700', marginBottom: 8 },
  statusRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6 },
  statusLabel: { fontSize: 13, fontWeight: '600' },
  statusValue: { fontSize: 13, fontWeight: '800' },
  refreshButton: { marginTop: 20, paddingVertical: 14, borderRadius: 12, alignItems: 'center' },
  refreshText: { color: '#fff', fontWeight: '800' },
});
