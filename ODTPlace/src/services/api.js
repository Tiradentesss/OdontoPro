import axios from "axios";

// Configure your backend URL here
// Use your local IP address so the app can reach the backend from a device/emulator
const API_BASE_URL = "http://192.168.1.108:3001/api"; // Use your local IP address here

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
    if (error.code === 'ECONNABORTED' || error.message.includes('Network Error')) {
      throw new Error('Não foi possível conectar ao servidor. Verifique sua conexão.');
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
