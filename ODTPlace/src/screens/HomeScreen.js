import { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TextInput,
    TouchableOpacity,
    SafeAreaView,
    FlatList,
    ImageBackground,
} from 'react-native';

export default function HomeScreen({ route }) {
    const usuario = route?.params?.userName ?? 'Paciente';
    const [search, setSearch] = useState('');
    const [clinicas] = useState([
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
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            resizeMode="cover"
        >
            <SafeAreaView style={styles.container}>
                <View style={styles.topCard}>
                    <View style={styles.topCardContent}>
                        <View style={styles.topHeader}>
                            <View>
                                <Text style={styles.welcomeLabel}>Bem-vindo,</Text>
                                <Text style={styles.welcomeName}>{usuario}</Text>
                            </View>

                            <TouchableOpacity style={styles.bellButton}>
                                <Text style={styles.bellIcon}>🔔</Text>
                            </TouchableOpacity>
                        </View>

                        <View style={styles.searchBox}>
                            <Text style={styles.searchIcon}>🔍</Text>
                            <TextInput
                                value={search}
                                onChangeText={setSearch}
                                placeholder="Pesquise por nomes"
                                placeholderTextColor="#94a3b8"
                                style={styles.searchInput}
                            />
                            <TouchableOpacity style={styles.filterButton}>
                                <Text style={styles.filterText}>⌗</Text>
                            </TouchableOpacity>
                        </View>
                    </View>

                    <View style={styles.sectionBar}>
                        <Text style={styles.sectionBarText}>Clínicas Disponíveis</Text>
                    </View>
                </View>

                <FlatList
                    data={dadosFiltrados}
                    keyExtractor={(item) => item.id}
                    showsVerticalScrollIndicator={false}
                    contentContainerStyle={styles.listContent}
                    renderItem={({ item }) => (
                        <TouchableOpacity
                            style={styles.card}
                            activeOpacity={0.85}
                            onPress={() => alert(`Abrindo ${item.nome}`)}
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

                <View style={styles.bottomBar}>
                    <TouchableOpacity style={styles.bottomTab} activeOpacity={0.85}>
                        <Text style={styles.bottomTabIcon}>🏠</Text>
                        <Text style={styles.bottomTabLabel}>Home</Text>
                    </TouchableOpacity>
                </View>
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
    topCard: {
        marginTop: 24,
        marginHorizontal: -20,
        backgroundColor: '#0ea5e9',
        borderBottomLeftRadius: 32,
        borderBottomRightRadius: 32,
        overflow: 'hidden',
    },
    topCardContent: {
        paddingHorizontal: 24,
        paddingTop: 24,
        paddingBottom: 16,
    },
    topHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 18,
    },
    welcomeLabel: {
        color: '#dbeafe',
        fontSize: 16,
    },
    welcomeName: {
        color: '#ffffff',
        fontSize: 26,
        fontWeight: '800',
        marginTop: 4,
    },
    bellButton: {
        width: 44,
        height: 44,
        borderRadius: 14,
        backgroundColor: '#ffffff',
        alignItems: 'center',
        justifyContent: 'center',
    },
    bellIcon: {
        fontSize: 20,
    },
    searchBox: {
        width: '92%',
        alignSelf: 'center',
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#ffffff',
        borderRadius: 16,
        paddingHorizontal: 14,
        paddingVertical: 10,
    },
    searchIcon: {
        fontSize: 18,
        marginRight: 10,
        color: '#64748b',
    },
    searchInput: {
        flex: 1,
        color: '#0f172a',
        fontSize: 16,
    },
    filterButton: {
        width: 38,
        height: 38,
        borderRadius: 12,
        backgroundColor: '#e0f2fe',
        alignItems: 'center',
        justifyContent: 'center',
    },
    filterText: {
        fontSize: 18,
        color: '#0284c7',
    },
    sectionBar: {
        backgroundColor: '#0b6eb1',
        paddingVertical: 14,
        paddingHorizontal: 20,
    },
    sectionBarText: {
        paddingLeft: 10,
        color: '#ffffff',
        fontSize: 17,
        fontWeight: '700',
    },
    listContent: {
        paddingBottom: 180,
        paddingHorizontal: 20,
        paddingTop: 14,
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
    bottomBar: {
        position: 'absolute',
        left: 20,
        right: 20,
        bottom: 34,
        borderRadius: 28,
        backgroundColor: '#ffffff',
        paddingVertical: 14,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOpacity: 0.16,
        shadowOffset: { width: 0, height: 10 },
        shadowRadius: 20,
        elevation: 16,
        borderTopWidth: 1,
        borderTopColor: '#f8fafc',
    },
    bottomTab: {
        width: 92,
        height: 92,
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#0ea5e9',
        borderRadius: 24,
        paddingVertical: 14,
    },
    bottomTabIcon: {
        fontSize: 24,
        marginBottom: 8,
        color: '#ffffff',
    },
    bottomTabLabel: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '700',
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