import { useState } from 'react';
import { View, Text, StyleSheet, Alert, Image, TouchableOpacity, StatusBar } from 'react-native';
import CustomInput from '../components/CustomInput';
import CustomButton3 from '../components/CustomButton3';

export default function ForgotPassword({ navigation }) {
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

    navigation.navigate('CheckEmail', { email });
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
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <Text style={styles.backText}>‹</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.pageTitle}>Esqueceu a sua senha?</Text>
        <Text style={styles.description}>Digite seu e-mail para redefinir sua senha.</Text>

        <View style={styles.form}>
          <Text style={styles.label}>Email</Text>
          <CustomInput
            placeholder="exemplo@email.com"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
          />
        </View>

        <CustomButton3 title="Redefinir Senha" onPress={handleRegister} style={styles.primaryButton} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9ff',
    padding: 24,
  },
  content: {
    flex: 1,
  },
  backgroundImage: {
    position: 'absolute',
    width: '100%',
    height: '100%',
  },
  headerRow: {
    marginTop: 32,
    marginBottom: 24,
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
    marginBottom: 8,
  },
  description: {
    color: '#5b6b8f',
    fontSize: 15,
    lineHeight: 22,
    marginBottom: 30,
    maxWidth: 360,
  },
  form: {
    marginBottom: 30,
  },
  label: {
    marginBottom: 10,
    color: '#5b6b8f',
    fontSize: 14,
    fontWeight: '600',
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
});
