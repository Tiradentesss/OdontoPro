import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  FlatList,
  Image,
  ScrollView,
} from 'react-native';

import HomeHeader from '../components/HomeHeaderP';
import BottomNavBar from '../components/BottomNavBar';

export default function HomeProfissional({ route, navigation }) {
  const usuario = route?.params?.userName ?? 'Profissional';

  const [search, setSearch] = useState('');

  const pacientes = [
    {
      id: '1',
      nome: 'Alex Batista',
      consulta: 'Presencial',
      convenio: 'Particular',
      imagem:
        'https://randomuser.me/api/portraits/men/32.jpg',
    },
    {
      id: '2',
      nome: 'Eduarda Maria',
      consulta: 'Online',
      convenio: 'Amil',
      imagem:
        'https://randomuser.me/api/portraits/women/44.jpg',
    },
    {
      id: '3',
      nome: 'Hugo Pontes',
      consulta: 'Presencial',
      convenio: 'Unimed',
      imagem:
        'https://randomuser.me/api/portraits/men/11.jpg',
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <HomeHeader
        usuario={usuario}
        search={search}
        setSearch={setSearch}
        onBellPress={() => navigation.navigate('Notifications')}
        onFilterPress={() => {}}
      />

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.content}
      >
        {/* MÉTRICAS */}
        <View style={styles.metricsRow}>
          <View style={styles.metricCard}>
            <Text style={styles.metricNumber}>50</Text>
            <Text style={styles.metricLabel}>Pacientes</Text>
          </View>

          <View style={styles.metricCard}>
            <Text style={styles.metricNumber}>23</Text>
            <Text style={styles.metricLabel}>Consultas</Text>
          </View>

          <View style={styles.metricCard}>
            <Text style={styles.metricNumber}>92%</Text>
            <Text style={styles.metricLabel}>Avaliação</Text>
          </View>
        </View>

        {/* GRÁFICO */}
        <Text style={styles.sectionTitle}>
          Consultas da Semana
        </Text>

        <View style={styles.graphCard}>
          <View style={styles.fakeGraph}>
            <View style={styles.graphLine} />
          </View>
        </View>

        {/* PACIENTES */}
        <Text style={styles.sectionTitle}>
          Pacientes recentes
        </Text>

        {pacientes.map((item) => (
          <TouchableOpacity
            key={item.id}
            style={styles.patientCard}
            activeOpacity={0.85}
          >
            <Image
              source={{ uri: item.imagem }}
              style={styles.avatar}
            />

            <View style={styles.patientInfo}>
              <Text style={styles.patientName}>
                {item.nome}
              </Text>

              <Text style={styles.patientText}>
                Convênio: {item.convenio}
              </Text>

              <Text style={styles.patientText}>
                Consulta: {item.consulta}
              </Text>
            </View>

            <Text style={styles.more}>⋮</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <BottomNavBar
        activeTab="home"
        onTabPress={(tab) => {
          if (tab === 'schedule') {
            navigation.navigate('Schedule');
          } else if (tab === 'settings') {
            navigation.navigate('Settings');
          } else if (tab === 'notifications') {
            navigation.navigate('Notifications');
          }
        }}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fb',
  },

  content: {
    padding: 20,
    paddingBottom: 140,
  },

  metricsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 28,
  },

  metricCard: {
    width: '31%',
    backgroundColor: '#fff',
    borderRadius: 22,
    paddingVertical: 20,
    alignItems: 'center',

    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 3 },
    shadowRadius: 10,
    elevation: 4,
  },

  metricNumber: {
    fontSize: 24,
    fontWeight: '800',
    color: '#0a247c',
  },

  metricLabel: {
    marginTop: 6,
    color: '#64748b',
    fontSize: 13,
  },

  sectionTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#111827',
    marginBottom: 18,
  },

  graphCard: {
    backgroundColor: '#fff',
    borderRadius: 28,
    padding: 20,
    marginBottom: 30,

    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 10,
    elevation: 4,
  },

  fakeGraph: {
    height: 180,
    justifyContent: 'center',
    alignItems: 'center',
  },

  graphLine: {
    width: '100%',
    height: 6,
    borderRadius: 20,
    backgroundColor: '#1bc4eb',
  },

  patientCard: {
    backgroundColor: '#fff',
    borderRadius: 24,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,

    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 3 },
    shadowRadius: 10,
    elevation: 4,
  },

  avatar: {
    width: 68,
    height: 68,
    borderRadius: 18,
    marginRight: 14,
  },

  patientInfo: {
    flex: 1,
  },

  patientName: {
    fontSize: 18,
    fontWeight: '800',
    color: '#1565d8',
    marginBottom: 4,
  },

  patientText: {
    color: '#333',
    fontSize: 14,
    marginBottom: 2,
  },

  more: {
    fontSize: 26,
    color: '#1565d8',
    marginBottom: 20,
  },
});