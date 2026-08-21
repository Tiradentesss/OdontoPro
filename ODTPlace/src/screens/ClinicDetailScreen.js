import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    SafeAreaView,
    ImageBackground,
    ScrollView,
    TextInput,
    Linking,
    Alert,
    Image,
} from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import * as Clipboard from 'expo-clipboard';
import ScheduleHeader from '../components/ScheduleHeader';
import BottomNavBar from '../components/BottomNavBar';
import { getClinicSpecialties } from '../services/api';
import { useTheme } from '../components/ThemeContext';

const resolveBannerImages = (clinicInfo) => {
    const sourceFromClinic = clinicInfo?.banner || clinicInfo?.banners || clinicInfo?.imagens || clinicInfo?.imagem || clinicInfo?.logo;

    if (Array.isArray(sourceFromClinic)) {
        return sourceFromClinic.filter(Boolean).map((image) => (typeof image === 'string' ? { uri: image } : image));
    }

    if (typeof sourceFromClinic === 'string' && sourceFromClinic.trim()) {
        return [{ uri: sourceFromClinic }];
    }

    if (sourceFromClinic && typeof sourceFromClinic === 'object' && sourceFromClinic.uri) {
        return [sourceFromClinic];
    }

    return [];
};

const resolveClinicAddress = (clinicInfo) => {
    const addressParts = [
        clinicInfo?.rua,
        clinicInfo?.numero,
        clinicInfo?.bairro,
        clinicInfo?.cidade,
        clinicInfo?.estado,
        clinicInfo?.cep,
    ].filter(Boolean);

    if (typeof clinicInfo?.endereco === 'string' && clinicInfo.endereco.trim()) {
        return clinicInfo.endereco.trim();
    }

    return addressParts.length ? addressParts.join(', ') : 'Endereço não informado';
};

const resolveClinicRating = (clinicInfo) => {
    const value = clinicInfo?.avaliacao ?? clinicInfo?.rating ?? clinicInfo?.media_avaliacao ?? clinicInfo?.avaliacao_media;
    const rating = Number(value);
    return Number.isFinite(rating) && rating > 0 ? rating.toFixed(1) : '—';
};

const resolveClinicReviewCount = (clinicInfo) => {
    const value = clinicInfo?.num_avaliacoes ?? clinicInfo?.avaliacoes ?? clinicInfo?.total_avaliacoes ?? clinicInfo?.review_count;
    const count = Number(value);
    return Number.isFinite(count) && count >= 0 ? count : 0;
};

export default function ClinicDetailScreen({ route, navigation }) {
    const clinic = route?.params?.clinic ?? {};
    const user = route?.params?.user;
    const clinicName = String(clinic?.nome ?? 'Clínica');
    const clinicDescription = typeof clinic?.descricao === 'string' ? clinic.descricao : '';
    const clinicPhone = typeof clinic?.telefone === 'string' ? clinic.telefone : '';
    const { isDarkMode, colors } = useTheme();
    const [showFullDescription, setShowFullDescription] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [showAllSpecialties, setShowAllSpecialties] = useState(false);
    const [specialties, setSpecialties] = useState([]);
    const [loadingSpecialties, setLoadingSpecialties] = useState(true);
    const [specialtiesError, setSpecialtiesError] = useState(null);
    const [bannerImages, setBannerImages] = useState(() => resolveBannerImages(clinic));
    const [mapRegion, setMapRegion] = useState(null);
    const clinicAddress = resolveClinicAddress(clinic);

    useEffect(() => {
        setBannerImages(resolveBannerImages(clinic));
    }, [clinic]);

    useEffect(() => {
        const loadSpecialties = async () => {
            if (!clinic.id) {
                setLoadingSpecialties(false);
                return;
            }
            try {
                const data = await getClinicSpecialties(clinic.id);
                setSpecialties(Array.isArray(data) ? data : []);
                setSpecialtiesError(null);
            } catch (error) {
                setSpecialtiesError('Não foi possível carregar especialidades.');
            } finally {
                setLoadingSpecialties(false);
            }
        };

        loadSpecialties();
    }, [clinic.id]);

    useEffect(() => {
        let isMounted = true;

        const geocodeClinic = async () => {
            const addressValue = clinic?.endereco || [clinic?.rua, clinic?.numero, clinic?.bairro, clinic?.cidade, clinic?.estado, clinic?.cep].filter(Boolean).join(', ');
            const queryCep = clinic?.cep?.toString().replace(/[^0-9]/g, '');

            if (!addressValue && !queryCep) {
                setMapRegion(null);
                return;
            }

            try {
                const params = new URLSearchParams({
                    format: 'jsonv2',
                    limit: '1',
                    addressdetails: '1',
                });

                if (queryCep && queryCep.length >= 8) {
                    params.set('postalcode', queryCep);
                    params.set('countrycodes', 'br');
                } else {
                    params.set('q', addressValue);
                }

                const requestUrl = `https://nominatim.openstreetmap.org/search?${params.toString()}`;
                const requestHeaders = {
                    Accept: 'application/json',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                    'User-Agent': 'OdontoPlaceApp/1.0 (contato@odontoplacemed.com)',
                    Referer: 'https://odonto-place.app/',
                };

                const response = await fetch(requestUrl, { method: 'GET', headers: requestHeaders });
                const rawText = await response.text();

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${rawText.slice(0, 180)}`);
                }

                let results;
                try {
                    results = JSON.parse(rawText);
                } catch (parseError) {
                    console.log('Clinic map geocode returned non-JSON response:', rawText.slice(0, 220));
                    return;
                }

                if (!isMounted || !Array.isArray(results) || results.length === 0) {
                    return;
                }

                const firstMatch = results[0];
                if (!firstMatch || typeof firstMatch !== 'object') {
                    return;
                }
                const latitude = Number(firstMatch.lat);
                const longitude = Number(firstMatch.lon);

                if (Number.isFinite(latitude) && Number.isFinite(longitude)) {
                    setMapRegion({
                        latitude,
                        longitude,
                        latitudeDelta: 0.02,
                        longitudeDelta: 0.02,
                    });
                }
            } catch (error) {
                console.log('Clinic map geocode failed:', error);
                if (isMounted) {
                    setMapRegion(null);
                }
            }
        };

        geocodeClinic();

        return () => {
            isMounted = false;
        };
    }, [clinic?.cep, clinic?.rua, clinic?.numero, clinic?.bairro, clinic?.cidade, clinic?.estado, clinic?.endereco]);

    const services = specialties.length > 0
        ? specialties.map((specialty, index) => ({
            name: typeof specialty?.nome === 'string' && specialty.nome.trim() ? specialty.nome.trim() : `Especialidade ${index + 1}`,
            description: specialty?.descricao,
            price: specialty?.preco ?? clinic.preco ?? 'R$ 250,00',
            availability: clinic.horarios ?? ['Ter. 14 - Dez • 08:00', 'Qua. 15 - Dez • 09:00'],
        }))
        : Array.isArray(clinic.services) ? clinic.services.filter(Boolean).map((service, index) => ({
            ...service,
            name: typeof service.name === 'string' && service.name.trim() ? service.name.trim() : `Especialidade ${index + 1}`,
        })) : [
            {
                name: typeof clinic.especialidade === 'string' && clinic.especialidade.trim() ? clinic.especialidade.trim() : 'Especialidade',
                price: clinic.preco ?? 'R$ 250,00',
                availability: ['Ter. 14 - Dez • 08:00', 'Qua. 15 - Dez • 09:00'],
            },
        ];

    const filteredServices = services.filter((item) =>
        String(item?.name ?? '').toLowerCase().startsWith(searchQuery.toLowerCase())
    );

    const visibleServices = showAllSpecialties ? filteredServices : filteredServices.slice(0, 5);
    const hasMoreSpecialties = filteredServices.length > 5;

    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            imageStyle={!isDarkMode ? { transform: [{ scale: 1.2 }] } : undefined}
            resizeMode="cover"
        >
            <SafeAreaView style={[styles.container, { backgroundColor: isDarkMode ? colors.container : 'transparent' }]}> 
                <ScheduleHeader title="Perfil da Clínica" onBack={() => navigation.goBack()} />

                <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
                    <View style={[styles.clinicCard, isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155' }]}> 
                        <View style={styles.clinicHeader}>
                            {(clinic.logo || clinic.imagem) ? (
                                <Image
                                    source={{ uri: clinic.logo || clinic.imagem }}
                                    style={styles.clinicImage}
                                    resizeMode="contain"
                                />
                            ) : (
                                <View style={[styles.clinicImagePlaceholder, isDarkMode && { backgroundColor: '#1E293B' }]}> 
                                    <Text style={[styles.imageLabel, { color: isDarkMode ? '#38BDF8' : '#0ea5e9' }]}>Foto</Text>
                                </View>
                            )}
                            <View style={styles.clinicHeaderInfo}>
                                <Text style={[styles.clinicTitle, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]} numberOfLines={2}>{clinicName}</Text>
                                {clinic.especialidade ? (
                                    <Text style={[styles.clinicSubtitle, { color: isDarkMode ? '#38BDF8' : '#0ea5e9' }]} numberOfLines={1}>{clinic.especialidade}</Text>
                                ) : null}
                                <Text style={[styles.clinicInfoText, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>Atendimento: {clinic.modalidades}</Text>
                            </View>
                        </View>
                        {clinicDescription ? (
                            <View style={styles.clinicDescriptionContainer}>
                                <Text style={[styles.description, { color: isDarkMode ? '#E2E8F0' : '#0f172a' }]}> 
                                    {showFullDescription || clinicDescription.length <= 120
                                        ? clinicDescription
                                        : `${clinicDescription.slice(0, 120).trim()}...`}
                                </Text>
                                {clinicDescription.length > 120 ? (
                                    <TouchableOpacity
                                        onPress={() => setShowFullDescription(prev => !prev)}
                                    >
                                        <Text style={[styles.descriptionToggle, { color: isDarkMode ? '#38BDF8' : '#0ea5e9' }]}> 
                                            {showFullDescription ? 'Ver menos' : 'Ver mais'}
                                        </Text>
                                    </TouchableOpacity>
                                ) : null}
                            </View>
                        ) : null}

                        <View style={styles.ratingRow}>
                            <View style={[styles.ratingPill, isDarkMode && { backgroundColor: '#1E293B' }]}> 
                                <Text style={[styles.ratingValue, { color: isDarkMode ? '#38BDF8' : '#0ea5e9' }]}>{resolveClinicRating(clinic)} ★</Text>
                            </View>
                            <Text style={[styles.ratingCount, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>{resolveClinicReviewCount(clinic)} avaliações</Text>
                        </View>
                    </View>

                    <View style={styles.serviceSection}>
                        <Text style={[styles.sectionTitle, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Especialidades</Text>
                        <TextInput
                            style={[styles.searchInput, isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155', color: '#F8FAFC' }]}
                            placeholder="Pesquisar especialidades"
                            placeholderTextColor="#94a3b8"
                            value={searchQuery}
                            onChangeText={setSearchQuery}
                        />
                        <View style={styles.serviceGrid}>
                            {visibleServices.map((service) => (
                                <TouchableOpacity
                                    key={`${service.name}-${service.id ?? service.price}`}
                                    style={[styles.serviceCard, isDarkMode && { backgroundColor: '#0F172A', borderColor: '#334155' }]}
                                    activeOpacity={0.85}
                                    onPress={() => navigation.navigate('Professionals', { clinic, user, selectedSpecialty: service.name })}
                                >
                                    <Text style={[styles.serviceName, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>{service.name}</Text>
                                    <Text style={[styles.servicePrice, { color: isDarkMode ? '#38BDF8' : '#0ea5e9' }]}>{typeof service.price === 'string' && service.price.trim().startsWith('R') ? service.price : `R$ ${service.price}`}</Text>
                                    <Text style={[styles.description, { color: isDarkMode ? '#CBD5E1' : '#0f172a' }]} numberOfLines={3}>{service.description ?? 'descrição...'}</Text>
                                </TouchableOpacity>
                            ))}
                            {visibleServices.length === 0 && (
                                <Text style={[styles.noResultsText, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>Nenhuma especialidade encontrada.</Text>
                            )}
                        </View>
                        {hasMoreSpecialties && (
                            <TouchableOpacity
                                style={styles.showMoreButton}
                                activeOpacity={0.85}
                                onPress={() => setShowAllSpecialties((prev) => !prev)}
                            >
                                <Text style={styles.showMoreText}>{showAllSpecialties ? 'Ver menos' : 'Ver mais'}</Text>
                            </TouchableOpacity>
                        )}
                    </View>

                    <TouchableOpacity
                        style={[styles.chooseButton, isDarkMode && { backgroundColor: '#38BDF8' }]}
                        activeOpacity={0.85}
                        onPress={() => navigation.navigate('Professionals', { clinic, user })}
                    >
                        <Text style={styles.chooseButtonText}>Escolher Profissional</Text>
                    </TouchableOpacity>

                    <View style={styles.sectionHeader}>
                        <Text style={[styles.sectionTitle, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Informações da Clínica</Text>
                    </View>

                    {bannerImages.length > 0 ? (
                        <ScrollView
                            horizontal
                            pagingEnabled
                            showsHorizontalScrollIndicator={false}
                            contentContainerStyle={styles.bannerCarouselContent}
                            style={[styles.bannerCarousel, isDarkMode && { borderColor: '#334155' }]}
                        >
                            {bannerImages.map((banner, index) => (
                                <Image
                                    key={`${banner?.uri || index}-banner`}
                                    source={banner}
                                    style={styles.bannerImage}
                                    resizeMode="cover"
                                />
                            ))}
                        </ScrollView>
                    ) : (
                        <View style={[styles.bannerPlaceholder, isDarkMode && { backgroundColor: '#0F172A', borderColor: '#334155' }]}>
                            <Text style={[styles.mapPlaceholderText, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>Banner da Clínica</Text>
                        </View>
                    )}

                    <View style={[styles.addressCard, isDarkMode && { backgroundColor: '#0F172A', borderWidth: 1, borderColor: '#334155' }]}> 
                        <Text style={[styles.addressLabel, { color: isDarkMode ? '#38BDF8' : '#0ea5e9' }]}>Endereço</Text>
                        <Text style={[styles.addressText, { color: isDarkMode ? '#E2E8F0' : '#0f172a' }]}>{clinicAddress}</Text>
                        <Text style={[styles.addressLabel, { marginTop: 14, color: isDarkMode ? '#38BDF8' : '#0ea5e9' }]}>Contate-nos</Text>
                        <View style={styles.contactRow}>
                            <TouchableOpacity
                                style={[styles.contactButton, isDarkMode && { backgroundColor: '#1E293B', borderColor: '#334155' }]}
                                activeOpacity={0.85}
                                onPress={async () => {
                                        const phone = clinicPhone || '(91) 98132-2686';
                                        try {
                                            await Clipboard.setStringAsync(phone);
                                            Alert.alert('Número copiado', `Número copiado para a área de transferência: ${phone}`);
                                        } catch (e) {
                                            console.log('Clipboard failed:', e);
                                            Alert.alert('Erro', 'Não foi possível copiar o número.');
                                        }
                                    }}
                            >
                                <Text style={[styles.contactButtonTitle, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Telefone</Text>
                                <Text style={[styles.contactButtonText, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>{clinicPhone || '(91) 98132-2686'}</Text>
                            </TouchableOpacity>
                            <TouchableOpacity style={[styles.contactButton, styles.contactButtonLast, isDarkMode && { backgroundColor: '#1E293B', borderColor: '#334155' }]} activeOpacity={0.85} onPress={() => {
                                const wa = clinicPhone ? `https://wa.me/${clinicPhone.replace(/[^0-9]/g, '')}` : null;
                                if (wa) Linking.openURL(wa);
                            }}>
                                <Text style={[styles.contactButtonTitle, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>WhatsApp</Text>
                                <Text style={[styles.contactButtonText, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>Enviar mensagem</Text>
                            </TouchableOpacity>
                        </View>
                    </View>

                    {mapRegion ? (
                        <MapView
                            style={styles.map}
                            initialRegion={mapRegion}
                            region={mapRegion}
                            showsUserLocation={false}
                            showsMyLocationButton={false}
                        >
                            <Marker
                                coordinate={{ latitude: mapRegion.latitude, longitude: mapRegion.longitude }}
                                title={clinicName}
                                description={clinicAddress}
                            />
                        </MapView>
                    ) : (
                        <View style={[styles.mapPlaceholder, isDarkMode && { backgroundColor: '#0F172A', borderColor: '#334155' }]}> 
                            <Text style={[styles.mapPlaceholderText, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>Mapa da Clínica</Text>
                        </View>
                    )}
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
    topRow: {
        marginTop: 24,
        marginHorizontal: 20,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    backButton: {
        width: 44,
        height: 44,
        borderRadius: 14,
        backgroundColor: '#ffffff',
        alignItems: 'center',
        justifyContent: 'center',
    },
    backText: {
        fontSize: 28,
        color: '#0f172a',
        lineHeight: 30,
    },
    content: {
        paddingHorizontal: 20,
        paddingTop: 40,
        paddingBottom: 80,
    },
    clinicCard: {
        backgroundColor: '#ffffff',
        borderRadius: 28,
        padding: 20,
        marginBottom: 12,
        shadowColor: '#000',
        shadowOpacity: 0.08,
        shadowOffset: { width: 0, height: 8 },
        shadowRadius: 20,
        elevation: 10,
    },
    clinicHeader: {
        flexDirection: 'row',
        alignItems: 'flex-start',
        marginBottom: 16,
    },
    clinicImagePlaceholder: {
        width: 110,
        height: 110,
        borderRadius: 24,
        backgroundColor: '#e0f2fe',
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 16,
    },
    clinicImage: {
        width: 110,
        height: 110,
        borderRadius: 24,
        marginRight: 16,
        backgroundColor: '#e0f2fe',
    },
    imageLabel: {
        color: '#0ea5e9',
        fontWeight: '700',
        fontSize: 14,
    },
    clinicHeaderInfo: {
        flex: 1,
        minWidth: 0,
        flexShrink: 1,
    },
    clinicTitle: {
        color: '#0f172a',
        fontSize: 24,
        fontWeight: '800',
        marginBottom: 6,
        flexShrink: 1,
    },
    clinicSubtitle: {
        color: '#0ea5e9',
        fontSize: 16,
        marginBottom: 12,
        flexShrink: 1,
    },
    clinicInfoText: {
        color: '#64748b',
        fontSize: 13,
        marginTop: 6,
    },
    clinicDescriptionContainer: {
        marginTop: 14,
    },
    serviceSection: {
        marginBottom: 22,
    },
    searchInput: {
        width: '100%',
        height: 48,
        backgroundColor: '#f1f5f9',
        borderRadius: 14,
        paddingHorizontal: 16,
        marginTop: 12,
        marginBottom: 12,
        color: '#0f172a',
    },
    serviceGrid: {
        marginTop: 0,
    },
    serviceCard: {
        width: '100%',
        backgroundColor: '#f8fafc',
        borderRadius: 18,
        paddingVertical: 14,
        paddingHorizontal: 18,
        marginBottom: 14,
        borderWidth: 1,
        borderColor: '#e2e8f0',
    },
    noResultsText: {
        color: '#64748b',
        fontSize: 14,
        marginTop: 8,
        textAlign: 'center',
    },
    showMoreButton: {
        alignSelf: 'flex-start',
        marginTop: 4,
        paddingVertical: 12,
        paddingHorizontal: 20,
        backgroundColor: '#0ea5e9',
        borderRadius: 16,
    },
    showMoreText: {
        color: '#ffffff',
        fontWeight: '700',
    },
    serviceName: {
        fontSize: 14,
        fontWeight: '700',
        color: '#0f172a',
        marginBottom: 6,
    },
    servicePrice: {
        fontSize: 13,
        color: '#0ea5e9',
        fontWeight: '700',
    },
    availabilityLabel: {
        fontSize: 12,
        color: '#64748b',
        marginTop: 10,
        marginBottom: 8,
    },
    availabilityList: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginTop: 0,
    },
    ratingRow: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    ratingPill: {
        backgroundColor: '#e0f2fe',
        borderRadius: 16,
        paddingVertical: 8,
        paddingHorizontal: 12,
        marginRight: 10,
    },
    ratingValue: {
        fontSize: 14,
        fontWeight: '700',
        color: '#0ea5e9',
    },
    ratingCount: {
        color: '#64748b',
        fontSize: 13,
        marginLeft: 8,
    },
    screenTitle: {
        fontSize: 18,
        fontWeight: '800',
        color: '#0f172a',
    },
    clinicInfoText: {
        color: '#64748b',
        fontSize: 13,
        marginTop: 4,
    },
    timeChip: {
        backgroundColor: '#ffffff',
        borderWidth: 1,
        borderColor: '#0ea5e9',
        borderRadius: 14,
        paddingVertical: 8,
        paddingHorizontal: 12,
        marginRight: 8,
        marginBottom: 8,
    },
    timeChipText: {
        color: '#0ea5e9',
        fontSize: 12,
        fontWeight: '700',
    },
    chooseButton: {
        backgroundColor: '#0ea5e9',
        borderRadius: 24,
        paddingVertical: 16,
        alignItems: 'center',
        marginBottom: 24,
    },
    chooseButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '700',
    },
    addressCard: {
        backgroundColor: '#ffffff',
        borderRadius: 24,
        padding: 18,
        shadowColor: '#000',
        shadowOpacity: 0.06,
        shadowOffset: { width: 0, height: 6 },
        shadowRadius: 14,
        elevation: 5,
        marginBottom: 20,
    },
    addressLabel: {
        fontSize: 13,
        color: '#64748b',
        marginBottom: 6,
    },
    addressText: {
        fontSize: 14,
        color: '#0f172a',
        lineHeight: 20,
    },
    contactRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginTop: 10,
    },
    contactButton: {
        flex: 1,
        backgroundColor: '#eef6ff',
        borderRadius: 16,
        paddingVertical: 14,
        paddingHorizontal: 14,
        borderWidth: 1,
        borderColor: '#dbeafe',
    },
    contactButtonLast: {
        marginLeft: 10,
    },
    contactButtonTitle: {
        fontSize: 12,
        color: '#64748b',
        marginBottom: 6,
    },
    contactButtonText: {
        fontSize: 14,
        fontWeight: '700',
        color: '#0f172a',
    },
    bannerCarousel: {
        height: 180,
        width: '100%',
        borderRadius: 24,
        overflow: 'hidden',
        marginBottom: 20,
        borderWidth: 1,
        borderColor: '#dfeaf5',
    },
    bannerCarouselContent: {
        alignItems: 'center',
    },
    bannerImage: {
        width: 330,
        height: 180,
        borderRadius: 24,
        alignSelf: 'center',
    },
    bannerPlaceholder: {
        height: 180,
        borderRadius: 24,
        backgroundColor: '#e2f2ff',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 20,
        borderWidth: 1,
        borderColor: '#dfeaf5',
    },
    map: {
        height: 180,
        borderRadius: 24,
        marginBottom: 40,
        overflow: 'hidden',
    },
    mapPlaceholder: {
        height: 180,
        borderRadius: 24,
        backgroundColor: '#e2f2ff',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 40,
    },
    mapPlaceholderText: {
        color: '#475569',
        fontSize: 14,
        fontWeight: '600',
    },
    rowBetween: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 18,
    },
    label: {
        fontSize: 12,
        color: '#64748b',
        marginBottom: 4,
    },
    value: {
        fontSize: 18,
        fontWeight: '700',
        color: '#0f172a',
    },
    detailsBlock: {
        marginBottom: 14,
    },
    detailLabel: {
        fontSize: 13,
        color: '#94a3b8',
        marginBottom: 6,
    },
    detailText: {
        fontSize: 15,
        color: '#0f172a',
        fontWeight: '600',
    },
    sectionHeader: {
        marginBottom: 12,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: '700',
        color: '#0f172a',
    },
    hourList: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        marginBottom: 24,
    },
    hourTag: {
        backgroundColor: '#e0f2fe',
        borderRadius: 14,
        paddingVertical: 10,
        paddingHorizontal: 14,
        marginRight: 10,
        marginBottom: 10,
    },
    hourText: {
        color: '#0369a1',
        fontSize: 13,
        fontWeight: '600',
    },
    description: {
        color: '#475569',
        fontSize: 14,
        lineHeight: 20,
        marginBottom: 10,
    },
    descriptionToggle: {
        color: '#0ea5e9',
        fontSize: 13,
        fontWeight: '700',
        marginBottom: 12,
    },
    actionButton: {
        backgroundColor: '#0ea5e9',
        borderRadius: 20,
        paddingVertical: 16,
        alignItems: 'center',
    },
    actionButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '700',
    },
});
