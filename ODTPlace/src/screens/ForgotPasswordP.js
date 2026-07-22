import { useState } from 'react';
import { View, Text, StyleSheet, Alert, TouchableOpacity, StatusBar } from 'react-native';
import CustomInput2 from '../components/CustomInput2';
import CustomButton3 from '../components/CustomButton3';

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
        <View style={[styles.circle, styles.circleLeftOuter]} />
        <View style={[styles.circle, styles.circleLeftWide]} />
        <View style={[styles.circle, styles.circleLeftMiddle]} />
        <View style={[styles.circle, styles.circleLeftSoft]} />
        <View style={[styles.circle, styles.circleLeftInner]} />
        <View style={[styles.circle, styles.circleRightOuter]} />
        <View style={[styles.circle, styles.circleRightWide]} />
        <View style={[styles.circle, styles.circleRightMiddle]} />
        <View style={[styles.circle, styles.circleRightSoft]} />
        <View style={[styles.circle, styles.circleRightInner]} />
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

      <CustomButton3 title="Redefinir Senha" onPress={handleRegister} style={styles.primaryButton} />
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
  },
  circleLeftOuter: {
    width: 980,
    height: 980,
    borderRadius: 490,
    backgroundColor: 'rgba(27,195,234,0.006)',
    top: -450,
    left: -450,
  },
  circleLeftWide: {
    width: 840,
    height: 840,
    borderRadius: 420,
    backgroundColor: 'rgba(27,195,234,0.009)',
    top: -380,
    left: -380,
  },
  circleLeftMiddle: {
    width: 700,
    height: 700,
    borderRadius: 350,
    backgroundColor: 'rgba(27,195,234,0.013)',
    top: -310,
    left: -310,
  },
  circleLeftSoft: {
    width: 560,
    height: 560,
    borderRadius: 280,
    backgroundColor: 'rgba(27,195,234,0.018)',
    top: -240,
    left: -240,
  },
  circleLeftInner: {
    width: 440,
    height: 440,
    borderRadius: 220,
    backgroundColor: 'rgba(27,195,234,0.025)',
    top: -185,
    left: -185,
  },
  circleRightOuter: {
    width: 900,
    height: 900,
    borderRadius: 450,
    backgroundColor: 'rgba(27,195,234,0.005)',
    bottom: -440,
    right: -440,
  },
  circleRightWide: {
    width: 780,
    height: 780,
    borderRadius: 390,
    backgroundColor: 'rgba(27,195,234,0.008)',
    bottom: -380,
    right: -380,
  },
  circleRightMiddle: {
    width: 650,
    height: 650,
    borderRadius: 325,
    backgroundColor: 'rgba(27,195,234,0.012)',
    bottom: -315,
    right: -315,
  },
  circleRightSoft: {
    width: 540,
    height: 540,
    borderRadius: 270,
    backgroundColor: 'rgba(27,195,234,0.016)',
    bottom: -260,
    right: -260,
  },
  circleRightInner: {
    width: 390,
    height: 390,
    borderRadius: 195,
    backgroundColor: 'rgba(27,195,234,0.023)',
    bottom: -185,
    right: -185,
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
