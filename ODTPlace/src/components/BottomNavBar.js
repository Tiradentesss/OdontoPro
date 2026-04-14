import React from 'react';
import { View, TouchableOpacity, Text, Image, StyleSheet } from 'react-native';

const tabs = [
    { key: 'home', label: 'Home', icon: require('../../assets/IconHome.png') },
    { key: 'schedule', label: 'Agendamentos', icon: require('../../assets/IconClipboard.png') },
    { key: 'notifications', label: 'Notificações', icon: require('../../assets/IconNotificacao.png') },
    { key: 'settings', label: 'Configurações', icon: require('../../assets/IconConfiguracao.png') },
];

export default function BottomNavBar({ activeTab = 'home', onTabPress = () => {} }) {
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
                        <Image source={tab.icon} style={[styles.bottomTabIcon, isActive && styles.activeIcon]} resizeMode="contain" />
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
        justifyContent: 'space-around',
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
        width: 84,
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
        width: 32,
        height: 32,
        marginBottom: 4,
        tintColor: '#94a3b8',
    },
    bottomTabLabel: {
        fontSize: 10,
        color: '#64748b',
        textAlign: 'center',
    },
    activeIcon: {
        tintColor: '#0ea5e9',
    },
    activeLabel: {
        color: '#0b4a88',
        fontWeight: '700',
    },
});
