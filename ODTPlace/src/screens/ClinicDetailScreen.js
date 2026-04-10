import React from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    SafeAreaView,
    ImageBackground,
    ScrollView,
} from 'react-native';
import NotificationButton from '../components/NotificationButton';

export default function ClinicDetailScreen({ route, navigation }) {
    const clinic = route?.params?.clinic ?? {};

    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            resizeMode="cover"
        >
            <SafeAreaView style={styles.container}>
                <View style={styles.topRow}>
                    <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
                        <Text style={styles.backText}>‹</Text>
                    </TouchableOpacity>
                    <NotificationButton onPress={() => {}} />
                </View>

                <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
                    <View style={styles.infoCard}>
                        <Text style={styles.clinicTitle}>{clinic.nome}</Text>
                        <Text style={styles.clinicSubtitle}>{clinic.especialidade}</Text>

                        <View style={styles.rowBetween}>
                            <View>
                                <Text style={styles.label}>Avaliação</Text>
                                <Text style={styles.value}>{clinic.avaliacao} ★</Text>
                            </View>
                            <View>
                                <Text style={styles.label}>Consultas</Text>
                                <Text style={styles.value}>{clinic.avaliacoes}</Text>
                            </View>
                        </View>

                        <View style={styles.detailsBlock}>
                            <Text style={styles.detailLabel}>Modalidade</Text>
                            <Text style={styles.detailText}>{clinic.modalidades}</Text>
                        </View>
                        <View style={styles.detailsBlock}>
                            <Text style={styles.detailLabel}>Valor da consulta</Text>
                            <Text style={styles.detailText}>{clinic.preco}</Text>
                        </View>
                        <View style={styles.detailsBlock}>
                            <Text style={styles.detailLabel}>Próxima disponibilidade</Text>
                            <Text style={styles.detailText}>{clinic.dia}</Text>
                        </View>
                    </View>

                    <View style={styles.sectionHeader}>
                        <Text style={styles.sectionTitle}>Horários disponíveis</Text>
                    </View>
                    <View style={styles.hourList}>
                        {clinic.horarios?.map((hora) => (
                            <View key={hora} style={styles.hourTag}>
                                <Text style={styles.hourText}>{hora}</Text>
                            </View>
                        ))}
                    </View>

                    <View style={styles.sectionHeader}>
                        <Text style={styles.sectionTitle}>Sobre a clínica</Text>
                    </View>
                    <Text style={styles.description}>
                        Clínica especializada em odontologia com atendimento personalizado e equipe dedicada a
                        seu conforto. Marque sua consulta e cuide do seu sorriso com quem entende do assunto.
                    </Text>

                    <TouchableOpacity style={styles.actionButton} activeOpacity={0.85} onPress={() => alert('Consulta agendada!')}>
                        <Text style={styles.actionButtonText}>Agendar consulta</Text>
                    </TouchableOpacity>
                </ScrollView>
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
        paddingBottom: 100,
    },
    infoCard: {
        backgroundColor: '#ffffff',
        borderRadius: 28,
        padding: 24,
        marginBottom: 20,
        shadowColor: '#000',
        shadowOpacity: 0.08,
        shadowOffset: { width: 0, height: 8 },
        shadowRadius: 20,
        elevation: 10,
    },
    clinicTitle: {
        color: '#0f172a',
        fontSize: 24,
        fontWeight: '800',
        marginBottom: 6,
    },
    clinicSubtitle: {
        color: '#0ea5e9',
        fontSize: 16,
        marginBottom: 18,
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
        lineHeight: 22,
        marginBottom: 24,
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
