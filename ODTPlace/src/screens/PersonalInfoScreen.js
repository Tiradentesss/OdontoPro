import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    SafeAreaView,
    ImageBackground,
    ScrollView,
    Alert,
    ActivityIndicator,
} from 'react-native';
import ScheduleHeader from '../components/ScheduleHeader';
import { useAuth } from '../context/AuthContext';
import { updatePatientProfile } from '../services/api';
import { useTheme } from '../components/ThemeContext';

export default function PersonalInfoScreen({ navigation }) {
    const { user, login } = useAuth();
    const { isDarkMode, colors } = useTheme();
    const [fullName, setFullName] = useState('');
    const [cpf, setCpf] = useState('');
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');
    const [address, setAddress] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (user) {
            setFullName(user.nome || user.fullName || '');
            setCpf(user.cpf || '');
            setEmail(user.email || '');
            setPhone(user.telefone || user.phone || '');
            setAddress(user.endereco || user.address || '');
        }
    }, [user]);

    const handleSave = async () => {
        if (!user?.id) return;
        setLoading(true);
        try {
            const profileData = {
                nome: fullName,
                cpf,
                email,
                telefone: phone,
                endereco: address,
            };

            const updatedProfile = await updatePatientProfile(user.id, profileData);
            login({ ...user, ...updatedProfile });
            Alert.alert('Sucesso', 'Informações atualizadas com sucesso.');
        } catch (error) {
            console.log('Profile update error:', error);
            if (error?.response?.status === 404) {
                Alert.alert('Aviso', 'Funcionalidade de atualização ainda não implementada no backend. Os dados foram salvos localmente.');
                login({ ...user, nome: fullName, cpf, email, telefone: phone, endereco: address });
            } else {
                const errorMessage = error?.response?.data?.error || error.message || 'Não foi possível salvar as informações.';
                Alert.alert('Erro', errorMessage);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            imageStyle={!isDarkMode ? { transform: [{ scale: 1.2 }] } : undefined}
            resizeMode="cover"
        >
            <SafeAreaView style={[styles.container, { backgroundColor: isDarkMode ? colors.container : 'transparent' }]}> 
                <ScheduleHeader title="Informações Pessoais" onBack={() => navigation.goBack()} iconName="user" />

                <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
                    <Text style={[styles.heading, { color: isDarkMode ? '#F8FAFC' : '#0f172a' }]}>Editar Informações</Text>

                    {loading ? (
                        <ActivityIndicator size="large" color="#0ea5e9" style={{ marginTop: 32 }} />
                    ) : null}

                    <View style={styles.fieldGroup}>
                        <Text style={[styles.label, { color: isDarkMode ? '#CBD5E1' : '#64748b' }]}>Nome Completo</Text>
                        <TextInput
                            value={fullName}
                            onChangeText={setFullName}
                            placeholder="Nome completo"
                            placeholderTextColor="#94a3b8"
                            style={styles.input}
                        />
                    </View>

                    <View style={styles.fieldGroup}>
                        <Text style={styles.label}>CPF</Text>
                        <TextInput
                            value={cpf}
                            onChangeText={setCpf}
                            placeholder="000.000.000-00"
                            placeholderTextColor="#94a3b8"
                            style={styles.input}
                        />
                    </View>

                    <View style={styles.fieldGroup}>
                        <Text style={styles.label}>Email</Text>
                        <TextInput
                            value={email}
                            onChangeText={setEmail}
                            placeholder="email@example.com"
                            placeholderTextColor="#94a3b8"
                            keyboardType="email-address"
                            autoCapitalize="none"
                            style={styles.input}
                        />
                    </View>

                    <View style={styles.fieldGroup}>
                        <Text style={styles.label}>Número de Celular</Text>
                        <TextInput
                            value={phone}
                            onChangeText={setPhone}
                            placeholder="(91) 0000 - 0000"
                            placeholderTextColor="#94a3b8"
                            keyboardType="phone-pad"
                            style={styles.input}
                        />
                    </View>

                    <View style={styles.fieldGroup}>
                        <Text style={styles.label}>Endereço</Text>
                        <TextInput
                            value={address}
                            onChangeText={setAddress}
                            placeholder="Rua, número, bairro"
                            placeholderTextColor="#94a3b8"
                            style={styles.input}
                        />
                    </View>

                    <TouchableOpacity style={styles.saveButton} activeOpacity={0.85} onPress={handleSave} disabled={loading}>
                        <Text style={styles.saveButtonText}>Alterar Informações</Text>
                    </TouchableOpacity>
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
        color: '#0f172a',
        fontSize: 22,
        fontWeight: '800',
        marginBottom: 22,
    },
    fieldGroup: {
        marginBottom: 16,
    },
    label: {
        color: '#64748b',
        fontSize: 13,
        marginBottom: 8,
    },
    input: {
        width: '100%',
        backgroundColor: '#ffffff',
        borderRadius: 16,
        paddingHorizontal: 16,
        paddingVertical: 14,
        fontSize: 15,
        color: '#0f172a',
        shadowColor: '#000',
        shadowOpacity: 0.05,
        shadowOffset: { width: 0, height: 2 },
        shadowRadius: 8,
        elevation: 3,
    },
    saveButton: {
        marginTop: 24,
        backgroundColor: '#0ea5e9',
        borderRadius: 18,
        paddingVertical: 16,
        alignItems: 'center',
        shadowColor: '#000',
        shadowOpacity: 0.12,
        shadowOffset: { width: 0, height: 10 },
        shadowRadius: 20,
        elevation: 8,
    },
    saveButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '700',
    },
});
