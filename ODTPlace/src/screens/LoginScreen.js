import { useState } from 'react';
import { View, Text, StyleSheet, Alert, Image, TouchableOpacity, ImageBackground } from 'react-native';
import CustomInput from '../components/CustomInput';
import CustomButton3 from '../components/CustomButton3';
import { loginPatient } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const { login } = useAuth();

  const handleLogin = async () => {
    if (email === '' || senha === '') {
      Alert.alert('Erro', 'Preencha todos os campos!');
      return;
    }

    if (!email.includes('@') || !email.includes('.')) {
      Alert.alert('Erro', 'Email inválido!');
      return;
    }

    try {
      const user = await loginPatient(email, senha);
      if (user && (user.id || user.email)) {
        login(user);
        navigation.replace('Home');
      } else {
        Alert.alert('Erro', 'Resposta inválida do servidor.');
      }
    } catch (error) {
      console.log('Login error:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Falha ao fazer login.';
      Alert.alert('Erro', errorMessage);
    }
  };

  return (
    <ImageBackground
      source={require('../../assets/imagem background.png')}
      style={styles.container}
      resizeMode="cover"
    >
      <View style={styles.header}>
        <TouchableOpacity
          activeOpacity={0.8}
          onPress={() => navigation.navigate('PreLogin')}
        >
          <Image
            source={require('../../assets/LogoODTPlace.png')}
            style={styles.logo}
            resizeMode="contain"
          />
        </TouchableOpacity>
        <View style={styles.headerText}>
          <Text style={styles.headerTitle}>OdontoPlace</Text>
          <Text style={styles.headerSubtitle}>Sistema de gerenciamento</Text>
        </View>
      </View>

      <Text style={styles.pageTitle}>Faça login com sua conta</Text>
      <Text style={styles.description}>Digite seu e-mail e senha para fazer login</Text>

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

      <TouchableOpacity activeOpacity={0.7} onPress={() => navigation.navigate('ForgotPassword')}>
        <Text style={styles.forgot}>Esqueceu a Senha ?</Text>
      </TouchableOpacity>

      <CustomButton3
        title="Entrar na Conta"
        onPress={handleLogin}
        style={{ width: 335, alignSelf: 'center' }}
      />

      <Text style={styles.or}>Ou</Text>

      <TouchableOpacity style={styles.socialButton} onPress={handleLogin} activeOpacity={0.8}>
        <Text style={styles.socialText}>Continuar com Google</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.socialButton} onPress={handleLogin} activeOpacity={0.8}>
        <Text style={styles.socialText}>Continuar com Facebook</Text>
      </TouchableOpacity>

      <TouchableOpacity activeOpacity={0.7} onPress={() => navigation.navigate('Cadastro')}>
        <Text style={styles.signup}>Quero me cadastrar</Text>
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
    marginBottom: 30,
    flexDirection: 'row',
    alignItems: 'center',
  },
  logo: {
    width: 44,
    height: 44,
    resizeMode: 'contain',
  },
  headerText: {
    marginLeft: 10,
  },
  headerTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#07336d',
  },
  headerSubtitle: {
    fontSize: 11,
    color: '#6b7a90',
    marginTop: 2,
  },
  pageTitle: {
    fontSize: 28,
    fontWeight: '700',
    marginBottom: 8,
    color: '#07336d',
  },
  description: {
    color: '#6b7a90',
    marginBottom: 22,
    fontSize: 15,
    lineHeight: 22,
  },
  label: {
    marginTop: 10,
    marginBottom: 6,
    color: '#6b7a90',
    fontSize: 13,
  },
  forgot: {
    textAlign: 'right',
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#00bceb',
    fontSize: 13,
  },
  line: {
    flex: 1,
    height: 1,
    backgroundColor: '#fff',
    opacity: 0.5,
  },
  orText: {
    marginHorizontal: 10,
    color: '#fff',
    fontSize: 14,
  },
  or: {
    textAlign: 'center',
    marginVertical: 16,
    color: '#000',
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
  signup: {
    textAlign: 'center',
    fontWeight: 'bold',
    marginTop: 22,
    color: '#00bceb',
    fontSize: 15,
  },
});
