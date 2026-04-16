import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    SafeAreaView,
    ImageBackground,
    ScrollView,
} from 'react-native';
import ScheduleHeader from '../components/ScheduleHeader';

export default function PersonalInfoScreen({ navigation }) {
    const [fullName, setFullName] = useState('Gabriel Gomes Matos');
    const [cpf, setCpf] = useState('000.000.000-01');
    const [email, setEmail] = useState('gabrielgomes@gmail.com');
    const [phone, setPhone] = useState('(91) 0000 - 0000');
    const [gender, setGender] = useState('Masculino');
    const [address, setAddress] = useState('45 Nova Batista Campos, Belém Pará');

    return (
        <ImageBackground
            source={require('../../assets/imagem background.png')}
            style={styles.pageBackground}
            resizeMode="cover"
        >
            <SafeAreaView style={styles.container}>
                <ScheduleHeader title="Informações Pessoais" onBack={() => navigation.goBack()} />

                <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
                    <Text style={styles.heading}>Editar Informações</Text>

                    <View style={styles.fieldGroup}>
                        <Text style={styles.label}>Nome Completo</Text>
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
                        <Text style={styles.label}>Gênero</Text>
                        <TextInput
                            value={gender}
                            onChangeText={setGender}
                            placeholder="Masculino"
                            placeholderTextColor="#94a3b8"
                            style={styles.input}
                        />
                    </View>
                    <View style={styles.fieldGroup}>
                        <Text style={styles.label}>Endereço</Text>
                        <TextInput
                            value={address}
                            onChangeText={setAddress}
                            placeholder="Rua, número, bairro, cidade"
                            placeholderTextColor="#94a3b8"
                            style={styles.input}
                        />
                    </View>

                    <TouchableOpacity style={styles.saveButton} activeOpacity={0.85} onPress={() => {}}>
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
