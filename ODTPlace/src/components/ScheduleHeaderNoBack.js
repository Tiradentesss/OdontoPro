import React from 'react';
import { View, Text, StyleSheet, Platform, StatusBar } from 'react-native';

const statusBarHeight = Platform.OS === 'android' ? StatusBar.currentHeight || 24 : 44;

export default function ScheduleHeaderNoBack({ title }) {
    return (
        <View style={styles.headerWrapper}>
            <View style={styles.headerContainer}>
                <Text style={styles.title}>{title}</Text>
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
    title: {
        flex: 1,
        fontSize: 18,
        fontWeight: '800',
        color: '#ffffff',
    },
});
