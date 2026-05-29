import { useState } from 'react';
import { View, Text, StyleSheet, Alert, Image, TouchableOpacity } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import CustomInput2 from '../components/CustomInput2';
import CustomButton from '../components/CustomButton4';

export default function LoginProfissional({ navigation }) {
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
    navigation.replace('HomeP', { userName });
  };

  return (
    <LinearGradient 
    start={{ x: 0, y: 0 }}
    end={{ x: 0.5, y: 1 }}
    colors={['#0a247c', '#1BC4EB']}
    style={styles.container}>
      <View style={styles.header}>
        <Image
          source={require('../../assets/LogoP.png')}
          style={styles.logo}
          resizeMode="contain"
        />
        <View style={styles.headerText}>
          <Text style={styles.headerTitle}>OdontoPlace</Text>
          <Text style={styles.headerSubtitle}>Sistema de gerenciamento</Text>
        </View>
      </View>

      <Text style={styles.pageTitle}>Faça login com sua conta</Text>
      <Text style={styles.description}>Digite seu e-mail e senha para fazer login</Text>

      <Text style={styles.label}>Email</Text>
      <CustomInput2
        placeholder="Digite seu email"
        value={email}
        onChangeText={setEmail}
      />

      <Text style={styles.label}>Senha</Text>
      <CustomInput2
        placeholder="Digite sua senha"
        value={senha}
        onChangeText={setSenha}
        secureTextEntry
      />

      <TouchableOpacity activeOpacity={0.7} onPress={() => navigation.navigate('ForgotPasswordP')}>
        <Text style={styles.forgot}>Esqueceu a Senha?</Text>
      </TouchableOpacity>

      <CustomButton
        title="Entrar na Conta"
        onPress={handleLogin}
        style={{ width: 335, alignSelf: 'center' }}
      />

    <View style={styles.orContainer}>
      <View style={styles.line} />
      <Text style={styles.or}>Ou</Text>
      <View style={styles.line} />
    </View>

      <TouchableOpacity style={styles.socialButton} onPress={handleLogin} activeOpacity={0.8}>
        <Text style={styles.socialText}>Continuar com Google</Text>
      </TouchableOpacity>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    backgroundColor: '#08a4c4',
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
    fontFamily: 'Poppins-Bold',
    fontSize: 14,
    fontWeight: '700',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 11,
    color: '#fff',
    marginTop: 2,
  },
  pageTitle: {
    fontSize: 28,
    fontWeight: '700',
    marginBottom: 8,
    color: '#fff',
  },
  description: {
    color: '#fff',
    marginBottom: 22,
    fontSize: 15,
    lineHeight: 22,
  },
  label: {
    marginTop: 10,
    marginBottom: 6,
    color: '#fff',
    fontSize: 13,
  },
  forgot: {
    textAlign: 'right',
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#fff',
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
    marginVertical: 20,
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
    color: '#000000',
  },
  signup: {
    textAlign: 'center',
    fontWeight: 'bold',
    marginTop: 22,
    color: '#fff',
    fontSize: 15,
  },
});
