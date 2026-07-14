import React, { useState } from "react";
import { View, Text, FlatList, StyleSheet, TouchableOpacity, StatusBar, Platform } from "react-native";
import { Clock, CheckCircle2, AlertCircle, ArrowLeft, Filter } from "lucide-react-native";

const HISTORY_DATA = [
  { id: "1", patient: "João Silva", procedure: "Limpeza Dental", date: "03 Jul, 14:00", status: "completed" },
  { id: "2", patient: "Maria Souza", procedure: "Tratamento de Canal", date: "02 Jul, 09:30", status: "pending" },
  { id: "3", patient: "Carlos Lima", procedure: "Avaliação Ortodôntica", date: "30 Jun, 11:00", status: "completed" },
];

const FILTERS = ["Todas", "Concluídas", "Pendentes"];

export default function HistoryScreen({ navigation }) {
  const [selectedFilter, setSelectedFilter] = useState("Todas");

  const filteredData = HISTORY_DATA.filter((item) => {
    if (selectedFilter === "Concluídas") return item.status === "completed";
    if (selectedFilter === "Pendentes") return item.status === "pending";
    return true;
  });

  return (
    <View style={styles.container}>
      {/* Header Customizado */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <ArrowLeft size={24} color="#0f172a" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Histórico</Text>
      </View>

      {/* Filtros */}
      <View style={styles.filterContainer}>
        {FILTERS.map((filter) => (
          <TouchableOpacity
            key={filter}
            style={[styles.filterChip, selectedFilter === filter && styles.filterChipActive]}
            onPress={() => setSelectedFilter(filter)}
          >
            <Text style={[styles.filterText, selectedFilter === filter && styles.filterTextActive]}>
              {filter}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Lista */}
      <FlatList
        data={filteredData}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <View style={styles.cardLeft}>
              <View style={[styles.iconBox, { backgroundColor: item.status === 'completed' ? '#f0fdf4' : '#fff7ed' }]}>
                {item.status === 'completed' 
                  ? <CheckCircle2 size={20} color="#22c55e" /> 
                  : <AlertCircle size={20} color="#f97316" />
                }
              </View>
              <View>
                <Text style={styles.patientName}>{item.patient}</Text>
                <Text style={styles.procedure}>{item.procedure}</Text>
              </View>
            </View>
            <Text style={styles.date}>{item.date}</Text>
          </View>
        )}
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: "#f8fafc", 
    paddingTop: Platform.OS === "android" ? StatusBar.currentHeight + 20 : 60 
  },
  header: { flexDirection: "row", alignItems: "center", paddingHorizontal: 24, marginBottom: 20 },
  backButton: { marginRight: 16, padding: 4 },
  headerTitle: { fontSize: 22, fontWeight: "800", color: "#0f172a" },
  
  filterContainer: { flexDirection: "row", paddingHorizontal: 24, marginBottom: 20, gap: 10 },
  filterChip: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, backgroundColor: "#e2e8f0" },
  filterChipActive: { backgroundColor: "#0ea5e9" },
  filterText: { fontSize: 13, fontWeight: "600", color: "#64748b" },
  filterTextActive: { color: "#ffffff" },

  listContent: { paddingHorizontal: 24, paddingBottom: 100 },
  card: { backgroundColor: "#ffffff", padding: 16, borderRadius: 16, flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12, borderWidth: 1, borderColor: "#e2e8f0" },
  cardLeft: { flexDirection: "row", alignItems: "center", gap: 12 },
  iconBox: { width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  patientName: { fontSize: 16, fontWeight: "700", color: "#0f172a" },
  procedure: { fontSize: 14, color: "#64748b", marginTop: 2 },
  date: { fontSize: 12, fontWeight: "600", color: "#475569" },
});