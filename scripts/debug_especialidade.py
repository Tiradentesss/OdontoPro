from config.database import get_connection

clinica_id = 1

queries = {
    'especialidades': "SELECT id, nome FROM odontoPro_especialidade ORDER BY nome ASC",
    'consulta_columns': "SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'odontoPro_consulta'",
    'consultas_relacao': '''
SELECT
    c.id AS consulta_id,
    c.especialidade_id AS consulta_especialidade_id,
    e.id AS especialidade_id,
    e.nome AS especialidade_nome
FROM odontoPro_consulta c
LEFT JOIN odontoPro_especialidade e
ON e.id = c.especialidade_id
WHERE c.clinica_id = %s
''',
    'consultas_filter_by_enome': "SELECT COUNT(*) FROM odontoPro_consulta c LEFT JOIN odontoPro_especialidade e ON e.id = c.especialidade_id WHERE c.clinica_id = %s AND LOWER(TRIM(e.nome)) = %s",
    'consultas_filter_by_ctext': "SELECT COUNT(*) FROM odontoPro_consulta c WHERE c.clinica_id = %s AND LOWER(TRIM(COALESCE(c.especialidade, ''))) = %s",
    'total_consultas': "SELECT COUNT(*) FROM odontoPro_consulta c WHERE c.clinica_id = %s",
}

conn = None
try:
    conn = get_connection()
    cursor = conn.cursor()

    print('\n--- Especialidades (odontoPro_especialidade) ---')
    cursor.execute(queries['especialidades'])
    rows = cursor.fetchall()
    for r in rows:
        print(r)

        # Prepare deduplicated list same as preparar_especialidades_para_combo
        especialidades_unicas = {}
        for especialidade_id, nome in rows:
            nome_limpo = (nome or '').strip()
            if especialidade_id is not None and nome_limpo:
                chave = nome_limpo.casefold()
                especialidades_unicas.setdefault(chave, (especialidade_id, nome_limpo))
        prepared = sorted(especialidades_unicas.values(), key=lambda item: item[1].lower())
        print('\n--- Especialidades preparadas para combo (id, nome) ---')
        for item in prepared:
            print(item)

        # Show which id would be selected for 'Clínico Geral'
        target_display = 'Clínico Geral'
        target_key = target_display.casefold()
        chosen = especialidades_unicas.get(target_key)
        print(f"\nChosen ID for '{target_display}' in prepared list: {chosen}")
    print('\n--- Colunas odontoPro_consulta ---')
    cursor.execute(queries['consulta_columns'])
    cols = [c[0] for c in cursor.fetchall()]
    print(cols)

    print('\n--- Consultas (id, especialidade_id, consulta.especialidade text, especialidade.id, especialidade.nome) ---')
    cursor.execute(queries['consultas_relacao'], (clinica_id,))
    consultas = cursor.fetchall()
    for r in consultas:
        print(r)

        # Analyze consultas for 'Clínico Geral'
        consulta_ids_for_name = [r[0] for r in consultas if (r[3] or '').casefold() == target_key]
        consulta_ids_for_chosen_id = [r[0] for r in consultas if r[1] == (chosen[0] if chosen else None)]
        print(f"\nConsultas referencing especialidade nome '{target_display}': {consulta_ids_for_name}")
        print(f"Consultas referencing chosen ID {chosen[0] if chosen else None}: {consulta_ids_for_chosen_id}")
    print('\n--- Total consultas (clinica_id=1) ---')
    cursor.execute(queries['total_consultas'], (clinica_id,))
    print(cursor.fetchone()[0])

    # Check filter counts for 'Clínico Geral' in both e.nome and c.especialidade text
    target = 'clínico geral'
    cursor.execute(queries['consultas_filter_by_enome'], (clinica_id, target))
    count_enome = cursor.fetchone()[0]
    cursor.execute(queries['consultas_filter_by_ctext'], (clinica_id, target))
    count_ctext = cursor.fetchone()[0]
    print(f"\nCount where e.nome = '{target}': {count_enome}")
    print(f"Count where c.especialidade text = '{target}': {count_ctext}")

except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    try:
        if cursor:
            cursor.close()
    except:
        pass
    try:
        if conn:
            conn.close()
    except:
        pass

print('\n--- Script debug_especialidade.py finalizado ---')
