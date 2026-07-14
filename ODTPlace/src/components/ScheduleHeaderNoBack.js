import React from 'react';
import { View, Text, StyleSheet, Platform, StatusBar, TouchableOpacity } from 'react-native';
import { ChevronLeft } from 'lucide-react-native';

const statusBarHeight = Platform.OS === 'android' ? StatusBar.currentHeight || 24 : 44;

export default function ScheduleHeader({ title, onBackPress }) {
    return (
        <View style={styles.headerWrapper}>
            <View style={styles.headerContainer}>
                {/* Botão de Voltar */}
                <TouchableOpacity onPress={onBackPress} style={styles.backButton}>
                    <ChevronLeft size={28} color="#0f172a" strokeWidth={2.5} />
                </TouchableOpacity>

                {/* Título alinhado à esquerda, ao lado da seta */}
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
        backgroundColor: '#ffffff',
        paddingTop: statusBarHeight + 15,
        paddingBottom: 20,
        paddingHorizontal: 16,
        elevation: 0,
        shadowOpacity: 0,
    },
    headerContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        // justify-content removido ou alterado para flex-start para alinhar à esquerda
        justifyContent: 'flex-start', 
    },
    backButton: {
        marginRight: 10, // Espaço entre a seta e o texto
    },
    title: {
        fontSize: 24, // Aumentado um pouco para bater com o visual do print
        fontWeight: '800',
        color: '#0f172a',
        // flex: 1 removido para o texto não ser forçado a centralizar
    },
});