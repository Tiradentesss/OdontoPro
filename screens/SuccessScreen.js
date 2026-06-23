import React, { useEffect, useRef } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  SafeAreaView, 
  StatusBar, 
  Animated, 
  Easing 
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../ThemeContext'; // Importação do tema global

export default function SuccessScreen({ navigation }) {
  // Consome as propriedades globais do tema
  const { isDarkMode, colors } = useTheme();

  // Constantes de animação do React Native
  const scaleAnim = useRef(new Animated.Value(0)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;
  
  // Limpa o histórico de navegação e joga o profissional de volta à Agenda
  const handleGoBackToAgenda = () => {
    navigation.reset({
      index: 0,
      routes: [{ name: 'Main', state: { routes: [{ name: 'AgendaTab' }] } }],
    });
  };

  useEffect(() => {
    // 1. Inicia as animações em paralelo assim que a tela monta
    Animated.parallel([
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 45,
        friction: 6,
        useNativeDriver: true,
      }),
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 500,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      })
    ]).start();

    // 2. Redirecionamento automático após 2.5 segundos (2500ms)
    const autoRedirectTimer = setTimeout(() => {
      handleGoBackToAgenda();
    }, 2500);

    // Limpa o timer caso o usuário clique no botão antes do tempo acabar
    return () => clearTimeout(autoRedirectTimer);
  }, []);

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={colors.container} 
        translucent={false} 
      />
      
      <Animated.View style={[styles.content, { opacity: fadeAnim }]}>
        {/* Círculo de Sucesso Animado (Mantém o verde esmeralda semântico) */}
        <Animated.View style={[
          styles.successCircle, 
          { 
            transform: [{ scale: scaleAnim }],
            shadowColor: '#10B981' 
          }
        ]}>
          <Feather name="check" size={54} color="#FFFFFF" />
        </Animated.View>

        {/* Textos com tipografia e espaçamentos Premium adaptados */}
        <Text style={[styles.successTitle, { color: colors.text }]}>Consulta Confirmada!</Text>
        <Text style={[styles.successSubtitle, { color: colors.mutedText }]}>
          O status do agendamento foi atualizado e o paciente já foi notificado.
        </Text>
      </Animated.View>

      {/* Footer Minimalista com Botão de Ação */}
      <View style={styles.footer}>
        <TouchableOpacity 
          style={[styles.actionButton, { backgroundColor: colors.brandBlue, shadowColor: colors.brandBlue }]} 
          activeOpacity={0.8}
          onPress={handleGoBackToAgenda}
        >
          <Text style={styles.actionButtonText}>Voltar para Agenda</Text>
          <Feather name="arrow-right" size={18} color="#FFFFFF" style={{ marginLeft: 8 }} />
        </TouchableOpacity>
        <Text style={[styles.autoRedirectText, { color: colors.mutedText }]}>
          Redirecionando automaticamente...
        </Text>
      </View>
    </SafeAreaView>
  );
}

// =========================================================================
// DESIGN SYSTEM & ESTILOS PREMIUM (TOTALMENTE OTIMIZADOS PARA TEMAS)
// =========================================================================
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  successCircle: {
    width: 110,
    height: 110,
    borderRadius: 55,
    backgroundColor: '#10B981', // Verde esmeralda preservado para consistência de sucesso
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 28,
    // Efeito de elevação premium
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 5,
  },
  successTitle: {
    fontSize: 24,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: 12,
    letterSpacing: -0.5,
  },
  successSubtitle: {
    fontSize: 15,
    fontWeight: '500',
    textAlign: 'center',
    lineHeight: 22,
    paddingHorizontal: 16,
  },
  footer: {
    paddingHorizontal: 24,
    paddingBottom: 40,
    alignItems: 'center',
  },
  actionButton: {
    flexDirection: 'row',
    height: 54,
    width: '100%',
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 10,
    elevation: 3,
    marginBottom: 16,
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
  },
  autoRedirectText: {
    fontSize: 12,
    fontWeight: '500',
    letterSpacing: 0.3,
    opacity: 0.8,
  },
});