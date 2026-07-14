import { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  SafeAreaView,
} from "react-native";
import { Star, Clock, MapPin, ChevronRight } from "lucide-react-native";
import HomeHeader from "../components/HomeHeader";
import BottomNavBar from "../components/BottomNavBar";

export default function HomeScreen({
  route,
  navigation,
  showBottomNav = true,
}) {
  const usuario = route?.params?.userName ?? "Gabriel";
  const [search, setSearch] = useState("");
  const [clinicas] = useState([
    {
      id: "1",
      nome: "Clínica Sorriso Vivo",
      especialidade: "Odontologia",
      avaliacao: "5.0",
      avaliacoes: "83",
      preco: "R$ 250,00",
      horarios: ["11:00", "12:00"],
    },
  ]);

  const dadosFiltrados = clinicas.filter((c) =>
    c.nome.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <SafeAreaView style={styles.container}>
      <HomeHeader
        usuario={usuario}
        search={search}
        setSearch={setSearch}
        onBellPress={() => navigation.navigate("Notifications")}
      />

      <FlatList
        data={dadosFiltrados}
        keyExtractor={(item) => item.id}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.listContent}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.card}
            activeOpacity={0.9}
            onPress={() =>
              navigation.navigate("ClinicDetail", { clinic: item })
            }
          >
            <View style={styles.cardTop}>
              <View style={styles.logoPlaceholder} />
              <View style={styles.headerInfo}>
                <Text style={styles.title}>{item.nome}</Text>
                <View style={styles.row}>
                  <MapPin size={14} color="#64748b" />
                  <Text style={styles.subtitle}> {item.especialidade}</Text>
                </View>
              </View>
              <View style={styles.ratingBadge}>
                <Star size={14} color="#fbbf24" fill="#fbbf24" />
                <Text style={styles.ratingText}>{item.avaliacao}</Text>
              </View>
            </View>

            <View style={styles.divider} />

            <View style={styles.cardBottom}>
              <View>
                <Text style={styles.label}>Valor</Text>
                <Text style={styles.price}>{item.preco}</Text>
              </View>

              <View style={styles.timeContainer}>
                <Clock size={14} color="#0ea5e9" style={{ marginRight: 6 }} />
                {item.horarios.map((hora) => (
                  <Text key={hora} style={styles.hourText}>
                    {hora}
                  </Text>
                ))}
                <ChevronRight
                  size={16}
                  color="#cbd5e1"
                  style={{ marginLeft: 8 }}
                />
              </View>
            </View>
          </TouchableOpacity>
        )}
      />

      {showBottomNav && (
        <BottomNavBar
          activeTab="home"
          onTabPress={(tab) =>
            navigation.navigate(
              tab === "home"
                ? "Home"
                : tab.charAt(0).toUpperCase() + tab.slice(1),
            )
          }
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  listContent: { padding: 20, paddingBottom: 100 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 24,
    padding: 20,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 12,
    elevation: 4,
  },
  cardTop: { flexDirection: "row", alignItems: "center", marginBottom: 16 },
  logoPlaceholder: {
    width: 50,
    height: 50,
    borderRadius: 16,
    backgroundColor: "#f1f5f9",
  },
  headerInfo: { flex: 1, marginLeft: 12 },
  title: { fontSize: 17, fontWeight: "700", color: "#1e293b" },
  subtitle: { fontSize: 13, color: "#64748b" },
  row: { flexDirection: "row", alignItems: "center", marginTop: 4 },
  ratingBadge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fffbeb",
    padding: 6,
    borderRadius: 10,
  },
  ratingText: { fontWeight: "700", color: "#b45309", marginLeft: 4 },
  divider: { height: 1, backgroundColor: "#f1f5f9", marginBottom: 16 },
  cardBottom: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  label: { fontSize: 11, color: "#94a3b8", textTransform: "uppercase" },
  price: { fontSize: 16, fontWeight: "800", color: "#0f172a" },
  timeContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#f0f9ff",
    padding: 8,
    borderRadius: 12,
  },
  hourText: {
    fontSize: 13,
    fontWeight: "600",
    color: "#0284c7",
    marginHorizontal: 4,
  },
});
