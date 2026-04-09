import React from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';

export default function HomeHeader({ usuario, search, setSearch, onBellPress, onFilterPress }) {
    return (
        <View style={styles.topCard}>
            <View style={styles.topCardContent}>
                <View style={styles.topHeader}>
                    <View>
                        <Text style={styles.welcomeLabel}>Bem-vindo,</Text>
                        <Text style={styles.welcomeName}>{usuario}</Text>
                    </View>

                    <TouchableOpacity style={styles.bellButton} onPress={onBellPress} activeOpacity={0.8}>
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
                    <TouchableOpacity style={styles.filterButton} onPress={onFilterPress} activeOpacity={0.8}>
                        <Text style={styles.filterText}>⌗</Text>
                    </TouchableOpacity>
                </View>
            </View>

            <View style={styles.sectionBar}>
                <Text style={styles.sectionBarText}>Clínicas Disponíveis</Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
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
        backgroundColor: '#e0f2fe',
        paddingVertical: 14,
        paddingHorizontal: 20,
    },
    sectionBarText: {
        color: '#0f172a',
        fontSize: 15,
        fontWeight: '700',
    },
});
