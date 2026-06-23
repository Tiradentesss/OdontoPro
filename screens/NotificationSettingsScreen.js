import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  SafeAreaView, 
  Platform, 
  StatusBar, 
  Switch, 
  ScrollView 
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../ThemeContext'; // 1. Importa o hook global de tema

export default function NotificationSettingsScreen({ navigation }) {
  // Estados lógicos de preferências
  const [generalEnabled, setGeneralEnabled] = useState(true);
  const [soundsEnabled, setSoundsEnabled] = useState(true);
  const [vibrationsEnabled, setVibrationsEnabled] = useState(false);
  const [messagesEnabled, setMessagesEnabled] = useState(true);

  // 2. Consome o estado do tema e a paleta de cores dinâmica
  const { isDarkMode, colors } = useTheme();

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={colors.container} 
        translucent={false} 
      />

      {/* Cabeçalho Premium Sincronizado */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={[styles.backButton, { backgroundColor: colors.backButtonBg }]} 
          onPress={() => navigation?.goBack()}
          activeOpacity={0.6}
        >
          <Feather name="arrow-left" size={24} color={colors.brandBlue} />
        </TouchableOpacity>
        
        <View style={styles.headerTitleContainer}>
          <Text style={[styles.headerTitle, { color: colors.text }]}>Notificações</Text>
        </View>
        
        <View style={styles.headerSpacer} />
      </View>

      <ScrollView 
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {/* Título de Seção Sutil e Descrição de Contexto */}
        <View style={styles.introSection}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Preferências de Alerta</Text>
          <Text style={[styles.sectionSubtitle, { color: colors.mutedText }]}>
            Escolha como e quando você deseja ser avisado sobre as atividades do sistema.
          </Text>
        </View>

        {/* Grupo de Configurações: Central de Avisos */}
        <Text style={[styles.sectionHeader, { color: colors.mutedText }]}>Configurações de Alerta</Text>
        <View style={[styles.card, { backgroundColor: colors.card, borderColor: colors.border }]}>
          
          {/* Linha 1: Notificação Geral */}
          <View style={styles.settingRow}>
            <View style={styles.textContainer}>
              <Text style={[styles.settingLabel, { color: colors.text }]}>Notificações Gerais</Text>
              <Text style={[styles.settingDescription, { color: colors.mutedText }]}>
                Permitir que o aplicativo envie avisos importantes na barra de status.
              </Text>
            </View>
            <Switch
              trackColor={{ false: isDarkMode ? '#334155' : '#CBD5E1', true: colors.brandBlue }}
              thumbColor="#FFFFFF"
              ios_backgroundColor={isDarkMode ? '#334155' : '#CBD5E1'}
              onValueChange={setGeneralEnabled}
              value={generalEnabled}
            />
          </View>

          <View style={[styles.divider, { backgroundColor: colors.border }]} />

          {/* Linha 2: Sons */}
          <View style={styles.settingRow}>
            <View style={styles.textContainer}>
              <Text style={[
                styles.settingLabel, 
                { color: colors.text },
                !generalEnabled && { color: colors.mutedText }
              ]}>
                Alertas Sonoros
              </Text>
              <Text style={[styles.settingDescription, { color: colors.mutedText }]}>
                Emitir som padrão do sistema ao receber atualizações de consultas.
              </Text>
            </View>
            <Switch
              trackColor={{ false: isDarkMode ? '#334155' : '#CBD5E1', true: colors.brandBlue }}
              thumbColor="#FFFFFF"
              ios_backgroundColor={isDarkMode ? '#334155' : '#CBD5E1'}
              onValueChange={setSoundsEnabled}
              value={soundsEnabled}
              disabled={!generalEnabled}
            />
          </View>

          <View style={[styles.divider, { backgroundColor: colors.border }]} />

          {/* Linha 3: Vibrações */}
          <View style={styles.settingRow}>
            <View style={styles.textContainer}>
              <Text style={[
                styles.settingLabel, 
                { color: colors.text },
                !generalEnabled && { color: colors.mutedText }
              ]}>
                Vibrar Dispositivo
              </Text>
              <Text style={[styles.settingDescription, { color: colors.mutedText }]}>
                Ativar resposta tátil para lembretes urgentes e confirmações de agenda.
              </Text>
            </View>
            <Switch
              trackColor={{ false: isDarkMode ? '#334155' : '#CBD5E1', true: colors.brandBlue }}
              thumbColor="#FFFFFF"
              ios_backgroundColor={isDarkMode ? '#334155' : '#CBD5E1'}
              onValueChange={setVibrationsEnabled}
              value={vibrationsEnabled}
              disabled={!generalEnabled}
            />
          </View>

          <View style={[styles.divider, { backgroundColor: colors.border }]} />

          {/* Linha 4: Mensagens */}
          <View style={styles.settingRow}>
            <View style={styles.textContainer}>
              <Text style={[
                styles.settingLabel, 
                { color: colors.text },
                !generalEnabled && { color: colors.mutedText }
              ]}>
                Lembretes de Pacientes
              </Text>
              <Text style={[styles.settingDescription, { color: colors.mutedText }]}>
                Avisar quando um paciente responder ao SMS ou WhatsApp de confirmação.
              </Text>
            </View>
            <Switch
              trackColor={{ false: isDarkMode ? '#334155' : '#CBD5E1', true: colors.brandBlue }}
              thumbColor="#FFFFFF"
              ios_backgroundColor={isDarkMode ? '#334155' : '#CBD5E1'}
              onValueChange={setMessagesEnabled}
              value={messagesEnabled}
              disabled={!generalEnabled}
            />
          </View>
          
        </View>

        {/* Informação do Ecossistema */}
        <Text style={[styles.infoFooterText, { color: colors.mutedText }]}>
          As preferências acima são aplicadas apenas para este dispositivo móvel.
        </Text>

      </ScrollView>
    </SafeAreaView>
  );
}

// =========================================================================
// DESIGN SYSTEM & ESTILOS PREMIUM
// =========================================================================
const styles = StyleSheet.create({
  container: { 
    flex: 1, 
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight + 16 : 16,
    paddingBottom: 16,
  },
  backButton: {
    padding: 10,
    borderRadius: 14,
  },
  headerTitleContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: '700',
    letterSpacing: -0.5,
    textAlign: 'center',
  },
  headerSpacer: {
    width: 44, 
  },
  scrollContent: { 
    paddingHorizontal: 24, 
    paddingTop: 8,
    paddingBottom: 60 
  },
  introSection: {
    marginBottom: 20,
    paddingHorizontal: 4,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: -0.3,
  },
  sectionSubtitle: {
    fontSize: 12,
    marginTop: 2,
    lineHeight: 16,
  },
  sectionHeader: { 
    fontSize: 11,
    fontWeight: '700', 
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 8,
    marginTop: 8,
    marginLeft: 4,
  },
  card: {
    borderRadius: 20,
    paddingHorizontal: 18,
    borderWidth: 1,
    marginBottom: 16,
  },
  settingRow: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'space-between', 
    paddingVertical: 18 
  },
  textContainer: {
    flex: 1,
    paddingRight: 16,
  },
  settingLabel: { 
    fontSize: 14, 
    fontWeight: '600', 
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 11,
    lineHeight: 15,
    fontWeight: '400',
  },
  divider: { 
    height: 1, 
  },
  infoFooterText: {
    textAlign: 'center',
    fontSize: 11,
    marginTop: 8,
    fontWeight: '400',
    paddingHorizontal: 16,
  }
});