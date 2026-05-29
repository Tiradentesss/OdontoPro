import { useState } from 'react';
import {View, Text, StyleSheet, Alert, TouchableOpacity, ImageBackground,} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import CustomInput2 from '../components/CustomInput2';
import CustomButton from '../components/CustomButton4';

export default function NewPasswordScreen({ navigation }) {

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleChangePassword = () => {

    if (!password || !confirmPassword) {
      Alert.alert('Erro', 'Preencha todos os campos!');
      return;
    }

    if (password.length < 3) {
      Alert.alert('Erro', 'A senha deve ter pelo menos 6 caracteres');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Erro', 'As senhas não coincidem');
      return;
    }

    Alert.alert(
      'Sucesso',
      'Senha alterada com sucesso!'
    );

    navigation.replace('HomeP');
  };

  return (
    <LinearGradient 
              start={{ x: 0, y: 0 }}
              end={{ x: 0.5, y: 1 }}
              colors={['#0a247c', '#1BC4EB']}
              style={styles.container}>

      <View style={styles.header}>

        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          <Text style={styles.backText}>‹</Text>
        </TouchableOpacity>

        <View style={styles.headerText}>
          <Text
            style={styles.pageTitle}
            numberOfLines={1}
          >
            Digite a nova Senha
          </Text>

          <Text style={styles.description}>
            Crie uma nova senha. Certifique-se de que ela seja diferente das anteriores por motivos de segurança.
          </Text>
        </View>

      </View>

      <CustomInput2
        placeholder="Nova Senha"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      <CustomInput2
        placeholder="Confirme a nova senha"
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        secureTextEntry
      />

      <CustomButton
        title="Mudar Senha"
        onPress={handleChangePassword}
      />

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
    lineHeight: 20,
  },
});