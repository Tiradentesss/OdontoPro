from config.database import get_connection
from controllers.consulta_controller import ConsultaController


def run():
    conn = get_connection()
    cur = conn.cursor()

    print('\n1) Raw SELECT id, nome FROM odontoPro_especialidade ORDER BY nome, id;')
    cur.execute('SELECT id, nome FROM odontoPro_especialidade ORDER BY nome, id')
    rows = cur.fetchall() or []
    for r in rows:
        print(r)

    print(f'\nTotal especialidades rows: {len(rows)}')

    print('\n2) ConsultaController.listar_especialidades_para_combo() output:')
    especialidades = ConsultaController.listar_especialidades_para_combo()
    for eid, nome in especialidades:
        print((eid, nome))

    mapping = {nome: eid for eid, nome in especialidades}

    def show(name):
        print(f"\n{name!r} -> ID? -> ", mapping.get(name))

    print('\n3) Specific mappings:')
    for name in ['Clínico Geral', 'Ortodontia', 'Endodontia']:
        show(name)

    # 4) Simulate Agenda selection of 'Clínico Geral'
    selected_value = 'Clínico Geral'
    print('\n4) Simulate Agenda selection for value:', selected_value)
    combo_value = selected_value
    found_id = None
    # simulate the loop used in agenda: for especialidade_id, nome in especialidades_carregadas
    for eid, nome in especialidades:
        if nome == combo_value:
            found_id = eid
            break
    print(' - value of ComboBox:', combo_value)
    print(' - ID found:', found_id)
    print(' - dict used (name->id):', mapping)
    print(' - ID sent to listar_por_clinica():', found_id)

    # 5) Call listar_por_clinica with clinica_id=1 and found_id
    print('\n5) Calling ConsultaController.listar_por_clinica(clinica_id=1, especialidade_id=found_id)')
    if found_id is None:
        print('No ID found for Clinico Geral; aborting listar_por_clinica call')
    else:
        dados = ConsultaController.listar_por_clinica(1, especialidade_id=found_id)
        print('\n- Number of records returned by listar_por_clinica():', len(dados))
        # Extract consulta ids
        consulta_ids = [row[0] for row in dados]
        print('- consulta ids:', consulta_ids)

        # 6) For each, fetch consulta_id, especialidade_id, especialidade name
        if consulta_ids:
            placeholders = ','.join(['%s'] * len(consulta_ids))
            q = f"SELECT c.id, c.especialidade_id, COALESCE(e.nome,'') FROM odontoPro_consulta c LEFT JOIN odontoPro_especialidade e ON e.id = c.especialidade_id WHERE c.id IN ({placeholders})"
            cur.execute(q, tuple(consulta_ids))
            details = cur.fetchall() or []
            print('\n6) Details per consulta: (consulta_id, especialidade_id, especialidade_nome)')
            for d in details:
                print(d)

            # 7) Confirm if any are Clinico Geral (by name or id)
            print('\n7) Confirming if there are consultas of "Clínico Geral":')
            clinico_id = mapping.get('Clínico Geral')
            found = any(d[1] == clinico_id or d[2].lower() == 'clínico geral' for d in details)
            if found:
                print('[OK] Filtro funcionando')
            else:
                print('[FALHA] Ainda existe divergência')
        else:
            # no rows returned
            print('\nNo consultas returned by listar_por_clinica for that especialidade_id')
            print('[FALHA] Ainda existe divergência')

    cur.close()
    conn.close()

if __name__ == '__main__':
    run()
