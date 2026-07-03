import axios from "axios";
import { Platform } from "react-native";

// Configure your backend URL here.
// Android Emulator should use 10.0.2.2, while physical devices need your machine's LAN IP.
const resolveApiBaseUrl = () => {
  if (process.env.EXPO_PUBLIC_API_URL) {
    return process.env.EXPO_PUBLIC_API_URL;
  }

  if (Platform.OS === "android") {
    return "http://10.0.2.2:3001/api";
  }

  return "http://localhost:3001/api";
};

const API_BASE_URL = resolveApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const testConnection = async () => {
  try {
    const response = await api.get('/test');
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const getClinics = async () => {
  try {
    const response = await api.get('/clinics');
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const getClinicById = async (clinicId) => {
  try {
    const response = await api.get(`/clinics/${clinicId}`);
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const getClinicSpecialties = async (clinicId) => {
  try {
    const response = await api.get(`/clinics/${clinicId}/specialties`);
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const getClinicDoctors = async (clinicId) => {
  try {
    const response = await api.get(`/clinics/${clinicId}/doctors`);
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const loginPatient = async (email, senha) => {
  try {
    const response = await api.post('/login', { email, senha });
    return response.data;
  } catch (error) {
    console.error('Login API Error:', error.message);
    console.error('API Base URL:', API_BASE_URL);
    
    // Network connection errors
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      throw new Error('Conexão expirou. O servidor está respondendo?');
    }
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error') || !error.response) {
      throw new Error('Não foi possível conectar ao servidor.\n\nVerifique:\n1. O backend está rodando em ' + API_BASE_URL + '?\n2. Sua conexão de rede?');
    }
    // Server errors
    if (error.response) {
      throw error;
    }
    throw new Error('Erro de conexão. Tente novamente.');
  }
};

export const registerPatient = async (patientData) => {
  try {
    const response = await api.post('/register', patientData);
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const createAppointment = async (appointmentData) => {
  try {
    const response = await api.post('/appointments', appointmentData);
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const getPatientAppointments = async (email) => {
  try {
    const response = await api.get(`/appointments/${email}`);
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const getPatientProfile = async (patientId) => {
  try {
    const response = await api.get(`/patients/${patientId}`);
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const updatePatientProfile = async (patientId, profileData) => {
  try {
    const response = await api.put(`/patients/${patientId}`, profileData);
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};
