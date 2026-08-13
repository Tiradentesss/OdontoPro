/**
 * useImageUpload Hook
 * 
 * Custom hook to handle image selection and upload to Cloudinary
 * Provides simplified interface for components needing image upload functionality
 */

import { useState } from 'react';
import { pickImage } from '../services/cloudinaryService';
import { uploadImage } from '../services/api';
import {
  CLOUDINARY_ERROR_CODES,
  getErrorMessage,
} from '../services/cloudinaryService';

export const useImageUpload = (options = {}) => {
  const {
    folder = 'users',
    metadata = {},
    onSuccess = null,
    onError = null,
  } = options;

  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);

  /**
   * Select image from device gallery
   */
  const selectImage = async () => {
    setError(null);
    const result = await pickImage();

    if (!result.success) {
      if (result.code === CLOUDINARY_ERROR_CODES.SELECTION_CANCELLED) {
        return { success: false, cancelled: true };
      }

      const errorMessage = getErrorMessage(result.code, result.error);
      setError(errorMessage);

      if (onError) {
        onError({
          code: result.code,
          message: errorMessage,
          error: result.error,
        });
      }

      return { success: false, cancelled: false, error: errorMessage };
    }

    setSelectedImage(result.image);
    return { success: true, image: result.image };
  };

  /**
   * Upload selected or provided image
   */
  const uploadImage_ = async (imageToUpload = null) => {
    const imageFile = imageToUpload || selectedImage;

    if (!imageFile) {
      const errorMessage = 'No image selected';
      setError(errorMessage);
      if (onError) {
        onError({
          code: CLOUDINARY_ERROR_CODES.INVALID_FILE,
          message: errorMessage,
          error: new Error(errorMessage),
        });
      }
      return { success: false, error: errorMessage };
    }

    setError(null);
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const uploadResult = await uploadImage(
        imageFile,
        folder,
        metadata,
        (progress) => setUploadProgress(progress)
      );

      if (!uploadResult || !uploadResult.secure_url) {
        throw new Error('No URL returned from server');
      }

      setSelectedImage(null);
      setUploadProgress(0);

      if (onSuccess) {
        onSuccess({
          url: uploadResult.secure_url,
          publicId: uploadResult.public_id,
          imageData: uploadResult,
        });
      }

      return {
        success: true,
        url: uploadResult.secure_url,
        publicId: uploadResult.public_id,
        imageData: uploadResult,
      };
    } catch (err) {
      console.error('Upload error:', err);

      let code = CLOUDINARY_ERROR_CODES.UPLOAD_FAILED;
      if (err.message?.includes('timeout')) {
        code = CLOUDINARY_ERROR_CODES.TIMEOUT_ERROR;
      } else if (err.code === 'ECONNREFUSED') {
        code = CLOUDINARY_ERROR_CODES.NETWORK_ERROR;
      }

      const errorMessage = getErrorMessage(code, err);
      setError(errorMessage);

      if (onError) {
        onError({
          code,
          message: errorMessage,
          error: err,
        });
      }

      return { success: false, error: errorMessage };
    } finally {
      setIsUploading(false);
    }
  };

  /**
   * Cancel upload and reset state
   */
  const cancel = () => {
    setSelectedImage(null);
    setUploadProgress(0);
    setError(null);
    setIsUploading(false);
  };

  /**
   * Reset all state
   */
  const reset = () => {
    cancel();
    setUploadProgress(0);
  };

  return {
    isUploading,
    uploadProgress,
    error,
    selectedImage,
    selectImage,
    uploadImage: uploadImage_,
    cancel,
    reset,
  };
};
