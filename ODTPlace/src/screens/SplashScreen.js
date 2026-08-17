import { useEffect, useRef } from 'react';
import {
  Animated,
  Easing,
  Image,
  ImageBackground,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';

export default function SplashScreen({ navigation }) {
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

    const timeout = setTimeout(() => {
      navigation.replace('PreLogin');
    }, 2200);

    return () => {
      animation.stop();
      clearTimeout(timeout);
    };
  }, [navigation, rotateAnim]);

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

            <Text style={styles.name}>Odonto Place</Text>

            <View style={styles.loaderWrap}>
              <Animated.View style={[styles.loader, { transform: [{ rotate }] }]} />
            </View>
          </LinearGradient>
        </BlurView>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  card: {
    width: '92%',
    maxWidth: 420,
    borderRadius: 28,
    overflow: 'hidden',
    borderWidth: 1.2,
    borderColor: 'rgba(255, 255, 255, 0.76)',
    transform: [{ translateY: -18 }],
    shadowColor: '#1BC3EA',
    shadowOffset: { width: 0, height: 12 },
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
    marginBottom: -28,
    resizeMode: 'contain',
  },
  name: {
    fontSize: 26,
    fontWeight: '600',
    color: '#07336d',
    letterSpacing: 0.5,
    textAlign: 'center',
    marginBottom: 18,
  },
  loaderWrap: {
    width: 52,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loader: {
    width: 40,
    height: 40,
    borderWidth: 4,
    borderColor: '#cfe3ff',
    borderTopColor: '#07336d',
    borderRadius: 50,
  },
});