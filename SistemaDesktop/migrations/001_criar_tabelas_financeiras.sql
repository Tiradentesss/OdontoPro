-- ============================================
-- SCRIPT PARA CRIAR TABELAS FINANCEIRAS
-- OdontoPro - Banco de Dados
-- Data: 28/05/2026
-- ============================================

-- Verificar se a tabela já existe
DROP TABLE IF EXISTS `odontoPro_financeiro`;

-- ============================================
-- TABELA PRINCIPAL DE FINANCEIRO
-- ============================================
CREATE TABLE `odontoPro_financeiro` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `clinica_id` INT NOT NULL,
    `tipo` ENUM('receita', 'despesa') NOT NULL,
    `descricao` VARCHAR(255) NOT NULL,
    `valor` DECIMAL(10, 2) NOT NULL,
    `categoria` VARCHAR(100),
    `data` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `criado_em` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `atualizado_em` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices para melhor performance
    INDEX `idx_clinica_id` (`clinica_id`),
    INDEX `idx_tipo` (`tipo`),
    INDEX `idx_data` (`data`),
    INDEX `idx_categoria` (`categoria`),
    
    -- Relacionamento com clínica
    CONSTRAINT `fk_financeiro_clinica` 
        FOREIGN KEY (`clinica_id`) 
        REFERENCES `odontoPro_clinica`(`id`) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- ALGUNS DADOS DE EXEMPLO (Opcional)
-- ============================================
-- Descomente para popular com dados de teste

/*
INSERT INTO `odontoPro_financeiro` 
(`clinica_id`, `tipo`, `descricao`, `valor`, `categoria`, `data`) 
VALUES 
(1, 'receita', 'Consulta Odontológica - Paciente 1', 250.00, 'Consulta', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(1, 'despesa', 'Materiais de Limpeza', 450.00, 'Material', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(1, 'despesa', 'Manutenção Ar Condicionado', 300.00, 'Manutenção', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(1, 'receita', 'Consulta Odontológica - Paciente 2', 250.00, 'Consulta', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(1, 'receita', 'Tratamento de Canal', 800.00, 'Tratamento', DATE_SUB(NOW(), INTERVAL 5 DAY)),
(1, 'despesa', 'Aluguel', 2000.00, 'Aluguel', DATE_SUB(NOW(), INTERVAL 7 DAY)),
(1, 'receita', 'Limpeza Dental - Paciente 3', 150.00, 'Limpeza', DATE_SUB(NOW(), INTERVAL 8 DAY));
*/

-- ============================================
-- VERIFICAR ESTRUTURA
-- ============================================
-- DESCRIBE `odontoPro_financeiro`;

-- ============================================
-- VISUALIZAÇÕES (VIEWS) ÚTEIS
-- ============================================

-- View para resumo diário
CREATE OR REPLACE VIEW `vw_financeiro_diario` AS
SELECT 
    DATE(data) as data,
    SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END) as total_receita,
    SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END) as total_despesa,
    (SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END) - 
     SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END)) as lucro_diario,
    clinica_id
FROM `odontoPro_financeiro`
GROUP BY DATE(data), clinica_id
ORDER BY data DESC;

-- View para resumo mensal
CREATE OR REPLACE VIEW `vw_financeiro_mensal` AS
SELECT 
    YEAR(data) as ano,
    MONTH(data) as mes,
    DATE_FORMAT(data, '%Y-%m') as periodo,
    SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END) as total_receita,
    SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END) as total_despesa,
    (SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END) - 
     SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END)) as lucro_mensal,
    clinica_id
FROM `odontoPro_financeiro`
GROUP BY YEAR(data), MONTH(data), clinica_id
ORDER BY ano DESC, mes DESC;

-- View para resumo por categoria
CREATE OR REPLACE VIEW `vw_financeiro_categoria` AS
SELECT 
    categoria,
    tipo,
    COUNT(*) as quantidade,
    SUM(valor) as total,
    AVG(valor) as media,
    clinica_id
FROM `odontoPro_financeiro`
WHERE categoria IS NOT NULL
GROUP BY categoria, tipo, clinica_id
ORDER BY total DESC;

-- ============================================
-- QUERIES ÚTEIS
-- ============================================

-- Buscar saldo geral de uma clínica
-- SELECT 
--     clinica_id,
--     SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END) as total_receita,
--     SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END) as total_despesa,
--     (SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END) - 
--      SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END)) as saldo_total
-- FROM `odontoPro_financeiro`
-- WHERE clinica_id = 1
-- GROUP BY clinica_id;

-- ============================================
-- FIM DO SCRIPT
-- ============================================
