import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Dimensions, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../ThemeContext'; 

const { width } = Dimensions.get('window');

const TAB_CONFIG = {
  PainelTab: { label: 'Início', icon: 'home' },
  AgendaTab: { label: 'Agenda', icon: 'calendar' },
  HistóricoTab: { label: 'Relatórios', icon: 'stats-chart' },
  ConfigTab: { label: 'Ajustes', icon: 'settings' },
};

export default function CustomTabBar({ state, descriptors, navigation }) {
  const { isDarkMode, colors } = useTheme();

  return (
    <View style={styles.container}>
      {/* Barra flutuante com blur/sombra extremamente suave e bordas cirúrgicas */}
      <View style={[
        styles.tabBar, 
        { 
          backgroundColor: colors.card, 
          borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.06)' : 'rgba(15, 23, 42, 0.06)',
          shadowColor: isDarkMode ? '#000000' : '#0F172A'
        }
      ]}>
        {state.routes.map((route, index) => {
          const { options } = descriptors[route.key];
          if (options.tabBarVisible === false) return null;

          const isFocused = state.index === index;
          const config = TAB_CONFIG[route.name] || { label: route.name, icon: 'square' };

          // Cores baseadas no rigor do minimalismo
          const activeColor = colors.brandBlue; 
          const inactiveColor = isDarkMode ? '#64748B' : '#94A3B8';

          const onPress = () => {
            const event = navigation.emit({
              type: 'tabPress',
              target: route.key,
              canPreventDefault: true,
            });

            if (!isFocused && !event.defaultPrevented) {
              navigation.navigate({ name: route.name, merge: true });
            }
          };

          return (
            <TouchableOpacity
              key={route.key}
              accessibilityRole="button"
              accessibilityState={isFocused ? { selected: true } : {}}
              onPress={onPress}
              style={styles.tabItem}
              activeOpacity={0.7}
            >
              {/* Indicador superior ultra-fino e discreto (apenas 2px de espessura) */}
              <View style={[
                styles.topIndicator, 
                { backgroundColor: isFocused ? activeColor : 'transparent' }
              ]} />

              <View style={styles.contentContainer}>
                <Ionicons 
                  name={isFocused ? config.icon : `${config.icon}-outline`} 
                  size={22} 
                  color={isFocused ? activeColor : inactiveColor} 
                  style={isFocused ? styles.activeIcon : null}
                />
                
                <Text style={[
                  styles.label, 
                  { 
                    color: isFocused ? (isDarkMode ? '#F8FAFC' : '#0F172A') : inactiveColor, 
                    fontWeight: isFocused ? '600' : '500',
                  }
                ]}>
                  {config.label}
                </Text>
              </View>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: Platform.OS === 'ios' ? 24 : 16, 
    left: 0,
    right: 0,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
  },
  tabBar: {
    flexDirection: 'row',
    width: width * 0.92, 
    height: 64, // Altura reduzida para um perfil mais slim e sofisticado
    borderRadius: 20, 
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 8,
    borderWidth: 1,
    // Sombra de estúdio: muito suave, quase imperceptível, focada em profundidade limpa
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 12,
    elevation: 4,
  },
  tabItem: {
    flex: 1,
    height: '100%',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  topIndicator: {
    position: 'absolute',
    top: 0,
    width: 24, // Pequeno traço minimalista no topo do item ativo
    height: 2,
    borderRadius: 1,
  },
  contentContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 4,
  },
  activeIcon: {
    // Leve ganho de peso visual por iluminação/presença (opcional)
    transform: [{ scale: 1.02 }],
  },
  label: {
    fontSize: 10, // Diminuído para dar hierarquia elegante em relação ao ícone
    marginTop: 4,
    letterSpacing: 0.2,
  },
});