import { useEffect, useRef  } from 'react';
import { View, Text, Image, StyleSheet, Animated, Easing } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

export default function SplashScreen({ navigation }) {

  const rotateAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    setTimeout(() => {
      navigation.replace('Login');
    }, 2000);
  }, []);

  const startAnimation = () => {
    rotateAnim.setValue(0);

    Animated.loop(
      Animated.timing(rotateAnim, {
        toValue: 1,
        duration: 1000,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    ).start();
  };

  const rotate = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });


  return (
    <LinearGradient
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 0.6 }}
      colors={['#0246A3', '#1BC4EB']}
      style={styles.container}
    >
      <Image 
        source={require('../../assets/LogoODTPlace.png')} 
        style={{ width: 150, height: 150, marginBottom: 20 }} 
      />
      <Text style={styles.logo}>Odonto Place</Text>
      <Text style={styles.textobaixo}>Sistema de Agendamento</Text>

      <Animated.View style={[styles.loader, { transform: [{ rotate }] }]} />

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
    fontSize: 50,
    color: '#023C8B',
    fontWeight: 'regular',
  },
  textobaixo: {
    fontSize: 20,
    color: '#023C8B',
    fontWeight: 'regular',
  },
  loader: {
    marginTop: 25,
    width: 40,
    height: 40,
    borderWidth: 4,
    borderColor: '#cfe3ff',
    borderTopColor: '#07336d',
    borderRadius: 50,
  },
});