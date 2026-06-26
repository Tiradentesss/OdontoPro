import React, { useState } from 'react';
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
import { useTheme } from '../components/ThemeContext'; // 1. Importa o hook global de tema

export default function PersonalDataScreen({ navigation }) {
  // Estados para gerenciar as informações do formulário
  const [name, setName] = useState('Gabriel Gomes');
  const [cpf, setCpf] = useState('100.000.111-90');
  const [email, setEmail] = useState('gabrielgomes@gmail.com');
  const [phone, setPhone] = useState('(91) 98765-4321');
  const [gender, setGender] = useState('Masculino');
  const [address, setAddress] = useState('45 Nova Batista Campos, Belém Pará');

  // Estados de Foco para feedback visual premium
  const [focusedInput, setFocusedInput] = useState(null);

  // 2. Consome o estado do tema e a paleta de cores dinâmica
  const { isDarkMode, colors } = useTheme();

  const handleSave = () => {
    Alert.alert(
      'Informações Atualizadas', 
      'Seus dados cadastrais foram salvos com sucesso no sistema.',
      [{ text: 'Ok', onPress: () => navigation.goBack() }]
    );
  };

  const renderGenderButton = (option) => {
    const isSelected = gender === option;
    return (
      <TouchableOpacity
        key={option}
        style={[
          styles.genderButton,
          isSelected && { backgroundColor: colors.brandBlue }
        ]}
        activeOpacity={0.7}
        onPress={() => setGender(option)}
      >
        <Text style={[
          styles.genderButtonText,
          { color: isSelected ? '#FFFFFF' : colors.mutedText },
          isSelected && { fontWeight: '600' }
        ]}>
          {option}
        </Text>
      </TouchableOpacity>
    );
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

          {/* Input: CPF */}
          <View style={styles.inputGroup}>
            <Text style={[styles.inputLabel, { color: colors.mutedText }]}>CPF</Text>
            <TextInput 
              style={[
                styles.input, 
                { 
                  backgroundColor: isDarkMode ? '#1E293B' : '#F8FAFC', 
                  borderColor: colors.border, 
                  color: colors.text 
                },
                focusedInput === 'cpf' && [styles.inputFocused, { borderColor: colors.brandBlue }]
              ]} 
              value={cpf} 
              onChangeText={setCpf}
              onFocus={() => setFocusedInput('cpf')}
              onBlur={() => setFocusedInput(null)}
              keyboardType="numeric"
              placeholder="000.000.000-00"
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

          {/* Seletor Inline de Gênero Premium */}
          <View style={styles.inputGroup}>
            <Text style={[styles.inputLabel, { color: colors.mutedText }]}>Gênero</Text>
            <View style={[styles.genderContainer, { backgroundColor: isDarkMode ? '#1E293B' : '#F8FAFC', borderColor: colors.border }]}>
              {['Masculino', 'Feminino', 'Outro'].map(renderGenderButton)}
            </View>
          </View>

          {/* Input: Endereço */}
          <View style={[styles.inputGroup, { marginBottom: 4 }]}>
            <Text style={[styles.inputLabel, { color: colors.mutedText }]}>Endereço Clínico / Residencial</Text>
            <TextInput 
              style={[
                styles.input, 
                { 
                  backgroundColor: isDarkMode ? '#1E293B' : '#F8FAFC', 
                  borderColor: colors.border, 
                  color: colors.text 
                },
                focusedInput === 'address' && [styles.inputFocused, { borderColor: colors.brandBlue }]
              ]} 
              value={address} 
              onChangeText={setAddress}
              onFocus={() => setFocusedInput('address')}
              onBlur={() => setFocusedInput(null)}
              placeholder="Rua, Número, Bairro, Cidade"
              placeholderTextColor={isDarkMode ? '#64748B' : '#94A3B8'}
            />
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
        >
          <Text style={styles.saveButtonText}>Salvar Alterações</Text>
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
  genderContainer: {
    flexDirection: 'row',
    padding: 4,
    borderRadius: 12,
    borderWidth: 1,
  },
  genderButton: {
    flex: 1,
    height: 38,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 8,
  },
  genderButtonText: {
    fontSize: 13,
    fontWeight: '500',
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