import React from 'react';
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