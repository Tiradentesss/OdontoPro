import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';

export default function Button({ title, onPress, variant = 'primary' }) {
  return (
    <TouchableOpacity 
      style={[styles.button, variant === 'danger' ? styles.danger : styles.primary]} 
      onPress={onPress}
      activeOpacity={0.7}
    >
      <Text style={styles.text}>{title}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    marginVertical: 8,
  },
  primary: {
    backgroundColor: '#0F4C81', // Azul Premium do seu design
  },
  danger: {
    backgroundColor: '#FF3B30', // Botão "Sim" de sair / "Cancelar"
  },
  text: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
    fontFamily: 'System', // Substitua por Plus Jakarta Sans / Poppins se já estiver configurado
  },
});