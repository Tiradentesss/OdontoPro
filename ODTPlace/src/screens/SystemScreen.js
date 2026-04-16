import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    TouchableOpacity,
    ImageBackground,
    ScrollView,
    Switch,
} from 'react-native';
import ScheduleHeader from '../components/ScheduleHeader';

export default function SystemScreen({ navigation }) {
    const [darkMode, setDarkMode] = useState(false);
    const [autoUpdates, setAutoUpdates] = useState(true);
    const [locationAccess, setLocationAccess] = useState(false);

    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            resizeMode="cover"
        >
            <SafeAreaView style={styles.container}>
                <ScheduleHeader title="Sistema" onBack={() => navigation.goBack()} />
                <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
                    <Text style={styles.heading}>Configurações do Sistema</Text>
                    <View style={styles.section}>
                        <View style={styles.optionRow}>
                            <View style={styles.optionTextBlock}>
                                <Text style={styles.optionLabel}>Modo escuro</Text>
                                <Text style={styles.optionSubtitle}>Ativa o tema escuro no app</Text>
                            </View>
                            <Switch
                                value={darkMode}
                                onValueChange={setDarkMode}
                                thumbColor={darkMode ? '#0ea5e9' : '#f8fafc'}
                                trackColor={{ false: '#cbd5e1', true: '#bae6fd' }}
                            />
                        </View>
                        <View style={styles.optionRow}>
                            <View style={styles.optionTextBlock}>
                                <Text style={styles.optionLabel}>Atualizações automáticas</Text>
                                <Text style={styles.optionSubtitle}>Receba atualizações em segundo plano</Text>
                            </View>
                            <Switch
                                value={autoUpdates}
                                onValueChange={setAutoUpdates}
                                thumbColor={autoUpdates ? '#0ea5e9' : '#f8fafc'}
                                trackColor={{ false: '#cbd5e1', true: '#bae6fd' }}
                            />
                        </View>
                        <View style={styles.optionRow}>
                            <View style={styles.optionTextBlock}>
                                <Text style={styles.optionLabel}>Acesso à localização</Text>
                                <Text style={styles.optionSubtitle}>Permitir sincronização de horários e rotas</Text>
                            </View>
                            <Switch
                                value={locationAccess}
                                onValueChange={setLocationAccess}
                                thumbColor={locationAccess ? '#0ea5e9' : '#f8fafc'}
                                trackColor={{ false: '#cbd5e1', true: '#bae6fd' }}
                            />
                        </View>
                    </View>
                </ScrollView>
            </SafeAreaView>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    pageBackground: {
        flex: 1,
    },
    container: {
        flex: 1,
        backgroundColor: 'transparent',
        paddingTop: 120,
    },
    content: {
        paddingHorizontal: 20,
        paddingBottom: 120,
        paddingTop: 24,
    },
    heading: {
        fontSize: 22,
        fontWeight: '800',
        color: '#0f172a',
        marginBottom: 20,
    },
    section: {
        backgroundColor: '#ffffff',
        borderRadius: 24,
        padding: 18,
        shadowColor: '#000',
        shadowOpacity: 0.06,
        shadowOffset: { width: 0, height: 8 },
        shadowRadius: 16,
        elevation: 6,
    },
    optionRow: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 16,
    },
    optionTextBlock: {
        flex: 1,
        marginRight: 12,
    },
    optionLabel: {
        fontSize: 15,
        fontWeight: '700',
        color: '#0f172a',
        marginBottom: 4,
    },
    optionSubtitle: {
        fontSize: 13,
        color: '#64748b',
        lineHeight: 18,
    },
});
