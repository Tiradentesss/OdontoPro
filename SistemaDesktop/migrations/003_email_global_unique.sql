DELIMITER $$

CREATE TABLE IF NOT EXISTS odontoPro_email_global (
    id BIGINT NOT NULL AUTO_INCREMENT,
    email_normalizado VARCHAR(255) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    entidade_id BIGINT NOT NULL,
    criado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    UNIQUE KEY uk_odontoPro_email_global_email (email_normalizado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci$$

INSERT INTO odontoPro_email_global (email_normalizado, tipo, entidade_id)
SELECT LOWER(TRIM(email)), 'paciente', id
FROM odontoPro_paciente
WHERE email IS NOT NULL AND TRIM(email) <> ''
ON DUPLICATE KEY UPDATE entidade_id = VALUES(entidade_id)$$

INSERT INTO odontoPro_email_global (email_normalizado, tipo, entidade_id)
SELECT LOWER(TRIM(email)), 'medico', id
FROM odontoPro_medico
WHERE email IS NOT NULL AND TRIM(email) <> ''
ON DUPLICATE KEY UPDATE entidade_id = VALUES(entidade_id)$$

INSERT INTO odontoPro_email_global (email_normalizado, tipo, entidade_id)
SELECT LOWER(TRIM(email)), 'gerente', id
FROM odontoPro_gerenciamento
WHERE email IS NOT NULL AND TRIM(email) <> ''
ON DUPLICATE KEY UPDATE entidade_id = VALUES(entidade_id)$$

DROP TRIGGER IF EXISTS trg_paciente_email_ai$$
CREATE TRIGGER trg_paciente_email_ai
AFTER INSERT ON odontoPro_paciente
FOR EACH ROW
BEGIN
    IF NEW.email IS NOT NULL AND TRIM(NEW.email) <> '' THEN
        INSERT IGNORE INTO odontoPro_email_global (email_normalizado, tipo, entidade_id)
        VALUES (LOWER(TRIM(NEW.email)), 'paciente', NEW.id);
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_paciente_email_au$$
CREATE TRIGGER trg_paciente_email_au
AFTER UPDATE ON odontoPro_paciente
FOR EACH ROW
BEGIN
    DELETE FROM odontoPro_email_global
    WHERE tipo = 'paciente' AND entidade_id = OLD.id;

    IF NEW.email IS NOT NULL AND TRIM(NEW.email) <> '' THEN
        INSERT IGNORE INTO odontoPro_email_global (email_normalizado, tipo, entidade_id)
        VALUES (LOWER(TRIM(NEW.email)), 'paciente', NEW.id);
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_paciente_email_ad$$
CREATE TRIGGER trg_paciente_email_ad
AFTER DELETE ON odontoPro_paciente
FOR EACH ROW
BEGIN
    DELETE FROM odontoPro_email_global
    WHERE tipo = 'paciente' AND entidade_id = OLD.id;
END$$

DROP TRIGGER IF EXISTS trg_medico_email_ai$$
CREATE TRIGGER trg_medico_email_ai
AFTER INSERT ON odontoPro_medico
FOR EACH ROW
BEGIN
    IF NEW.email IS NOT NULL AND TRIM(NEW.email) <> '' THEN
        INSERT IGNORE INTO odontoPro_email_global (email_normalizado, tipo, entidade_id)
        VALUES (LOWER(TRIM(NEW.email)), 'medico', NEW.id);
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_medico_email_au$$
CREATE TRIGGER trg_medico_email_au
AFTER UPDATE ON odontoPro_medico
FOR EACH ROW
BEGIN
    DELETE FROM odontoPro_email_global
    WHERE tipo = 'medico' AND entidade_id = OLD.id;

    IF NEW.email IS NOT NULL AND TRIM(NEW.email) <> '' THEN
        INSERT IGNORE INTO odontoPro_email_global (email_normalizado, tipo, entidade_id)
        VALUES (LOWER(TRIM(NEW.email)), 'medico', NEW.id);
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_medico_email_ad$$
CREATE TRIGGER trg_medico_email_ad
AFTER DELETE ON odontoPro_medico
FOR EACH ROW
BEGIN
    DELETE FROM odontoPro_email_global
    WHERE tipo = 'medico' AND entidade_id = OLD.id;
END$$

DROP TRIGGER IF EXISTS trg_gerente_email_ai$$
CREATE TRIGGER trg_gerente_email_ai
AFTER INSERT ON odontoPro_gerenciamento
FOR EACH ROW
BEGIN
    IF NEW.email IS NOT NULL AND TRIM(NEW.email) <> '' THEN
        INSERT IGNORE INTO odontoPro_email_global (email_normalizado, tipo, entidade_id)
        VALUES (LOWER(TRIM(NEW.email)), 'gerente', NEW.id);
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_gerente_email_au$$
CREATE TRIGGER trg_gerente_email_au
AFTER UPDATE ON odontoPro_gerenciamento
FOR EACH ROW
BEGIN
    DELETE FROM odontoPro_email_global
    WHERE tipo = 'gerente' AND entidade_id = OLD.id;

    IF NEW.email IS NOT NULL AND TRIM(NEW.email) <> '' THEN
        INSERT IGNORE INTO odontoPro_email_global (email_normalizado, tipo, entidade_id)
        VALUES (LOWER(TRIM(NEW.email)), 'gerente', NEW.id);
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_gerente_email_ad$$
CREATE TRIGGER trg_gerente_email_ad
AFTER DELETE ON odontoPro_gerenciamento
FOR EACH ROW
BEGIN
    DELETE FROM odontoPro_email_global
    WHERE tipo = 'gerente' AND entidade_id = OLD.id;
END$$

DELIMITER ;
