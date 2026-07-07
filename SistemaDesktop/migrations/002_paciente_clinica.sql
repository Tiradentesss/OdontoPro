-- ============================================
-- MIGRATION: criar tabela paciente_clinica e migrar vínculos existentes
-- ============================================

-- Cria a tabela de vínculo entre pacientes e clínicas
CREATE TABLE IF NOT EXISTS `paciente_clinica` (
    `paciente_id` BIGINT NOT NULL,
    `clinica_id` BIGINT NOT NULL,
    `data_vinculo` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status` VARCHAR(30) NOT NULL DEFAULT 'ativo',
    PRIMARY KEY (`paciente_id`, `clinica_id`),
    INDEX `idx_paciente_clinica_clinica_id` (`clinica_id`),
    CONSTRAINT `fk_paciente_clinica_paciente`
        FOREIGN KEY (`paciente_id`) REFERENCES `odontoPro_paciente`(`id`)
        ON DELETE CASCADE,
    CONSTRAINT `fk_paciente_clinica_clinica`
        FOREIGN KEY (`clinica_id`) REFERENCES `odontoPro_clinica`(`id`)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Migrar vínculos existentes de pacientes para clínicas
INSERT IGNORE INTO `paciente_clinica` (`paciente_id`, `clinica_id`, `data_vinculo`, `status`)
SELECT `id`, `clinica_id`, NOW(), 'ativo'
FROM `odontoPro_paciente`
WHERE `clinica_id` IS NOT NULL;

-- Remover referência direta à clínica na tabela de pacientes
ALTER TABLE `odontoPro_paciente`
    DROP FOREIGN KEY `odontoPro_paciente_clinica_id_8bbed182_fk_odontoPro_clinica_id`;

ALTER TABLE `odontoPro_paciente`
    DROP COLUMN `clinica_id`;

-- Verificação rápida
-- DESCRIBE `paciente_clinica`;
-- SELECT COUNT(*) FROM `paciente_clinica`;
