import React from "react";
import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  StyleSheet, 
  Platform, 
  StatusBar 
} from "react-native";
import { Search, SlidersHorizontal } from "lucide-react-native";
import { LinearGradient } from "expo-linear-gradient";
import NotificationButton from "./NotificationButton";

const statusBarHeight = Platform.OS === "android" ? StatusBar.currentHeight || 24 : 44;

export default function HomeHeader({
  usuario,
  search,
  setSearch,
  onBellPress,
  onFilterPress,
  sectionText = "Clínicas Disponíveis",
}) {
  return (
    <View style={styles.wrapper}>
      <LinearGradient 
        colors={["#0ea5e9", "#0284c7"]} 
        style={styles.topCard}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.topCardContent}>
          <View style={styles.topHeader}>
            <View>
              <Text style={styles.welcomeText}>Bem-vindo(a),</Text>
              <Text style={styles.welcomeName}>{usuario}</Text>
            </View>
            
            {/* O onBellPress aqui agora dispara a navegação definida no HomeScreen */}
            <NotificationButton onPress={onBellPress} />
          </View>

          <View style={styles.searchContainer}>
            <View style={styles.searchBox}>
              <Search size={20} color="#94a3b8" />
              <TextInput
                value={search}
                onChangeText={setSearch}
                placeholder="Pesquisar clínicas..."
                placeholderTextColor="#cbd5e1"
                style={styles.searchInput}
              />
            </View>
            <TouchableOpacity
              style={styles.filterButton}
              onPress={onFilterPress}
              activeOpacity={0.7}
            >
              <SlidersHorizontal size={20} color="#0284c7" />
            </TouchableOpacity>
          </View>
        </View>
      </LinearGradient>

      <Text style={styles.sectionText}>{sectionText}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    paddingBottom: 4,
  },
  topCard: {
    paddingBottom: 32,
    borderBottomLeftRadius: 36,
    borderBottomRightRadius: 36,
    shadowColor: "#0284c7",
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 8,
  },
  topCardContent: {
    paddingHorizontal: 24,
    paddingTop: statusBarHeight + 20,
  },
  topHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 28,
  },
  welcomeText: { 
    color: "#e0f2fe", 
    fontSize: 14, 
    fontWeight: "400",
    letterSpacing: 0.2 
  },
  welcomeName: { 
    color: "#ffffff", 
    fontSize: 20, 
    fontWeight: "700",
    marginTop: 2 
  },
  searchContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  searchBox: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#ffffff",
    borderRadius: 16,
    paddingHorizontal: 16,
    height: 52,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 3,
  },
  searchInput: {
    flex: 1,
    marginLeft: 10,
    fontSize: 15,
    color: "#334155",
  },
  filterButton: {
    width: 52,
    height: 52,
    borderRadius: 16,
    backgroundColor: "#ffffff",
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionText: {
    fontSize: 18,
    fontWeight: "700",
    color: "#0f172a",
    marginTop: 28,
    marginHorizontal: 24,
  },
});