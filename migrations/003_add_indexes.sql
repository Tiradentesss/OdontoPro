-- Migration 003: Add useful indexes to speed up lookups
-- Run this once against the application's database.

-- Index for medico lookup by clinica_id
ALTER TABLE odontoPro_medico
  ADD INDEX idx_medico_clinica_id (clinica_id);

-- Index for medico lookup by status/ativo
ALTER TABLE odontoPro_medico
  ADD INDEX idx_medico_ativo (ativo);

-- Index for medico_especialidades lookup by medico_id and especialidade_id
ALTER TABLE odontoPro_medico_especialidades
  ADD INDEX idx_me_medico_id (medico_id),
  ADD INDEX idx_me_especialidade_id (especialidade_id);

-- Index for consultas that reference especialidade_id
ALTER TABLE odontoPro_consulta
  ADD INDEX idx_consulta_especialidade_id (especialidade_id);

-- Index for any user/gerenciamento lookups by clinica_id
ALTER TABLE odontoPro_gerenciamento
  ADD INDEX idx_gerenciamento_clinica_id (clinica_id);

-- Note: If these indexes already exist, the ALTER TABLE will fail. Run with
-- caution or adapt to check information_schema before creating.
