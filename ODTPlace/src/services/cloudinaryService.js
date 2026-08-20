/**
 * Cloudinary Image Service
 * 
 * Handles all image upload/delete operations through the backend.
 * The backend is responsible for Cloudinary authentication.
 * This service only handles image selection, validation, and communication with backend.
 */

import * as ImagePicker from 'expo-image-picker';
import axios from 'axios';

const normalizeBaseUrl = (value) => {
  if (!value) return null;
  return value.trim().replace(/\/+$/, '');
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

/**
 * Error codes for consistent error handling
 */
export const CLOUDINARY_ERROR_CODES = {
  PERMISSION_DENIED: 'IMAGE_PERMISSION_ERROR',
  SELECTION_CANCELLED: 'IMAGE_SELECTION_CANCELLED',
  INVALID_FILE: 'IMAGE_INVALID_FILE',
  FILE_TOO_LARGE: 'IMAGE_FILE_TOO_LARGE',
  INVALID_FORMAT: 'IMAGE_INVALID_FORMAT',
  UPLOAD_FAILED: 'IMAGE_UPLOAD_FAILED',
  NETWORK_ERROR: 'IMAGE_NETWORK_ERROR',
  TIMEOUT_ERROR: 'IMAGE_TIMEOUT_ERROR',
  DATABASE_ERROR: 'IMAGE_DATABASE_ERROR',
  UNKNOWN_ERROR: 'IMAGE_UNKNOWN_ERROR',
};

/**
 * Configuration for image upload
 */
const IMAGE_CONFIG = {
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  ALLOWED_MIME_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
  ALLOWED_EXTENSIONS: ['jpg', 'jpeg', 'png', 'webp'],
};

/**
 * Validate selected image file
 */
const validateImage = (image) => {
  // Check if file exists
  if (!image || !image.uri) {
    return {
      valid: false,
      code: CLOUDINARY_ERROR_CODES.INVALID_FILE,
      message: 'Arquivo inválido',
    };
  }

  // Check file size (use size if available, otherwise estimate)
  if (image.size && image.size > IMAGE_CONFIG.MAX_FILE_SIZE) {
    return {
      valid: false,
      code: CLOUDINARY_ERROR_CODES.FILE_TOO_LARGE,
      message: `Arquivo muito grande (máximo 5MB)`,
    };
  }

  // Check MIME type if available
  if (image.mimeType && !IMAGE_CONFIG.ALLOWED_MIME_TYPES.includes(image.mimeType)) {
    return {
      valid: false,
      code: CLOUDINARY_ERROR_CODES.INVALID_FORMAT,
      message: 'Formato de imagem não suportado',
    };
  }

  // Check file extension
  const extension = image.uri.split('.').pop().toLowerCase();
  if (!IMAGE_CONFIG.ALLOWED_EXTENSIONS.includes(extension)) {
    return {
      valid: false,
      code: CLOUDINARY_ERROR_CODES.INVALID_FORMAT,
      message: 'Formato de imagem não suportado',
    };
  }

  return { valid: true };
};

/**
 * Pick image from device gallery
 * 
 * @returns {Object} - { success: boolean, image: Object | null, error: Error | null, code: string | null }
 */
export const pickImage = async () => {
  try {
    // Launch picker - will request permission automatically if needed
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: false,
      aspect: [1, 1],
      quality: 0.8,
    });

    // Handle cancellation - check for both possible properties
    if (result.cancelled === true || result.canceled === true) {
      return {
        success: false,
        image: null,
        error: null,
        code: CLOUDINARY_ERROR_CODES.SELECTION_CANCELLED,
      };
    }

    // Get the first selected image
    const selectedImage = result.assets?.[0];
    if (!selectedImage) {
      return {
        success: false,
        image: null,
        error: new Error('Nenhuma imagem selecionada'),
        code: CLOUDINARY_ERROR_CODES.INVALID_FILE,
      };
    }

    // Validate image
    const validation = validateImage(selectedImage);
    if (!validation.valid) {
      return {
        success: false,
        image: null,
        error: new Error(validation.message),
        code: validation.code,
      };
    }

    return {
      success: true,
      image: selectedImage,
      error: null,
      code: null,
    };
  } catch (error) {
    console.error('Erro ao selecionar imagem:', error);
    
    // Check if it's a permission error
    if (error.message?.includes('Permission') || error.message?.includes('permission')) {
      return {
        success: false,
        image: null,
        error,
        code: CLOUDINARY_ERROR_CODES.PERMISSION_DENIED,
      };
    }

    return {
      success: false,
      image: null,
      error,
      code: CLOUDINARY_ERROR_CODES.UNKNOWN_ERROR,
    };
  }
};

/**
 * Upload image to Cloudinary through backend
 * 
 * @param {Object} image - Image object from pickImage()
 * @param {string} folder - Cloudinary folder (e.g., 'users', 'professionals', 'clinics')
 * @param {Object} metadata - Additional metadata (e.g., userId, entityId)
 * @param {Function} onProgress - Progress callback: (progress) => void
 * @returns {Object} - { success: boolean, url: string | null, publicId: string | null, error: Error | null, code: string | null }
 */
export const uploadImageToCloudinary = async (image, folder = 'users', metadata = {}, onProgress = null) => {
  try {
    if (!image || !image.uri) {
      return {
        success: false,
        url: null,
        publicId: null,
        error: new Error('Invalid image'),
        code: CLOUDINARY_ERROR_CODES.INVALID_FILE,
      };
    }

    // Prepare FormData
    const formData = new FormData();
    
    // Append image file
    formData.append('file', {
      uri: image.uri,
      name: image.filename || `image_${Date.now()}.jpg`,
      type: image.mimeType || 'image/jpeg',
    });

    // Append folder and metadata
    formData.append('folder', folder);
    if (metadata && Object.keys(metadata).length > 0) {
      formData.append('metadata', JSON.stringify(metadata));
    }

    // Upload with progress tracking
    const response = await axios.post(
      `${API_BASE_URL}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 second timeout
        onUploadProgress: (progressEvent) => {
          if (onProgress) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(percentCompleted);
          }
        },
      }
    );

    // Validate response
    if (!response.data || response.status !== 200) {
      return {
        success: false,
        url: null,
        publicId: null,
        error: new Error('Invalid response from server'),
        code: CLOUDINARY_ERROR_CODES.UPLOAD_FAILED,
      };
    }

    const { secure_url, public_id } = response.data;

    if (!secure_url) {
      return {
        success: false,
        url: null,
        publicId: null,
        error: new Error('No URL returned from server'),
        code: CLOUDINARY_ERROR_CODES.UPLOAD_FAILED,
      };
    }

    return {
      success: true,
      url: secure_url,
      publicId: public_id || null,
      error: null,
      code: null,
    };
  } catch (error) {
    console.error('Image upload error:', error);

    // Categorize network errors
    let code = CLOUDINARY_ERROR_CODES.UPLOAD_FAILED;
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      code = CLOUDINARY_ERROR_CODES.TIMEOUT_ERROR;
    } else if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      code = CLOUDINARY_ERROR_CODES.NETWORK_ERROR;
    }

    return {
      success: false,
      url: null,
      publicId: null,
      error,
      code,
    };
  }
};

/**
 * Delete image from Cloudinary through backend
 * 
 * @param {string} publicId - Cloudinary public ID of the image
 * @returns {Object} - { success: boolean, error: Error | null, code: string | null }
 */
export const deleteImageFromCloudinary = async (publicId) => {
  try {
    if (!publicId) {
      return {
        success: false,
        error: new Error('Public ID is required'),
        code: CLOUDINARY_ERROR_CODES.INVALID_FILE,
      };
    }

    const response = await axios.delete(
      `${API_BASE_URL}/images/${publicId}`,
      { timeout: 10000 }
    );

    if (response.status === 200 || response.status === 204) {
      return {
        success: true,
        error: null,
        code: null,
      };
    }

    return {
      success: false,
      error: new Error('Failed to delete image'),
      code: CLOUDINARY_ERROR_CODES.UPLOAD_FAILED,
    };
  } catch (error) {
    console.error('Image deletion error:', error);

    let code = CLOUDINARY_ERROR_CODES.UPLOAD_FAILED;
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      code = CLOUDINARY_ERROR_CODES.TIMEOUT_ERROR;
    } else if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      code = CLOUDINARY_ERROR_CODES.NETWORK_ERROR;
    }

    return {
      success: false,
      error,
      code,
    };
  }
};

/**
 * Get user-friendly error message
 */
export const getErrorMessage = (code, error = null) => {
  const messages = {
    [CLOUDINARY_ERROR_CODES.PERMISSION_DENIED]: 'Permissão negada para acessar a galeria de fotos',
    [CLOUDINARY_ERROR_CODES.SELECTION_CANCELLED]: 'Seleção de imagem cancelada',
    [CLOUDINARY_ERROR_CODES.INVALID_FILE]: 'Arquivo inválido',
    [CLOUDINARY_ERROR_CODES.FILE_TOO_LARGE]: 'Arquivo muito grande (máximo 5MB)',
    [CLOUDINARY_ERROR_CODES.INVALID_FORMAT]: 'Formato de imagem não suportado',
    [CLOUDINARY_ERROR_CODES.UPLOAD_FAILED]: 'Falha ao enviar imagem',
    [CLOUDINARY_ERROR_CODES.NETWORK_ERROR]: 'Erro de conexão. Verifique sua internet',
    [CLOUDINARY_ERROR_CODES.TIMEOUT_ERROR]: 'Conexão expirou. Tente novamente',
    [CLOUDINARY_ERROR_CODES.DATABASE_ERROR]: 'Erro ao salvar dados',
    [CLOUDINARY_ERROR_CODES.UNKNOWN_ERROR]: 'Erro desconhecido',
  };

  return messages[code] || 'Erro desconhecido. Tente novamente.';
};
