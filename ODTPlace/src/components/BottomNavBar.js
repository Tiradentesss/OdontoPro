import React from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';

const tabs = [
    { key: 'consultas', label: 'Consultas', icon: '📅' },
    { key: 'mensagens', label: 'Mensagens', icon: '💬' },
    { key: 'pacientes', label: 'Meus Pacientes', icon: '👥' },
    { key: 'mais', label: 'Mais', icon: '⋯' },
];

export default function BottomNavBar({ activeTab = 'consultas', onTabPress = () => {} }) {
    return (
        <View style={styles.bottomBar}>
            {tabs.map((tab) => {
                const isActive = activeTab === tab.key;
                return (
                    <TouchableOpacity
                        key={tab.key}
                        style={[styles.bottomTab, isActive && styles.bottomTabActive]}
                        onPress={() => onTabPress(tab.key)}
                        activeOpacity={0.8}
                    >
                        <Text style={[styles.bottomTabIcon, isActive && styles.activeIcon]}>{tab.icon}</Text>
                        <Text style={[styles.bottomTabLabel, isActive && styles.activeLabel]}>{tab.label}</Text>
                    </TouchableOpacity>
                );
            })}
        </View>
    );
}

const styles = StyleSheet.create({
    bottomBar: {
        position: 'absolute',
        left: 20,
        right: 20,
        bottom: 34,
        borderRadius: 32,
        backgroundColor: '#ffffff',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 14,
        paddingHorizontal: 16,
        shadowColor: '#000',
        shadowOpacity: 0.12,
        shadowOffset: { width: 0, height: 10 },
        shadowRadius: 18,
        elevation: 18,
    },
    bottomTab: {
        width: 72,
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 6,
    },
    bottomTabActive: {
        backgroundColor: '#e5f5ff',
        borderRadius: 20,
        paddingVertical: 10,
        paddingHorizontal: 6,
    },
    bottomTabIcon: {
        fontSize: 22,
        color: '#94a3b8',
        marginBottom: 4,
    },
    bottomTabLabel: {
        fontSize: 11,
        color: '#64748b',
        textAlign: 'center',
    },
    activeIcon: {
        color: '#0ea5e9',
    },
    activeLabel: {
        color: '#0b4a88',
        fontWeight: '700',
    },
});
