import React, { useEffect, useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TextInput, 
  TouchableOpacity, 
  SafeAreaView, 
  Platform, 
  StatusBar, 
  ScrollView, 
  Alert 
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { useTheme } from '../components/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { getDoctorById, updateDoctorProfile } from '../services/api';

export default function PersonalDataScreen({ navigation }) {
  const { user, login } = useAuth();
  const [name, setName] = useState('');
  const [cro, setCro] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [specialties, setSpecialties] = useState([]);
  const [focusedInput, setFocusedInput] = useState(null);
  const [saving, setSaving] = useState(false);

  const { isDarkMode, colors } = useTheme();

  useEffect(() => {
    const hydrateFromUser = () => {
      setName(user?.nome || user?.name || '');
      setEmail(user?.email || '');
      setPhone(user?.telefone || '');
      setCro(user?.crm_cro || user?.cpf || '');
      setSpecialties(Array.isArray(user?.especialidades) ? user.especialidades.filter(Boolean) : []);
    };

    hydrateFromUser();

    if (!user?.id) return;

    const loadDoctorProfile = async () => {
      try {
        const doctor = await getDoctorById(user.id);
        if (!doctor) return;

        setName(doctor.nome || user?.nome || '');
        setEmail(doctor.email || user?.email || '');
        setPhone(doctor.telefone || user?.telefone || '');
        setCro(doctor.crm_cro || user?.crm_cro || '');
        setSpecialties(Array.isArray(doctor.especialidades) ? doctor.especialidades.filter(Boolean) : []);
      } catch (error) {
        console.log('Error loading doctor profile:', error);
      }
    };

    loadDoctorProfile();
  }, [user?.id, user?.nome, user?.email, user?.telefone, user?.crm_cro, user?.cpf, user?.especialidades]);

  const handleSave = async () => {
    if (!user?.id) {
      Alert.alert('Erro', 'Faça login novamente para atualizar seus dados.');
      return;
    }

    try {
      setSaving(true);
      const payload = {
        nome: name,
        email,
        telefone: phone,
        crm_cro: cro,
      };

      const updated = await updateDoctorProfile(user.id, payload);
      login({ ...user, ...updated, nome: updated?.nome || name, email: updated?.email || email, telefone: updated?.telefone || phone, crm_cro: updated?.crm_cro || cro });
      Alert.alert('Informações Atualizadas', 'Seus dados cadastrais foram salvos com sucesso no sistema.', [{ text: 'Ok', onPress: () => navigation.goBack() }]);
    } catch (error) {
      console.log('Error updating doctor profile:', error);
      Alert.alert('Erro', 'Não foi possível atualizar seus dados no momento.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.container }]}>
      <StatusBar 
        barStyle={isDarkMode ? 'light-content' : 'dark-content'} 
        backgroundColor={colors.container} 
        translucent={false} 
      />

      {/* Cabeçalho Premium Alinhado */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={[styles.backButton, { backgroundColor: colors.backButtonBg }]} 
          onPress={() => navigation?.goBack()}
          activeOpacity={0.6}
        >
          <Feather name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        
        <View style={styles.headerTitleContainer}>
          <Text style={[styles.headerTitle, { color: colors.text }]}>Informações Pessoais</Text>
        </View>
        
        <View style={styles.headerSpacer} />
      </View>

      <ScrollView 
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
      >
        {/* Título de seção sutil e descrição contextual */}
        <View style={styles.introSection}>
          <Text style={[styles.sectionTitle, { color: colors.text }]}>Seus Dados Cadastrais</Text>
          <Text style={[styles.sectionSubtitle, { color: colors.mutedText }]}>Mantenha seus canais de contato e documentação atualizados.</Text>
        </View>

        {/* Formulário em Bloco Único Premium */}
        <View style={[styles.formCard, { backgroundColor: colors.card, borderColor: colors.border }]}>
          
          {/* Input: Nome */}
          <View style={styles.inputGroup}>
            <Text style={[styles.inputLabel, { color: colors.mutedText }]}>Nome Completo</Text>
            <TextInput 
              style={[
                styles.input, 
                { 
                  backgroundColor: isDarkMode ? '#1E293B' : '#F8FAFC', 
                  borderColor: colors.border, 
                  color: colors.text 
                },
                focusedInput === 'name' && [styles.inputFocused, { borderColor: colors.brandBlue }]
              ]} 
              value={name} 
              onChangeText={setName}
              onFocus={() => setFocusedInput('name')}
              onBlur={() => setFocusedInput(null)}
              placeholder="Digite seu nome completo"
              placeholderTextColor={isDarkMode ? '#64748B' : '#94A3B8'}
            />
          </View>

          {/* Input: CRO */}
          <View style={styles.inputGroup}>
            <Text style={[styles.inputLabel, { color: colors.mutedText }]}>CRO</Text>
            <TextInput 
              style={[
                styles.input, 
                { 
                  backgroundColor: isDarkMode ? '#1E293B' : '#F8FAFC', 
                  borderColor: colors.border, 
                  color: colors.text 
                },
                focusedInput === 'cro' && [styles.inputFocused, { borderColor: colors.brandBlue }]
              ]} 
              value={cro} 
              onChangeText={setCro}
              onFocus={() => setFocusedInput('cro')}
              onBlur={() => setFocusedInput(null)}
              placeholder="Informe seu CRO"
              placeholderTextColor={isDarkMode ? '#64748B' : '#94A3B8'}
            />
          </View>

          {/* Input: Email */}
          <View style={styles.inputGroup}>
            <Text style={[styles.inputLabel, { color: colors.mutedText }]}>E-mail Profissional</Text>
            <TextInput 
              style={[
                styles.input, 
                { 
                  backgroundColor: isDarkMode ? '#1E293B' : '#F8FAFC', 
                  borderColor: colors.border, 
                  color: colors.text 
                },
                focusedInput === 'email' && [styles.inputFocused, { borderColor: colors.brandBlue }]
              ]} 
              value={email} 
              onChangeText={setEmail}
              onFocus={() => setFocusedInput('email')}
              onBlur={() => setFocusedInput(null)}
              keyboardType="email-address"
              autoCapitalize="none"
              placeholder="seuemail@gmail.com"
              placeholderTextColor={isDarkMode ? '#64748B' : '#94A3B8'}
            />
          </View>

          {/* Input: Celular */}
          <View style={styles.inputGroup}>
            <Text style={[styles.inputLabel, { color: colors.mutedText }]}>Número de Celular</Text>
            <TextInput 
              style={[
                styles.input, 
                { 
                  backgroundColor: isDarkMode ? '#1E293B' : '#F8FAFC', 
                  borderColor: colors.border, 
                  color: colors.text 
                },
                focusedInput === 'phone' && [styles.inputFocused, { borderColor: colors.brandBlue }]
              ]} 
              value={phone} 
              onChangeText={setPhone}
              onFocus={() => setFocusedInput('phone')}
              onBlur={() => setFocusedInput(null)}
              keyboardType="phone-pad"
              placeholder="(91) 90000-0000"
              placeholderTextColor={isDarkMode ? '#64748B' : '#94A3B8'}
            />
          </View>

          <View style={[styles.infoCard, { backgroundColor: isDarkMode ? '#1E293B' : '#F8FAFC', marginTop: 4 }]}> 
            <Text style={[styles.infoCardLabel, { color: colors.mutedText }]}>Especialidades</Text>
            <Text style={[styles.infoCardValue, { color: colors.text }]}>
              {specialties.length > 0 ? specialties.join(', ') : 'Nenhuma especialidade cadastrada'}
            </Text>
          </View>

          {/* Nota de Segurança de Dados Privados */}
          <View style={[styles.securityNotice, { backgroundColor: isDarkMode ? '#1E293B' : '#F8FAFC' }]}>
            <Feather name="shield" size={13} color={colors.mutedText} />
            <Text style={[styles.securityNoticeText, { color: colors.mutedText }]}>Os dados acima são protegidos por criptografia de ponta a ponta.</Text>
          </View>

        </View>

        {/* Botão de Ação Inferior Sóbrio e Elegante */}
        <TouchableOpacity 
          style={[styles.saveButton, { backgroundColor: colors.brandBlue, shadowColor: colors.brandBlue }]} 
          activeOpacity={0.85}
          onPress={handleSave}
          disabled={saving}
        >
          <Text style={styles.saveButtonText}>{saving ? 'Salvando...' : 'Salvar Alterações'}</Text>
        </TouchableOpacity>

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
    paddingBottom: 60,
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
  formCard: {
    borderRadius: 20,
    padding: 20,
    marginBottom: 24,
    borderWidth: 1,
  },
  inputGroup: {
    marginBottom: 18,
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 6,
    marginLeft: 2,
  },
  input: {
    height: 48,
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 14,
    fontWeight: '500',
    borderWidth: 1,
  },
  inputFocused: {
    backgroundColor: 'transparent',
    borderWidth: 1.5,
  },
  infoGrid: {
    flexDirection: 'row',
    gap: 10,
  },
  infoCard: {
    flex: 1,
    borderRadius: 12,
    padding: 12,
  },
  infoCardLabel: {
    fontSize: 11,
    fontWeight: '600',
    marginBottom: 4,
  },
  infoCardValue: {
    fontSize: 13,
    fontWeight: '600',
    lineHeight: 18,
  },
  securityNotice: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    padding: 10,
    borderRadius: 10,
  },
  securityNoticeText: {
    fontSize: 11,
    marginLeft: 6,
    fontWeight: '400',
  },
  saveButton: {
    height: 52,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 2,
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
    letterSpacing: -0.2,
  },
});