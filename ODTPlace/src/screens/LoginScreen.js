import { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  Alert,
  Image,
  TouchableOpacity,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import CustomInput from "../components/CustomInput";
import CustomButton from "../components/CustomButton";

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");

  const handleLogin = () => {
    if (email === "" || senha === "") {
      Alert.alert("Erro", "Preencha todos os campos!");
      return;
    }

    if (!email.includes("@") || !email.includes(".")) {
      Alert.alert("Erro", "E-mail inválido!");
      return;
    }

    const userName = email.split("@")[0];
    navigation.replace("Home", { userName });
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        style={styles.keyboardAvoid}
        behavior={Platform.OS === "ios" ? "padding" : "height"}
      >
        <View style={styles.mainContainer}>
          {/* Cabeçalho */}
          <View style={styles.headerSection}>
            {/* Logo sem contorno */}
            <View style={styles.logoContainer}>
              <Image
                source={require("../../assets/logo_icon.png")}
                style={styles.logoMain}
                resizeMode="contain"
              />
            </View>
            {/* Nome OdontoHub removido */}
            <Text style={styles.brandSubtitle}>Entre na sua conta</Text>
          </View>

          {/* Formulário Central */}
          <View style={styles.formSection}>
            <View style={styles.inputGroup}>
              <CustomInput
                placeholder="Número do celular ou e-mail"
                placeholderTextColor="#94A3B8"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                style={styles.inputStyle}
              />
            </View>

            <View style={styles.inputGroup}>
              <CustomInput
                placeholder="Senha de acesso"
                placeholderTextColor="#94A3B8"
                value={senha}
                onChangeText={setSenha}
                secureTextEntry
                style={styles.inputStyle}
              />

              <TouchableOpacity
                activeOpacity={0.6}
                style={styles.forgotPasswordContainer}
              >
                <Text style={styles.forgotPasswordText}>Esqueceu a senha?</Text>
              </TouchableOpacity>
            </View>

            <View style={styles.buttonContainer}>
              <CustomButton
                title="Entrar na Conta"
                onPress={handleLogin}
                style={styles.loginButton}
                textStyle={styles.loginButtonText}
              />
            </View>
          </View>

          <View style={styles.dividerContainer}>
            <View style={styles.line} />
            <Text style={styles.orText}>ou continue com</Text>
            <View style={styles.line} />
          </View>

          <View style={styles.socialSection}>
            <TouchableOpacity style={styles.socialButton} activeOpacity={0.7}>
              <Text style={styles.socialIconGoogle}>G</Text>
              <Text style={styles.socialButtonText}>Google</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.socialButton} activeOpacity={0.7}>
              <Text style={styles.socialIconFacebook}>f</Text>
              <Text style={styles.socialButtonText}>Facebook</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.footerSection}>
            <TouchableOpacity
              activeOpacity={0.7}
              onPress={() => navigation.navigate("Cadastro")}
              style={styles.createAccountButton}
            >
              <Text style={styles.createAccountText}>Criar nova conta</Text>
            </TouchableOpacity>

            {/* Logo aumentada */}
            <View style={styles.brandFooter}>
              <Image
                source={require("../../assets/logo_completa.png")}
                style={styles.footerLogo}
                resizeMode="contain"
              />
            </View>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: "#FFFFFF" },
  keyboardAvoid: { flex: 1 },
  mainContainer: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 40,
    paddingBottom: 24,
    justifyContent: "center",
  },
  headerSection: { alignItems: "center", marginBottom: 32 },
  // LogoContainer limpo (sem border/background)
  logoContainer: {
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
  },
  logoMain: { width: 80, height: 80, tintColor: "#06B6D4" },
  brandSubtitle: { fontSize: 16, color: "#64748B", textAlign: "center" },
  formSection: { width: "100%" },
  inputGroup: { marginBottom: 12 },
  inputStyle: {
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    color: "#0F172A",
    borderRadius: 16,
    height: 52,
    paddingHorizontal: 18,
    fontSize: 15,
  },
  forgotPasswordContainer: { alignItems: "flex-end", paddingTop: 8 },
  forgotPasswordText: { fontSize: 13, fontWeight: "600", color: "#06B6D4" },
  buttonContainer: { marginTop: 16, marginBottom: 24 },
  loginButton: {
    backgroundColor: "#06B6D4",
    borderRadius: 16,
    height: 52,
    width: "100%",
    justifyContent: "center",
    alignItems: "center",
  },
  loginButtonText: { fontSize: 16, fontWeight: "700", color: "#FFFFFF" },
  dividerContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 20,
  },
  line: { flex: 1, height: 1, backgroundColor: "#E2E8F0" },
  orText: {
    marginHorizontal: 16,
    fontSize: 13,
    fontWeight: "500",
    color: "#94A3B8",
  },
  socialSection: {
    flexDirection: "row",
    justifyContent: "space-between",
    width: "100%",
    marginBottom: 24,
  },
  socialButton: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderRadius: 16,
    height: 52,
    marginHorizontal: 6,
  },
  socialIconGoogle: {
    fontSize: 16,
    fontWeight: "900",
    marginRight: 8,
    color: "#DB4437",
  },
  socialIconFacebook: {
    fontSize: 16,
    fontWeight: "900",
    marginRight: 8,
    color: "#1877F2",
  },
  socialButtonText: { fontSize: 14, fontWeight: "600", color: "#334155" },
  footerSection: { width: "100%", alignItems: "center" },
  createAccountButton: {
    width: "100%",
    height: 52,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderRadius: 16,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#F8FAFC",
    marginBottom: 16,
  },
  createAccountText: { fontSize: 15, fontWeight: "700", color: "#0F172A" },
  brandFooter: { alignItems: "center", marginTop: 10 },
  // Logo aumentada
  footerLogo: { width: 120, height: 60, opacity: 0.6 },
});
