import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Feather, MaterialCommunityIcons } from '@expo/vector-icons';
import { useTheme } from '../ThemeContext'; // 1. Vinculação ao tema global do ecossistema

export default function FeatureCard({ title, iconName, iconType = 'feather', onPress }) {
  // Consome o estado do tema
  const { isDarkMode, colors } = useTheme();

  // Renderização segura de ícones com Fallback
  const renderIcon = () => {
    const iconColor = '#FFFFFF'; 
    const fallbackName = 'help-circle'; // Evita quebra caso a prop venha errada

    if (iconType === 'material') {
      return <MaterialCommunityIcons name={iconName || 'help'} size={20} color={iconColor} />;
    }
    return <Feather name={iconName || fallbackName} size={20} color={iconColor} />;
  };

  // Define dinamicamente o fundo do card com base no tema
  // Mantemos o azul institucional no modo claro, mas trazemos um tom escuro premium se o Dark Mode estiver ativo
  const cardBgColor = isDarkMode ? colors.card : colors.brandBlue;
  const strokeColor = isDarkMode ? colors.border : 'rgba(255, 255, 255, 0.15)';
  const textColor = isDarkMode ? colors.text : '#FFFFFF';
  const mutedTextColor = isDarkMode ? colors.mutedText : 'rgba(255, 255, 255, 0.6)';

  return (
    <TouchableOpacity 
      style={[
        styles.card, 
        { 
          backgroundColor: cardBgColor, 
          shadowColor: cardBgColor,
          borderColor: isDarkMode ? colors.border : 'transparent',
          borderWidth: isDarkMode ? 1 : 0
        }
      ]} 
      onPress={onPress}
      activeOpacity={0.85}
    >
      {/* Luz ambiente superior adaptativa */}
      <View style={[styles.topLightStreaks, { backgroundColor: strokeColor }]} />
      {!isDarkMode && <View style={styles.ambientGlow} />}
      
      <View style={styles.contentRow}>
        {/* Bloco de Ícone na Esquerda */}
        <View style={[styles.iconWrapper, { backgroundColor: isDarkMode ? colors.backButtonBg : 'rgba(255, 255, 255, 0.12)' }]}>
          {renderIcon()}
        </View>

        {/* Textos de Identificação */}
        <View style={styles.textContainer}>
          <Text style={[styles.cardTitle, { color: textColor }]}>{title}</Text>
          <View style={styles.actionRow}>
            <Text style={[styles.cardAction, { color: mutedTextColor }]}>Acessar recurso</Text>
            <Feather name="chevron-right" size={12} color={textColor} style={styles.chevronIcon} />
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    width: '100%',
    height: 84, 
    borderRadius: 18,
    marginBottom: 12,
    position: 'relative',
    overflow: 'hidden',
    // Sombra de dispersão limpa
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 3,
  },
  topLightStreaks: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 1,
  },
  ambientGlow: {
    position: 'absolute',
    right: -30,
    bottom: -30,
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#FFFFFF',
    opacity: 0.05, 
  },
  contentRow: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    zIndex: 2,
  },
  iconWrapper: {
    width: 44,
    height: 44,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
    marginRight: 16,
  },
  textContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: -0.3,
  },
  actionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  cardAction: {
    fontSize: 12,
    fontWeight: '500',
    letterSpacing: -0.1,
  },
  chevronIcon: {
    opacity: 0.5,
    marginLeft: 2,
    marginTop: 1,
  },
});