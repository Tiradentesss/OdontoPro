import React from 'react';
<<<<<<< HEAD
import { TouchableOpacity, Image, StyleSheet } from 'react-native';
import { useTheme } from './ThemeContext';

export default function NotificationButton({ onPress, style }) {
    const { isDarkMode } = useTheme();

    return (
        <TouchableOpacity style={[styles.button, { backgroundColor: isDarkMode ? '#1E293B' : '#ffffff' }, style]} onPress={onPress} activeOpacity={0.8}>
            <Image
                source={require('../../assets/IconNotificacao.png')}
                style={[styles.icon, { tintColor: isDarkMode ? '#38BDF8' : '#0EA5E9' }]}
                resizeMode="contain"
            />
        </TouchableOpacity>
    );
=======
import {
  TouchableOpacity,
  Image,
  StyleSheet,
  View,
} from 'react-native';

export default function NotificationButton({
  onPress,
  notifications = [],
}) {

  // Verifica se existe alguma notificação não lida
  const hasNotification = notifications.some(item => !item.read);

  return (
    <TouchableOpacity
      style={styles.button}
      onPress={onPress}
      activeOpacity={0.8}
    >
      <Image
        source={require('../../assets/IconNotificacao.png')}
        style={styles.icon}
        resizeMode="contain"
      />

      {hasNotification && <View style={styles.badge} />}
    </TouchableOpacity>
  );
>>>>>>> bc929680add156067d33a13b19141625ac1c6c55
}

const styles = StyleSheet.create({
  button: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#00BCEB',
    borderWidth: 2,
    borderColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },

  icon: {
    width: 22,
    height: 22,
    tintColor: '#FFF',
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