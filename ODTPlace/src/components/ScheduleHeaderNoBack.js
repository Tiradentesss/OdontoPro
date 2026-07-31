import React from 'react';
import { View, Text, StyleSheet, Platform, StatusBar } from 'react-native';
import { useTheme } from './ThemeContext';

const statusBarHeight = Platform.OS === 'android' ? StatusBar.currentHeight || 24 : 44;

export default function ScheduleHeaderNoBack({ title }) {
    const { isDarkMode } = useTheme();

    return (
        <View style={[styles.headerWrapper, { backgroundColor: isDarkMode ? '#020617' : '#00bceb' }]}> 
            <View style={styles.headerContainer}>
                <Text style={[styles.title, { color: isDarkMode ? '#F8FAFC' : '#ffffff' }]}>{title}</Text>
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
        paddingTop: statusBarHeight + 10,
        paddingBottom: 18,
        paddingHorizontal: 20,
    },
    headerContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    title: {
        flex: 1,
        fontSize: 18,
        fontWeight: '800',
        color: '#ffffff',
    },
});
