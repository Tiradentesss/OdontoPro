import { useEffect } from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

export default function SplashScreen({ navigation }) {

  useEffect(() => {
    setTimeout(() => {
      navigation.replace('Login');
    }, 2000);
  }, []);

  return (
    <LinearGradient
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 0.6 }}
      colors={['#0246A3', '#1BC4EB']} // cores do gradiente
      style={styles.container}
    >
      <Image 
        source={require('../../assets/logo icon.png')} 
        style={{ width: 150, height: 150, marginBottom: 20 }} 
      />
      <Text style={styles.logo}>Odonto Place</Text>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: {
    fontSize: 28,
    color: '#07336d',
    fontWeight: 'bold',
  },
});