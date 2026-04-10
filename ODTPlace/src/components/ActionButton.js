import React from 'react';
import { TouchableOpacity, View, Text, Image, StyleSheet } from 'react-native';

export default function ActionButton({ icon, title, onPress }) {
    return (
        <TouchableOpacity style={styles.button} activeOpacity={0.85} onPress={onPress}>
            <View style={styles.iconWrapper}>
                <Image source={icon} style={styles.icon} resizeMode="contain" />
            </View>
            <Text style={styles.title}>{title}</Text>
        </TouchableOpacity>
    );
}

const styles = StyleSheet.create({
    button: {
        flex: 1,
        minHeight: 110,
        borderRadius: 24,
        backgroundColor: '#ffffff',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 16,
        marginRight: 14,
        shadowColor: '#000',
        shadowOpacity: 0.06,
        shadowOffset: { width: 0, height: 6 },
        shadowRadius: 14,
        elevation: 6,
    },
    iconWrapper: {
        width: 48,
        height: 48,
        borderRadius: 18,
        backgroundColor: '#e0f2fe',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 12,
    },
    icon: {
        width: 26,
        height: 26,
    },
    title: {
        fontSize: 14,
        fontWeight: '700',
        color: '#0f172a',
        textAlign: 'center',
    },
});
