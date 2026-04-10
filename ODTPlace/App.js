App.js
// Importando navegação
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

// Importando telas
import HomeScreen from './src/screens/HomeScreen';
import LoginScreen from './src/screens/LoginScreen';
import SplashScreen from './src/screens/SplashScreen';
import CadastroScreen from './src/screens/CadastroScreen';
import ClinicDetailScreen from './src/screens/ClinicDetailScreen';
import ScheduleScreen from './src/screens/ScheduleScreen';
// import ProfileScreen from './src/screens/ProfileScreen';

// Criando o stack
const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>

      <Stack.Navigator screenOptions={{ headerShown: false }}>

        <Stack.Screen name="Splash" component={SplashScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Cadastro" component={CadastroScreen} />
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Schedule" component={ScheduleScreen} />
        <Stack.Screen name="ClinicDetail" component={ClinicDetailScreen} />
        {/* <Stack.Screen name="Profile" component={ProfileScreen} /> */}

      </Stack.Navigator>

    </NavigationContainer>
  );
}
