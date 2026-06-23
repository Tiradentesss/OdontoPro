import React from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  Image, 
  TouchableOpacity, 
  SafeAreaView, 
  Platform, 
  StatusBar, 
  Alert, 
  ScrollView, 
  Dimensions 
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../ThemeContext'; // Importação corrigida apontando para src/

const { width } = Dimensions.get('window');

const PRIMARY_BLUE = "#0F1E36"; 
const ACCENT_BLUE = "#1E40AF";
const MUTED_TEXT = "#64748B";

export default function ConfigScreen({ navigation }) {
  // Consome o estado global do tema e a função de alternar
  const { isDarkMode, toggleTheme, colors } = useTheme();

  const handleLogout = () => {
    Alert.alert(
      "Sair do Aplicativo",
      "Tem certeza que deseja encerrar sua sessão no OdontoPro?",
      [
        { text: "Cancelar", style: "cancel" },
        { 
          text: "Sair", 
          style: "destructive",
          onPress: () => {
            console.log("Usuário deslogado");
          }
        }
      ]
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={colors.container} 
        translucent={false} 
      />

      {/* Cabeçalho Premium */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={[styles.backButton, { backgroundColor: colors.backButtonBg }]} 
          onPress={() => navigation?.goBack()}
          activeOpacity={0.6}
        >
          <Feather name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        
        <View style={styles.headerTitleContainer}>
          <Text style={[styles.headerTitle, { color: colors.text }]}>Ajustes</Text>
        </View>
        
        <View style={styles.headerSpacer} />
      </View>

      <ScrollView 
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {/* Bloco do Perfil do Usuário */}
        <View style={[styles.profileCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <View style={styles.avatarContainer}>
            <Image 
              source={{ uri: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&q=80&w=150&h=150' }} 
              style={[styles.avatar, { borderColor: colors.border }]} 
            />
            <TouchableOpacity style={[styles.editBadge, { backgroundColor: colors.brandBlue }]} activeOpacity={0.8}>
              <Feather name="camera" size={12} color="#FFFFFF" />
            </TouchableOpacity>
          </View>

          <View style={styles.profileInfo}>
            <Text style={[styles.userName, { color: colors.text }]}>Gabriel Gomes</Text>
            <Text style={styles.userEmail}>gabrielgomes@gmail.com</Text>
          </View>
        </View>

        {/* Grupo 1: Gerenciamento da Conta */}
        <Text style={styles.sectionHeader}>Sua Conta</Text>
        <View style={[styles.menuCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <TouchableOpacity 
            style={styles.menuItem} 
            activeOpacity={0.6}
            onPress={() => navigation?.navigate('PersonalDataScreen')}
          >
            <View style={[styles.iconWrapper, { backgroundColor: '#EFF6FF' }]}>
              <Feather name="user" size={18} color={ACCENT_BLUE} />
            </View>
            <View style={styles.menuItemTextContainer}>
              <Text style={[styles.menuItemTitle, { color: colors.text }]}>Informações Pessoais</Text>
              <Text style={styles.menuItemDescription}>Altere seus dados cadastrais e registro profissional.</Text>
            </View>
            <Feather name="chevron-right" size={18} color="#94A3B8" />
          </TouchableOpacity>
        </View>

        {/* Grupo 2: Preferências e Dispositivo */}
        <Text style={styles.sectionHeader}>Preferências</Text>
        <View style={[styles.menuCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          
          <TouchableOpacity 
            style={styles.menuItem} 
            activeOpacity={0.6}
            onPress={() => navigation?.navigate('NotificationSettingsScreen')}
          >
            <View style={[styles.iconWrapper, { backgroundColor: '#FFF7ED' }]}>
              <Feather name="bell" size={18} color="#EA580C" />
            </View>
            <View style={styles.menuItemTextContainer}>
              <Text style={[styles.menuItemTitle, { color: colors.text }]}>Notificações e Alertas</Text>
              <Text style={styles.menuItemDescription}>Gerencie avisos de no-show, confirmações e novos relatórios.</Text>
            </View>
            <Feather name="chevron-right" size={18} color="#94A3B8" />
          </TouchableOpacity>

          {/* Divisor interno usando a cor adaptável da borda */}
          <View style={[styles.divider, { backgroundColor: colors.border }]} />

          {/* ITEM DE SELEÇÃO: Mudar para Tema Black */}
          <TouchableOpacity 
            style={styles.menuItem} 
            activeOpacity={0.6}
            onPress={toggleTheme} // Dispara a alteração global no aplicativo
          >
            <View style={[styles.iconWrapper, { backgroundColor: isDarkMode ? '#334155' : '#F1F5F9' }]}>
              <Feather name={isDarkMode ? "sun" : "moon"} size={18} color={isDarkMode ? "#F59E0B" : "#475569"} />
            </View>
            <View style={styles.menuItemTextContainer}>
              <Text style={[styles.menuItemTitle, { color: colors.text }]}>Modo Escuro</Text>
              <Text style={styles.menuItemDescription}>Alterne a interface entre o modo claro e o tema black.</Text>
            </View>
            
            {/* Indicador visual ON/OFF dinâmico */}
            <View style={[styles.toggleIndicator, { backgroundColor: isDarkMode ? '#10B981' : '#CBD5E1' }]}>
              <Text style={styles.toggleIndicatorText}>{isDarkMode ? "ON" : "OFF"}</Text>
            </View>
          </TouchableOpacity>

        </View>

        {/* Grupo 3: Ações de Segurança */}
        <Text style={styles.sectionHeader}>Segurança</Text>
        <View style={[styles.menuCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <TouchableOpacity style={styles.menuItem} activeOpacity={0.6} onPress={handleLogout}>
            <View style={[styles.iconWrapper, { backgroundColor: '#FEE2E2' }]}>
              <Feather name="log-out" size={18} color="#DC2626" />
            </View>
            <View style={styles.menuItemTextContainer}>
              <Text style={[styles.menuItemTitle, styles.logoutText]}>Sair da Conta</Text>
              <Text style={styles.menuItemDescription}>Desconecte seu usuário com segurança deste aparelho.</Text>
            </View>
            <Feather name="chevron-right" size={18} color="#FCA5A5" />
          </TouchableOpacity>
        </View>

        {/* Informação da Versão do App */}
        <Text style={styles.versionText}>OdontoPro v1.0.0 — Premium Dashboard Ecosystem</Text>

      </ScrollView>
    </SafeAreaView>
  );
}

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
    paddingBottom: 120,
  },
  profileCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
    marginBottom: 20,
  },
  avatarContainer: {
    position: 'relative',
    marginRight: 16,
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    borderWidth: 2,
  },
  editBadge: {
    position: 'absolute',
    bottom: -2,
    right: -2,
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FFFFFF',
  },
  profileInfo: {
    flex: 1,
    justifyContent: 'center',
  },
  userName: {
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: -0.3,
  },
  userEmail: {
    fontSize: 12,
    color: MUTED_TEXT,
    fontWeight: '400',
    marginTop: 2,
  },
  sectionHeader: {
    fontSize: 11,
    fontWeight: '700',
    color: MUTED_TEXT,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: 8,
    marginTop: 8,
    marginLeft: 4,
  },
  menuCard: {
    borderRadius: 20, 
    paddingHorizontal: 16,
    marginBottom: 16,
    borderWidth: 1,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
  },
  divider: {
    height: 1,
    width: '100%',
  },
  iconWrapper: {
    width: 38,
    height: 38,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  menuItemTextContainer: {
    flex: 1,
    paddingRight: 8,
  },
  menuItemTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 2,
  },
  menuItemDescription: {
    fontSize: 11,
    color: MUTED_TEXT,
    lineHeight: 15,
    fontWeight: '400',
  },
  toggleIndicator: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    minWidth: 38,
    alignItems: 'center',
  },
  toggleIndicatorText: {
    fontSize: 9,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  logoutText: {
    color: '#DC2626',
  },
  versionText: {
    textAlign: 'center',
    fontSize: 11,
    color: MUTED_TEXT,
    marginTop: 20,
    fontWeight: '500',
  },
});