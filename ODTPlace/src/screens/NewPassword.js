import { useState } from 'react';
import {View, Text, StyleSheet, Alert, TouchableOpacity, ImageBackground,} from 'react-native';
import CustomInput from '../components/CustomInput';
import CustomButton3 from '../components/CustomButton3';

export default function NewPasswordScreen({ navigation }) {

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleChangePassword = () => {

    if (!password || !confirmPassword) {
      Alert.alert('Erro', 'Preencha todos os campos!');
      return;
    }

    if (password.length < 6) {
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

    navigation.replace('Home');
  };

  return (
    <ImageBackground
      source={require('../../assets/imagem background.png')}
      style={styles.container}
      resizeMode="cover"
    >

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

      <CustomInput
        placeholder="Nova Senha"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      <CustomInput
        placeholder="Confirme a nova senha"
        value={confirmPassword}
        onChangeText={setConfirmPassword}
        secureTextEntry
      />

      <CustomButton3
        title="Mudar Senha"
        onPress={handleChangePassword}
      />

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
    marginRight: -20,
    marginBottom: 90,
  },

  backText: {
    fontSize: 34,
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
    lineHeight: 20,
  },
});