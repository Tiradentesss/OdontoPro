    def abrir_dialogo_marcar_consulta(self):
        """
        Abre uma janela de diálogo para marcar uma nova consulta.
        Totalmente integrada ao banco de dados com validações completas.
        """
        from tkinter import messagebox
        
        dialogo = ctk.CTkToplevel(self.master)
        dialogo.title("Marcar Nova Consulta")
        dialogo.geometry("680x900")
        dialogo.resizable(False, False)
        dialogo.grab_set()
        
        # Frame principal
        main_frame = ctk.CTkFrame(dialogo, fg_color=COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text="✚ Marcar Nova Consulta",
            font=font("large_title", "bold"),
            text_color=COLORS['text_primary']
        ).pack(pady=(0, 20))
        
        # Frame com scroll
        canvas_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=COLORS['card'],
            corner_radius=15,
            border_width=1,
            border_color=COLORS['border']
        )
        canvas_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # ===== ESTADO DO FORMULÁRIO =====
        estado_form = {
            'paciente_id': None,
            'medico_id': None,
            'data_obj': None,
            'hora_obj': None,
            'carregando_medicos': False,
            'medicos_cache': []
        }
        
        # ===== CAMPO PACIENTE (Busca dinâmica) =====
        ctk.CTkLabel(
            canvas_frame,
            text="👤 Paciente *",
            font=font("subtitle"),
            text_color=COLORS['text_primary']
        ).pack(anchor='w', padx=15, pady=(15, 5))
        
        paciente_entry = ctk.CTkEntry(
            canvas_frame,
            placeholder_text="Digite o nome ou CPF do paciente...",
            height=40,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            corner_radius=8
        )
        paciente_entry.pack(fill='x', padx=15, pady=(0, 5))
        
        paciente_lista_frame = ctk.CTkFrame(canvas_frame, fg_color=COLORS['bg_soft'], corner_radius=8)
        paciente_lista_frame.pack(fill='x', padx=15, pady=(0, 15), sticky='ew')
        paciente_lista_frame.pack_propagate(False)
        paciente_lista_frame.configure(height=0)
        
        paciente_listbox = None
        
        def atualizar_lista_pacientes(termo):
            """Atualiza a lista de pacientes conforme o usuário digita"""
            nonlocal paciente_listbox
            
            # Limpar listbox anterior
            if paciente_listbox:
                paciente_listbox.destroy()
            
            if len(termo.strip()) < 2:
                paciente_lista_frame.configure(height=0)
                return
            
            # Buscar pacientes
            pacientes = PacienteService.buscar_por_cpf_ou_nome(
                clinica_id=None,
                termo_busca=termo,
                limite=10,
                offset=0
            )
            
            if not pacientes:
                paciente_lista_frame.configure(height=0)
                return
            
            paciente_lista_frame.configure(height=min(len(pacientes) * 40, 150))
            
            paciente_listbox = ctk.CTkScrollableFrame(
                paciente_lista_frame,
                fg_color=COLORS['bg_soft'],
                corner_radius=8
            )
            paciente_listbox.pack(fill='both', expand=True)
            
            for pac in pacientes:
                pac_id, pac_nome, pac_cpf, pac_email, pac_telefone, pac_data_nasc = pac
                
                texto_display = PacienteService.formatar_exibicao(pac)
                
                def selecionar_pac(p_id=pac_id, p_texto=texto_display):
                    estado_form['paciente_id'] = p_id
                    paciente_entry.delete(0, 'end')
                    paciente_entry.insert(0, p_texto)
                    paciente_lista_frame.configure(height=0)
                
                btn_pac = ctk.CTkButton(
                    paciente_listbox,
                    text=texto_display,
                    height=38,
                    fg_color=COLORS['card'],
                    hover_color=COLORS['hover'],
                    text_color=COLORS['text_secondary'],
                    corner_radius=8,
                    command=selecionar_pac,
                    anchor='w'
                )
                btn_pac.pack(fill='x', padx=4, pady=2)
        
        paciente_entry.bind('<KeyRelease>', lambda e: atualizar_lista_pacientes(paciente_entry.get()))
        
        # ===== CAMPO MÉDICO (Carregamento automático por clínica) =====
        ctk.CTkLabel(
            canvas_frame,
            text="👨‍⚕️ Médico *",
            font=font("subtitle"),
            text_color=COLORS['text_primary']
        ).pack(anchor='w', padx=15, pady=(0, 5))
        
        medico_var = ctk.StringVar(value="Carregando médicos...")
        medico_combo = ctk.CTkComboBox(
            canvas_frame,
            variable=medico_var,
            height=40,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary_dark'],
            corner_radius=8,
            state='disabled'
        )
        medico_combo.pack(fill='x', padx=15, pady=(0, 15))
        
        def carregar_medicos_thread():
            """Carrega médicos em thread para não bloquear UI"""
            try:
                estado_form['carregando_medicos'] = True
                medicos = MedicoService.listar_por_clinica(self.clinica_id)
                estado_form['medicos_cache'] = medicos
                
                if medicos:
                    medicos_display = [MedicoService.formatar_exibicao(m) for m in medicos]
                    
                    def atualizar_combo():
                        medico_combo.configure(values=medicos_display, state='normal')
                        medico_combo.set(medicos_display[0] if medicos_display else "")
                    
                    dialogo.after(0, atualizar_combo)
                else:
                    def mostrar_erro():
                        medico_combo.configure(state='normal')
                        medico_combo.set("Nenhum médico disponível")
                    
                    dialogo.after(0, mostrar_erro)
            
            except Exception as e:
                print(f"[Agenda] Erro ao carregar médicos: {e}")
                
                def mostrar_erro():
                    medico_combo.configure(state='normal')
                    medico_combo.set("Erro ao carregar")
                
                dialogo.after(0, mostrar_erro)
            
            finally:
                estado_form['carregando_medicos'] = False
        
        thread_medicos = threading.Thread(target=carregar_medicos_thread, daemon=True)
        thread_medicos.start()
        
        def ao_selecionar_medico(value):
            """Preenche automaticamente a especialidade ao selecionar o médico"""
            medico_display = value
            medico_id = MedicoService.extrair_id_de_display(medico_display, self.clinica_id)
            
            if medico_id:
                estado_form['medico_id'] = medico_id
                especialidade = MedicoService.obter_especialidade_principal(medico_id)
                especialidade_entry.delete(0, 'end')
                especialidade_entry.insert(0, especialidade)
                
                # Se data já foi preenchida, atualizar horários
                if estado_form['data_obj']:
                    atualizar_horarios_sugeridos()
        
        medico_combo.configure(command=ao_selecionar_medico)
        
        # ===== CAMPO DATA =====
        ctk.CTkLabel(
            canvas_frame,
            text="📅 Data da Consulta *",
            font=font("subtitle"),
            text_color=COLORS['text_primary']
        ).pack(anchor='w', padx=15, pady=(0, 5))
        
        data_entry = ctk.CTkEntry(
            canvas_frame,
            placeholder_text="DD/MM/YYYY",
            height=40,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            corner_radius=8
        )
        data_entry.pack(fill='x', padx=15, pady=(0, 5))
        
        data_erro_label = ctk.CTkLabel(
            canvas_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#EF4444"
        )
        data_erro_label.pack(anchor='w', padx=15, pady=(0, 10))
        
        def validar_data(event=None):
            """Valida e atualiza horários ao mudar a data"""
            data_str = data_entry.get().strip()
            
            if not data_str:
                data_erro_label.configure(text="")
                estado_form['data_obj'] = None
                hora_entry.configure(state='disabled')
                return
            
            valido, mensagem, data_obj = ConsultaService.validar_data(data_str)
            
            if valido:
                estado_form['data_obj'] = data_obj
                data_erro_label.configure(text="")
                hora_entry.configure(state='normal')
                
                # Atualizar horários disponíveis se médico foi selecionado
                if estado_form['medico_id'] and estado_form['data_obj']:
                    atualizar_horarios_sugeridos()
            else:
                estado_form['data_obj'] = None
                data_erro_label.configure(text=f"❌ {mensagem}")
                hora_entry.configure(state='disabled')
        
        data_entry.bind('<KeyRelease>', validar_data)
        data_entry.bind('<FocusOut>', validar_data)
        
        # ===== CAMPO HORA =====
        ctk.CTkLabel(
            canvas_frame,
            text="🕐 Hora da Consulta *",
            font=font("subtitle"),
            text_color=COLORS['text_primary']
        ).pack(anchor='w', padx=15, pady=(0, 5))
        
        hora_entry = ctk.CTkEntry(
            canvas_frame,
            placeholder_text="HH:MM",
            height=40,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            corner_radius=8,
            state='disabled'
        )
        hora_entry.pack(fill='x', padx=15, pady=(0, 5))
        
        hora_erro_label = ctk.CTkLabel(
            canvas_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#EF4444"
        )
        hora_erro_label.pack(anchor='w', padx=15, pady=(0, 10))
        
        def validar_hora(event=None):
            """Valida e verifica disponibilidade do horário"""
            hora_str = hora_entry.get().strip()
            
            if not hora_str:
                hora_erro_label.configure(text="")
                estado_form['hora_obj'] = None
                return
            
            valido, mensagem, hora_obj = ConsultaService.validar_hora(hora_str)
            
            if not valido:
                hora_erro_label.configure(text=f"❌ {mensagem}")
                estado_form['hora_obj'] = None
                return
            
            estado_form['hora_obj'] = hora_obj
            
            # Verificar disponibilidade
            if estado_form['medico_id'] and estado_form['data_obj']:
                disponivel, msg_disponibilidade = ConsultaService.verificar_horario_disponivel(
                    estado_form['medico_id'],
                    estado_form['data_obj'].date(),
                    hora_obj
                )
                
                if disponivel:
                    hora_erro_label.configure(text="✓ Horário disponível", text_color="#10B981")
                else:
                    hora_erro_label.configure(text=f"❌ {msg_disponibilidade}", text_color="#EF4444")
                    estado_form['hora_obj'] = None
            else:
                hora_erro_label.configure(text="")
        
        hora_entry.bind('<KeyRelease>', validar_hora)
        hora_entry.bind('<FocusOut>', validar_hora)
        
        # ===== CAMPO ESPECIALIDADE (Preenchimento automático) =====
        ctk.CTkLabel(
            canvas_frame,
            text="🦷 Especialidade *",
            font=font("subtitle"),
            text_color=COLORS['text_primary']
        ).pack(anchor='w', padx=15, pady=(0, 5))
        
        especialidade_entry = ctk.CTkEntry(
            canvas_frame,
            placeholder_text="Preenchida automaticamente",
            height=40,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            corner_radius=8,
            state='disabled'
        )
        especialidade_entry.pack(fill='x', padx=15, pady=(0, 15))
        
        # ===== CAMPO OBSERVAÇÕES =====
        ctk.CTkLabel(
            canvas_frame,
            text="📝 Observações (opcional)",
            font=font("subtitle"),
            text_color=COLORS['text_primary']
        ).pack(anchor='w', padx=15, pady=(0, 5))
        
        obs_text = ctk.CTkTextbox(
            canvas_frame,
            height=80,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            border_width=1,
            corner_radius=8
        )
        obs_text.pack(fill='x', padx=15, pady=(0, 15))
        
        # ===== FUNÇÃO AUXILIAR: Atualizar horários sugeridos =====
        def atualizar_horarios_sugeridos():
            """Mostra horários já ocupados quando médico + data são preenchidos"""
            if estado_form['medico_id'] and estado_form['data_obj']:
                horarios_ocupados = ConsultaService.listar_horarios_ocupados_no_dia(
                    estado_form['medico_id'],
                    estado_form['data_obj'].date()
                )
                
                if horarios_ocupados:
                    horarios_str = ", ".join(horarios_ocupados)
                    hora_erro_label.configure(
                        text=f"ℹ️ Horários ocupados: {horarios_str}",
                        text_color=COLORS['text_muted']
                    )
        
        # ===== BOTÕES =====
        button_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        button_frame.pack(fill='x', pady=(0, 0))
        
        def salvar_consulta():
            """Salva a consulta com todas as validações"""
            # Validar campos obrigatórios
            if not estado_form['paciente_id']:
                messagebox.showwarning("Aviso", "Selecione um paciente válido.")
                return
            
            if not estado_form['medico_id']:
                messagebox.showwarning("Aviso", "Selecione um médico.")
                return
            
            if not estado_form['data_obj']:
                messagebox.showwarning("Aviso", "Data inválida ou não preenchida.")
                return
            
            if not estado_form['hora_obj']:
                messagebox.showwarning("Aviso", "Hora inválida ou não preenchida.")
                return
            
            especialidade = especialidade_entry.get().strip()
            if not especialidade:
                messagebox.showwarning("Aviso", "Especialidade não foi preenchida.")
                return
            
            # Combinar data e hora
            data_hora = datetime.combine(
                estado_form['data_obj'].date(),
                estado_form['hora_obj']
            )
            
            # Salvar consulta usando o serviço
            resultado = ConsultaService.criar_consulta(
                self.clinica_id,
                estado_form['paciente_id'],
                estado_form['medico_id'],
                data_hora,
                especialidade,
                status='agendada',
                observacoes=obs_text.get('1.0', 'end-1c').strip()
            )
            
            if resultado['sucesso']:
                messagebox.showinfo(
                    "✓ Sucesso",
                    f"Consulta marcada com sucesso!"
                )
                
                # Atualizar agenda e fechar diálogo
                self.refresh_data()
                dialogo.destroy()
            else:
                messagebox.showerror(
                    "❌ Erro",
                    f"Erro ao marcar consulta:\n{resultado['mensagem']}"
                )
        
        # Botão Salvar
        btn_salvar = ctk.CTkButton(
            button_frame,
            text="✓ Salvar Consulta",
            height=44,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            text_color='white',
            font=font("button", "bold"),
            command=salvar_consulta
        )
        btn_salvar.pack(side='left', fill='x', expand=True, padx=(0, 8))
        
        # Botão Cancelar
        btn_cancelar = ctk.CTkButton(
            button_frame,
            text="✕ Cancelar",
            height=44,
            fg_color=COLORS['danger'],
            hover_color="#DC2626",
            text_color='white',
            font=font("button", "bold"),
            command=dialogo.destroy
        )
        btn_cancelar.pack(side='left', fill='x', expand=True, padx=(8, 0))
