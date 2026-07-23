from controllers.consulta_controller import ConsultaController

if __name__ == '__main__':
    especialidades = ConsultaController.listar_especialidades_para_combo()
    mapping = {nome: eid for eid, nome in especialidades}
    print('prepared list:', especialidades)
    print('\nname -> id mapping:')
    for nome, eid in mapping.items():
        print(f"{nome!r}: {eid}")
