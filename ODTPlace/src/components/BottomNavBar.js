import React from "react";
import { View, TouchableOpacity, StyleSheet, Text } from "react-native";
import { BlurView } from "expo-blur";
import { Home, CalendarDays, History, Settings } from "lucide-react-native";

const tabs = [
  { key: "home", label: "Home", icon: Home },
  { key: "schedule", label: "Consultas", icon: CalendarDays },
  { key: "history", label: "Histórico", icon: History },
  { key: "settings", label: "Config", icon: Settings },
];

export default function BottomNavBar({
  activeTab = "home",
  onTabPress = () => {},
}) {
  return (
    <BlurView intensity={90} tint="light" style={styles.container}>
      <View style={styles.bottomBar}>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.key;
          const IconComponent = tab.icon;
          return (
            <TouchableOpacity
              key={tab.key}
              style={[styles.bottomTab, isActive && styles.bottomTabActive]}
              // Certifique-se de que a chamada abaixo seja exatamente assim:
              onPress={() => onTabPress(tab.key)} 
              activeOpacity={0.8}
            >
              <IconComponent
                size={22}
                color={isActive ? "#ffffff" : "#64748b"}
                strokeWidth={isActive ? 2.5 : 2}
              />
              {isActive && <Text style={styles.activeText}>{tab.label}</Text>}
            </TouchableOpacity>
          );
        })}
      </View>
    </BlurView>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    left: 20,
    right: 20,
    bottom: 34,
    borderRadius: 35,
    overflow: "hidden",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 15,
    elevation: 8,
    borderWidth: 1,
    borderColor: "rgba(255, 255, 255, 0.5)",
  },
  bottomBar: {
    height: 70,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 24,
    backgroundColor: "rgba(255, 255, 255, 0.75)",
  },
  bottomTab: { 
    padding: 8, 
    alignItems: "center", 
    justifyContent: "center" 
  },
  bottomTabActive: {
    backgroundColor: "#0ea5e9",
    borderRadius: 20,
    flexDirection: "row",
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  activeText: {
    color: "#ffffff",
    marginLeft: 6,
    fontWeight: "700",
    fontSize: 12,
  },
});