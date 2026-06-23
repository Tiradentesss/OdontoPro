import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';

// 1. Importa o provedor de tema que está na pasta src
import { ThemeProvider } from './src/ThemeContext';

import CustomTabBar from './src/components/CustomTabBar';
import HomeScreen from './src/screens/HomeScreen';
import PatientsScreen from './src/screens/PatientsScreen'; 
import ReportsScreen from './src/screens/ReportsScreen';
import AgendaScreen from './src/screens/AgendaScreen'; 
import PatientProfileScreen from './src/screens/PatientProfileScreen'; 
import AppointmentDetailsScreen from './src/screens/AppointmentDetailsScreen'; 
import SuccessScreen from './src/screens/SuccessScreen'; 
import RescheduleScreen from './src/screens/RescheduleScreen'; 
import ConfigScreen from './src/screens/ConfigScreen'; 
import PersonalDataScreen from './src/screens/PersonalDataScreen'; 

import NotificationsScreen from './src/screens/NotificationsScreen'; 
import NotificationSettingsScreen from './src/screens/NotificationSettingsScreen'; 

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function TabNavigator() {
  return (
    <Tab.Navigator
      tabBar={(props) => <CustomTabBar {...props} />}
      screenOptions={{ headerShown: false }}
    >
      <Tab.Screen name="PainelTab" component={HomeScreen} options={{ title: 'Painel' }} />
      <Tab.Screen name="AgendaTab" component={AgendaScreen} options={{ title: 'Agenda' }} />
      <Tab.Screen name="HistóricoTab" component={ReportsScreen} options={{ title: 'Relatórios' }} />
      <Tab.Screen name="ConfigTab" component={ConfigScreen} options={{ title: 'Config' }} />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    // 2. Envolve todo o ecossistema de telas com o ThemeProvider global
    <ThemeProvider>
      <NavigationContainer>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          
          {/* Menu de Abas Principal */}
          <Stack.Screen name="Main" component={TabNavigator} />
          
          {/* TELAS EM TELA CHEIA (Escondem o menu inferior) */}
          <Stack.Screen name="PatientsScreen" component={PatientsScreen} />
          <Stack.Screen name="PatientProfileScreen" component={PatientProfileScreen} />
          <Stack.Screen name="AppointmentDetailsScreen" component={AppointmentDetailsScreen} />
          <Stack.Screen name="SuccessScreen" component={SuccessScreen} />
          <Stack.Screen name="RescheduleScreen" component={RescheduleScreen} />
          
          {/* Centrais e Ajustes */}
          <Stack.Screen name="NotificationsScreen" component={NotificationsScreen} />
          <Stack.Screen name="PersonalDataScreen" component={PersonalDataScreen} />
          <Stack.Screen name="NotificationSettingsScreen" component={NotificationSettingsScreen} />

        </Stack.Navigator>
      </NavigationContainer>
    </ThemeProvider>
  );
}