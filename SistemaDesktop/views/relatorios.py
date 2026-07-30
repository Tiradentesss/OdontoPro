import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import queue
from datetime import datetime, timedelta

from config.database import get_connection
from .base import BaseScreen
from .theme import font, COLORS, INNER_CARD_BORDER, INNER_CARD_RADIUS
from controllers.consulta_controller import ConsultaController


class Relatorios(BaseScreen):
    def __init__(self, parent, clinica_id=None):
        super().__init__(parent, "Relatórios")

        self.clinica_id = clinica_id
        self._loading = False
        self._load_queue = queue.Queue()
        self._current_thread_id = 0
        self._timeout_id = None
        self._cache = {}
        self._medicos_map = {"Todos": None}
        self._especialidades_map = {"Todos": None}

        self.periodo_var = ctk.StringVar(value="Hoje")
        self.medico_var = ctk.StringVar(value="Todos")
        self.especialidade_var = ctk.StringVar(value="Todos")
        self.status_var = ctk.StringVar(value="Todos")

        self.main_container = self.content_card

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color=COLORS["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._build_structure()
        self._load_data_async()

    def _build_structure(self):
        header = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text="Relatórios",
            font=font("title", "bold"),
            text_color=COLORS["text"]
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Ações",
            width=100,
            height=34,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white",
            corner_radius=8,
            state="disabled"
        ).pack(side="right")

        cards_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=(0, 20))
        for idx in range(4):
            cards_frame.grid_columnconfigure(idx, weight=1, uniform="report_cards")

        self._card_value_labels = {}
        cards = [
            ("📅", "Consultas", "0"),
            ("👥", "Pacientes", "0"),
            ("🩺", "Médicos", "0"),
            ("❌", "Cancelamentos", "0"),
        ]

        for index, (icon, title, value) in enumerate(cards):
            card = ctk.CTkFrame(
                cards_frame,
                fg_color=COLORS["card"],
                corner_radius=INNER_CARD_RADIUS,
                border_width=1,
                border_color=INNER_CARD_BORDER
            )
            card.grid(row=0, column=index, sticky="nsew", padx=(0, 10) if index < len(cards) - 1 else 0)

            ctk.CTkLabel(
                card,
                text=icon,
                font=font("subtitle", "bold"),
                text_color=COLORS["primary"]
            ).pack(anchor="w", padx=16, pady=(16, 4))

            ctk.CTkLabel(
                card,
                text=title,
                font=font("small"),
                text_color=COLORS["text_secondary"]
            ).pack(anchor="w", padx=16)

            value_label = ctk.CTkLabel(
                card,
                text=value,
                font=font("title", "bold"),
                text_color=COLORS["text"]
            )
            value_label.pack(anchor="w", padx=16, pady=(8, 16))
            self._card_value_labels[title] = value_label

        filters_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        filters_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        filters_header = ctk.CTkLabel(
            filters_frame,
            text="Filtros",
            font=font("subtitle", "bold"),
            text_color=COLORS["text"]
        )
        filters_header.pack(anchor="w", padx=20, pady=(20, 10))

        form_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=(0, 20))
        form_frame.columnconfigure((0, 1, 2), weight=1, uniform="filter_cols")

        periodo_frame = ctk.CTkFrame(form_frame, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=INNER_CARD_BORDER)
        periodo_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        ctk.CTkLabel(periodo_frame, text="Período", font=font("small", "bold"), text_color=COLORS["text_secondary"]).pack(anchor="w", padx=16, pady=(12, 6))
        self.periodo_combo = ctk.CTkComboBox(
            periodo_frame,
            values=["Hoje", "Semana", "Mês", "Ano", "Personalizado"],
            corner_radius=8,
            fg_color=COLORS["bg_soft"],
            button_color=COLORS["input_bg"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["card"],
            width=1
        )
        self.periodo_combo.set(self.periodo_var.get())
        self.periodo_combo.pack(fill="x", padx=16, pady=(0, 16))

        medico_frame = ctk.CTkFrame(form_frame, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=INNER_CARD_BORDER)
        medico_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=0)
        ctk.CTkLabel(medico_frame, text="Médico", font=font("small", "bold"), text_color=COLORS["text_secondary"]).pack(anchor="w", padx=16, pady=(12, 6))
        self.medico_combo = ctk.CTkComboBox(
            medico_frame,
            values=["Todos"],
            corner_radius=8,
            fg_color=COLORS["bg_soft"],
            button_color=COLORS["input_bg"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["card"],
            width=1
        )
        self.medico_combo.set(self.medico_var.get())
        self.medico_combo.pack(fill="x", padx=16, pady=(0, 16))

        especialidade_frame = ctk.CTkFrame(form_frame, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=INNER_CARD_BORDER)
        especialidade_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=0)
        ctk.CTkLabel(especialidade_frame, text="Especialidade", font=font("small", "bold"), text_color=COLORS["text_secondary"]).pack(anchor="w", padx=16, pady=(12, 6))
        self.especialidade_combo = ctk.CTkComboBox(
            especialidade_frame,
            values=["Todos"],
            corner_radius=8,
            fg_color=COLORS["bg_soft"],
            button_color=COLORS["input_bg"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["card"],
            width=1
        )
        self.especialidade_combo.set(self.especialidade_var.get())
        self.especialidade_combo.pack(fill="x", padx=16, pady=(0, 16))

        status_frame = ctk.CTkFrame(filters_frame, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=INNER_CARD_BORDER)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        status_frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(status_frame, text="Status", font=font("small", "bold"), text_color=COLORS["text_secondary"]).pack(anchor="w", padx=16, pady=(12, 6))
        self.status_combo = ctk.CTkComboBox(
            status_frame,
            values=["Todos", "Agendada", "Realizada", "Cancelada"],
            corner_radius=8,
            fg_color=COLORS["bg_soft"],
            button_color=COLORS["input_bg"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["card"],
            width=1
        )
        self.status_combo.set(self.status_var.get())
        self.status_combo.pack(fill="x", padx=16, pady=(0, 16))

        action_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.update_button = ctk.CTkButton(
            action_frame,
            text="Atualizar Relatório",
            width=180,
            height=38,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white",
            corner_radius=12,
            command=self._load_data_async
        )
        self.update_button.pack(side="right")

        self._loading_label = ctk.CTkLabel(
            filters_frame,
            text="",
            font=font("small"),
            text_color=COLORS["text_secondary"]
        )
        self._loading_label.pack(anchor="w", padx=20, pady=(0, 10))
        self._loading_label.pack_forget()

        self.chart_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        self.chart_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(
            self.chart_card,
            text="Consultas por Período",
            font=font("subtitle", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        self._chart_canvas_container = ctk.CTkFrame(self.chart_card, fg_color=COLORS["card"], corner_radius=10)
        self._chart_canvas_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.specialty_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        self.specialty_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(
            self.specialty_card,
            text="Consultas por Especialidade",
            font=font("subtitle", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        self._specialty_canvas_container = ctk.CTkFrame(self.specialty_card, fg_color=COLORS["card"], corner_radius=10)
        self._specialty_canvas_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.productivity_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        self.productivity_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(
            self.productivity_card,
            text="Médicos Mais Produtivos",
            font=font("subtitle", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        table_header = ctk.CTkFrame(self.productivity_card, fg_color=COLORS["card_soft"], corner_radius=12)
        table_header.pack(fill="x", padx=20, pady=(0, 4))
        table_header.columnconfigure((0, 1, 2, 3), weight=1, uniform="prod_cols")

        ctk.CTkLabel(table_header, text="Posição", font=font("small", "bold"), text_color=COLORS["text_secondary"]).grid(row=0, column=0, sticky="w", padx=12, pady=12)
        ctk.CTkLabel(table_header, text="Nome", font=font("small", "bold"), text_color=COLORS["text_secondary"]).grid(row=0, column=1, sticky="w", padx=12, pady=12)
        ctk.CTkLabel(table_header, text="Especialidade", font=font("small", "bold"), text_color=COLORS["text_secondary"]).grid(row=0, column=2, sticky="w", padx=12, pady=12)
        ctk.CTkLabel(table_header, text="Consultas", font=font("small", "bold"), text_color=COLORS["text_secondary"]).grid(row=0, column=3, sticky="e", padx=12, pady=12)

        self._productivity_rows_frame = ctk.CTkFrame(self.productivity_card, fg_color="transparent")
        self._productivity_rows_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        stats_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent"
        )
        stats_frame.pack(fill="x", padx=20, pady=(0, 20))
        for idx in range(4):
            stats_frame.grid_columnconfigure(idx, weight=1, uniform="small_stats")

        self._stat_value_labels = {}
        stats = [
            ("Comparecimento", "0%"),
            ("Cancelamentos", "0"),
            ("Novos Pacientes", "0"),
            ("Retornos", "0"),
        ]

        for index, (label_text, value) in enumerate(stats):
            small_card = ctk.CTkFrame(
                stats_frame,
                fg_color=COLORS["card"],
                corner_radius=INNER_CARD_RADIUS,
                border_width=1,
                border_color=INNER_CARD_BORDER
            )
            small_card.grid(row=0, column=index, sticky="nsew", padx=(0, 10) if index < len(stats) - 1 else 0)

            ctk.CTkLabel(
                small_card,
                text=label_text,
                font=font("small", "bold"),
                text_color=COLORS["text_secondary"]
            ).pack(anchor="w", padx=16, pady=(16, 4))

            value_label = ctk.CTkLabel(
                small_card,
                text=value,
                font=font("title", "bold"),
                text_color=COLORS["text"]
            )
            value_label.pack(anchor="w", padx=16, pady=(0, 16))
            self._stat_value_labels[label_text] = value_label

    def _load_data_async(self):
        if self._loading:
            return

        self._loading = True
        self.update_button.configure(state="disabled")
        self._loading_label.configure(text="Carregando relatório...")
        self._loading_label.pack(anchor="w", padx=20, pady=(0, 10))

        snapshot = self._capture_filter_snapshot()
        medico_id = self._medicos_map.get(snapshot["medico_name"])
        especialidade_id = self._especialidades_map.get(snapshot["especialidade_name"])

        self._current_thread_id += 1
        thread_id = self._current_thread_id

        def thread_wrapper():
            try:
                self._load_data_thread(
                    thread_id,
                    snapshot["periodo"],
                    snapshot["status"],
                    snapshot["medico_name"],
                    snapshot["especialidade_name"],
                    medico_id,
                    especialidade_id,
                )
            except Exception as e:
                print(f"[RELATÓRIOS] _load_data_thread error: {e}")
                import traceback
                traceback.print_exc()
                self._load_queue.put((thread_id, None, None, None, None, None, None, f"Erro interno: {e}"))

        thread = threading.Thread(target=thread_wrapper, daemon=False)
        thread.start()

        if self._timeout_id is not None:
            try:
                self.after_cancel(self._timeout_id)
            except Exception:
                pass

        self._timeout_id = self.winfo_toplevel().after(40000, lambda: self._timeout_loading(thread_id))
        self.winfo_toplevel().after(100, self._process_load_queue)

    def _timeout_loading(self, thread_id):
        if self._current_thread_id != thread_id:
            return

        self._loading = False
        self._timeout_id = None
        self.update_button.configure(state="normal")
        self._loading_label.configure(text="Tempo de carregamento esgotado. Tente novamente.")

    def _capture_filter_snapshot(self):
        return {
            "periodo": self.periodo_combo.get(),
            "status": self.status_combo.get(),
            "medico_name": self.medico_combo.get(),
            "especialidade_name": self.especialidade_combo.get(),
        }

    def _build_filter_conditions(self, medico_id, especialidade_id, medico_name, especialidade_name, status):
        conditions = ["c.clinica_id = %s"]
        params = [self.clinica_id]

        if status and status not in ['Todos', 'Status', '']:
            conditions.append("LOWER(TRIM(c.status)) = %s")
            params.append(status.lower())

        if medico_id not in [None, '', 'Todos', 'Médico']:
            conditions.append("c.medico_id = %s")
            params.append(medico_id)
        elif medico_name and medico_name not in ['Todos', 'Médico', '']:
            conditions.append("m.nome = %s")
            params.append(medico_name)

        if especialidade_id not in [None, '', 'Todos', 'Especialidade']:
            conditions.append("c.especialidade_id = %s")
            params.append(especialidade_id)
        elif especialidade_name and especialidade_name not in ['Todos', 'Especialidade', '']:
            conditions.append("LOWER(TRIM(e.nome)) = %s")
            params.append(especialidade_name.lower())

        return " AND ".join(conditions), params

    def _get_date_range(self, periodo):
        agora = datetime.now()
        if periodo == "Hoje":
            inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
            fim = agora
            tipo = "hoje"
        elif periodo == "Semana":
            inicio = agora - timedelta(days=7)
            fim = agora
            tipo = "semana"
        elif periodo == "Mês":
            inicio = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fim = agora
            tipo = "mes"
        elif periodo == "Ano":
            inicio = agora.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            fim = agora
            tipo = "ano"
        else:
            inicio = agora - timedelta(days=30)
            fim = agora
            tipo = "personalizado"

        return inicio, fim, tipo

    def _load_data_thread(self, thread_id, periodo, status, medico_name, especialidade_name, medico_id, especialidade_id):
        inicio, fim, periodo_tipo = self._get_date_range(periodo)
        filtro_base, filtro_params = self._build_filter_conditions(
            medico_id,
            especialidade_id,
            medico_name,
            especialidade_name,
            status
        )

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Cache filter options once for the clinic session
            if "filter_options" not in self._cache:
                medicos = ConsultaController.listar_medicos(self.clinica_id)
                especialidades = ConsultaController.listar_especialidades_para_combo()
                self._cache["filter_options"] = {
                    "medicos": medicos,
                    "especialidades": especialidades,
                }
            else:
                medicos = self._cache["filter_options"]["medicos"]
                especialidades = self._cache["filter_options"]["especialidades"]

            # Top cards and counts
            consulta_params = filtro_params + [inicio, fim]
            cursor.execute(f"""
                SELECT
                    COUNT(*) AS total_consultas,
                    COUNT(DISTINCT c.paciente_id) AS total_pacientes,
                    COUNT(DISTINCT c.medico_id) AS total_medicos,
                    SUM(LOWER(TRIM(c.status)) = 'cancelada') AS cancelamentos,
                    SUM(LOWER(TRIM(c.status)) = 'realizada') AS realizadas
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id
                WHERE {filtro_base}
                  AND c.data_hora BETWEEN %s AND %s
            """, tuple(consulta_params))
            row = cursor.fetchone() or (0, 0, 0, 0, 0)
            total_consultas, total_pacientes, total_medicos, cancelamentos, realizadas = row

            if total_consultas:
                comparecimento = int(round((realizadas or 0) / total_consultas * 100))
            else:
                comparecimento = 0

            # Novos pacientes: primeira consulta no período
            cursor.execute("""
                SELECT COUNT(*)
                FROM (
                    SELECT paciente_id, MIN(data_hora) AS primeira_consulta
                    FROM odontoPro_consulta
                    WHERE clinica_id = %s
                    GROUP BY paciente_id
                ) primeiro
                WHERE primeira_consulta BETWEEN %s AND %s
            """, (self.clinica_id, inicio, fim))
            row_new = cursor.fetchone()
            novos_pacientes = int(row_new[0] or 0) if row_new else 0

            # Retornos: paciente com consulta no período e primeira consulta antes do início
            retorno_params = [self.clinica_id, self.clinica_id, inicio, fim, inicio]
            # Reuse the same filters for the period query
            retorno_where = "c.clinica_id = %s AND c.data_hora BETWEEN %s AND %s AND firsts.primeira_consulta < %s"
            if status and status not in ['Todos', 'Status', '']:
                retorno_where += " AND LOWER(TRIM(c.status)) = %s"
                retorno_params.append(status.lower())
            if medico_id not in [None, '', 'Todos', 'Médico']:
                retorno_where += " AND c.medico_id = %s"
                retorno_params.append(medico_id)
            elif medico_name and medico_name not in ['Todos', 'Médico', '']:
                retorno_where += " AND m.nome = %s"
                retorno_params.append(medico_name)
            if especialidade_id not in [None, '', 'Todos', 'Especialidade']:
                retorno_where += " AND c.especialidade_id = %s"
                retorno_params.append(especialidade_id)
            elif especialidade_name and especialidade_name not in ['Todos', 'Especialidade', '']:
                retorno_where += " AND LOWER(TRIM(e.nome)) = %s"
                retorno_params.append(especialidade_name.lower())

            cursor.execute(f"""
                SELECT COUNT(DISTINCT c.paciente_id)
                FROM odontoPro_consulta c
                JOIN (
                    SELECT paciente_id, MIN(data_hora) AS primeira_consulta
                    FROM odontoPro_consulta
                    WHERE clinica_id = %s
                    GROUP BY paciente_id
                ) firsts ON firsts.paciente_id = c.paciente_id
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id
                WHERE {retorno_where}
            """, tuple(retorno_params))
            row_retorno = cursor.fetchone()
            retornos = int(row_retorno[0] or 0) if row_retorno else 0

            # Consultas por período para gráfico
            chart_period = self._fetch_period_chart(cursor, filtro_base, filtro_params, inicio, fim, periodo_tipo)

            # Consultas por especialidade para gráfico de pizza
            cursor.execute(f"""
                SELECT COALESCE(e.nome, 'Sem Especialidade') AS especialidade,
                       COUNT(*) AS total
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id
                WHERE {filtro_base}
                  AND c.data_hora BETWEEN %s AND %s
                GROUP BY especialidade
                ORDER BY total DESC
                LIMIT 8
            """, tuple(consulta_params))
            specialty_data = cursor.fetchall() or []

            # Médicos mais produtivos
            cursor.execute(f"""
                SELECT m.nome AS medico,
                       COALESCE(e.nome, 'Sem Especialidade') AS especialidade,
                       COUNT(*) AS consultas
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id
                WHERE {filtro_base}
                  AND c.data_hora BETWEEN %s AND %s
                GROUP BY c.medico_id, m.nome, e.nome
                ORDER BY consultas DESC
                LIMIT 5
            """, tuple(consulta_params))
            productivity_rows = cursor.fetchall() or []

            self._load_queue.put((
                thread_id,
                {
                    "total_consultas": int(total_consultas or 0),
                    "total_pacientes": int(total_pacientes or 0),
                    "total_medicos": int(total_medicos or 0),
                    "cancelamentos": int(cancelamentos or 0),
                    "comparecimento": int(comparecimento),
                    "novos_pacientes": int(novos_pacientes or 0),
                    "retornos": int(retornos or 0),
                },
                chart_period,
                specialty_data,
                productivity_rows,
                medicos,
                especialidades,
                None
            ))

        except Exception as e:
            print(f"[RELATÓRIOS] erro ao carregar dados: {e}")
            import traceback
            traceback.print_exc()
            self._load_queue.put((thread_id, None, None, None, None, None, None, str(e)))

        finally:
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            except Exception:
                pass

    def _fetch_period_chart(self, cursor, filtro_base, filtro_params, inicio, fim, periodo_tipo):
        if periodo_tipo == "hoje":
            label_keys = list(range(24))
            labels = [f"{h}h" for h in label_keys]
            group_expr = "HOUR(c.data_hora)"
        elif periodo_tipo == "semana" or periodo_tipo == "personalizado":
            delta = (fim.date() - inicio.date()).days
            label_keys = [inicio.date() + timedelta(days=i) for i in range(delta + 1)]
            labels = [d.strftime("%d/%m") for d in label_keys]
            group_expr = "DATE(c.data_hora)"
        elif periodo_tipo == "mes":
            start_date = inicio.date()
            delta = (fim.date() - start_date).days
            label_keys = [start_date + timedelta(days=i) for i in range(delta + 1)]
            labels = [d.strftime("%d/%m") for d in label_keys]
            group_expr = "DATE(c.data_hora)"
        else:
            label_keys = list(range(1, 13))
            labels = [datetime(1900, m, 1).strftime("%b") for m in label_keys]
            group_expr = "MONTH(c.data_hora)"

        params = filtro_params + [inicio, fim]
        cursor.execute(f"""
            SELECT {group_expr} AS periodo,
                   COUNT(*) AS total
            FROM odontoPro_consulta c
            LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
            LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id
            WHERE {filtro_base}
              AND c.data_hora BETWEEN %s AND %s
            GROUP BY periodo
            ORDER BY periodo
        """, tuple(params))

        rows = cursor.fetchall() or []
        counts = {row[0]: int(row[1] or 0) for row in rows}
        values = [counts.get(key, 0) for key in label_keys]
        return {"labels": labels, "values": values}

    def _clear_chart_container(self, container):
        for child in container.winfo_children():
            child.destroy()

    def _render_bar_chart(self, chart_period):
        self._clear_chart_container(self._chart_canvas_container)
        self._chart_canvas = None

        labels = chart_period.get("labels", [])
        values = chart_period.get("values", [])
        fig = Figure(figsize=(9, 3), dpi=100, facecolor=COLORS["card"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS["card"])

        bar_color = COLORS.get("primary", "#4f8cff")
        text_color = COLORS.get("text", "#000000")
        border_color = COLORS.get("border", "#cccccc")

        bars = ax.bar(range(len(labels)), values, color=bar_color, edgecolor=bar_color, width=0.65)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=9, color=text_color, rotation=45, ha="right")
        ax.tick_params(axis="y", colors=text_color)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(border_color)
        ax.spines["bottom"].set_color(border_color)
        ax.yaxis.grid(True, color=border_color, alpha=0.25, linestyle="--")
        ax.xaxis.grid(False)
        ax.set_ylabel("Consultas", color=text_color, fontsize=9)

        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{int(height)}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
                color=text_color,
            )

        canvas = FigureCanvasTkAgg(fig, master=self._chart_canvas_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=0)
        self._chart_canvas = canvas

    def _render_pie_chart(self, specialty_data):
        self._clear_chart_container(self._specialty_canvas_container)
        self._specialty_canvas = None

        labels = [row[0] or "Sem Especialidade" for row in specialty_data]
        values = [int(row[1] or 0) for row in specialty_data]
        pie_colors = [
            COLORS.get("primary", "#06B6D4"),
            COLORS.get("secondary", "#3B82F6"),
            COLORS.get("success", "#10B981"),
            COLORS.get("warning", "#F59E0B"),
            COLORS.get("danger", "#EF4444"),
            COLORS.get("info", "#8B5CF6"),
            COLORS.get("purple", "#A855F7"),
            COLORS.get("gray", "#6B7280"),
        ]

        fig = Figure(figsize=(6, 3.5), dpi=100, facecolor=COLORS["card"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS["card"])

        # Se não houver valores (todos zero), evitar chamar ax.pie() — mostra mensagem amigável
        if sum(values) == 0:
            empty_label = ctk.CTkLabel(
                self._specialty_canvas_container,
                text="Nenhum dado disponível",
                font=font("small"),
                text_color=COLORS["text_secondary"]
            )
            empty_label.pack(padx=12, pady=12)
            return

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=pie_colors[: len(values)],
            autopct="%1.0f%%",
            textprops={"color": COLORS["text"], "fontsize": 9},
            wedgeprops={"edgecolor": COLORS["card"], "linewidth": 1}
        )

        for text in texts:
            text.set_color(COLORS["text"])
        for autotext in autotexts:
            autotext.set_color(COLORS["text"])
            autotext.set_fontsize(8)

        ax.axis("equal")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self._specialty_canvas_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=0)
        self._specialty_canvas = canvas

    def _render_productivity(self, productivity_rows):
        for child in self._productivity_rows_frame.winfo_children():
            child.destroy()

        if not productivity_rows:
            empty_label = ctk.CTkLabel(
                self._productivity_rows_frame,
                text="Nenhum médico encontrado para o período selecionado.",
                font=font("small"),
                text_color=COLORS["text_secondary"]
            )
            empty_label.pack(anchor="w", pady=12)
            return

        for index, row_data in enumerate(productivity_rows):
            medico, especialidade, consultas = row_data
            row_bg = COLORS["bg_soft"] if index % 2 == 0 else COLORS["card"]
            row = ctk.CTkFrame(self._productivity_rows_frame, fg_color=row_bg, corner_radius=12)
            row.pack(fill="x", padx=0, pady=2)
            row.columnconfigure((0, 1, 2, 3), weight=1, uniform="prod_cols")

            pos_label = "" if index >= 3 else ["🥇", "🥈", "🥉"][index]
            ctk.CTkLabel(row, text=pos_label, font=font("text"), text_color=COLORS["text"], anchor="w").grid(row=0, column=0, sticky="w", padx=12, pady=14)
            ctk.CTkLabel(row, text=medico or "-", font=font("text"), text_color=COLORS["text"], anchor="w").grid(row=0, column=1, sticky="w", padx=12, pady=14)
            ctk.CTkLabel(row, text=especialidade or "-", font=font("text"), text_color=COLORS["text_secondary"], anchor="w").grid(row=0, column=2, sticky="w", padx=12, pady=14)
            ctk.CTkLabel(row, text=str(int(consultas or 0)), font=font("text", "bold"), text_color=COLORS["text"], anchor="e").grid(row=0, column=3, sticky="e", padx=12, pady=14)

    def _update_filter_options(self, medicos, especialidades):
        if medicos:
            values = ["Todos"] + [medico[1] for medico in medicos]
            self._medicos_map = {"Todos": None}
            self._medicos_map.update({medico[1]: medico[0] for medico in medicos})
            try:
                self.medico_combo.configure(values=values)
            except Exception:
                pass

        if especialidades:
            values = ["Todos"] + [especialidade[1] for especialidade in especialidades]
            self._especialidades_map = {"Todos": None}
            self._especialidades_map.update({especialidade[1]: especialidade[0] for especialidade in especialidades})
            try:
                self.especialidade_combo.configure(values=values)
            except Exception:
                pass

    def _apply_loaded_data(self, summary, chart_period, specialty_data, productivity_rows, medicos, especialidades):
        if summary is None:
            return

        self._card_value_labels["Consultas"].configure(text=str(summary["total_consultas"]))
        self._card_value_labels["Pacientes"].configure(text=str(summary["total_pacientes"]))
        self._card_value_labels["Médicos"].configure(text=str(summary["total_medicos"]))
        self._card_value_labels["Cancelamentos"].configure(text=str(summary["cancelamentos"]))

        self._stat_value_labels["Comparecimento"].configure(text=f"{summary['comparecimento']}%")
        self._stat_value_labels["Cancelamentos"].configure(text=str(summary["cancelamentos"]))
        self._stat_value_labels["Novos Pacientes"].configure(text=str(summary["novos_pacientes"]))
        self._stat_value_labels["Retornos"].configure(text=str(summary["retornos"]))

        if medicos is not None or especialidades is not None:
            self._update_filter_options(medicos or [], especialidades or [])

        if chart_period:
            self._render_bar_chart(chart_period)
        if specialty_data is not None:
            self._render_pie_chart(specialty_data)
        if productivity_rows is not None:
            self._render_productivity(productivity_rows)

    def _process_load_queue(self):
        processed_item = None

        while True:
            try:
                item = self._load_queue.get_nowait()
            except queue.Empty:
                break

            thread_id, summary, chart_period, specialty_data, productivity_rows, medicos, especialidades, error_msg = item
            if thread_id == self._current_thread_id:
                processed_item = item
                break

        if processed_item is None:
            if self._loading:
                self.after(100, self._process_load_queue)
            return

        thread_id, summary, chart_period, specialty_data, productivity_rows, medicos, especialidades, error_msg = processed_item

        if self._timeout_id is not None:
            try:
                self.winfo_toplevel().after_cancel(self._timeout_id)
            except Exception:
                pass
            self._timeout_id = None

        self._loading = False
        self.update_button.configure(state="normal")
        self._loading_label.pack_forget()

        if error_msg:
            self._loading_label.configure(text=f"Erro ao carregar: {error_msg}")
            self._loading_label.pack(anchor="w", padx=20, pady=(0, 10))
            return

        self._apply_loaded_data(summary, chart_period, specialty_data, productivity_rows, medicos, especialidades)
        pass

    def create_transactions_section(self):
        container = ctk.CTkFrame(self.main_container, fg_color=COLORS["card"],
                                corner_radius=12, border_width=1, border_color=COLORS["border"])
        container.pack(fill="both", expand=True)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(header, text="🧾 Transações",
                     font=font("subtitle", "bold")).pack(side="left")

        self.render_table(container)

    def render_table(self, container):
        table_container = ctk.CTkFrame(container, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configuração de colunas
        def configure_table_grid(frame):
            frame.columnconfigure(0, weight=1, uniform="col")  # Data
            frame.columnconfigure(1, weight=4, uniform="col")  # Descrição
            frame.columnconfigure(2, weight=1, uniform="col")  # Tipo
            frame.columnconfigure(3, weight=1, uniform="col")  # Valor
        
        # ========== CABEÇALHO ==========
        headers_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        headers_frame.pack(fill="x", pady=(0, 5))
        configure_table_grid(headers_frame)
        
        # Data
        ctk.CTkLabel(
            headers_frame, 
            text="Data", 
            font=font("small", "bold"), 
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=8)
        
        # Descrição
        ctk.CTkLabel(
            headers_frame, 
            text="Descrição", 
            font=font("small", "bold"), 
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=15, pady=8)
        
        # Tipo
        ctk.CTkLabel(
            headers_frame, 
            text="Tipo", 
            font=font("small", "bold"), 
            text_color=COLORS["text_secondary"],
            anchor="center"
        ).grid(row=0, column=2, sticky="we", padx=0, pady=8)
        
        # Valor
        ctk.CTkLabel(
            headers_frame, 
            text="Valor", 
            font=font("small", "bold"), 
            text_color=COLORS["text_secondary"],
            anchor="e"
        ).grid(row=0, column=3, sticky="e", padx=15, pady=8)
        
        # Linha separadora
        ctk.CTkFrame(table_container, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=5)
        
        # ========== DADOS DA TABELA ==========
        for i, (data, descricao, tipo, valor) in enumerate(self.transacoes):
            # Definir cor baseado no tipo
            cor = COLORS["primary"] if tipo.lower() == "receita" else COLORS["danger"]
            
            # Cor de fundo alternada
            bg = COLORS["bg_soft"] if i % 2 == 0 else "transparent"
            row_frame = ctk.CTkFrame(table_container, fg_color=bg, corner_radius=8)
            row_frame.pack(fill="x", pady=2)
            configure_table_grid(row_frame)
            
            # Data
            ctk.CTkLabel(
                row_frame, 
                text=data, 
                font=font("small"),
                anchor="w"
            ).grid(row=0, column=0, sticky="w", padx=15, pady=8)
            
            # Descrição
            ctk.CTkLabel(
                row_frame, 
                text=descricao, 
                font=font("small"),
                anchor="w"
            ).grid(row=0, column=1, sticky="w", padx=15, pady=8)
            
            # Tipo (com badge)
            ctk.CTkLabel(
                row_frame, 
                text=tipo, 
                font=font("small", "bold"),
                text_color=("white", "white"),
                fg_color=cor,
                corner_radius=10,
                anchor="center",
                width=55,
                height=22
            ).grid(row=0, column=2, sticky="we", padx=0, pady=8)
            
            # Valor
            ctk.CTkLabel(
                row_frame, 
                text=f"R$ {valor:,.2f}".replace(",", "."), 
                font=font("small", "bold"), 
                text_color=cor,
                anchor="e"
            ).grid(row=0, column=3, sticky="e", padx=15, pady=8)

    def adicionar_transacao(self, data, descricao, tipo, valor):
        """Adiciona uma nova transação e sincroniza a interface"""
        self.transacoes.append((data, descricao, tipo, valor))
        self.atualizar_interface()
    
    def remover_transacao(self, indice):
        """Remove uma transação pelo índice e sincroniza a interface"""
        if 0 <= indice < len(self.transacoes):
            del self.transacoes[indice]
            self.atualizar_interface()
    
    def atualizar_interface(self):
        """Sincroniza todos os componentes da interface com os dados atuais"""
        # Limpar e reconstruir a interface
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.setup_ui()
    
    def obter_transacoes(self):
        """Retorna a lista de transações"""
        return self.transacoes
    
    def obter_totais(self):
        """Retorna os totais de receita e despesa"""
        total_receita, total_despesa, lucro = self.calcular_kpis()
        return {
            "receita": total_receita,
            "despesa": total_despesa,
            "lucro": lucro
        }