import { useState } from 'react';
import { View, Text, StyleSheet, Alert, TouchableOpacity, StatusBar } from 'react-native';
import CustomInput2 from '../components/CustomInput2';
import CustomButton from '../components/CustomButton4';

export default function ForgotPasswordP({ navigation }) {
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

    navigation.navigate('CheckEmailP', { email });
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f8f9ff" />
      <View style={styles.bgDecor}>
        <View style={[styles.circle, styles.circleLeft]} />
        <View style={[styles.circle, styles.circleRight]} />
      </View>

      <View style={styles.headerRow}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Text style={styles.backText}>‹</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.pageTitle}>Esqueceu a sua senha?</Text>
      <Text style={styles.description}>Digite seu e-mail institucional para redefinir sua senha.</Text>

      <View style={styles.form}>
        <Text style={styles.label}>E-mail Institucional</Text>
        <CustomInput2
          placeholder="exemplo@clinicadental.com"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
        />
      </View>

      <CustomButton title="Redefinir Senha" onPress={handleRegister} style={styles.primaryButton} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9ff',
    paddingHorizontal: 24,
    paddingTop: 24,
  },
  bgDecor: {
    position: 'absolute',
    inset: 0,
  },
  circle: {
    position: 'absolute',
    borderRadius: 999,
    opacity: 0.28,
  },
  circleLeft: {
    width: 384,
    height: 384,
    backgroundColor: 'rgba(27,195,234,0.12)',
    top: -96,
    left: -96,
  },
  circleRight: {
    width: 320,
    height: 320,
    backgroundColor: 'rgba(27,195,234,0.12)',
    bottom: -120,
    right: -120,
  },
  headerRow: {
    marginTop: 32,
    marginBottom: 22,
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
    marginTop: 24,
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
    flex: 1,
  },
  label: {
    marginBottom: 10,
    color: '#5b6b8f',
    fontSize: 14,
    fontWeight: '600',
  },
  primaryButton: {
    marginTop: 0,
  },
});