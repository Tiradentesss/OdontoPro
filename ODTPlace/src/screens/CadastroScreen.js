import { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  Alert, 
  TouchableOpacity, 
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  TextInput,
  StatusBar,
  ActivityIndicator,
  Modal
} from 'react-native';
import { ChevronLeft, Calendar, Eye, EyeOff, CheckCircle } from 'lucide-react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import CustomButton from '../components/CustomButton';

export default function RegisterScreen({ navigation }) {
  const [nome, setNome] = useState('');
  const [sobrenome, setSobrenome] = useState('');
  const [email, setEmail] = useState('');
  const [telefone, setTelefone] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmarSenha, setConfirmarSenha] = useState('');
  
  // Estados de visibilidade das senhas
  const [hidePassword, setHidePassword] = useState(true);
  const [hideConfirmPassword, setHideConfirmPassword] = useState(true);

  // Estados de Carregamento e Sucesso
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  // Lógica do Calendário de Data de Nascimento
  const [date, setDate] = useState(new Date());
  const [showPicker, setShowPicker] = useState(false);
  const [dateSelected, setDateSelected] = useState(false);

  const handleRegister = () => {
    // Validações básicas
    if (!nome || !sobrenome || !email || !telefone || !senha || !confirmarSenha || !dateSelected) {
      Alert.alert('Erro', 'Preencha todos os campos!');
      return;
    }
    if (!email.includes('@') || !email.includes('.')) {
      Alert.alert('Erro', 'Email inválido!');
      return;
    }
    if (senha !== confirmarSenha) {
      Alert.alert('Erro', 'As senhas não coincidem!');
      return;
    }

    // Inicia o fluxo visual de carregamento
    setIsSubmitting(true);

    // Aqui simula o tempo do backend (Ex: 2 segundos processando)
    setTimeout(() => {
      setIsSubmitting(false); // Para de carregar
      setIsSuccess(true);     // Mostra tela de sucesso

      // Aguarda mais 2 segundos lendo a mensagem de sucesso e redireciona
      setTimeout(() => {
        setIsSuccess(false);
        // Usamos replace para impedir que o usuário volte para a tela de sucesso ao apertar o botão voltar no celular
        navigation.replace('Login'); 
      }, 2000);

    }, 2000); 
  };

  const onDateChange = (event, selectedDate) => {
    setShowPicker(false);
    if (selectedDate) {
      setDate(selectedDate);
      setDateSelected(true);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      
      {/* Modal de Loading / Sucesso sobrepondo a tela inteira */}
      <Modal transparent={true} visible={isSubmitting || isSuccess} animationType="fade">
        <View style={styles.overlay}>
          <View style={styles.feedbackCard}>
            {isSubmitting ? (
              <>
                <ActivityIndicator size="large" color="#06B6D4" />
                <Text style={styles.feedbackTitle}>Criando conta...</Text>
                <Text style={styles.feedbackText}>Aguarde um momento</Text>
              </>
            ) : isSuccess ? (
              <>
                <CheckCircle color="#10B981" size={64} strokeWidth={2.5} />
                <Text style={styles.feedbackTitle}>Conta criada com sucesso!</Text>
                <Text style={styles.feedbackText}>Redirecionando para o login...</Text>
              </>
            ) : null}
          </View>
        </View>
      </Modal>

      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
          
          {/* Botão Voltar */}
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
            <ChevronLeft color="#0F172A" size={32} strokeWidth={2.5} />
          </TouchableOpacity>

          {/* Título e Subtítulo */}
          <View style={styles.header}>
            <Text style={styles.pageTitle}>Registro</Text>
            <Text style={styles.description}>Crie sua conta para Continuar</Text>
          </View>

          {/* Inputs */}
          <TextInput 
            style={styles.input} 
            placeholder="Nome" 
            placeholderTextColor="#94A3B8"
            value={nome} 
            onChangeText={setNome} 
            editable={!isSubmitting && !isSuccess} // Bloqueia durante o carregamento
          />
          
          <TextInput 
            style={styles.input} 
            placeholder="Sobrenome" 
            placeholderTextColor="#94A3B8"
            value={sobrenome} 
            onChangeText={setSobrenome} 
            editable={!isSubmitting && !isSuccess}
          />
          
          <TextInput 
            style={styles.input} 
            placeholder="Email" 
            placeholderTextColor="#94A3B8"
            value={email} 
            onChangeText={setEmail} 
            keyboardType="email-address" 
            autoCapitalize="none"
            editable={!isSubmitting && !isSuccess}
          />
          
          {/* Card de Data de Nascimento com Ícone */}
          <TouchableOpacity 
            style={styles.inputContainer} 
            onPress={() => !isSubmitting && !isSuccess && setShowPicker(true)} 
            activeOpacity={0.7}
          >
            <Text style={[styles.inputText, !dateSelected && { color: '#94A3B8' }]}>
              {dateSelected ? date.toLocaleDateString('pt-BR') : 'Data de nascimento'}
            </Text>
            <Calendar color="#94A3B8" size={20} />
          </TouchableOpacity>

          {showPicker && (
            <DateTimePicker
              value={date}
              mode="date"
              display="default"
              onChange={onDateChange}
            />
          )}

          <TextInput 
            style={styles.input} 
            placeholder="Telefone" 
            placeholderTextColor="#94A3B8"
            value={telefone} 
            onChangeText={setTelefone} 
            keyboardType="phone-pad" 
            editable={!isSubmitting && !isSuccess}
          />
          
          {/* Card de Senha */}
          <View style={styles.inputContainer}>
            <TextInput 
              style={styles.inputFlex} 
              placeholder="Senha" 
              placeholderTextColor="#94A3B8"
              value={senha} 
              onChangeText={setSenha} 
              secureTextEntry={hidePassword} 
              editable={!isSubmitting && !isSuccess}
            />
            <TouchableOpacity onPress={() => setHidePassword(!hidePassword)}>
              {hidePassword ? <EyeOff color="#94A3B8" size={20} /> : <Eye color="#94A3B8" size={20} />}
            </TouchableOpacity>
          </View>

          {/* Card de Confirmar Senha */}
          <View style={styles.inputContainer}>
            <TextInput 
              style={styles.inputFlex} 
              placeholder="Confirmar senha" 
              placeholderTextColor="#94A3B8"
              value={confirmarSenha} 
              onChangeText={setConfirmarSenha} 
              secureTextEntry={hideConfirmPassword} 
              editable={!isSubmitting && !isSuccess}
            />
            <TouchableOpacity onPress={() => setHideConfirmPassword(!hideConfirmPassword)}>
              {hideConfirmPassword ? <EyeOff color="#94A3B8" size={20} /> : <Eye color="#94A3B8" size={20} />}
            </TouchableOpacity>
          </View>

          {/* Botão Registrar */}
          <View style={styles.buttonContainer}>
            <CustomButton 
              title="Registrar Conta" 
              onPress={handleRegister} 
              style={styles.registerButton} 
              textStyle={styles.registerButtonText}
              disabled={isSubmitting || isSuccess} // Desativa o botão se já estiver clicado
            />
          </View>

        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#FFFFFF' },
  container: { flex: 1 },
  scrollContent: { 
    paddingHorizontal: 24, 
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight + 20 : 20, 
    paddingBottom: 40 
  },
  
  backButton: { marginBottom: 24, marginLeft: -8 },
  header: { marginBottom: 32 },
  pageTitle: { fontSize: 32, fontWeight: '900', color: '#0F172A', letterSpacing: -0.5 },
  description: { color: '#64748B', fontSize: 16, marginTop: 6 },
  
  input: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 16,
    height: 56,
    paddingHorizontal: 18,
    fontSize: 15,
    color: '#0F172A',
    marginBottom: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 16,
    height: 56,
    paddingHorizontal: 18,
    marginBottom: 16,
  },
  inputFlex: { flex: 1, fontSize: 15, color: '#0F172A', height: '100%' },
  inputText: { flex: 1, fontSize: 15, color: '#0F172A' },

  buttonContainer: { marginTop: 16 },
  registerButton: {
    backgroundColor: '#06B6D4',
    borderRadius: 16,
    height: 56,
    justifyContent: 'center',
    alignItems: 'center',
  },
  registerButtonText: { fontSize: 16, fontWeight: '700', color: '#FFFFFF' },

  // Estilos do Modal de Feedback (Loading e Sucesso)
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.4)', // Fundo escurinho translúcido
    justifyContent: 'center',
    alignItems: 'center',
  },
  feedbackCard: {
    backgroundColor: '#FFFFFF',
    padding: 32,
    borderRadius: 24,
    alignItems: 'center',
    width: '80%',
    // Sombra para dar destaque
    elevation: 5,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
  },
  feedbackTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0F172A',
    marginTop: 20,
    textAlign: 'center',
  },
  feedbackText: {
    fontSize: 15,
    color: '#64748B',
    marginTop: 8,
    textAlign: 'center',
  },
});