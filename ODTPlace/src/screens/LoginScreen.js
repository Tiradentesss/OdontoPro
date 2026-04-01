import { useState } from 'react';
import { View, Text, StyleSheet, Alert, Image, TouchableOpacity } from 'react-native';
import CustomInput from '../components/CustomInput';
import CustomButton from '../components/CustomButton';

export default function LoginScreen({ navigation }) {

  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');

  const handleLogin = () => {
    if (email === '' || senha === '') {
      Alert.alert('Erro', 'Preencha todos os campos!');
      return;
    }

    if (!email.includes('@') || !email.includes('.')) {
      Alert.alert('Erro', 'Email inválido!');
      return;
    }

    navigation.replace('Home');
  };

  return (
    <View style={styles.container}>

      {/* Logo */}
      <View style={styles.header}>
        <Image
          source={require('../../assets/LogoODTPlace.png')}
          style={styles.logo}
        />
        <Text style={styles.subtitle}>SISTEMA DE GERENCIAMENTO</Text>
      </View>

      {/* Título */}
      <Text style={styles.title}>Faça login com sua conta</Text>
      <Text style={styles.description}>
        Digite seu e-mail e senha para fazer login
      </Text>

      {/* Inputs */}
      <Text style={styles.label}>Email</Text>
      <CustomInput
        placeholder="Digite seu email"
        value={email}
        onChangeText={setEmail}
      />

      <Text style={styles.label}>Senha</Text>
      <CustomInput
        placeholder="Digite sua senha"
        value={senha}
        onChangeText={setSenha}
        secureTextEntry
      />

      {/* Esqueceu senha */}
      <TouchableOpacity>
        <Text style={styles.forgot}>Esqueceu a Senha ?</Text>
      </TouchableOpacity>

      {/* Botão principal */}
      <CustomButton
        title="Entrar na Conta"
        onPress={handleLogin}
      />

      {/* Divisor */}
      <Text style={styles.or}>Ou</Text>

      {/* Botões sociais */}
      <View style={styles.socialButton}>
        <Text>Continuar com Google</Text>
      </View>

      <View style={styles.socialButton}>
        <Text>Continuar com Facebook</Text>
      </View>

      {/* Cadastro */}
      <TouchableOpacity>
        <Text style={styles.signup}>Quero me cadastrar</Text>
      </TouchableOpacity>

    </View>
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
    marginBottom: 30,
  },

  logo: {
    width: 150,
    height: 50,
    resizeMode: 'contain',
  },

  subtitle: {
    fontSize: 12,
    color: '#6b7a90',
  },

  title: {
    fontSize: 26,
    fontWeight: 'bold',
    marginBottom: 8,
  },

  description: {
    color: '#6b7a90',
    marginBottom: 20,
  },

  label: {
    marginTop: 10,
    marginBottom: 5,
    color: '#6b7a90',
  },

  forgot: {
    textAlign: 'right',
    marginTop: 10,
    marginBottom: 20,
    color: '#1f4ed8',
  },

  or: {
    textAlign: 'center',
    marginVertical: 15,
    color: '#888',
  },

  socialButton: {
    backgroundColor: '#fff',
    padding: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#eee',
  },

  signup: {
    textAlign: 'center',
    marginTop: 20,
    color: '#1f4ed8',
  },
});