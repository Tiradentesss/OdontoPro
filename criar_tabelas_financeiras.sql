-- ========================================
-- TABELAS FINANCEIRAS - OdontoPro
-- ========================================

-- Tabela de Transações Financeiras
CREATE TABLE IF NOT EXISTS odontoPro_financeiro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    clinica_id INT NOT NULL,
    tipo ENUM('receita', 'despesa') NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    categoria VARCHAR(100),
    data DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (clinica_id) REFERENCES odontoPro_clinica(id) ON DELETE CASCADE,
    INDEX idx_clinica_id (clinica_id),
    INDEX idx_data (data),
    INDEX idx_tipo (tipo),
    INDEX idx_clinica_data (clinica_id, data)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- INSERTS DE TESTE (OPCIONAL)
-- ========================================
-- INSERT INTO odontoPro_financeiro (clinica_id, tipo, descricao, valor, categoria, data) 
-- VALUES 
-- (1, 'receita', 'Consulta Odontológica - João Silva', 250.00, 'Consulta', '2026-05-04 14:30:00'),
-- (1, 'despesa', 'Materiais de Limpeza', 450.00, 'Insumos', '2026-05-03 09:15:00'),
-- (1, 'despesa', 'Manutenção Ar Condicionado', 300.00, 'Manutenção', '2026-05-02 10:00:00');
