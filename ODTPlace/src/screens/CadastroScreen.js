import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  TouchableOpacity,
  Image,
  StatusBar,
} from 'react-native';
import CustomInput from '../components/CustomInput';
import CustomButton3 from '../components/CustomButton3';
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
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f8f9ff" />
      <Image
        source={require('../../assets/imagem background.png')}
        style={styles.backgroundImage}
        resizeMode="cover"
      />

      <View style={styles.content}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <Text style={styles.backText}>‹</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.pageTitle}>Crie sua conta</Text>
        <Text style={styles.description}>Preencha seus dados para continuar</Text>

        <View style={styles.form}>
          <View style={styles.fieldRow}>
            <View style={styles.fieldHalf}>
              <Text style={styles.label}>Nome</Text>
              <CustomInput
                placeholder="Seu nome"
                value={nome}
                onChangeText={setNome}
              />
            </View>
            <View style={styles.fieldHalf}>
              <Text style={styles.label}>Sobrenome</Text>
              <CustomInput
                placeholder="Sobrenome"
                value={sobrenome}
                onChangeText={setSobrenome}
              />
            </View>
          </View>

          <Text style={styles.label}>Email</Text>
          <CustomInput
            placeholder="exemplo@email.com"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
          />

          <View style={styles.fieldRow}>
            <View style={styles.fieldHalf}>
              <Text style={styles.label}>Nascimento</Text>
              <CustomInput
                placeholder="DD/MM/AAAA"
                value={dataNascimento}
                onChangeText={setDataNascimento}
                keyboardType="numbers-and-punctuation"
              />
            </View>
            <View style={styles.fieldHalf}>
              <Text style={styles.label}>Telefone</Text>
              <CustomInput
                placeholder="(00) 00000-0000"
                value={telefone}
                onChangeText={setTelefone}
                keyboardType="phone-pad"
              />
            </View>
          </View>

          <Text style={styles.label}>Senha</Text>
          <CustomInput
            placeholder="Crie uma senha"
            value={senha}
            onChangeText={setSenha}
            secureTextEntry
          />

          <CustomButton3 title="Criar minha conta" onPress={handleRegister} />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  content: {
    flex: 1,
    padding: 24,
  },
  backgroundImage: {
    position: 'absolute',
    top: 0,
    right: 0,
    bottom: 0,
    left: 0,
  },
  header: {
    marginTop: 28,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: 'rgba(27,195,234,0.12)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  backText: {
    color: '#1bc3ea',
    fontSize: 28,
    lineHeight: 32,
  },
  pageTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#0b1c30',
    marginBottom: 6,
  },
  description: {
    color: '#5b6b8f',
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 18,
  },
  form: {
    marginBottom: 8,
  },
  fieldRow: {
    flexDirection: 'row',
    gap: 10,
  },
  fieldHalf: {
    flex: 1,
  },
  label: {
    marginBottom: 6,
    color: '#5b6b8f',
    fontSize: 13,
    fontWeight: '600',
  },
});