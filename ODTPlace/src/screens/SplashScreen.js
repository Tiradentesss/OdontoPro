import { useEffect, useRef } from 'react';
import { Image, ImageBackground, StyleSheet, View, Animated, Easing } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';

export default function SplashScreen({ onFinish }) {

  const rotateAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
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
    <ImageBackground
      source={require('../../assets/imagem background.png')}
      style={styles.container}
      resizeMode="cover"
    >
      <View style={styles.card}>
        <BlurView intensity={35} tint="light" style={styles.blur}>
          <LinearGradient
            colors={['#f8f8f8', '#e1e6ee', '#fff']}
            start={{ x: 1, y: 0 }}
            end={{ x: 0, y: 1 }}
            style={styles.gradient}
          >
            <Image
              source={require('../../assets/OdontoHub.png')}
              style={styles.logo}
            />
            <Animated.View style={[styles.loader, { transform: [{ rotate }] }]} />
          </LinearGradient>
        </BlurView>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  card: {
    width: '92%',
    maxWidth: 420,
    borderRadius: 28,
    overflow: 'hidden',
    borderWidth: 1.2,
    borderColor: 'rgba(257, 255, 255, 0.76)',
    transform: [{ translateY: -18 }],
    shadowColor: '#1BC3EA',
    shadowOffset: {
      width: 0,
      height: 12,
    },
    shadowOpacity: 0.15,
    shadowRadius: 25,
    elevation: 12,
  },
  blur: {
    borderRadius: 28,
    overflow: 'hidden',
  },
  gradient: {
    paddingVertical: 45,
    paddingHorizontal: 25,
    alignItems: 'center',
  },
  logo: {
    width: 280,
    height: 280,
    marginBottom: -40,
    resizeMode: 'contain',
  },
  loader: {
    width: 32,
    height: 32,
    borderWidth: 3,
    borderColor: '#cfe3ff',
    borderTopColor: '#07336d',
    borderRadius: 50,
  },
});