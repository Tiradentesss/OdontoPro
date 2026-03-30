import { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function SplashScreen({ navigation }) {

  // Executa ao abrir a tela
  useEffect(() => {
    setTimeout(() => {
      navigation.replace('Login'); // troca de tela
    }, 2000); // 2 segundos
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>Meu App 🚀</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#007bff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: {
    fontSize: 28,
    color: '#fff',
    fontWeight: 'bold',
  },
});