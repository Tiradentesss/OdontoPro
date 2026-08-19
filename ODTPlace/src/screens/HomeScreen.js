import { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, FlatList, ImageBackground, ActivityIndicator, Image } from 'react-native';
import HomeHeader from '../components/HomeHeader';
import BottomNavBar from '../components/BottomNavBar';
import { getClinics } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../components/ThemeContext';

const resolveClinicRating = (clinic) => {
    const value = clinic?.avaliacao ?? clinic?.rating ?? clinic?.media_avaliacao ?? clinic?.avaliacao_media;
    const rating = Number(value);
    return Number.isFinite(rating) && rating > 0 ? rating.toFixed(1) : '—';
};

const resolveClinicReviewCount = (clinic) => {
    const value = clinic?.num_avaliacoes ?? clinic?.avaliacoes ?? clinic?.total_avaliacoes ?? clinic?.review_count;
    const count = Number(value);
    return Number.isFinite(count) && count >= 0 ? count : 0;
};

export default function HomeScreen({ route, navigation, showBottomNav = true }) {
    const { user } = useAuth();
    const { isDarkMode, colors } = useTheme();
    const usuario = user?.nome ?? 'Paciente';
    const [search, setSearch] = useState('');
    const [clinicas, setClinicas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadClinicas = async () => {
            try {
                const data = await getClinics();
                setClinicas(data);
                setError(null);
            } catch (err) {
                setError('Não foi possível carregar as clínicas.');
            } finally {
                setLoading(false);
            }
        };

        loadClinicas();
    }, []);

    const dadosFiltrados = clinicas.filter((clinica) =>
        clinica.nome?.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            imageStyle={!isDarkMode ? { transform: [{ scale: 1.2 }] } : undefined}
            resizeMode="cover"
        >
            <SafeAreaView style={[styles.container, { backgroundColor: isDarkMode ? colors.container : 'transparent' }]}> 
                <HomeHeader
                    usuario={usuario}
                    search={search}
                    setSearch={setSearch}
                    onBellPress={() => navigation.navigate('Notifications')}
                    onFilterPress={() => {}}
                />

                {loading ? (
                    <View style={styles.loadingContainer}>
                        <ActivityIndicator size="large" color={isDarkMode ? '#38BDF8' : '#0EA5E9'} />
                        <Text style={[styles.loadingText, { color: isDarkMode ? '#E2E8F0' : '#0F172A' }]}>Carregando clínicas...</Text>
                    </View>
                ) : (
                    <FlatList
                    key="home-flatlist"
                    data={dadosFiltrados}
                    keyExtractor={(item) => String(item.id)}
                    showsVerticalScrollIndicator={false}
                    contentContainerStyle={styles.listContent}
                    renderItem={({ item }) => (
                        <TouchableOpacity
                        style={[styles.card, { backgroundColor: isDarkMode ? '#1E293B' : '#FFFFFF', borderColor: isDarkMode ? '#334155' : '#E2E8F0' }]}
                        activeOpacity={0.85}
                        onPress={() => navigation.navigate('ClinicDetail', { clinic: item, user })}
                        >
                                <View style={styles.cardHeader}>
                                        {item.logo || item.imagem ? (
                                            <Image
                                                source={{ uri: item.logo || item.imagem }}
                                                style={styles.clinicLogoImage}
                                                resizeMode="cover"
                                            />
                                        ) : (
                                            <View style={styles.clinicLogo} />
                                        )}

                                    <View style={styles.infoBlock}>
                                        <Text style={[styles.clinicName, { color: isDarkMode ? '#F8FAFC' : '#0F172A' }]}>{item.nome}</Text>
                                        {item.descricao ? (
                                            <Text style={[styles.clinicSpecialty, { marginTop: 6, color: isDarkMode ? '#94A3B8' : '#64748B' }]} numberOfLines={2}>{item.descricao}</Text>
                                        ) : null}
                                    </View>

                                    <View style={styles.ratingBox}>
                                        <Text style={[styles.ratingValue, { color: isDarkMode ? '#F8FAFC' : '#0F172A' }]}>{resolveClinicRating(item)} ★</Text>
                                        <Text style={[styles.ratingCount, { color: isDarkMode ? '#94A3B8' : '#64748B' }]}>{resolveClinicReviewCount(item)} avaliações</Text>
                                    </View>
                                </View>
                            </TouchableOpacity>
                        )}
                        ListEmptyComponent={
                            <Text style={[styles.emptyText, { color: isDarkMode ? '#94A3B8' : '#64748B' }]}>{error ?? 'Nenhuma clínica encontrada.'}</Text>
                        }
                    />
                )}

                {showBottomNav && (
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
                )}
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
        alignItems: 'flex-start',
    },
    clinicLogo: {
        width: 58,
        height: 58,
        borderRadius: 16,
        backgroundColor: '#e0f2fe',
        marginRight: 14,
    },
    clinicLogoImage: {
        width: 58,
        height: 58,
        borderRadius: 16,
        marginRight: 14,
        backgroundColor: '#e0f2fe',
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
    clinicName: {
        fontSize: 16,
        fontWeight: '700',
        color: '#0f172a',
        marginBottom: 6,
    },
    clinicSpecialty: {
        fontSize: 13,
        color: '#64748b',
    },
    ratingBox: {
        alignItems: 'flex-end',
    },
    ratingBox: {
        alignItems: 'flex-end',
        marginLeft: 8,
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