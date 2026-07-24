import { useState } from 'react';
import { View, Text, StyleSheet, Alert, Image, TouchableOpacity, StatusBar, Pressable } from 'react-native';
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
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f8f9ff" />
      <Image
        source={require('../../assets/imagem background.png')}
        style={styles.backgroundImage}
        resizeMode="cover"
      />
      <View style={styles.content}>
        <View style={styles.headerRow}>
          <TouchableOpacity
            activeOpacity={0.8}
            onPress={() => navigation.navigate('PreLogin')}
          >
            <Image
              source={require('../../assets/Logo_Transparente_1.png')}
              style={styles.logo}
              resizeMode="contain"
            />
          </TouchableOpacity>
        </View>

        <Text style={styles.pageTitle}>Faça Login com sua conta</Text>
        <Text style={styles.description}>Digite seu e-mail e senha para fazer login</Text>

        <Text style={styles.label}>Email</Text>
        <CustomInput
          placeholder="exemplo@email.com"
          value={email}
          onChangeText={setEmail}
        />

        <Text style={styles.label}>Senha</Text>
        <CustomInput
          placeholder="********"
          value={senha}
          onChangeText={setSenha}
          secureTextEntry
        />

        <TouchableOpacity activeOpacity={0.7} onPress={() => navigation.navigate('ForgotPassword')}>
          <Text style={styles.forgot}>Esqueci senha</Text>
        </TouchableOpacity>

        <CustomButton3
          title="Entrar na conta"
          onPress={handleLogin}
          style={styles.primaryButton}
        />

        <View style={styles.divider}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>Ou</Text>
          <View style={styles.dividerLine} />
        </View>

        <View style={styles.socialRow}>
          <TouchableOpacity style={styles.socialBtn} onPress={handleLogin} activeOpacity={0.8}>
            <Image
              source={require('../../assets/google-logo.png')}
              style={styles.socialIcon}
              resizeMode="contain"
            />
            <Text style={styles.socialText}>Continuar com Google</Text>
          </TouchableOpacity>
        </View>

        <Pressable
          onPress={() => navigation.navigate('LoginProfissional')}
          style={({ pressed }) => [
            styles.switchButton,
            pressed && styles.switchButtonPressed,
          ]}
        >
          {({ pressed }) => (
            <Text
              style={[
                styles.switchButtonText,
                pressed && styles.switchButtonTextPressed,
              ]}
            >
              Logar como profissional
            </Text>
          )}
        </Pressable>

        <View style={styles.signupRow}>
          <Text style={styles.signupText}>Ainda não tem uma conta?</Text>
          <TouchableOpacity activeOpacity={0.7} onPress={() => navigation.navigate('Cadastro')}>
            <Text style={styles.signupLink}>Cadastre-se</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9ff',
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
  headerRow: {
    marginTop: 32,
    marginBottom: 24,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  logo: {
    width: 180,
    height: 48,
    resizeMode: 'contain',
  },
  switchButton: {
    width: '100%',
    minHeight: 50,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#1bc3ea',
    backgroundColor: '#ffffff',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    marginBottom: 14,
    marginTop: 4,
    shadowColor: '#1bc3ea',
    shadowOffset: {
      width: 0,
      height: 6,
    },
    shadowOpacity: 0.12,
    shadowRadius: 12,
    elevation: 3,
  },
  switchButtonPressed: {
    backgroundColor: '#1bc3ea',
    transform: [
      {
        scale: 0.97,
      },
    ],
    shadowColor: '#1bc3ea',
    shadowOffset: {
      width: 0,
      height: 8,
    },
    shadowOpacity: 0.25,
    shadowRadius: 14,
    elevation: 8,
  },
  switchButtonText: {
    color: '#1bc3ea',
    fontSize: 15,
    fontWeight: '700',
  },
  switchButtonTextPressed: {
    color: '#ffffff',
  },
  pageTitle: {
    fontSize: 28,
    fontWeight: '700',
    marginBottom: 8,
    color: '#0b1c30',
  },
  description: {
    color: '#5b6b8f',
    marginBottom: 30,
    fontSize: 15,
    lineHeight: 22,
    maxWidth: 360,
  },
  label: {
    marginBottom: 10,
    color: '#5b6b8f',
    fontSize: 14,
    fontWeight: '600',
  },
  forgot: {
    textAlign: 'right',
    marginBottom: 20,
    color: '#1bc3ea',
    fontSize: 13,
    fontWeight: '700',
  },
  primaryButton: {
    marginTop: 2,
    backgroundColor: '#1bc3ea',
    borderRadius: 14,
    shadowColor: '#1bc3ea',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.18,
    shadowRadius: 14,
    elevation: 6,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 22,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#eee',
  },
  dividerText: {
    marginHorizontal: 14,
    color: '#999',
    fontSize: 14,
  },
  socialRow: {
    flexDirection: 'column',
    gap: 10,
    marginBottom: 16,
  },
  socialBtn: {
    width: '100%',
    minHeight: 50,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#d3e4fe',
    paddingVertical: 14,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  socialIcon: {
    width: 20,
    height: 20,
    marginRight: 10,
  },
  socialText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#0b1c30',
  },
  signupRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 6,
    marginTop: 14,
    flexWrap: 'wrap',
  },
  signupText: {
    color: '#333',
    fontSize: 14,
  },
  signupLink: {
    color: '#1bc3ea',
    fontSize: 14,
    fontWeight: '700',
  },
});
