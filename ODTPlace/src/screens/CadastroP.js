import { useState } from 'react';
import {View, Text, StyleSheet, Alert, TouchableOpacity, ImageBackground,} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import CustomInput2 from '../components/CustomInput2';
import CustomButton from '../components/CustomButton4';

export default function RegisterScreen({ navigation }) {
  const [nome, setNome] = useState('');
  const [sobrenome, setSobrenome] = useState('');
  const [email, setEmail] = useState('');
  const [dataNascimento, setDataNascimento] = useState('');
  const [telefone, setTelefone] = useState('');
  const [senha, setSenha] = useState('');

  const handleRegister = () => {
    if (
      !nome ||
      !sobrenome ||
      !email ||
      !dataNascimento ||
      !telefone ||
      !senha
    ) {
      Alert.alert('Erro', 'Preencha todos os campos!');
      return;
    }

    if (!email.includes('@') || !email.includes('.')) {
      Alert.alert('Erro', 'Email inválido!');
      return;
    }

    const userName = nome || 'Paciente';
    navigation.replace('HomeProfissional', { userName });
  };

  return (
    <LinearGradient 
        start={{ x: 0, y: 0 }}
        end={{ x: 0.5, y: 1 }}
        colors={['#0a247c', '#1BC4EB']}
        style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backText}>‹</Text>
        </TouchableOpacity>

        <View style={styles.headerText}>
          <Text style={styles.pageTitle}>Registro</Text>
          <Text style={styles.description}>
            Crie sua conta para Continuar
          </Text>
        </View>
      </View>

      <CustomInput2
        placeholder="Nome"
        value={nome}
        onChangeText={setNome}
      />
      <CustomInput2
        placeholder="Sobrenome"
        value={sobrenome}
        onChangeText={setSobrenome}
      />
      <CustomInput2
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
      />
      <CustomInput2
        placeholder="Data de nascimento"
        value={dataNascimento}
        onChangeText={setDataNascimento}
      />
      <CustomInput2
        placeholder="Telefone"
        value={telefone}
        onChangeText={setTelefone}
        keyboardType="phone-pad"
      />
      <CustomInput2
        placeholder="Senha"
        value={senha}
        onChangeText={setSenha}
        secureTextEntry
      />

      <CustomButton title="Registrar Conta" onPress={handleRegister} />

      <Text style={styles.or}>Ou</Text>

      <TouchableOpacity style={styles.socialButton} activeOpacity={0.8}>
        <Text style={styles.socialText}>Continuar com Google</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.socialButton} activeOpacity={0.8}>
        <Text style={styles.socialText}>Continuar com Facebook</Text>
      </TouchableOpacity>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    backgroundColor: '#f5f7fa',
  },
  header: {
    marginTop: 40,
    marginBottom: 24,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: {
    width: 36,
    height: 36,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  backText: {
    fontSize: 34,
    color: '#fff',
    lineHeight: 26,
  },
  headerText: {
    flex: 1,
  },
  pageTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#fff',
  },
  description: {
    color: '#fff',
    fontSize: 14,
    marginTop: 4,
  },
  or: {
    textAlign: 'center',
    marginVertical: 16,
    color: '#fff',
    fontSize: 14,
  },
  socialButton: {
    backgroundColor: '#fff',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  socialText: {
    fontSize: 15,
    fontFamily: 'Poppins-Bold',
    fontWeight: 'bold',
    color: '#000',
  },
});