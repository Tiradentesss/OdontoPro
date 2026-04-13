import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Platform, StatusBar } from 'react-native';

const statusBarHeight = Platform.OS === 'android' ? StatusBar.currentHeight || 24 : 44;

export default function ScheduleHeader({ title, onBack }) {
    return (
        <View style={styles.headerWrapper}>
            <View style={styles.headerContainer}>
                <TouchableOpacity style={styles.backButton} onPress={onBack} activeOpacity={0.8}>
                    <Text style={styles.backText}>‹</Text>
                </TouchableOpacity>
                <Text style={styles.title}>{title}</Text>
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
        backgroundColor: '#0ea5e9',
        borderBottomLeftRadius: 15,
        borderBottomRightRadius: 15,
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
    title: {
        flex: 1,
        textAlign: 'center',
        fontSize: 18,
        fontWeight: '800',
        color: '#ffffff',
    },
    rightPlaceholder: {
        width: 48,
        height: 48,
    },
});
