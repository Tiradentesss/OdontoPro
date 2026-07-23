"""
Migration script to deduplicate `odontoPro_especialidade` by normalized name.

Behavior:
- For each group of names that normalize to the same value (LOWER(TRIM(nome))):
  - Choose a keeper ID preferring an ID that is referenced in any table with a column named 'especialidade_id'.
    If multiple referenced IDs exist, choose the smallest among them. If none referenced, choose the smallest ID.
  - Update all tables that have an 'especialidade_id' column to replace duplicate IDs with the keeper ID.
  - Delete the duplicate rows (non-keeper) from odontoPro_especialidade.
- Add a generated column `nome_normalizado` and a UNIQUE index on it to prevent future duplicates.

IMPORTANT: Run on a backup or in maintenance window. This script performs DDL (adds column/index) and DML.
"""

try:
    from config.database import get_connection
except Exception:
    # Fallback when running from project root without PYTHONPATH set
    try:
        from SistemaDesktop.config.database import get_connection
    except Exception:
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        # prefer importing config.database (when PYTHONPATH points to SistemaDesktop)
        try:
            from config.database import get_connection
        except Exception:
            from SistemaDesktop.config.database import get_connection


def normalize(name):
    return name.strip().lower() if name and isinstance(name, str) else None


if __name__ == '__main__':
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 0) Report DB version and caveats about transactional DDL
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print('Database version:', version)
        print('Note: MySQL/MariaDB DDL (ALTER TABLE / CREATE INDEX) causes implicit commits and cannot be rolled back.')

        # 1) Find duplicate groups
        cursor.execute("SELECT id, nome FROM odontoPro_especialidade")
        rows = cursor.fetchall() or []
        groups = {}
        for r in rows:
            eid, nome = r
            key = normalize(nome)
            if not key:
                continue
            groups.setdefault(key, []).append((eid, nome))

        duplicates = {k: v for k, v in groups.items() if len(v) > 1}

        if not duplicates:
            print('No duplicates found.')
        else:
            print(f'Found {len(duplicates)} duplicated name groups.')

        # Discover tables that have column 'especialidade_id'
        cursor.execute("SELECT table_name FROM information_schema.columns WHERE table_schema = DATABASE() AND column_name = 'especialidade_id'")
        tables = [r[0] for r in cursor.fetchall() or []]
        print('Tables with especialidade_id:', tables)

        # 2) Prepare a full report before making changes
        planned_actions = []
        total_consultas_to_update = 0
        total_medicos_to_update = 0

        for key, items in duplicates.items():
            ids = [eid for eid, _ in items]
            # Find referenced ids among these
            referenced = []
            for t in tables:
                cursor.execute(f"SELECT especialidade_id, COUNT(*) FROM `{t}` WHERE especialidade_id IN ({','.join(['%s']*len(ids))}) GROUP BY especialidade_id", tuple(ids))
                for row in cursor.fetchall() or []:
                    referenced.append(row[0])

            if referenced:
                keeper = min(referenced)
            else:
                keeper = min(ids)

            to_delete = [i for i in ids if i != keeper]

            # Counts for report
            counts = {}
            for t in tables:
                if to_delete:
                    cursor.execute(f"SELECT COUNT(*) FROM `{t}` WHERE especialidade_id IN ({','.join(['%s']*len(to_delete))})", tuple(to_delete))
                    c = cursor.fetchone()[0]
                else:
                    c = 0
                counts[t] = c

            total_consultas_to_update += counts.get('odontoPro_consulta', 0)
            total_medicos_to_update += counts.get('odontoPro_medico_especialidades', 0)

            planned_actions.append({
                'group': key,
                'ids': ids,
                'keeper': keeper,
                'to_delete': to_delete,
                'counts': counts
            })

        # Print preview report
        print('\n=== PREVIEW: planned actions (no changes yet) ===')
        print('Duplicate groups count:', len(planned_actions))
        for a in planned_actions:
            print(f"Group '{a['group']}': keeper={a['keeper']}, to_delete={a['to_delete']}, counts={a['counts']}")

        print('\nSummary:')
        print('Total groups with duplicates:', len(planned_actions))
        print('Total consultas rows that would be affected:', total_consultas_to_update)
        print('Total medicos rows that would be affected:', total_medicos_to_update)
        print('Tables to be modified:', tables)

        # At this point we only prepare report. Do not perform any changes unless user authorizes.
        # The rest of this script implements a safe, transactional DML flow and a best-effort DDL step
        # but it will NOT execute changes automatically when run in preview mode.

        # The transactional DML portion (updates/deletes) - best effort to run inside a transaction
        # Note: DDL (ALTER TABLE / CREATE INDEX) will be executed after DML and is not transactional.

        # For safety we will ask for authorization variable via environment to proceed.
        import os
        proceed = os.getenv('MIGRATE_ESPECIALIDADES_PROCEED', 'no').lower() in ('1', 'true', 'yes')
        if not proceed:
            print('\nPreview only. To apply changes set environment variable MIGRATE_ESPECIALIDADES_PROCEED=1 and re-run this script.')
            # Also print the final validation queries that will be run after changes
            print('\nPost-migration validation queries to be executed when proceeding:')
            print("SELECT nome, COUNT(*) FROM odontoPro_especialidade GROUP BY nome HAVING COUNT(*) > 1;")
            print("SELECT COUNT(*) FROM odontoPro_consulta c LEFT JOIN odontoPro_especialidade e ON e.id = c.especialidade_id WHERE c.especialidade_id IS NOT NULL AND e.id IS NULL;")
            raise SystemExit(0)

        # Begin transaction for DML
        print('\nProceeding: starting transaction for DML updates...')
        conn.start_transaction()

        # Execute updates and deletes
        total_deleted = 0
        total_updates = 0
        for a in planned_actions:
            keeper = a['keeper']
            to_delete = a['to_delete']
            if not to_delete:
                continue
            for t in tables:
                # Update table t: set keeper where in to_delete
                placeholders = ','.join(['%s']*len(to_delete))
                params = tuple([keeper] + to_delete)
                cursor.execute(f"UPDATE `{t}` SET especialidade_id = %s WHERE especialidade_id IN ({placeholders})", params)
                affected = cursor.rowcount
                total_updates += affected
                print(f"Updated {affected} rows in {t} for group {a['group']}")

            # Validate no lingering references to to_delete
            for t in tables:
                if to_delete:
                    cursor.execute(f"SELECT COUNT(*) FROM `{t}` WHERE especialidade_id IN ({placeholders})", tuple(to_delete))
                    remaining = cursor.fetchone()[0]
                    if remaining != 0:
                        raise RuntimeError(f"After update, table {t} still has {remaining} references to ids {to_delete}")

            # Now safe to delete duplicate specialities
            cursor.execute(f"DELETE FROM odontoPro_especialidade WHERE id IN ({','.join(['%s']*len(to_delete))})", tuple(to_delete))
            deleted = cursor.rowcount
            total_deleted += deleted
            print(f"Deleted {deleted} duplicate rows from odontoPro_especialidade for group {a['group']}")

        # Commit DML
        conn.commit()
        print(f'DML phase committed. total_updates={total_updates}, total_deleted={total_deleted}')

        # DDL: add generated column and unique index if not exists
        print('Now attempting DDL to add generated column and unique index (non-transactional step)...')
        # Check if column exists
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'odontoPro_especialidade' AND column_name = 'nome_normalizado'")
        col_exists = cursor.fetchone()[0] > 0
        if not col_exists:
            try:
                cursor.execute("ALTER TABLE odontoPro_especialidade ADD COLUMN nome_normalizado VARCHAR(255) GENERATED ALWAYS AS (LOWER(TRIM(nome))) STORED")
                print('Added column nome_normalizado')
            except Exception as e:
                print('Warning: failed to add generated column:', e)

        # Check if index exists
        cursor.execute("SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name = 'odontoPro_especialidade' AND index_name = 'ux_especialidade_nome_normalizado'")
        idx_exists = cursor.fetchone()[0] > 0
        if not idx_exists:
            try:
                cursor.execute("CREATE UNIQUE INDEX ux_especialidade_nome_normalizado ON odontoPro_especialidade (nome_normalizado)")
                print('Created unique index ux_especialidade_nome_normalizado')
            except Exception as e:
                print('Warning: failed to create unique index:', e)

        # Final validations
        print('\nRunning post-migration validations...')
        cursor.execute("SELECT nome, COUNT(*) FROM odontoPro_especialidade GROUP BY nome HAVING COUNT(*) > 1")
        dup_after = cursor.fetchall() or []
        print('Duplicate name groups remaining (should be 0):', len(dup_after))
        if dup_after:
            for r in dup_after:
                print(r)

        cursor.execute("SELECT COUNT(*) FROM odontoPro_consulta c LEFT JOIN odontoPro_especialidade e ON e.id = c.especialidade_id WHERE c.especialidade_id IS NOT NULL AND e.id IS NULL")
        orphan_consultas = cursor.fetchone()[0]
        print('Consultas with missing especialidade references (should be 0):', orphan_consultas)

        # Final report
        cursor.execute("SELECT COUNT(*) FROM odontoPro_especialidade")
        total_after = cursor.fetchone()[0]
        total_before = len(rows)
        print('\n=== FINAL REPORT ===')
        print('Total especialidades before:', total_before)
        print('Total especialidades after:', total_after)
        print('Total duplicates removed:', total_deleted)
        print('Total consulta rows updated (approx):', total_consultas_to_update)
        print('Total medico rows updated (approx):', total_medicos_to_update)
        print('Orphan references found after migration (should be 0):', orphan_consultas)

        print('\nMigration script finished.')

    except SystemExit:
        # Preview exit
        pass
    except Exception as e:
        if conn:
            try:
                conn.rollback()
                print('Rolled back transaction due to error.')
            except Exception:
                pass
        print('Migration failed:', e)
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

