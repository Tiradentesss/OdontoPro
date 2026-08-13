import React from 'react';
import {
  TouchableOpacity,
  Image,
  StyleSheet,
  View,
} from 'react-native';
import { useTheme } from './ThemeContext';

export default function NotificationButton({
  onPress,
  notifications = [],
}) {
  const { isDarkMode, colors } = useTheme();

  // Verifica se existe alguma notificação não lida
  const hasNotification = notifications.some(item => !item.read);
  
  // Light mode: white background with blue border and blue icon
  // Dark mode: dark background with border and light icon
  const buttonBg = isDarkMode ? colors.container : '#FFFFFF';
  const buttonBorder = isDarkMode ? colors.border : '#0EA5E9';
  const iconContainerBg = isDarkMode ? '#334155' : '#0EA5E9';
  const iconTint = isDarkMode ? '#94A3B8' : '#FFFFFF';

  return (
    <TouchableOpacity
      style={[styles.button, { backgroundColor: buttonBg, borderColor: buttonBorder }]}
      onPress={onPress}
      activeOpacity={0.8}
    >
      <View style={[styles.iconContainer, { backgroundColor: iconContainerBg }]}> 
        <Image
          source={require('../../assets/IconNotificacao.png')}
          style={[styles.icon, { tintColor: iconTint }]}
          resizeMode="contain"
        />
      </View>

      {hasNotification && <View style={styles.badge} />}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    width: 44,
    height: 44,
    borderRadius: 22,
    borderWidth: 1,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },

  iconContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },

  icon: {
    width: 18,
    height: 18,
  },

  badge: {
    position: 'absolute',
    top: 4,
    right: 4,
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#FF3B30',
    borderWidth: 2,
    borderColor: '#FFF',
  },
});