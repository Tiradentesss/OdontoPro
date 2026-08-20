import axios from "axios";

const normalizeBaseUrl = (value) => {
  if (!value) return null;
  return value.trim().replace(/\/+$/, "");
};

const ONLINE_API_BASE_URL = "https://odontohubbackend.onrender.com/api";

const ensureApiSuffix = (value) => {
  if (!value) return value;
  return value.endsWith('/api') ? value : `${value}/api`;
};

const resolveApiBaseUrl = () => {
  const configuredUrl = normalizeBaseUrl(process.env.EXPO_PUBLIC_API_URL);
  if (configuredUrl) {
    return ensureApiSuffix(configuredUrl);
  }

  return ONLINE_API_BASE_URL;
};

const API_BASE_URL = resolveApiBaseUrl();

// Helpful debug log so the running app prints which backend URL it will call
if (typeof console !== 'undefined' && console.log) {
  console.log('Resolved API_BASE_URL:', API_BASE_URL);
}

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
      // Map common server response codes to friendly messages
      if (error.response.status === 401) {
        throw new Error('Credenciais inválidas. Verifique seu email e senha.');
      }
      // Otherwise rethrow the original error to preserve details
      const serverMessage = error.response.data?.error || error.response.statusText || 'Erro no servidor';
      throw new Error(serverMessage);
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

export const submitAppointmentRating = async (appointmentId, ratingData) => {
  try {
    const response = await api.post(`/appointments/${appointmentId}/rating`, ratingData);
    return response.data;
  } catch (error) {
    console.error('Appointment rating API error:', error);
    const message = error.response?.data?.error || 'Não foi possível enviar a avaliação.';
    throw new Error(message);
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

/**
 * Upload image file to Cloudinary through backend
 * @param {Object} image - Image object with uri, name, type
 * @param {string} folder - Cloudinary folder
 * @param {Object} metadata - Additional metadata
 * @param {Function} onProgress - Progress callback
 * @returns {Promise} - Upload response with secure_url and public_id
 */
export const uploadImage = async (image, folder = 'users', metadata = {}, onProgress = null) => {
  try {
    const formData = new FormData();
    
    formData.append('file', {
      uri: image.uri,
      name: image.filename || `image_${Date.now()}.jpg`,
      type: image.mimeType || 'image/jpeg',
    });

    formData.append('folder', folder);
    if (metadata && Object.keys(metadata).length > 0) {
      formData.append('metadata', JSON.stringify(metadata));
    }

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 30000,
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });

    if (!response.data || response.status !== 200) {
      throw new Error('Invalid response from server');
    }

    return response.data;
  } catch (error) {
    console.error('Image upload error:', error);
    throw error;
  }
};

/**
 * Delete image from Cloudinary through backend
 * @param {string} publicId - Cloudinary public ID
 * @returns {Promise} - Delete response
 */
export const deleteImage = async (publicId) => {
  try {
    if (!publicId) {
      throw new Error('Public ID is required');
    }

    const response = await api.delete(`/images/${publicId}`, {
      timeout: 10000,
    });

    return response.data;
  } catch (error) {
    console.error('Image delete error:', error);
    throw error;
  }
};

