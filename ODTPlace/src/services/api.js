import axios from "axios";
import { Platform } from "react-native";
import Constants from "expo-constants";

const normalizeBaseUrl = (value) => {
  if (!value) return null;
  return value.trim().replace(/\/+$/, "");
};

const ensureApiSuffix = (value) => {
  if (!value) return value;
  return value.endsWith('/api') ? value : `${value}/api`;
};

const resolveApiBaseUrl = () => {
  const configuredUrl = normalizeBaseUrl(process.env.EXPO_PUBLIC_API_URL);
  if (configuredUrl) {
    return ensureApiSuffix(configuredUrl);
  }

  const hostUri = Constants.expoConfig?.hostUri || Constants.manifest?.debuggerHost;
  if (hostUri) {
    const host = hostUri.split(":")[0];
    return `http://${host}:3001/api`;
  }

  if (Platform.OS === "android") {
    return "http://10.0.2.2:3001/api";
  }

  if (Platform.OS === "ios") {
    return "http://127.0.0.1:3001/api";
  }

  const fallbackHost = "192.168.61.104";
  return `http://${fallbackHost}:3001/api`;
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

export const getDoctorStats = async (doctorId) => {
  try {
    const response = await api.get(`/doctors/${doctorId}/stats`);
    return response.data;
  } catch (error) {
    // If the server returns 404 for stats, fall back to zeros instead of throwing
    if (error && error.response && error.response.status === 404) {
      console.warn(`Doctor stats not found for id=${doctorId} (404). Returning zeros.`);
      return { completed_consultations: 0, positive_reviews: 0 };
    }
    console.error('API Error (doctor stats):', error);
    throw error;
  }
};

export const getDoctorById = async (doctorId) => {
  try {
    const response = await api.get(`/doctors/${doctorId}`);
    return response.data;
  } catch (error) {
    console.error('API Error (doctor profile):', error);
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

export const loginProfessional = async (email, senha) => {
  try {
    const response = await api.post('/login/profissional', { email, senha });
    return response.data;
  } catch (error) {
    console.error('Professional Login API Error:', error.message);
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      throw new Error('Conexão expirou. O servidor está respondendo?');
    }
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error') || !error.response) {
      throw new Error('Não foi possível conectar ao servidor.\n\nVerifique:\n1. O backend está rodando em ' + API_BASE_URL + '?\n2. Sua conexão de rede?');
    }
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

export const getProfessionalAppointments = async (params = {}) => {
  try {
    const response = await api.get('/appointments', { params });
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const updateAppointment = async (appointmentId, payload) => {
  try {
    const response = await api.put(`/appointments/${appointmentId}`, payload);
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

export const updateDoctorProfile = async (doctorId, profileData) => {
  try {
    const response = await api.put(`/doctors/${doctorId}`, profileData);
    return response.data;
  } catch (error) {
    console.error('API Error (doctor profile update):', error);
    throw error;
  }
};
