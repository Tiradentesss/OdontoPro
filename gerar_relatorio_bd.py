#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para gerar PDF com relatório de diagnóstico do banco de dados OdontoPro
Requer: reportlab (instala automaticamente se não existir)
"""

import subprocess
import sys
import os

# Tentar importar reportlab, se não existir, instala
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
    from reportlab.lib import colors
    from datetime import datetime
except ImportError:
    print("Instalando reportlab...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
    from reportlab.lib import colors
    from datetime import datetime


def gerar_pdf():
    """Gera PDF com relatório de diagnóstico do banco de dados"""
    
    # Configurar caminho do PDF
    pdf_path = "DIAGNOSTICO_BANCO_DADOS.pdf"
    
    # Criar documento
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0891B2'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#0891B2'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=10,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    error_style = ParagraphStyle(
        'ErrorStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#DC2626'),
        spaceAfter=4,
        fontName='Courier'
    )
    
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=4,
        fontName='Courier',
        leftIndent=20
    )
    
    # Container para elementos
    elements = []
    
    # ==================== CAPA ====================
    elements.append(Spacer(1, 1.5*cm))
    elements.append(Paragraph("🔧 OdontoPro", title_style))
    elements.append(Paragraph("Diagnóstico do Banco de Dados", heading1_style))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 1*cm))
    
    # ==================== RESUMO EXECUTIVO ====================
    elements.append(Paragraph("📌 RESUMO EXECUTIVO", heading1_style))
    elements.append(Paragraph(
        "<b>Status Geral:</b> ⚠️ PARCIALMENTE CONECTADO",
        normal_style
    ))
    elements.append(Paragraph(
        "<b>Módulos Funcionais:</b> 60%",
        normal_style
    ))
    elements.append(Paragraph(
        "<b>Problemas Identificados:</b> 2 críticos",
        normal_style
    ))
    elements.append(Spacer(1, 0.5*cm))
    
    # ==================== PROBLEMAS ENCONTRADOS ====================
    elements.append(Paragraph("🚨 PROBLEMAS ENCONTRADOS", heading1_style))
    
    # Problema 1
    elements.append(Paragraph("❌ Problema 1: Tabela de Financeiro Não Existe", heading2_style))
    elements.append(Paragraph(
        "<b>Erro observado:</b>",
        normal_style
    ))
    elements.append(Paragraph(
        "[ERROR] Erro ao obter resumo: 1146 (42S02): Table 'odontoprodb.odontopro_financeiro' doesn't exist",
        error_style
    ))
    elements.append(Paragraph(
        "<b>Impacto:</b> A aba de Financeiro não consegue carregar dados de transações. "
        "O resumo financeiro no Painel não funciona.",
        normal_style
    ))
    elements.append(Paragraph(
        "<b>Solução:</b> Executar a migration SQL que cria a tabela odontoPro_financeiro.",
        normal_style
    ))
    elements.append(Spacer(1, 0.3*cm))
    
    # Problema 2
    elements.append(Paragraph("❌ Problema 2: Coluna clinica_id Faltando", heading2_style))
    elements.append(Paragraph(
        "<b>Erro observado:</b>",
        normal_style
    ))
    elements.append(Paragraph(
        "[ERROR] Erro ao contar cadastros: 1054 (42S22): Unknown column 'clinica_id' in 'where clause'",
        error_style
    ))
    elements.append(Paragraph(
        "<b>Impacto:</b> O Painel não consegue contar pacientes, médicos e gerentes. "
        "A seção 'Resumo de Cadastros' não funciona.",
        normal_style
    ))
    elements.append(Paragraph(
        "<b>Solução:</b> Adicionar coluna clinica_id em tabelas que não possuem.",
        normal_style
    ))
    elements.append(Spacer(1, 0.5*cm))
    
    # ==================== SOLUÇÃO RÁPIDA ====================
    elements.append(Paragraph("✅ SOLUÇÃO RÁPIDA (5 PASSOS)", heading1_style))
    
    # Passo 1
    elements.append(Paragraph("<b>PASSO 1: Criar Tabela de Financeiro</b>", heading2_style))
    elements.append(Paragraph(
        "Abra PowerShell e execute:",
        normal_style
    ))
    elements.append(Paragraph(
        "cd \"C:\\Users\\58143406\\Documents\\Desktop_2\\OdontoPro\"<br/>"
        "mysql -u root -h localhost odontoprodb &lt; SistemaDesktop\\migrations\\001_criar_tabelas_financeiras.sql",
        code_style
    ))
    elements.append(Paragraph(
        "<i>Ou importe o arquivo SQL via MySQL Workbench</i>",
        normal_style
    ))
    elements.append(Spacer(1, 0.3*cm))
    
    # Passo 2
    elements.append(Paragraph("<b>PASSO 2: Verificar Colunas clinica_id</b>", heading2_style))
    elements.append(Paragraph(
        "Execute estas queries no MySQL Workbench:",
        normal_style
    ))
    elements.append(Paragraph(
        "DESCRIBE odontoPro_paciente;<br/>"
        "DESCRIBE odontoPro_medico;<br/>"
        "DESCRIBE odontoPro_consulta;",
        code_style
    ))
    elements.append(Paragraph(
        "Se alguma coluna clinica_id estiver faltando, execute:",
        normal_style
    ))
    elements.append(Paragraph(
        "ALTER TABLE odontoPro_paciente ADD COLUMN clinica_id INT NOT NULL DEFAULT 1;<br/>"
        "ALTER TABLE odontoPro_medico ADD COLUMN clinica_id INT NOT NULL DEFAULT 1;<br/>"
        "ALTER TABLE odontoPro_consulta ADD COLUMN clinica_id INT NOT NULL DEFAULT 1;",
        code_style
    ))
    elements.append(Spacer(1, 0.3*cm))
    
    # Passo 3
    elements.append(Paragraph("<b>PASSO 3: Testar Conexão</b>", heading2_style))
    elements.append(Paragraph(
        "Crie arquivo test_db.py e execute: python test_db.py",
        normal_style
    ))
    elements.append(Spacer(1, 0.5*cm))
    
    # PAGE BREAK
    elements.append(PageBreak())
    
    # ==================== CHECKLIST DO BANCO ====================
    elements.append(Paragraph("📊 CHECKLIST DO BANCO DE DADOS", heading1_style))
    
    # Tabelas que existem
    elements.append(Paragraph("<b>✅ Tabelas que JÁ existem:</b>", heading2_style))
    
    tabelas_existentes = [
        "✓ odontoPro_clinica",
        "✓ odontoPro_gerenciamento",
        "✓ odontoPro_paciente",
        "✓ odontoPro_medico",
        "✓ odontoPro_consulta",
        "✓ odontoPro_especialidade",
        "✓ odontoPro_medico_especialidades",
        "✓ odontoPro_gerenciamento_permissoes",
        "✓ odontoPro_permissao",
    ]
    
    for tabela in tabelas_existentes:
        elements.append(Paragraph(tabela, normal_style))
    
    elements.append(Spacer(1, 0.3*cm))
    
    # Tabelas que faltam
    elements.append(Paragraph("<b>❌ Tabelas que FALTAM (CRÍTICO):</b>", heading2_style))
    elements.append(Paragraph("✗ odontoPro_financeiro (PRECISA CRIAR)", error_style))
    
    elements.append(Spacer(1, 0.3*cm))
    
    # Colunas que podem faltar
    elements.append(Paragraph("<b>⚠️ Colunas que PODEM estar faltando:</b>", heading2_style))
    colunas_suspeitas = [
        "⚠ clinica_id em odontoPro_paciente",
        "⚠ clinica_id em odontoPro_medico",
        "⚠ clinica_id em odontoPro_consulta",
    ]
    
    for coluna in colunas_suspeitas:
        elements.append(Paragraph(coluna, normal_style))
    
    elements.append(Spacer(1, 0.5*cm))
    
    # ==================== MÓDULOS CONECTADOS ====================
    elements.append(Paragraph("✅ MÓDULOS JÁ CONECTADOS", heading1_style))
    
    modulos = [
        ("Autenticação", "Login e autenticação funcionando 100%"),
        ("Pacientes", "CRUD completo com banco de dados"),
        ("Consultas", "Listagem com filtros avançados"),
        ("Médicos", "CRUD completo e gerenciamento"),
        ("Gerenciamento", "CRUD de gerentes e permissões"),
    ]
    
    for modulo, desc in modulos:
        elements.append(Paragraph(f"<b>✓ {modulo}</b>: {desc}", normal_style))
    
    elements.append(Spacer(1, 0.5*cm))
    
    # ==================== PRÓXIMOS PASSOS ====================
    elements.append(Paragraph("🚀 PRÓXIMOS PASSOS", heading1_style))
    
    passos = [
        "1. Executar migration SQL para criar tabela odontoPro_financeiro",
        "2. Verificar se colunas clinica_id existem em todas as tabelas",
        "3. Adicionar colunas faltantes se necessário",
        "4. Testar conexão com teste_conexoes.py",
        "5. Inserir dados de teste no banco",
        "6. Executar aplicação e validar funcionalidades",
    ]
    
    for passo in passos:
        elements.append(Paragraph(passo, normal_style))
    
    elements.append(Spacer(1, 0.5*cm))
    
    # ==================== CONTATO ====================
    elements.append(Paragraph("📞 SUPORTE", heading1_style))
    elements.append(Paragraph(
        "Para mais detalhes, consulte:<br/>"
        "<b>CHECKLIST_RAPIDO.md</b> - Instruções rápidas<br/>"
        "<b>COMO_CONECTAR.md</b> - Guia completo<br/>"
        "<b>STATUS_BANCO_DADOS.md</b> - Análise técnica detalhada",
        normal_style
    ))
    
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph(
        f"Relatório gerado em {datetime.now().strftime('%d de %B de %Y')}",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6B7280'),
            alignment=TA_CENTER
        )
    ))
    
    # Construir PDF
    doc.build(elements)
    print(f"✅ PDF gerado com sucesso: {pdf_path}")
    print(f"📄 Localização: {os.path.abspath(pdf_path)}")


if __name__ == "__main__":
    gerar_pdf()
