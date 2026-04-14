import React, { useMemo, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, ImageBackground, FlatList, TextInput } from 'react-native';
import ScheduleHeader from '../components/ScheduleHeader';
import BottomNavBar from '../components/BottomNavBar';

const sampleProfessionals = [
    { id: '1', name: 'Lucas Castro', specialty: 'Ortodontista', rating: 5, reviews: 120 },
    { id: '2', name: 'Diogo Gomes', specialty: 'Odontopediatra', rating: 5, reviews: 51 },
    { id: '3', name: 'Ana Borges', specialty: 'Endodontista', rating: 4, reviews: 77 },
    { id: '4', name: 'Marina Silva', specialty: 'Periodontista', rating: 4, reviews: 42 },
];

const ratingFilters = [5, 4, 3];

export default function ProfessionalsScreen({ route, navigation }) {
    const clinic = route?.params?.clinic ?? {};
    const selectedSpecialty = route?.params?.selectedSpecialty ?? null;
    const [search, setSearch] = useState('');
    const [activeSpecialty, setActiveSpecialty] = useState(selectedSpecialty);
    const [activeRating, setActiveRating] = useState(null);
    const [showSpecialtyFilters, setShowSpecialtyFilters] = useState(false);
    const [showRatingFilters, setShowRatingFilters] = useState(false);

    const specialtyOptions = useMemo(() => {
        const services = clinic.services ?? [];
        const unique = Array.from(new Set(services.map((service) => service.name)));
        return unique.length ? unique : ['Ortodontia', 'Odontopediatria', 'Endodontia'];
    }, [clinic.services]);

    const professionals = useMemo(() => {
        return sampleProfessionals.filter((professional) => {
            const matchesSearch =
                search.length === 0 ||
                professional.name.toLowerCase().includes(search.toLowerCase()) ||
                professional.specialty.toLowerCase().includes(search.toLowerCase());
            const matchesSpecialty =
                !activeSpecialty ||
                professional.specialty.toLowerCase().includes(activeSpecialty.toLowerCase());
            const matchesRating = !activeRating || professional.rating === activeRating;
            return matchesSearch && matchesSpecialty && matchesRating;
        });
    }, [search, activeSpecialty, activeRating]);

    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            resizeMode="cover"
        >
            <SafeAreaView style={styles.container}>
                <ScheduleHeader title="Profissionais" onBack={() => navigation.goBack()} />

                <View style={styles.searchArea}>
                    <View style={styles.searchBox}>
                        <Text style={styles.searchIcon}>🔍</Text>
                        <TextInput
                            value={search}
                            onChangeText={setSearch}
                            placeholder="Buscar profissional"
                            placeholderTextColor="#94a3b8"
                            style={styles.searchInput}
                        />
                    </View>
                    <View style={styles.filterButtonsRow}>
                        <TouchableOpacity
                            style={[styles.openFilterButton, showSpecialtyFilters && styles.openFilterButtonActive]}
                            onPress={() => {
                                setShowSpecialtyFilters(!showSpecialtyFilters);
                                setShowRatingFilters(false);
                            }}
                            activeOpacity={0.85}
                        >
                            <Text style={[styles.openFilterButtonText, showSpecialtyFilters && styles.openFilterButtonTextActive]}>
                                Especialidade
                            </Text>
                        </TouchableOpacity>
                        <TouchableOpacity
                            style={[styles.openFilterButton, showRatingFilters && styles.openFilterButtonActive]}
                            onPress={() => {
                                setShowRatingFilters(!showRatingFilters);
                                setShowSpecialtyFilters(false);
                            }}
                            activeOpacity={0.85}
                        >
                            <Text style={[styles.openFilterButtonText, showRatingFilters && styles.openFilterButtonTextActive]}>
                                Avaliação
                            </Text>
                        </TouchableOpacity>
                    </View>
                </View>

                <View style={styles.content}>
                    {showSpecialtyFilters && (
                        <View style={styles.filterSection}>
                            <View style={styles.filterRow}>
                                {specialtyOptions.map((specialty) => (
                                    <TouchableOpacity
                                        key={specialty}
                                        style={[
                                            styles.filterChip,
                                            activeSpecialty === specialty && styles.filterChipActive,
                                        ]}
                                        onPress={() => setActiveSpecialty(activeSpecialty === specialty ? null : specialty)}
                                        activeOpacity={0.85}
                                    >
                                        <Text
                                            style={[
                                                styles.filterChipText,
                                                activeSpecialty === specialty && styles.filterChipTextActive,
                                            ]}
                                        >
                                            {specialty}
                                        </Text>
                                    </TouchableOpacity>
                                ))}
                            </View>
                        </View>
                    )}

                    {showRatingFilters && (
                        <View style={styles.filterSection}>
                            <View style={styles.filterRow}>
                                {ratingFilters.map((rating) => (
                                    <TouchableOpacity
                                        key={rating}
                                        style={[
                                            styles.ratingChip,
                                            activeRating === rating && styles.ratingChipActive,
                                        ]}
                                        onPress={() => setActiveRating(activeRating === rating ? null : rating)}
                                        activeOpacity={0.85}
                                    >
                                        <Text
                                            style={[
                                                styles.ratingChipText,
                                                activeRating === rating && styles.ratingChipTextActive,
                                            ]}
                                        >
                                            {rating} ★
                                        </Text>
                                    </TouchableOpacity>
                                ))}
                            </View>
                        </View>
                    )}

                    <View style={styles.listHeader}>
                        <Text style={styles.listTitle}>Profissionais da Clínica</Text>
                        <Text style={styles.listSubtitle}>{professionals.length} encontrado(s)</Text>
                    </View>

                    <FlatList
                        data={professionals}
                        keyExtractor={(item) => item.id}
                        showsVerticalScrollIndicator={false}
                        contentContainerStyle={styles.listContent}
                        renderItem={({ item }) => (
                            <TouchableOpacity
                                style={styles.professionalCard}
                                activeOpacity={0.86}
                                onPress={() => {}}
                            >
                                <View style={styles.avatarPlaceholder}>
                                    <Text style={styles.avatarText}>{item.name.charAt(0)}</Text>
                                </View>
                                <View style={styles.professionalInfo}>
                                    <Text style={styles.professionalName}>{item.name}</Text>
                                    <Text style={styles.professionalSpecialty}>{item.specialty}</Text>
                                    <Text style={styles.reviewText}>{item.reviews} avaliações</Text>
                                </View>
                            </TouchableOpacity>
                        )}
                        ListEmptyComponent={
                            <Text style={styles.emptyText}>Nenhum profissional encontrado.</Text>
                        }
                    />
                </View>

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
    customHeader: {
        marginTop: 24,
        marginHorizontal: 20,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 18,
    },
    backButton: {
        width: 44,
        height: 44,
        borderRadius: 14,
        backgroundColor: '#ffffff',
        alignItems: 'center',
        justifyContent: 'center',
        shadowColor: '#000',
        shadowOpacity: 0.06,
        shadowOffset: { width: 0, height: 3 },
        shadowRadius: 10,
        elevation: 6,
    },
    backText: {
        fontSize: 28,
        color: '#0f172a',
        lineHeight: 30,
    },
    headerPlaceholder: {
        width: 44,
    },
    screenTitle: {
        fontSize: 18,
        fontWeight: '800',
        color: '#0f172a',
    },
    searchArea: {
        paddingTop: 16,
        paddingHorizontal: 20,
        marginBottom: 16,
    },
    searchBox: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#ffffff',
        borderRadius: 18,
        paddingVertical: 12,
        paddingHorizontal: 16,
        shadowColor: '#000',
        shadowOpacity: 0.05,
        shadowOffset: { width: 0, height: 4 },
        shadowRadius: 12,
        elevation: 5,
    },
    searchIcon: {
        fontSize: 18,
        marginRight: 10,
        color: '#64748b',
    },
    searchInput: {
        flex: 1,
        fontSize: 16,
        color: '#0f172a',
    },
    filterButtonsRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginTop: 12,
    },
    openFilterButton: {
        flex: 1,
        backgroundColor: '#ffffff',
        borderRadius: 16,
        borderWidth: 1,
        borderColor: '#cbd5e1',
        paddingVertical: 12,
        alignItems: 'center',
        marginRight: 10,
    },
    openFilterButtonActive: {
        backgroundColor: '#0ea5e9',
        borderColor: '#0ea5e9',
    },
    openFilterButtonText: {
        fontSize: 13,
        color: '#0f172a',
        fontWeight: '700',
    },
    openFilterButtonTextActive: {
        color: '#ffffff',
    },
    openFilterButtonLast: {
        marginRight: 0,
    },
    content: {
        flex: 1,
        paddingHorizontal: 20,
        paddingBottom: 110,
    },
    filterSection: {
        marginBottom: 18,
    },
    filterTitle: {
        fontSize: 14,
        color: '#0f172a',
        fontWeight: '700',
        marginBottom: 10,
    },
    filterRow: {
        flexDirection: 'row',
        flexWrap: 'wrap',
    },
    filterChip: {
        backgroundColor: '#ffffff',
        borderRadius: 16,
        borderWidth: 1,
        borderColor: '#e2e8f0',
        paddingVertical: 10,
        paddingHorizontal: 14,
        marginRight: 10,
        marginBottom: 10,
    },
    filterChipActive: {
        backgroundColor: '#0ea5e9',
        borderColor: '#0ea5e9',
    },
    filterChipText: {
        fontSize: 13,
        color: '#0f172a',
    },
    filterChipTextActive: {
        color: '#ffffff',
    },
    ratingChip: {
        backgroundColor: '#ffffff',
        borderRadius: 16,
        borderWidth: 1,
        borderColor: '#e2e8f0',
        paddingVertical: 10,
        paddingHorizontal: 16,
        marginRight: 10,
        marginBottom: 10,
    },
    ratingChipActive: {
        backgroundColor: '#0ea5e9',
        borderColor: '#0ea5e9',
    },
    ratingChipText: {
        fontSize: 13,
        color: '#0f172a',
        fontWeight: '700',
    },
    ratingChipTextActive: {
        color: '#ffffff',
    },
    listHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 16,
    },
    listTitle: {
        fontSize: 16,
        color: '#0f172a',
        fontWeight: '700',
    },
    listSubtitle: {
        fontSize: 13,
        color: '#64748b',
    },
    listContent: {
        paddingBottom: 20,
    },
    professionalCard: {
        backgroundColor: '#ffffff',
        borderRadius: 20,
        padding: 16,
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 14,
        shadowColor: '#000',
        shadowOpacity: 0.05,
        shadowOffset: { width: 0, height: 6 },
        shadowRadius: 16,
        elevation: 6,
    },
    avatarPlaceholder: {
        width: 60,
        height: 60,
        borderRadius: 18,
        backgroundColor: '#e0f2fe',
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 14,
    },
    avatarText: {
        color: '#0ea5e9',
        fontSize: 24,
        fontWeight: '800',
    },
    professionalInfo: {
        flex: 1,
    },
    professionalName: {
        fontSize: 16,
        fontWeight: '800',
        color: '#0f172a',
        marginBottom: 4,
    },
    professionalSpecialty: {
        fontSize: 13,
        color: '#0ea5e9',
        marginBottom: 6,
    },
    reviewText: {
        fontSize: 12,
        color: '#64748b',
    },
    emptyText: {
        textAlign: 'center',
        color: '#64748b',
        marginTop: 20,
    },
});
