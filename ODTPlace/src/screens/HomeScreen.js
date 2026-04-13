import { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, FlatList, ImageBackground } from 'react-native';
import HomeHeader from '../components/HomeHeader';
import BottomNavBar from '../components/BottomNavBar';

export default function HomeScreen({ route, navigation }) {
    const usuario = route?.params?.userName ?? 'Paciente';
    const [search, setSearch] = useState('');
    const [clinicas] = useState([
        {
            id: '1',
            nome: 'Clínica Sorriso Vivo',
            descricao: 'Clínica com equipamentos modernos e equipe preparada para resolver seu caso.',
            especialidade: 'Odontologia',
            avaliacao: '5.0',
            avaliacoes: '83',
            preco: 'R$ 250,00',
            modalidades: 'Online',
            dia: 'Terça 14 - Dezembro',
            horarios: ['11:00', '12:00'],
            services: [
                {
                    name: 'Ortodontia',
                    price: 'R$ 280,00',
                    availability: ['Ter. 14 - Dez • 08:00', 'Qua. 15 - Dez • 09:00'],
                },
                {
                    name: 'Odontopediatria',
                    price: 'R$ 170,00',
                    availability: ['Ter. 14 - Dez • 10:30', 'Qui. 16 - Dez • 11:00'],
                },
                {
                    name: 'Periodontia',
                    price: 'R$ 210,00',
                    availability: ['Qua. 15 - Dez • 14:00', 'Sex. 17 - Dez • 15:30'],
                },
            ],
        },
    ]);

    const dadosFiltrados = clinicas.filter((clinica) =>
        clinica.nome.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            resizeMode="cover"
        >
            <SafeAreaView style={styles.container}>
                <HomeHeader
                    usuario={usuario}
                    search={search}
                    setSearch={setSearch}
                    onBellPress={() => {}}
                    onFilterPress={() => {}}
                />

                <FlatList
                    data={dadosFiltrados}
                    keyExtractor={(item) => item.id}
                    showsVerticalScrollIndicator={false}
                    contentContainerStyle={styles.listContent}
                    renderItem={({ item }) => (
                        <TouchableOpacity
                            style={styles.card}
                            activeOpacity={0.85}
                            onPress={() => navigation.navigate('ClinicDetail', { clinic: item })}
                        >
                            <View style={styles.cardHeader}>
                                <View style={styles.clinicLogo} />

                                <View style={styles.infoBlock}>
                                    <Text style={styles.clinicName}>{item.nome}</Text>
                                    <Text style={styles.clinicSpecialty}>{item.especialidade}</Text>
                                </View>

                                <View style={styles.ratingBox}>
                                    <Text style={styles.ratingValue}>{item.avaliacao}</Text>
                                    <Text style={styles.ratingCount}>{item.avaliacoes} avaliações</Text>
                                </View>
                            </View>

                            <Text style={styles.paymentText}>
                                Forma de pagamento: {item.modalidades}
                            </Text>
                            <Text style={styles.priceText}>Consulta: {item.preco}</Text>

                            <Text style={styles.scheduleTitle}>{item.dia}</Text>

                            <View style={styles.hours}>
                                {item.horarios.map((hora, index) => (
                                    <View
                                        key={hora}
                                        style={[
                                            styles.hourBadge,
                                            index < item.horarios.length - 1 && styles.hourMargin,
                                        ]}
                                    >
                                        <Text style={styles.hourText}>{hora}</Text>
                                    </View>
                                ))}
                            </View>
                        </TouchableOpacity>
                    )}
                    ListEmptyComponent={
                        <Text style={styles.emptyText}>Nenhuma clínica encontrada.</Text>
                    }
                />

                <BottomNavBar
                    activeTab="home"
                    onTabPress={(tab) => {
                        if (tab === 'schedule') {
                            navigation.navigate('Schedule');
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
    },
    listContent: {
        paddingBottom: 220,
        paddingHorizontal: 20,
        paddingTop: 14,
    },
    actionRow: {
        flexDirection: 'row',
        paddingHorizontal: 20,
        marginTop: 20,
        marginBottom: 6,
    },
    card: {
        backgroundColor: '#ffffff',
        borderRadius: 24,
        padding: 18,
        marginBottom: 16,
        shadowColor: '#000',
        shadowOpacity: 0.06,
        shadowOffset: { width: 0, height: 4 },
        shadowRadius: 10,
        elevation: 4,
    },
    cardHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 14,
    },
    clinicLogo: {
        width: 58,
        height: 58,
        borderRadius: 16,
        backgroundColor: '#e0f2fe',
        marginRight: 14,
    },
    infoBlock: {
        flex: 1,
        paddingRight: 10,
    },
    clinicName: {
        fontSize: 16,
        fontWeight: '700',
        color: '#0f172a',
        marginBottom: 4,
    },
    clinicSpecialty: {
        fontSize: 14,
        color: '#0ea5e9',
    },
    ratingBox: {
        alignItems: 'flex-end',
    },
    ratingValue: {
        fontSize: 16,
        fontWeight: '700',
        color: '#0f172a',
    },
    ratingCount: {
        fontSize: 12,
        color: '#64748b',
    },
    paymentText: {
        fontSize: 13,
        color: '#475569',
        marginBottom: 4,
    },
    priceText: {
        fontSize: 13,
        color: '#475569',
        marginBottom: 12,
    },
    scheduleTitle: {
        fontSize: 14,
        fontWeight: '600',
        color: '#0f172a',
        marginBottom: 10,
    },
    hours: {
        flexDirection: 'row',
        marginBottom: 4,
    },
    hourBadge: {
        backgroundColor: '#dbeafe',
        borderRadius: 12,
        paddingVertical: 8,
        paddingHorizontal: 12,
    },
    hourMargin: {
        marginRight: 10,
    },
    hourText: {
        color: '#0369a1',
        fontSize: 13,
    },
    emptyText: {
        textAlign: 'center',
        color: '#64748b',
        marginTop: 20,
    },
});