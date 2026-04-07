import { useState } from 'react';
import {
    View,
    Text,
    FlatList,
    StyleSheet,
    TextInput,
    TouchableOpacity,
    SafeAreaView,
} from 'react-native';
import CustomButton from '../components/CustomButton';

export default function HomeScreen() {
    const [search, setSearch] = useState('');
    const [clinicas, setClinicas] = useState([
        {
            id: '1',
            nome: 'Clínica Sorriso Vivo',
            especialidade: 'Odontologia',
            avaliacao: '5.0',
            avaliacoes: '83',
            preco: 'R$ 250,00',
            modalidades: 'Online',
            dia: 'Terça 14 - Dezembro',
            horarios: ['11:00', '12:00'],
        },
    ]);

    const dadosFiltrados = clinicas.filter((clinica) =>
        clinica.nome.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.header}>
                <View>
                    <Text style={styles.welcomeTitle}>Bem-vindo,</Text>
                    <Text style={styles.welcomeName}>Gabriel Gomes</Text>
                </View>

                <TouchableOpacity style={styles.bellButton}>
                    <Text style={styles.bellText}>🔔</Text>
                </TouchableOpacity>
            </View>

            <Text style={styles.subtitle}>Em busca de uma Clínica ?</Text>

            <View style={styles.searchBox}>
                <Text style={styles.searchIcon}>🔍</Text>
                <TextInput
                    value={search}
                    onChangeText={setSearch}
                    placeholder="Pesquise aqui"
                    placeholderTextColor="#9ca3af"
                    style={styles.searchInput}
                />
                <TouchableOpacity style={styles.filterButton}>
                    <Text style={styles.filterText}>⌗</Text>
                </TouchableOpacity>
            </View>

            <Text style={styles.sectionTitle}>Clinicas Disponíveis</Text>

            <FlatList
                data={dadosFiltrados}
                keyExtractor={(item) => item.id}
                showsVerticalScrollIndicator={false}
                contentContainerStyle={styles.listContent}
                renderItem={({ item }) => (
                    <View style={styles.card}>
                        <View style={styles.cardHeader}>
                            <View style={styles.clinicInfo}>
                                <Text style={styles.clinicName}>{item.nome}</Text>
                                <Text style={styles.clinicSpecialty}>{item.especialidade}</Text>
                            </View>
                            <View style={styles.rating}>
                                <Text style={styles.ratingValue}>{item.avaliacao}</Text>
                                <Text style={styles.ratingCount}>{item.avaliacoes} avaliações</Text>
                            </View>
                        </View>

                        <Text style={styles.paymentText}>Forma de pagamento: {item.modalidades}</Text>
                        <Text style={styles.priceText}>Consulta: {item.preco}</Text>

                        <Text style={styles.scheduleTitle}>{item.dia}</Text>

                        <View style={styles.hours}>
                            {item.horarios.map((hora) => (
                                <View key={hora} style={styles.hourBadge}>
                                    <Text style={styles.hourText}>{hora}</Text>
                                </View>
                            ))}
                        </View>

                        <CustomButton
                            title="Ver mais"
                            onPress={() => alert(`Você clicou em ${item.nome}`)}
                        />
                    </View>
                )}
            />
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f3f6fb',
        paddingHorizontal: 20,
    },
    header: {
        marginTop: 24,
        marginBottom: 20,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    welcomeTitle: {
        color: '#0f172a',
        fontSize: 18,
    },
    welcomeName: {
        color: '#0ea5e9',
        fontSize: 24,
        fontWeight: '800',
        marginTop: 4,
    },
    bellButton: {
        width: 40,
        height: 40,
        borderRadius: 12,
        backgroundColor: '#ffffff',
        alignItems: 'center',
        justifyContent: 'center',
        shadowColor: '#000',
        shadowOpacity: 0.08,
        shadowOffset: { width: 0, height: 2 },
        shadowRadius: 4,
        elevation: 3,
    },
    bellText: {
        fontSize: 18,
    },
    subtitle: {
        fontSize: 20,
        fontWeight: '700',
        color: '#0f172a',
        marginBottom: 16,
    },
    searchBox: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#ffffff',
        borderRadius: 16,
        paddingHorizontal: 14,
        paddingVertical: 10,
        shadowColor: '#000',
        shadowOpacity: 0.05,
        shadowOffset: { width: 0, height: 1 },
        shadowRadius: 2,
        elevation: 2,
        marginBottom: 20,
    },
    searchIcon: {
        fontSize: 18,
        marginRight: 10,
    },
    searchInput: {
        flex: 1,
        color: '#0f172a',
        fontSize: 16,
    },
    filterButton: {
        width: 36,
        height: 36,
        borderRadius: 12,
        backgroundColor: '#eef2ff',
        alignItems: 'center',
        justifyContent: 'center',
    },
    filterText: {
        fontSize: 18,
        color: '#2563eb',
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: '600',
        color: '#334155',
        marginBottom: 12,
    },
    listContent: {
        paddingBottom: 20,
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
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 12,
    },
    clinicInfo: {
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
        color: '#2563eb',
    },
    rating: {
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
        gap: 10,
        marginBottom: 16,
    },
    hourBadge: {
        backgroundColor: '#cffafe',
        borderRadius: 12,
        paddingVertical: 8,
        paddingHorizontal: 12,
    },
    hourText: {
        color: '#0c4a6e',
        fontSize: 13,
    },
});