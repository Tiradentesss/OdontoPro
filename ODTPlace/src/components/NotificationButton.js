import React from 'react';
import { TouchableOpacity, Image, StyleSheet } from 'react-native';
import { useTheme } from './ThemeContext';

export default function NotificationButton({ onPress, style }) {
    const { isDarkMode } = useTheme();

    return (
        <TouchableOpacity style={[styles.button, { backgroundColor: isDarkMode ? '#1E293B' : '#ffffff' }, style]} onPress={onPress} activeOpacity={0.8}>
            <Image
                source={require('../../assets/IconNotificacao.png')}
                style={[styles.icon, { tintColor: isDarkMode ? '#38BDF8' : '#0EA5E9' }]}
                resizeMode="contain"
            />
        </TouchableOpacity>
    );
}

const styles = StyleSheet.create({
    button: {
        width: 44,
        height: 44,
        borderRadius: 26,
        backgroundColor: '#ffffff',
        alignItems: 'center',
        justifyContent: 'center',
    },
    icon: {
        width: 24,
        height: 24,
    },
});
