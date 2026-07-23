"""Preview-only report for migrate_deduplicate_especialidades.
Does not modify the database. Prints detailed report of duplicates and the exact SQL that would be run.
"""
from config.database import get_connection


def normalize(name):
    return name.strip().lower() if name and isinstance(name, str) else None


def main():
    conn = get_connection()
    cur = conn.cursor()

    # DB version
    cur.execute("SELECT VERSION()")
    version = cur.fetchone()[0]
    print('Database version:', version)

    # load especialidades
    cur.execute("SELECT id, nome FROM odontoPro_especialidade")
    rows = cur.fetchall() or []
    total_especialidades = len(rows)
    print('\nTotal especialidades:', total_especialidades)

    groups = {}
    for eid, nome in rows:
        key = normalize(nome)
        if not key:
            continue
        groups.setdefault(key, []).append((eid, nome))

    duplicates = {k: v for k, v in groups.items() if len(v) > 1}
    print('Duplicate name groups:', len(duplicates))

    # find tables with especialidade_id
    cur.execute("SELECT table_name FROM information_schema.columns WHERE table_schema = DATABASE() AND column_name = 'especialidade_id'")
    tables = [r[0] for r in cur.fetchall() or []]
    print('Tables with especialidade_id:', tables)

    total_rows_to_update = 0
    total_ids_to_delete = 0
    detailed = []

    for key, items in duplicates.items():
        ids = [eid for eid, _ in items]
        names = list({nome for _, nome in items})
        # find references per id per table
        ref_counts = {iid: {} for iid in ids}
        referenced_ids = set()
        for t in tables:
            placeholders = ','.join(['%s']*len(ids))
            sql = f"SELECT especialidade_id, COUNT(*) FROM `{t}` WHERE especialidade_id IN ({placeholders}) GROUP BY especialidade_id"
            cur.execute(sql, tuple(ids))
            for rid, cnt in cur.fetchall() or []:
                ref_counts[rid][t] = cnt
                referenced_ids.add(rid)
        # choose keeper: prefer any referenced id (min if multiple), else min id
        if referenced_ids:
            keeper = min(referenced_ids)
            reason = 'keeper chosen because it is referenced in related tables (prefer referenced id; if multiple, choose smallest referenced id)'
        else:
            keeper = min(ids)
            reason = 'keeper chosen as smallest id because none are referenced'

        to_delete = [i for i in ids if i != keeper]
        total_ids_to_delete += len(to_delete)

        # for each to_delete compute counts per table
        per_id_info = []
        for tid in to_delete:
            counts = {t: ref_counts.get(tid, {}).get(t, 0) if isinstance(ref_counts.get(tid, {}), dict) else 0 for t in tables}
            # total references
            total_refs = sum(counts.values())
            total_rows_to_update += total_refs
            tables_to_modify = [t for t, c in counts.items() if c > 0]
            per_id_info.append({'id': tid, 'counts': counts, 'total_refs': total_refs, 'tables': tables_to_modify})

        # build SQL preview statements for this group
        preview_sql = []
        if to_delete:
            for t in tables:
                # only include updates if there are refs in that table
                # but show full SQL as preview regardless
                placeholders = ','.join([str(i) for i in to_delete])
                preview_sql.append(f"UPDATE `{t}` SET especialidade_id = {keeper} WHERE especialidade_id IN ({placeholders});")
            preview_sql.append(f"DELETE FROM odontoPro_especialidade WHERE id IN ({','.join([str(i) for i in to_delete])});")

        detailed.append({
            'nome_normalizado': key,
            'nomes': names,
            'ids': ids,
            'keeper': keeper,
            'keeper_reason': reason,
            'to_delete': to_delete,
            'per_id_info': per_id_info,
            'preview_sql': preview_sql
        })

    # Print detailed report
    print('\n--- Detailed duplicate groups report ---')
    for d in detailed:
        print('\nNome (normalizado):', d['nome_normalizado'])
        print('Nomes originais:', d['nomes'])
        print('IDs existentes:', d['ids'])
        print('Keeper ID:', d['keeper'], '-', d['keeper_reason'])
        print('IDs que seriam removidos:', d['to_delete'])
        for pid in d['per_id_info']:
            print(f"  ID {pid['id']}: total_refs={pid['total_refs']}; tables: {pid['tables']}; counts per table: {pid['counts']}")
        print('Preview SQL:')
        for s in d['preview_sql']:
            print('  ', s)

    # Validation queries
    print('\n--- Validation queries (current state) ---')
    cur.execute("SELECT nome, COUNT(*) FROM odontoPro_especialidade GROUP BY nome HAVING COUNT(*) > 1")
    dup_after = cur.fetchall() or []
    print('Query: duplicate names currently (name, count):')
    for r in dup_after:
        print('  ', r)

    cur.execute("SELECT COUNT(*) FROM odontoPro_consulta c LEFT JOIN odontoPro_especialidade e ON e.id = c.especialidade_id WHERE c.especialidade_id IS NOT NULL AND e.id IS NULL")
    orphan_consultas = cur.fetchone()[0]
    print('\nQuery: consultas referencing missing especialidade rows (should be 0):', orphan_consultas)

    # Final summary
    print('\n--- Summary ---')
    print('Total especialidades:', total_especialidades)
    print('Duplicate name groups:', len(duplicates))
    print('Total IDs that would be removed:', total_ids_to_delete)
    print('Total reference rows that would be updated (sum over tables):', total_rows_to_update)

    # Risks
    risk = 'Low' if orphan_consultas == 0 else 'Medium/High'
    print('\nRisk assessment:')
    print('  Orphan consultas currently:', orphan_consultas)
    print('  Risk level (based on current orphans):', risk)
    if total_ids_to_delete > 0:
        print('  Note: DDL operations (adding generated column and unique index) are not included in this preview and may cause implicit commits.')

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
