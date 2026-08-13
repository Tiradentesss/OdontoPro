/**
 * Image Selector Component
 * 
 * A reusable component for selecting and uploading images from the device gallery.
 * Handles image selection, validation, upload progress, and error display.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
  StyleSheet,
  Modal,
  ScrollView,
  Platform,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { pickImage } from '../services/cloudinaryService';
import { uploadImage } from '../services/api';
import {
  CLOUDINARY_ERROR_CODES,
  getErrorMessage,
} from '../services/cloudinaryService';

const ImageSelector = ({
  currentImageUri = null,
  onImageSelected = null,
  onUploadSuccess = null,
  onUploadError = null,
  folder = 'users',
  metadata = {},
  style = {},
  imageStyle = {},
  placeholderText = 'Selecionar Imagem',
  disabled = false,
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedImage, setSelectedImage] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Handle image selection from gallery
   */
  const handleSelectImage = async () => {
    if (disabled || isUploading) return;

    setError(null);

    // Pick image
    const pickResult = await pickImage();

    if (!pickResult.success) {
      // Ignore cancellation
      if (pickResult.code === CLOUDINARY_ERROR_CODES.SELECTION_CANCELLED) {
        return;
      }

      // Show error
      const errorMessage = getErrorMessage(pickResult.code, pickResult.error);
      setError(errorMessage);

      if (onUploadError) {
        onUploadError({
          code: pickResult.code,
          message: errorMessage,
          error: pickResult.error,
        });
      }

      Alert.alert('Erro na Seleção', errorMessage);
      return;
    }

    // Store selected image
    const image = pickResult.image;
    setSelectedImage(image);

    // Show preview
    setShowPreview(true);

    // Call callback with selected image
    if (onImageSelected) {
      onImageSelected(image);
    }
  };

  /**
   * Handle image upload to Cloudinary
   */
  const handleUploadImage = async () => {
    if (!selectedImage || isUploading) return;

    setError(null);
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const uploadResult = await uploadImage(
        selectedImage,
        folder,
        metadata,
        (progress) => setUploadProgress(progress)
      );

      if (!uploadResult || !uploadResult.secure_url) {
        throw new Error('No URL returned from server');
      }

      // Success
      setShowPreview(false);
      setSelectedImage(null);
      setUploadProgress(0);

      if (onUploadSuccess) {
        onUploadSuccess({
          url: uploadResult.secure_url,
          publicId: uploadResult.public_id,
          imageData: uploadResult,
        });
      }

      Alert.alert('Sucesso', 'Imagem enviada com sucesso!');
    } catch (error) {
      console.error('Upload error:', error);

      // Determine error code
      let code = CLOUDINARY_ERROR_CODES.UPLOAD_FAILED;
      if (error.message?.includes('timeout')) {
        code = CLOUDINARY_ERROR_CODES.TIMEOUT_ERROR;
      } else if (error.code === 'ECONNREFUSED') {
        code = CLOUDINARY_ERROR_CODES.NETWORK_ERROR;
      }

      const errorMessage = getErrorMessage(code, error);
      setError(errorMessage);

      if (onUploadError) {
        onUploadError({
          code,
          message: errorMessage,
          error,
        });
      }

      Alert.alert('Erro no Upload', errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  /**
   * Handle cancel
   */
  const handleCancel = () => {
    setShowPreview(false);
    setSelectedImage(null);
    setUploadProgress(0);
    setError(null);
  };

  return (
    <View style={[styles.container, style]}>
      {/* Display current image or button to select */}
      {currentImageUri ? (
        <View style={styles.currentImageContainer}>
          <Image
            source={{ uri: currentImageUri }}
            style={[styles.currentImage, imageStyle]}
            onError={() => setError('Failed to load image')}
          />
          <TouchableOpacity
            style={styles.editButton}
            onPress={handleSelectImage}
            disabled={disabled || isUploading}
          >
            <Feather name="edit-2" size={16} color="#fff" />
          </TouchableOpacity>
        </View>
      ) : (
        <TouchableOpacity
          style={[styles.selectButton, disabled && styles.selectButtonDisabled]}
          onPress={handleSelectImage}
          disabled={disabled || isUploading}
        >
          <Feather name="camera" size={24} color="#0ea5e9" />
          <Text style={styles.selectButtonText}>{placeholderText}</Text>
        </TouchableOpacity>
      )}

      {/* Error message */}
      {error && (
        <View style={styles.errorContainer}>
          <Feather name="alert-circle" size={16} color="#ef4444" />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Image Preview & Upload Modal */}
      <Modal
        visible={showPreview}
        transparent
        animationType="slide"
        onRequestClose={handleCancel}
      >
        <View style={styles.modalOverlay}>
          <ScrollView
            contentContainerStyle={styles.modalContent}
            showsVerticalScrollIndicator={false}
          >
            {/* Header */}
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Prévia da Imagem</Text>
              <TouchableOpacity
                onPress={handleCancel}
                disabled={isUploading}
              >
                <Feather name="x" size={24} color="#0f172a" />
              </TouchableOpacity>
            </View>

            {/* Image Preview */}
            <View style={styles.previewImageContainer}>
              {selectedImage?.uri && (
                <Image
                  source={{ uri: selectedImage.uri }}
                  style={styles.previewImage}
                  resizeMode="contain"
                  onError={() => setError('Failed to load preview')}
                />
              )}
            </View>

            {/* Upload Progress */}
            {isUploading && (
              <View style={styles.progressContainer}>
                <Text style={styles.progressText}>Enviando... {uploadProgress}%</Text>
                <View style={styles.progressBar}>
                  <View
                    style={[
                      styles.progressFill,
                      { width: `${uploadProgress}%` },
                    ]}
                  />
                </View>
              </View>
            )}

            {/* File Info */}
            <View style={styles.fileInfoContainer}>
              <Text style={styles.fileInfoLabel}>Nome do arquivo:</Text>
              <Text style={styles.fileInfoValue}>{selectedImage?.filename || 'imagem.jpg'}</Text>
              <Text style={styles.fileInfoLabel} style={{ marginTop: 8 }}>Tamanho:</Text>
              <Text style={styles.fileInfoValue}>
                {selectedImage?.size
                  ? `${(selectedImage.size / (1024 * 1024)).toFixed(2)} MB`
                  : 'Desconhecido'}
              </Text>
            </View>

            {/* Error Message in Modal */}
            {error && (
              <View style={styles.modalErrorContainer}>
                <Feather name="alert-circle" size={18} color="#ef4444" />
                <Text style={styles.modalErrorText}>{error}</Text>
              </View>
            )}

            {/* Action Buttons */}
            <View style={styles.buttonContainer}>
              <TouchableOpacity
                style={[styles.button, styles.cancelButton]}
                onPress={handleCancel}
                disabled={isUploading}
              >
                {isUploading ? (
                  <ActivityIndicator color="#0f172a" size="small" />
                ) : (
                  <Text style={styles.cancelButtonText}>Cancelar</Text>
                )}
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.button, styles.uploadButton, isUploading && styles.uploadButtonDisabled]}
                onPress={handleUploadImage}
                disabled={isUploading}
              >
                {isUploading ? (
                  <ActivityIndicator color="#fff" size="small" />
                ) : (
                  <>
                    <Feather name="upload-cloud" size={18} color="#fff" />
                    <Text style={styles.uploadButtonText}>Enviar Imagem</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          </ScrollView>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginVertical: 16,
  },

  currentImageContainer: {
    position: 'relative',
    alignItems: 'center',
  },

  currentImage: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#f1f5f9',
  },

  editButton: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#0ea5e9',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.25,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 3.84,
    elevation: 5,
  },

  selectButton: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#eef8ff',
    borderWidth: 2,
    borderColor: '#dbeafe',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
  },

  selectButtonDisabled: {
    opacity: 0.5,
  },

  selectButtonText: {
    color: '#0ea5e9',
    fontSize: 12,
    fontWeight: '600',
    marginTop: 8,
    textAlign: 'center',
  },

  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fee2e2',
    borderRadius: 8,
    padding: 12,
    marginTop: 12,
    marginHorizontal: 16,
  },

  errorText: {
    color: '#dc2626',
    fontSize: 12,
    marginLeft: 8,
    flex: 1,
    flexWrap: 'wrap',
  },

  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },

  modalContent: {
    flexGrow: 1,
    backgroundColor: '#fff',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 40,
  },

  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },

  modalTitle: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0f172a',
  },

  previewImageContainer: {
    width: '100%',
    height: 300,
    backgroundColor: '#f1f5f9',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },

  previewImage: {
    width: '100%',
    height: '100%',
    borderRadius: 12,
  },

  progressContainer: {
    marginBottom: 20,
  },

  progressText: {
    fontSize: 14,
    color: '#0f172a',
    marginBottom: 8,
    fontWeight: '600',
  },

  progressBar: {
    height: 4,
    backgroundColor: '#e2e8f0',
    borderRadius: 2,
    overflow: 'hidden',
  },

  progressFill: {
    height: '100%',
    backgroundColor: '#0ea5e9',
  },

  fileInfoContainer: {
    backgroundColor: '#f8fafc',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
  },

  fileInfoLabel: {
    fontSize: 12,
    color: '#64748b',
    fontWeight: '600',
    marginBottom: 4,
  },

  fileInfoValue: {
    fontSize: 14,
    color: '#0f172a',
    fontWeight: '500',
  },

  modalErrorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fee2e2',
    borderRadius: 8,
    padding: 12,
    marginBottom: 20,
  },

  modalErrorText: {
    color: '#dc2626',
    fontSize: 13,
    marginLeft: 8,
    flex: 1,
    flexWrap: 'wrap',
  },

  buttonContainer: {
    flexDirection: 'row',
    gap: 12,
  },

  button: {
    flex: 1,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    flexDirection: 'row',
    gap: 8,
  },

  cancelButton: {
    backgroundColor: '#e2e8f0',
  },

  cancelButtonText: {
    color: '#0f172a',
    fontWeight: '600',
    fontSize: 14,
  },

  uploadButton: {
    backgroundColor: '#0ea5e9',
  },

  uploadButtonDisabled: {
    opacity: 0.6,
  },

  uploadButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
  },
});

export default ImageSelector;
