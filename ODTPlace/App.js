import React from 'react';

import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { ThemeProvider } from './src/components/ThemeContext';
import { AuthProvider } from './src/context/AuthContext';

import HomeScreen from './src/screens/HomeScreen';
import HomeProfissional from './src/screens/HomeProfissional';
import LoginScreen from './src/screens/LoginScreen';
import LoginProfissional from './src/screens/LoginProfissional';
import SplashScreen from './src/screens/SplashScreen';
import CadastroScreen from './src/screens/CadastroScreen';
import ClinicDetailScreen from './src/screens/ClinicDetailScreen';
import ScheduleScreen from './src/screens/ScheduleScreen';
import ProfessionalsScreen from './src/screens/ProfessionalsScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import NotificationsScreen from './src/screens/NotificationsScreen';
import PreLogin from './src/screens/PreLogin';
import ForgotPassword from './src/screens/ForgotPassword';
import CheckEmail from './src/screens/CheckEmail';
import NewPassword from './src/screens/NewPassword';
import CadastroP from './src/screens/CadastroP';
import ForgotPasswordP from './src/screens/ForgotPasswordP';
import CheckEmailP from './src/screens/CheckEmailP';
import NewPasswordP from './src/screens/NewPasswordP';
import AgendaScreen from './src/screens/AgendaScreen';
import AppointmentDetailsScreen from './src/screens/AppointmentDetailsScreen';
import ConfigScreen from './src/screens/ConfigScreen';
import NotificationSettingScreen from './src/screens/NotificationSettingScreen';
import PatientProfileScreen from './src/screens/PatientProfileScreen';
import PatientsScreen from './src/screens/PatientsScreen';
import PersonalDataScreen from './src/screens/PersonalDataScreen';
import ReportsScreen from './src/screens/ReportsScreen';
import RescheduleScreen from './src/screens/RescheduleScreen';
import SuccessScreen from './src/screens/SuccessScreen';

import CustomTabBar from './src/components/CustomTabBar';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function TabNavigator() {
  return (
    <Tab.Navigator
      tabBar={(props) => <CustomTabBar {...props} />}
      screenOptions={{ headerShown: false }}
    >
      <Tab.Screen
        name="PainelTab"
        component={HomeProfissional}
        options={{ title: 'Painel' }}
      />
      <Tab.Screen
        name="AgendaTab"
        component={AgendaScreen}
        options={{ title: 'Agenda' }}
      />
      <Tab.Screen
        name="HistoricoTab"
        component={ReportsScreen}
        options={{ title: 'Relatórios' }}
      />
      <Tab.Screen
        name="ConfigTab"
        component={ConfigScreen}
        options={{ title: 'Config' }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <NavigationContainer>
          <Stack.Navigator screenOptions={{ headerShown: false }}>

            <Stack.Screen name="Splash" component={SplashScreen} />
            <Stack.Screen name="PreLogin" component={PreLogin} />
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="LoginProfissional" component={LoginProfissional} />
            <Stack.Screen name="Cadastro" component={CadastroScreen} />
            <Stack.Screen name="CadastroP" component={CadastroP} />

            <Stack.Screen name="Home" component={HomeScreen} />
            <Stack.Screen name="HomeP" component={TabNavigator} />

            <Stack.Screen name="Schedule" component={ScheduleScreen} />
            <Stack.Screen name="ClinicDetail" component={ClinicDetailScreen} />
            <Stack.Screen name="Professionals" component={ProfessionalsScreen} />
            <Stack.Screen name="Notifications" component={NotificationsScreen} />
            <Stack.Screen name="Settings" component={SettingsScreen} />

            <Stack.Screen name="ForgotPassword" component={ForgotPassword} />
            <Stack.Screen name="CheckEmail" component={CheckEmail} />
            <Stack.Screen name="NewPassword" component={NewPassword} />

            <Stack.Screen name="ForgotPasswordP" component={ForgotPasswordP} />
            <Stack.Screen name="CheckEmailP" component={CheckEmailP} />
            <Stack.Screen name="NewPasswordP" component={NewPasswordP} />

            <Stack.Screen
              name="AgendaScreen"
              component={AgendaScreen}
            />
            <Stack.Screen
              name="AppointmentDetails"
              component={AppointmentDetailsScreen}
            />
            <Stack.Screen
              name="ConfigScreen"
              component={ConfigScreen}
            />
            <Stack.Screen
              name="PatientProfileScreen"
              component={PatientProfileScreen}
            />
            <Stack.Screen
              name="PatientsScreen"
              component={PatientsScreen}
            />
            <Stack.Screen
              name="PersonalDataScreen"
              component={PersonalDataScreen}
            />
            <Stack.Screen
              name="ReportsScreen"
              component={ReportsScreen}
            />
            <Stack.Screen
              name="RescheduleScreen"
              component={RescheduleScreen}
            />
            <Stack.Screen
              name="SuccessScreen"
              component={SuccessScreen}
            />
            <Stack.Screen
              name="NotificationSetting"
              component={NotificationSettingScreen}
            />

          </Stack.Navigator>
        </NavigationContainer>
      </AuthProvider>
    </ThemeProvider>
  );
}