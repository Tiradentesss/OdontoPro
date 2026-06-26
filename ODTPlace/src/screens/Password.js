import { useState } from 'react';
import {View, Text, StyleSheet, Alert, TouchableOpacity, ImageBackground,} from 'react-native';
import CustomInput from '../components/CustomInput';
import CustomButton3 from '../components/CustomButton3';

export default function RegisterScreen({ navigation }) {
  const [email, setEmail] = useState('');

  const handleRegister = () => {
    if (!email) {
      Alert.alert('Erro', 'Preencha todos os campos!');
      return;
    }

    if (!email.includes('@') || !email.includes('.')) {
      Alert.alert('Erro', 'Email inválido!');
      return;
    }

    const userName = email.split('@')[0] || 'Paciente';
    navigation.replace('Home', { userName });
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
          <Text style={styles.pageTitle} numberOfLines={1}>
            Esqueceu a sua senha?
          </Text>
          <Text style={styles.description}>
            Por favor, insira seu e-mail para redefinir a senha
          </Text>
        </View>
      </View>
      <CustomInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
      />

      <CustomButton3 title="Redefinir Senha" onPress={handleRegister} />
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
    marginTop: 70,
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