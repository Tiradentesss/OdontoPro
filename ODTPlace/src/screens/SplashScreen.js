import { useEffect, useRef } from 'react';
import * as ExpoSplashScreen from 'expo-splash-screen';
import { Image, StyleSheet, View, Animated, Easing } from 'react-native';

export default function SplashScreen({ onFinish }) {

  const rotateAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    ExpoSplashScreen.hideAsync().catch(() => {});

    const animation = Animated.loop(
      Animated.timing(rotateAnim, {
        toValue: 1,
        duration: 1000,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    );
    animation.start();

    const timeout = setTimeout(onFinish, 1800);
    return () => {
      clearTimeout(timeout);
      animation.stop();
    };
  }, [onFinish, rotateAnim]);

  const rotate = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });


  return (
    <View style={styles.container}>
      <Image
        source={require('../../assets/LogoOdontoHubApp.png')}
        style={styles.logo}
      />
      <Animated.View style={[styles.loader, { transform: [{ rotate }] }]} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
  },
  logo: {
    width: 180,
    height: 180,
    marginBottom: 24,
    resizeMode: 'contain',
  },
  loader: {
    marginTop: 5,
    width: 32,
    height: 32,
    borderWidth: 3,
    borderColor: '#cfe3ff',
    borderTopColor: '#07336d',
    borderRadius: 50,
  },
});