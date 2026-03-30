import { useState } from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import CustomInput from '../components/CustomInput';
import CustomButton from '../components/CustomButton';

export default function LoginScreen({ navigation }) {

  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');

  const handleLogin = () => {

    // Validação simples
    if (email === '' || senha === '') {
      Alert.alert('Erro', 'Preencha todos os campos!');
      return;
    }

      if (!email.includes('@') || !email.includes('.')) {
    Alert.alert('Erro', 'Email inválido!');
    return;
}
    // Se passou na validação
    navigation.replace('Home');
  };
  return (
    <View style={styles.container}>

      <Text style={styles.titulo}>Login</Text>
      <CustomInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
      />
      <CustomInput
        placeholder="Senha"
        value={senha}
        onChangeText={setSenha}
        secureTextEntry
      />
      <CustomButton
        title="Entrar"
        onPress={handleLogin}
      />
    </View>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  titulo: {
    fontSize: 24,
    marginBottom: 20,
    textAlign: 'center',
  },
});