import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    SafeAreaView,
    ImageBackground,
    ScrollView,
} from 'react-native';
import ScheduleHeader from '../components/ScheduleHeader';
import BottomNavBar from '../components/BottomNavBar';

export default function ClinicDetailScreen({ route, navigation }) {
    const clinic = route?.params?.clinic ?? {};
    const [showFullDescription, setShowFullDescription] = useState(false);
    const services = clinic.services ?? [
        {
            name: clinic.especialidade ?? 'Especialidade',
            price: clinic.preco ?? 'R$ 250,00',
            availability: ['Ter. 14 - Dez • 08:00', 'Qua. 15 - Dez • 09:00'],
        },
    ];

    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            resizeMode="cover"
        >
            <SafeAreaView style={styles.container}>
                <ScheduleHeader title="Perfil da Clínica" onBack={() => navigation.goBack()} />

                <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
                    <View style={styles.clinicCard}>
                        <View style={styles.clinicHeader}>
                            <View style={styles.clinicImagePlaceholder}>
                                <Text style={styles.imageLabel}>Foto</Text>
                            </View>
                            <View style={styles.clinicHeaderInfo}>
                                <Text style={styles.clinicTitle} numberOfLines={2}>{clinic.nome}</Text>
                                {clinic.especialidade ? (
                                    <Text style={styles.clinicSubtitle} numberOfLines={1}>{clinic.especialidade}</Text>
                                ) : null}
                                <Text style={styles.clinicInfoText}>Atendimento: {clinic.modalidades}</Text>
                            </View>
                        </View>
                        {clinic.descricao ? (
                            <View style={styles.clinicDescriptionContainer}>
                                <Text style={styles.description}>
                                    {showFullDescription || clinic.descricao.length <= 120
                                        ? clinic.descricao
                                        : `${clinic.descricao.slice(0, 120).trim()}...`}
                                </Text>
                                {clinic.descricao.length > 120 ? (
                                    <TouchableOpacity
                                        onPress={() => setShowFullDescription(prev => !prev)}
                                    >
                                        <Text style={styles.descriptionToggle}>
                                            {showFullDescription ? 'Ver menos' : 'Ver mais'}
                                        </Text>
                                    </TouchableOpacity>
                                ) : null}
                            </View>
                        ) : null}

                        <View style={styles.ratingRow}>
                            <View style={styles.ratingPill}>
                                <Text style={styles.ratingValue}>{clinic.avaliacao} ★</Text>
                            </View>
                            <Text style={styles.ratingCount}>{clinic.avaliacoes} avaliações</Text>
                        </View>
                    </View>

                    <View style={styles.serviceSection}>
                        <Text style={styles.sectionTitle}>Especialidades</Text>
                        <View style={styles.serviceGrid}>
                            {services.map((service) => (
                                <TouchableOpacity
                                    key={service.name}
                                    style={styles.serviceCard}
                                    activeOpacity={0.85}
                                    onPress={() => navigation.navigate('Professionals', { clinic, selectedSpecialty: service.name })}
                                >
                                    <Text style={styles.serviceName}>{service.name}</Text>
                                    <Text style={styles.servicePrice}>{service.price}</Text>
                                    <Text style={styles.availabilityLabel}>Próximos horários</Text>
                                    <View style={styles.availabilityList}>
                                        {service.availability?.map((slot) => (
                                            <View key={slot} style={styles.timeChip}>
                                                <Text style={styles.timeChipText}>{slot}</Text>
                                            </View>
                                        ))}
                                    </View>
                                </TouchableOpacity>
                            ))}
                        </View>
                    </View>

                    <TouchableOpacity
                        style={styles.chooseButton}
                        activeOpacity={0.85}
                        onPress={() => navigation.navigate('Professionals', { clinic })}
                    >
                        <Text style={styles.chooseButtonText}>Escolher Profissional</Text>
                    </TouchableOpacity>

                    <View style={styles.sectionHeader}>
                        <Text style={styles.sectionTitle}>Informações da Clínica</Text>
                    </View>
                    <View style={styles.addressCard}>
                        <Text style={styles.addressLabel}>Endereço</Text>
                        <Text style={styles.addressText}>{clinic.endereco ?? 'Edifício Síntese Plaza - Av. Sen. Lemos, 791 - sala 1006 - Umarizal, Belém - PA, 66050-000'}</Text>
                        <Text style={[styles.addressLabel, { marginTop: 14 }]}>Contate-nos</Text>
                        <View style={styles.contactRow}>
                            <TouchableOpacity style={styles.contactButton} activeOpacity={0.85} onPress={() => {}}>
                                <Text style={styles.contactButtonTitle}>Telefone</Text>
                                <Text style={styles.contactButtonText}>{clinic.telefone ?? '(91) 98132-2686'}</Text>
                            </TouchableOpacity>
                            <TouchableOpacity style={[styles.contactButton, styles.contactButtonLast]} activeOpacity={0.85} onPress={() => {}}>
                                <Text style={styles.contactButtonTitle}>WhatsApp</Text>
                                <Text style={styles.contactButtonText}>Enviar mensagem</Text>
                            </TouchableOpacity>
                        </View>
                    </View>

                    <View style={styles.mapPlaceholder}>
                        <Text style={styles.mapPlaceholderText}>Mapa da Clínica</Text>
                    </View>
                </ScrollView>
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
        paddingVertical: 24,
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
    serviceGrid: {
        marginTop: 12,
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
