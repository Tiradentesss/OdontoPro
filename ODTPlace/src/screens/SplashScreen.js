import { useEffect } from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';

export default function SplashScreen({ navigation }) {

  // Executa ao abrir a tela
  useEffect(() => {
    setTimeout(() => {
      navigation.replace('Login'); // troca de tela
    }, 2000); // 2 segundos
  }, []);

  return (
    <View style={styles.container}>
      <Image source={require('../../assets/logo icon.png')} style={{ width: 150, height: 150, marginBottom: 20 }} />
      <Text style={styles.logo}>Odonto Place</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ecf4fd',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: {
    fontSize: 28,
    color: '#07336d',
    fontWeight: 'bold',
  },
});