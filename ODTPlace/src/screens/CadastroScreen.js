import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  TouchableOpacity,
  ImageBackground,
} from 'react-native';
import CustomInput from '../components/CustomInput';
import CustomButton from '../components/CustomButton';
import { registerPatient } from '../services/api';

export default function RegisterScreen({ navigation }) {
  const [nome, setNome] = useState('');
  const [sobrenome, setSobrenome] = useState('');
  const [email, setEmail] = useState('');
  const [dataNascimento, setDataNascimento] = useState('');
  const [telefone, setTelefone] = useState('');
  const [senha, setSenha] = useState('');

  const handleRegister = async () => {
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

    try {
      const nomeCompleto = `${nome.trim()} ${sobrenome.trim()}`;
      await registerPatient({
        nome: nomeCompleto,
        email,
        senha,
        telefone,
        cpf: '',
        data_nascimento: dataNascimento,
        sexo: '',
      });
      navigation.replace('Home', { user: { nome: nomeCompleto, email } });
    } catch (error) {
      Alert.alert('Erro', error.response?.data?.error ?? 'Falha ao registrar o usuário.');
    }
  };

  return (
    <ImageBackground
      source={require('../../assets/imagem background.png')}
      style={styles.container}
      resizeMode="cover"
    >
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

      <CustomInput
        placeholder="Nome"
        value={nome}
        onChangeText={setNome}
      />
      <CustomInput
        placeholder="Sobrenome"
        value={sobrenome}
        onChangeText={setSobrenome}
      />
      <CustomInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
      />
      <CustomInput
        placeholder="Data de nascimento"
        value={dataNascimento}
        onChangeText={setDataNascimento}
      />
      <CustomInput
        placeholder="Telefone"
        value={telefone}
        onChangeText={setTelefone}
        keyboardType="phone-pad"
      />
      <CustomInput
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
    </ImageBackground>
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
    backgroundColor: 'rgba(255,255,255,0.8)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  backText: {
    fontSize: 24,
    color: '#07336d',
    lineHeight: 26,
  },
  headerText: {
    flex: 1,
  },
  pageTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#07336d',
  },
  description: {
    color: '#6b7a90',
    fontSize: 14,
    marginTop: 4,
  },
  or: {
    textAlign: 'center',
    marginVertical: 16,
    color: '#888',
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
    color: '#24325f',
  },
});