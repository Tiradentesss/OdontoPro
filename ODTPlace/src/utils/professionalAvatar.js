const normalizeProfessionalPhoto = (value) => {
  if (!value || typeof value !== 'string') return null;
  const photo = value.trim();
  if (!photo) return null;
  if (photo.startsWith('http://') || photo.startsWith('https://') || photo.startsWith('data:')) {
    return photo;
  }
  return null;
};

const getProfessionalAvatarSource = (professional = {}) => {
  const photo =
    normalizeProfessionalPhoto(professional.foto) ||
    normalizeProfessionalPhoto(professional.profile_image) ||
    normalizeProfessionalPhoto(professional.image_url) ||
    normalizeProfessionalPhoto(professional.avatar) ||
    null;

  return photo ? { uri: photo } : null;
};

module.exports = {
  getProfessionalAvatarSource,
};