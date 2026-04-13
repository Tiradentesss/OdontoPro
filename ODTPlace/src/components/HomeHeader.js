import React from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Platform, StatusBar } from 'react-native';
import NotificationButton from './NotificationButton';

const statusBarHeight = Platform.OS === 'android' ? StatusBar.currentHeight || 24 : 44;

export default function HomeHeader({ usuario, search, setSearch, onBellPress, onFilterPress, sectionText = 'Clínicas Disponíveis' }) {
    return (
        <View style={styles.topCard}>
            <View style={styles.topCardContent}>
                <View style={styles.topHeader}>
                    <Text style={styles.welcomeText}>Bem-vindo, <Text style={styles.welcomeName}>{usuario}</Text></Text>
                    <NotificationButton onPress={onBellPress} />
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

                <Text style={styles.sectionText}>{sectionText}</Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    topCard: {
        marginTop: -statusBarHeight,
        marginHorizontal: -20,
        backgroundColor: '#0ea5e9',
        borderBottomLeftRadius: 32,
        borderBottomRightRadius: 32,
        overflow: 'hidden',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.12,
        shadowRadius: 18,
        elevation: 10,
    },
    topCardContent: {
        paddingHorizontal: 24,
        paddingTop: statusBarHeight + 40,
        paddingBottom: 18,
    },
    topHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 10,
        marginHorizontal: 14,
    },
    welcomeText: {
        color: '#dbeafe',
        fontSize: 18,
        fontWeight: '600',
        flexShrink: 1,
    },
    welcomeName: {
        color: '#ffffff',
        fontSize: 18,
        fontWeight: '800',
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
        borderRadius: 15,
        backgroundColor: '#e0f2fe',
        alignItems: 'center',
        justifyContent: 'center',
    },
    filterText: {
        fontSize: 18,
        color: '#0284c7',
    },
    sectionText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '700',
        marginTop: 16,
        marginLeft: 14,
    },
});
