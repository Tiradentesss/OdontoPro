import { useEffect } from 'react';
import { Image, StyleSheet, Text } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import CustomButton from '../components/CustomButton.js';
import CustomButton2 from '../components/CustomButton2.js';

// Esse componente representa a tela inicial
export default function PreLogin({ navigation }) {

  return (
    <LinearGradient
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 0.6 }}
      colors={['#0246A3', '#1BC4EB']}
      style={styles.container}>
      <Image source={require('../../assets/Logo.png')} style={{ width: 150, height: 150, marginBottom: 20 }} />
      <Text style={styles.logo}>OdontoPlace</Text>
      <Text style={styles.textobaixo}>Sistema de Agendamento</Text>
      <CustomButton
        title="Sou Paciente"
        onPress={() => navigation.navigate('Login')}
        style={{ width: 300, alignSelf: 'center' }}
      />
      <CustomButton2
        title="Sou Profissional"
        onPress={() => navigation.navigate('LoginProfissional')}
      />
    </LinearGradient>

  );
}
// Estilos da tela
const styles = StyleSheet.create({
  container: {
    flex: 1, // ocupa toda a tela
    alignItems: 'center', // centraliza horizontal
    justifyContent: 'center', // centraliza vertical
  },
  logo: {
    fontSize: 50,
    color: '#023C8B',
    fontWeight: 'regular',
    fontFamily: 'poppins-regular',
  },
  textobaixo: {
    fontSize: 20,
    color: '#023C8B',
    fontWeight: 'regular',
    fontFamily: 'poppins-regular',
  },
});