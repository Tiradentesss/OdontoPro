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
import { useTheme } from '../components/ThemeContext';

export default function SystemScreen({ navigation }) {
    const { isDarkMode, toggleTheme, colors } = useTheme();
    const [autoUpdates, setAutoUpdates] = useState(true);
    const [locationAccess, setLocationAccess] = useState(false);

    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            resizeMode="cover"
        >
            <SafeAreaView style={[styles.container, { backgroundColor: isDarkMode ? colors.container : 'transparent' }]}> 
                <ScheduleHeader title="Sistema" onBack={() => navigation.goBack()} iconName="shield" />
                <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
                    <Text style={[styles.heading, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Configurações do Sistema</Text>
                    <View style={[styles.section, { backgroundColor: isDarkMode ? '#1E293B' : '#ffffff' }]}> 
                        <View style={styles.optionRow}>
                            <View style={styles.optionTextBlock}>
                                <Text style={[styles.optionLabel, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Modo escuro</Text>
                                <Text style={[styles.optionSubtitle, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>Ativa o tema escuro no app</Text>
                            </View>
                            <Switch
                                value={isDarkMode}
                                onValueChange={toggleTheme}
                                thumbColor={isDarkMode ? '#0ea5e9' : '#f8fafc'}
                                trackColor={{ false: '#cbd5e1', true: '#bae6fd' }}
                            />
                        </View>
                        <View style={styles.optionRow}>
                            <View style={styles.optionTextBlock}>
                                <Text style={[styles.optionLabel, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Atualizações automáticas</Text>
                                <Text style={[styles.optionSubtitle, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>Receba atualizações em segundo plano</Text>
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
                                <Text style={[styles.optionLabel, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Acesso à localização</Text>
                                <Text style={[styles.optionSubtitle, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>Permitir sincronização de horários e rotas</Text>
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
        paddingTop: 136,
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
