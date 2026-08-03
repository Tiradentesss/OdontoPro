import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Platform, StatusBar } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from './ThemeContext';

const statusBarHeight = Platform.OS === 'android' ? StatusBar.currentHeight || 24 : 44;

export default function ScheduleHeader({ title, onBack, iconName }) {
    const { isDarkMode } = useTheme();

    return (
        <View style={[styles.headerWrapper, { backgroundColor: isDarkMode ? '#020617' : '#00bceb' }]}> 
            <View style={styles.headerContainer}>
                <TouchableOpacity style={[styles.backButton, { backgroundColor: isDarkMode ? '#1E293B' : '#ffffff' }]} onPress={onBack} activeOpacity={0.8}>
                    <Text style={[styles.backText, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>‹</Text>
                </TouchableOpacity>
                <View style={styles.titleContainer}>
                    {iconName ? (
                        <Feather name={iconName} size={16} color={isDarkMode ? '#F8FAFC' : '#ffffff'} style={styles.titleIcon} />
                    ) : null}
                    <Text style={[styles.title, { color: isDarkMode ? '#F8FAFC' : '#ffffff' }]}>{title}</Text>
                </View>
                <View style={styles.rightPlaceholder} />
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    headerWrapper: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 10,
        backgroundColor: '#00bceb',
        overflow: 'hidden',
        paddingTop: statusBarHeight + 25,
        paddingBottom: 18,
        paddingHorizontal: 20,
    },
    headerContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    backButton: {
        width: 48,
        height: 48,
        borderRadius: 16,
        backgroundColor: '#ffffff',
        alignItems: 'center',
        justifyContent: 'center',
        shadowColor: '#000',
        shadowOpacity: 0.08,
        shadowOffset: { width: 0, height: 4 },
        shadowRadius: 12,
        elevation: 6,
    },
    backText: {
        fontSize: 26,
        lineHeight: 28,
        color: '#0f172a',
    },
    titleContainer: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
    },
    title: {
        textAlign: 'center',
        fontSize: 18,
        fontWeight: '800',
        color: '#ffffff',
        flexShrink: 1,
    },
    titleIcon: {
        marginRight: 6,
    },
    rightPlaceholder: {
        width: 48,
        height: 48,
    },
});
