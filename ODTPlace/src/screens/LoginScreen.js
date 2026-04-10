import { useState } from 'react';
import { View, Text, StyleSheet, Alert, Image, TouchableOpacity, ImageBackground } from 'react-native';
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

    const userName = email.split('@')[0];
    navigation.replace('Home', { userName });
  };

  return (
    <ImageBackground
      source={require('../../assets/imagem background.png')}
      style={styles.container}
      resizeMode="cover"
    >
      <View style={styles.header}>
        <Image
          source={require('../../assets/LogoODTPlace.png')}
          style={styles.logo}
          resizeMode="contain"
        />
        <View style={styles.headerText}>
          <Text style={styles.headerTitle}>OdontoPro</Text>
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

      <TouchableOpacity activeOpacity={0.7}>
        <Text style={styles.forgot}>Esqueceu a Senha ?</Text>
      </TouchableOpacity>

      <CustomButton title="Entrar na Conta" onPress={handleLogin} />

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
    marginTop: 10,
    marginBottom: 20,
    color: '#1f4ed8',
    fontSize: 13,
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
  signup: {
    textAlign: 'center',
    marginTop: 22,
    color: '#1f4ed8',
    fontSize: 15,
  },
});
