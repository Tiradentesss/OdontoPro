const DEFAULT_AVATAR_COLORS = {
  background: '0D8ABC',
  color: 'fff',
  size: 120,
};

const normalizePatientPhoto = (value) => {
  if (!value || typeof value !== 'string') return null;
  const trimmed = value.trim();
  if (!trimmed) return null;
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://') || trimmed.startsWith('data:')) {
    return trimmed;
  }
  return null;
};

const getPatientAvatarSource = (patient = {}) => {
  const photo =
    normalizePatientPhoto(patient.foto) ||
    normalizePatientPhoto(patient.paciente_foto) ||
    normalizePatientPhoto(patient.image_url) ||
    normalizePatientPhoto(patient.avatar) ||
    normalizePatientPhoto(patient.profile_image) ||
    null;

  if (photo) {
    return { uri: photo };
  }

  const name = patient?.nome || patient?.name || 'Paciente';
  const encodedName = encodeURIComponent(name);
  return {
    uri: `https://ui-avatars.com/api/?name=${encodedName}&background=${DEFAULT_AVATAR_COLORS.background}&color=${DEFAULT_AVATAR_COLORS.color}&size=${DEFAULT_AVATAR_COLORS.size}`,
  };
};

module.exports = {
  getPatientAvatarSource,
  normalizePatientPhoto,
};
