import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    ImageBackground,
    ScrollView,
    Switch,
} from 'react-native';
import ScheduleHeader from '../components/ScheduleHeader';

export default function NotificationSettingsScreen({ navigation }) {
    const [notificationGeneral, setNotificationGeneral] = useState(true);
    const [soundsEnabled, setSoundsEnabled] = useState(true);
    const [vibrationsEnabled, setVibrationsEnabled] = useState(true);
    const [messagesEnabled, setMessagesEnabled] = useState(true);

    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            resizeMode="cover"
        >
            <SafeAreaView style={styles.container}>
                <ScheduleHeader title="Configurações de Notificações" onBack={() => navigation.goBack()} />
                <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
                    <Text style={styles.heading}>Notificações</Text>
                    <View style={styles.section}>
                        <View style={styles.optionRow}>
                            <Text style={styles.optionLabel}>Notificação Geral</Text>
                            <Switch
                                value={notificationGeneral}
                                onValueChange={setNotificationGeneral}
                                thumbColor={notificationGeneral ? '#0ea5e9' : '#f8fafc'}
                                trackColor={{ false: '#cbd5e1', true: '#bae6fd' }}
                            />
                        </View>
                        <View style={styles.optionRow}>
                            <Text style={styles.optionLabel}>Sons</Text>
                            <Switch
                                value={soundsEnabled}
                                onValueChange={setSoundsEnabled}
                                thumbColor={soundsEnabled ? '#0ea5e9' : '#f8fafc'}
                                trackColor={{ false: '#cbd5e1', true: '#bae6fd' }}
                            />
                        </View>
                        <View style={styles.optionRow}>
                            <Text style={styles.optionLabel}>Vibrações</Text>
                            <Switch
                                value={vibrationsEnabled}
                                onValueChange={setVibrationsEnabled}
                                thumbColor={vibrationsEnabled ? '#0ea5e9' : '#f8fafc'}
                                trackColor={{ false: '#cbd5e1', true: '#bae6fd' }}
                            />
                        </View>
                        <View style={styles.optionRow}>
                            <Text style={styles.optionLabel}>Mensagens</Text>
                            <Switch
                                value={messagesEnabled}
                                onValueChange={setMessagesEnabled}
                                thumbColor={messagesEnabled ? '#0ea5e9' : '#f8fafc'}
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
    optionLabel: {
        fontSize: 15,
        fontWeight: '700',
        color: '#0f172a',
        flex: 1,
        marginRight: 12,
    },
});
