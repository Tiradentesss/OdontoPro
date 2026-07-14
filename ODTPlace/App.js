import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

// Importação das telas
import MainTabs from './src/components/MainTabs';
import LoginScreen from './src/screens/LoginScreen';
import MySplashScreen from './src/screens/SplashScreen'; 
import CadastroScreen from './src/screens/CadastroScreen';
import ClinicDetailScreen from './src/screens/ClinicDetailScreen';
import ScheduleScreen from './src/screens/ScheduleScreen';
import ProfessionalsScreen from './src/screens/ProfessionalsScreen';
import ProfessionalInfoScreen from './src/screens/ProfessionalInfoScreen';
import AppointmentBookingScreen from './src/screens/AppointmentBookingScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import HistoryScreen from './src/screens/HistoryScreen';
import PersonalInfoScreen from './src/screens/PersonalInfoScreen';
import SystemScreen from './src/screens/SystemScreen';
import NotificationSettingsScreen from './src/screens/NotificationSettingsScreen';
// IMPORTANTE: Adicione a importação da tela de notificações aqui:
import NotificationsScreen from './src/screens/NotificationsScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator 
        initialRouteName="Splash"
        screenOptions={{ 
          headerShown: false,
          animation: 'slide_from_right'
        }}
      >
        <Stack.Screen name="Splash" component={MySplashScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Cadastro" component={CadastroScreen} />
        <Stack.Screen name="Home" component={MainTabs} />
        <Stack.Screen name="Schedule" component={ScheduleScreen} />
        <Stack.Screen name="ClinicDetail" component={ClinicDetailScreen} />
        <Stack.Screen name="Professionals" component={ProfessionalsScreen} />
        <Stack.Screen name="ProfessionalInfo" component={ProfessionalInfoScreen} />
        <Stack.Screen name="AppointmentBooking" component={AppointmentBookingScreen} />
        
        {/* Agora History e Notifications abrem telas diferentes */}
        <Stack.Screen name="History" component={HistoryScreen} />
        <Stack.Screen name="Notifications" component={NotificationsScreen} /> 
        
        <Stack.Screen name="Settings" component={SettingsScreen} />
        <Stack.Screen name="PersonalInfo" component={PersonalInfoScreen} />
        <Stack.Screen name="System" component={SystemScreen} />
        <Stack.Screen name="NotificationSettings" component={NotificationSettingsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}