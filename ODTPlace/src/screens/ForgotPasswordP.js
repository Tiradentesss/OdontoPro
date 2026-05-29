import { useState } from 'react';
import {View, Text, StyleSheet, Alert, TouchableOpacity, ImageBackground,} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import CustomInput2 from '../components/CustomInput2';
import CustomButton from '../components/CustomButton4';

export default function ({ navigation }) {
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

    navigation.navigate('CheckEmailP', {email,});
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
          <Text style={styles.pageTitle} numberOfLines={1}>Esqueceu a sua senha?</Text>
          <Text style={styles.description}>
            Por favor, insira seu e-mail para redefinir a senha
          </Text>
        </View>
      </View>
      <CustomInput2
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
      />

      <CustomButton title="Redefinir Senha" onPress={handleRegister} />
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
    marginRight: -20,
    marginBottom: 90,
  },
  backText: {
    fontSize: 34,
    color: '#fff',
    lineHeight: 26,
    marginBottom: 4,
  },
  headerText: {
    flex: 1,
  },
  pageTitle: {
    marginTop: 70,
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