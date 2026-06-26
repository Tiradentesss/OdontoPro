import { useState, useRef, useEffect} from 'react';
import {View, Text, StyleSheet, Alert, TouchableOpacity, ImageBackground, TextInput} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import CustomInput from '../components/CustomInput';
import CustomButton from '../components/CustomButton4';

export default function CheckEmail({ navigation, route }) {
  const { email } = route.params;

  const [code, setCode] = useState(['', '', '', '', '']);
  const [timer, setTimer] = useState(59);

  const inputs = useRef([]);

  useEffect(() => {
    if (timer > 0) {
      const interval = setInterval(() => {
        setTimer(prev => prev - 1);
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [timer]);

  const handleChange = (text, index) => {
    if (text.length > 1) return;

    const newCode = [...code];
    newCode[index] = text;
    setCode(newCode);

    // vai para o próximo input
    if (text && index < 4) {
      inputs.current[index + 1].focus();
    }
  };

  const handleVerify = () => {
    const finalCode = code.join('');

    if (finalCode.length < 5) {
      Alert.alert('Erro', 'Digite o código completo');
      return;
    }

    navigation.navigate('NewPasswordP');
  };

  const resendCode = () => {
    setTimer(59);
    Alert.alert('Código reenviado!');
  };

  return (
      <LinearGradient 
          start={{ x: 0, y: 0 }}
          end={{ x: 0.5, y: 1 }}
          colors={['#0a247c', '#1BC4EB']}
          style={styles.container}>
      <TouchableOpacity
        onPress={() => navigation.goBack()}
        style={styles.backButton}
      >
        <Text style={styles.backText}>‹</Text>
      </TouchableOpacity>

      <Text style={styles.title}>Verifique seu e-mail</Text>

      <Text style={styles.description}>
        Enviamos um link de redefinição para{' '}
        {email.replace(/(.{4}).+(@.+)/, '$1****$2')}
      </Text>

      <View style={styles.codeContainer}>
        {code.map((digit, index) => (
          <TextInput
            key={index}
            ref={ref => (inputs.current[index] = ref)}
            style={styles.codeInput}
            keyboardType="number-pad"
            maxLength={1}
            value={digit}
            onChangeText={text => handleChange(text, index)}
          />
        ))}
      </View>

      <TouchableOpacity style={styles.button} onPress={handleVerify}>
        <Text style={styles.buttonText}>Verificar Código</Text>
      </TouchableOpacity>

      <Text style={styles.timer}>⏰ 00:{timer < 10 ? `0${timer}` : timer}</Text>

      <TouchableOpacity
        disabled={timer > 0}
        onPress={resendCode}
      >
        <Text
          style={[0,
            styles.resend,
            { color: timer > 0 ? '#ffffff00' : '#fff' },
          ]}
        >
          Reenviar E-mail
        </Text>
      </TouchableOpacity>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 28,
  },

  backButton: {
    marginTop: 60,
    width: 40,
    height: 40,
    justifyContent: 'center',
  },

  backText: {
    fontSize: 34,
    color: '#fff',
  },

  title: {
    marginTop: 40,
    fontSize: 34,
    fontWeight: '700',
    color: '#fff',
  },

  description: {
    marginTop: 14,
    fontSize: 15,
    color: '#fff',
    lineHeight: 22,
  },

  codeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 40,
    
  },

  codeInput: {
    width: 58,
    height: 68,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.3)',
    color: '#fff',
    textAlign: 'center',
    fontSize: 24,
    fontWeight: '700',
    borderWidth: 1,
    borderColor: '#fff',
  },

  button: {
    marginTop: 40,
    backgroundColor: '#fff',
    height: 58,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },

  buttonText: {
    color: '#00bceb',
    fontSize: 17,
    fontWeight: '700',
  },

  timer: {
    marginTop: 28,
    textAlign: 'center',
    fontSize: 16,
    color: '#fff',
    fontWeight: '600',
  },

  resend: {
    marginTop: 40,
    textAlign: 'center',
    fontSize: 16,
    fontWeight: '600',
  },
});