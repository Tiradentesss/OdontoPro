import customtkinter as ctk
import tkinter as tk
from .base import BaseScreen

class Configuracoes(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Configurações")

        # --- Vibe Colors (Extracted from Image) ---
        self.colors = {
            "bg_main": "#F3F4F6",       # Light gray background
            "bg_card": "#FFFFFF",       # White card
            "text_primary": "#333333",  # Dark text
            "text_secondary": "#9CA3AF",# Light gray text (inactive tabs/labels)
            "accent": "#22D3EE",        # Cyan (Active tab, Button, Asterisks)
            "btn_hover": "#06B6D4",     # Darker Cyan for hover
            "border": "#E5E7EB",        # Light border
            "input_bg": "#FFFFFF",      # Input background
            "input_border": "#E2E8F0"   # Subtle blue-gray border for inputs
        }

        # State to track active tab
        # Default set to 'Segurança' to match the provided image context
        self.current_tab = "Segurança" 
        self.tab_buttons = {} 

        self.setup_ui()

    def setup_ui(self):
        # 1. Main Background
        self.content_card.configure(fg_color=self.colors["bg_main"])

        # 2. White Card Container
        self.main_card = ctk.CTkFrame(
            self.content_card,
            fg_color=self.colors["bg_card"],
            corner_radius=20,
            border_width=0
        )
        self.main_card.pack(fill="both", expand=True, padx=20, pady=20)

        # 3. Top Navigation (Tabs)
        self._build_tabs(self.main_card)

        # 4. Dynamic Content Area
        self.content_area = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=40, pady=20)

        # 5. Bottom Action Button
        self._build_footer(self.main_card)

        # Initial Render
        self.switch_tab(self.current_tab)

    def _build_tabs(self, parent):
        """Creates the interactive tab header"""
        tab_frame = ctk.CTkFrame(parent, fg_color="transparent", height=50)
        tab_frame.pack(fill="x", padx=40, pady=(30, 20))

        tabs = ["Perfil", "Preferencias", "Segurança"]
        
        # Container for the buttons
        self.tab_container = ctk.CTkFrame(tab_frame, fg_color="transparent")
        self.tab_container.pack(side="left", fill="y")

        for tab_name in tabs:
            btn = ctk.CTkButton(
                self.tab_container,
                text=tab_name,
                fg_color="transparent",
                hover_color=self.colors["bg_main"],
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.colors["text_secondary"],
                anchor="w",
                width=110, # Slightly wider to accommodate spacing
                command=lambda t=tab_name: self.switch_tab(t)
            )
            btn.pack(side="left", padx=(0, 5))
            self.tab_buttons[tab_name] = btn

        # The Floating Underline (Visual Indicator)
        self.underline = ctk.CTkFrame(
            tab_frame, 
            height=3, 
            width=80, 
            fg_color=self.colors["accent"]
        )
        self.underline.place(x=0, y=38) 

        # Divider Line (Background line)
        divider = ctk.CTkFrame(parent, height=1, fg_color=self.colors["border"])
        divider.pack(fill="x", padx=40)

    def switch_tab(self, tab_name):
        """Handles logic to switch views and update visuals"""
        self.current_tab = tab_name

        # 1. Update Tab Visuals (Colors & Underline)
        tab_order = ["Perfil", "Preferencias", "Segurança"]
        
        for name, btn in self.tab_buttons.items():
            if name == tab_name:
                btn.configure(text_color=self.colors["accent"])
                # Move underline logic
                idx = tab_order.index(name)
                # 115 is approximate width + padding of buttons
                self.underline.place(x=10 + (idx * 115), y=38) 
            else:
                btn.configure(text_color=self.colors["text_secondary"])

        # 2. Clear Content
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # 3. Render Specific View
        if tab_name == "Perfil":
            self._render_profile(self.content_area)
        elif tab_name == "Preferencias":
            self._render_preferences(self.content_area)
        elif tab_name == "Segurança":
            self._render_security(self.content_area)

    # ----------------------------------------------------------------
    # VIEW: SEGURANÇA (Refactored based on Image)
    # ----------------------------------------------------------------
    def _render_security(self, parent):
        """Builds the Change Password view"""
        
        # Sub-header: "Alterar a senha"
        lbl_subtitle = ctk.CTkLabel(
            parent, 
            text="Alterar a senha", 
            font=ctk.CTkFont(size=18, weight="normal"), # Medium weight
            text_color="#4B5563" # Slightly lighter than pure black
        )
        lbl_subtitle.pack(anchor="w", pady=(10, 25))

        # Input 1: Nova Senha
        self._create_password_input(parent, "Nova Senha")

        # Input 2: Confirme sua senha
        self._create_password_input(parent, "Confirme sua senha")

    def _create_password_input(self, parent, label_text):
        """Helper for password fields with Cyan placeholders"""
        
        # Label
        lbl = ctk.CTkLabel(
            parent, 
            text=label_text, 
            font=ctk.CTkFont(size=15),
            text_color=self.colors["text_primary"]
        )
        lbl.pack(anchor="w", pady=(0, 8))

        # Entry
        entry = ctk.CTkEntry(
            parent,
            width=400, # Not full width, but wide enough
            height=50,
            corner_radius=12,
            border_width=1,
            border_color=self.colors["input_border"],
            fg_color=self.colors["input_bg"],
            text_color=self.colors["text_primary"],
            
            # Vibe Match: The image shows blue asterisks. 
            # We use placeholder text color to mimic this style.
            placeholder_text="**********",
            placeholder_text_color=self.colors["accent"] 
        )
        # Note: In a real app, use show="*" to mask actual typing. 
        # For the visual vibe of the mockup, we rely on the placeholder styling.
        entry.pack(anchor="w", pady=(0, 25))

    # ----------------------------------------------------------------
    # VIEW: PREFERENCIAS
    # ----------------------------------------------------------------
    def _render_preferences(self, parent):
        lbl_title = ctk.CTkLabel(
            parent, 
            text="Notificações", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        lbl_title.pack(anchor="w", pady=(10, 20))
        self._create_switch(parent, "Mensagens", True)
        self._create_switch(parent, "Notificações", True)

    def _create_switch(self, parent, text, default_val=False):
        switch = ctk.CTkSwitch(
            parent, text=text, font=ctk.CTkFont(size=15),
            text_color=self.colors["text_primary"],
            progress_color=self.colors["accent"], fg_color="#D1D5DB",
            button_color="white", button_hover_color="white",
            switch_height=24, switch_width=48, onvalue=True, offvalue=False
        )
        switch.pack(anchor="w", pady=12)
        if default_val: switch.select()

    # ----------------------------------------------------------------
    # VIEW: PERFIL
    # ----------------------------------------------------------------
    def _render_profile(self, parent):
        parent.grid_columnconfigure(0, weight=0)
        parent.grid_columnconfigure(1, weight=1)
        
        self._build_avatar_section(parent)
        
        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
        form_frame.grid_columnconfigure((0, 1), weight=1)

        self._create_profile_input(form_frame, "Nome", "Gabriel Gomes", 0, 0)
        self._create_profile_input(form_frame, "CPF", "000.000.000 - 00", 0, 1)
        self._create_profile_input(form_frame, "Email", "gabrielgomes@gmail.com", 1, 0)
        self._create_profile_input(form_frame, "Endereço", "Rua Nova Batistas Campos", 1, 1)
        self._create_profile_input(form_frame, "Cidade", "Belém", 2, 1)
        
        # Date Input
        lbl = ctk.CTkLabel(form_frame, text="Data de Nascimento", font=ctk.CTkFont(size=14), text_color=self.colors["text_primary"])
        lbl.grid(row=4, column=0, padx=(0, 15), sticky="w")
        
        date_combo = ctk.CTkComboBox(
            form_frame, values=["24/05/2002"], height=45, corner_radius=10,
            border_color=self.colors["border"], fg_color=self.colors["input_bg"],
            text_color=self.colors["text_secondary"], dropdown_fg_color="white"
        )
        date_combo.grid(row=5, column=0, padx=(0, 15), pady=(5, 20), sticky="ew")

    def _build_avatar_section(self, parent):
        avatar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        avatar_frame.grid(row=0, column=0, sticky="n", padx=(0, 20), pady=10)

        canvas = tk.Canvas(avatar_frame, width=120, height=120, bg=self.colors["bg_card"], highlightthickness=0)
        canvas.pack()
        canvas.create_oval(5, 5, 115, 115, fill="#E5E7EB", outline="")
        canvas.create_text(60, 60, text="GG", font=("Arial", 30, "bold"), fill="white")

        ctk.CTkButton(
            avatar_frame, text="✎", width=30, height=30, corner_radius=15,
            fg_color=self.colors["accent"], hover_color=self.colors["btn_hover"]
        ).place(relx=0.85, rely=0.85, anchor="center")

    def _create_profile_input(self, parent, label, placeholder, row, col):
        """Helper specifically for the Grid layout in Profile"""
        lbl = ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=14), text_color=self.colors["text_primary"])
        pad_x = (0, 15) if col == 0 else (15, 0)
        lbl.grid(row=row * 2, column=col, padx=pad_x, sticky="w")
        
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder, height=45, corner_radius=10,
            border_color=self.colors["border"], fg_color=self.colors["input_bg"],
            text_color=self.colors["text_primary"], placeholder_text_color=self.colors["text_secondary"]
        )
        entry.grid(row=(row * 2) + 1, column=col, padx=pad_x, pady=(5, 20), sticky="ew")
        if placeholder: entry.insert(0, placeholder)

    # ----------------------------------------------------------------
    # FOOTER
    # ----------------------------------------------------------------
    def _build_footer(self, parent):
        """Creates the Save button aligned to the right"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.pack(fill="x", side="bottom", padx=40, pady=40)

        save_btn = ctk.CTkButton(
            footer_frame,
            text="Salvar",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["btn_hover"],
            corner_radius=10,
            height=45,
            width=140,
            command=self.save_data
        )
        save_btn.pack(side="right")

    def save_data(self):
        print(f"Salvando dados da aba: {self.current_tab}")