"""
===============================================================================
PROJETO: OmniOverlay - Theme Engine, Custom Backgrounds & Flexible Layouts
===============================================================================
"""

import json
import os
import random
import subprocess
import time
import urllib.parse
import webbrowser
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from tkVideoPlayer import TkinterVideo

import psutil
from pynput import keyboard

CONFIG_FILE = "app_config.json"

# Definições Universais de Cores Refinadas (Modo Claro / Escuro Ajustados)
COLOR_TEXT_PRIMARY = ("#0F172A", "#F8FAFC")
COLOR_TEXT_SECONDARY = ("#475569", "#94A3B8")
COLOR_BG_SURFACE = ("#F1F5F9", "#0F172A")
COLOR_BG_CARD = ("#FFFFFF", "#1E293B")
COLOR_INPUT_BG = ("#F8FAFC", "#1E293B")
COLOR_BORDER = ("#CBD5E1", "#334155")

COLOR_ACCENTS = {
    "azul": {"primary": "#2563EB", "hover": "#1D4ED8"},
    "vermelho": {"primary": "#DC2626", "hover": "#B91C1C"},
    "verde": {"primary": "#16A34A", "hover": "#15803D"},
    "roxo": {"primary": "#9333EA", "hover": "#7E22CE"},
}


class AccountManager:
    """Gerencia leitura e gravação dos perfis e configurações."""

    @staticmethod
    def carregar_dados():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    if "perfis" in dados and len(dados["perfis"]) > 0:
                        for p in dados["perfis"]:
                            p.setdefault("atalhos_custom", [])
                            p.setdefault("foto_perfil", "")
                            p.setdefault("fundo_imagem", "")
                            p.setdefault("modo_layout", "grid")
                        return dados
            except Exception as e:
                print(f"[ERRO] Falha ao ler arquivo de configuração: {e}")

        dados_padrao = {
            "perfis": [
                {
                    "id": "p1",
                    "nome": "Jogador Principal",
                    "cor_acento": "azul",
                    "foto_perfil": "",
                    "fundo_imagem": "",
                    "modo_layout": "grid",
                    "atalhos_custom": []
                }
            ],
            "ultimo_perfil": "p1",
            "modo_tema": "dark"
        }
        AccountManager.salvar_dados(dados_padrao)
        return dados_padrao

    @staticmethod
    def salvar_dados(dados):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ERRO] Falha ao salvar arquivo de configuração: {e}")


class ProfileSelectorFrame(ctk.CTkFrame):
    """Tela de Seleção de Perfis."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG_SURFACE, corner_radius=12)
        self.controller = controller
        self.criar_interface()

    def criar_interface(self):
        header = ctk.CTkFrame(self, fg_color=COLOR_BG_SURFACE, height=50, corner_radius=0)
        header.pack(fill="x")

        lbl_titulo = ctk.CTkLabel(
            header,
            text="🎮 Escolha sua Conta",
            font=("Segoe UI", 14, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        lbl_titulo.pack(side="left", padx=16, pady=12)

        btn_fechar = ctk.CTkButton(
            header,
            text="✕",
            width=30,
            height=30,
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="#FFFFFF",
            command=self.controller.destroy,
        )
        btn_fechar.pack(side="right", padx=12)

        self.scroll_perfis = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_perfis.pack(fill="both", expand=True, padx=20, pady=15)

        frame_criar = ctk.CTkFrame(self, fg_color=COLOR_BG_CARD, corner_radius=12, border_color=COLOR_BORDER, border_width=1)
        frame_criar.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            frame_criar,
            text="Criar Nova Conta",
            font=("Segoe UI", 11, "bold"),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(anchor="w", padx=12, pady=(8, 2))

        self.entry_novo_nome = ctk.CTkEntry(
            frame_criar,
            placeholder_text="Nome da conta...",
            height=36,
            fg_color=COLOR_INPUT_BG,
            text_color=COLOR_TEXT_PRIMARY,
            border_color=COLOR_BORDER
        )
        self.entry_novo_nome.pack(fill="x", padx=12, pady=4)
        self.entry_novo_nome.bind("<Return>", lambda e: self.acao_criar_perfil())

        btn_novo = ctk.CTkButton(
            frame_criar,
            text="+ Criar e Entrar",
            height=36,
            corner_radius=8,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            command=self.acao_criar_perfil,
        )
        btn_novo.pack(fill="x", padx=12, pady=(4, 12))

    def atualizar_lista(self):
        for widget in self.scroll_perfis.winfo_children():
            widget.destroy()

        perfis = self.controller.dados_config.get("perfis", [])

        for perfil in perfis:
            card = ctk.CTkFrame(self.scroll_perfis, fg_color=COLOR_BG_CARD, corner_radius=12, border_color=COLOR_BORDER, border_width=1)
            card.pack(fill="x", pady=6, ipady=4)

            foto_path = perfil.get("foto_perfil", "")
            img_avatar = None
            if foto_path and os.path.exists(foto_path):
                try:
                    pil_img = Image.open(foto_path)
                    img_avatar = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(36, 36))
                except Exception:
                    img_avatar = None

            lbl_avatar = ctk.CTkLabel(
                card,
                text="" if img_avatar else "👤",
                image=img_avatar,
                width=42,
                height=42,
                corner_radius=21,
                fg_color=COLOR_BG_SURFACE,
                text_color=COLOR_TEXT_PRIMARY,
                font=("Segoe UI", 16),
            )
            lbl_avatar.pack(side="left", padx=12)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True)

            lbl_nome = ctk.CTkLabel(
                info_frame,
                text=perfil["nome"],
                font=("Segoe UI", 12, "bold"),
                text_color=COLOR_TEXT_PRIMARY,
                anchor="w",
            )
            lbl_nome.pack(fill="x", pady=(12, 0))

            btn_entrar = ctk.CTkButton(
                card,
                text="Entrar",
                width=80,
                height=32,
                corner_radius=6,
                fg_color="#16A34A",
                hover_color="#15803D",
                text_color="#FFFFFF",
                font=("Segoe UI", 11, "bold"),
                command=lambda p=perfil: self.controller.entrar_no_perfil(p),
            )
            btn_entrar.pack(side="right", padx=12)

    def acao_criar_perfil(self):
        nome = self.entry_novo_nome.get().strip()
        if not nome:
            return

        novo_id = f"p_{int(time.time())}"
        novo_perfil = {
            "id": novo_id,
            "nome": nome,
            "cor_acento": "azul",
            "foto_perfil": "",
            "fundo_imagem": "",
            "modo_layout": "grid",
            "atalhos_custom": []
        }

        self.controller.dados_config["perfis"].append(novo_perfil)
        AccountManager.salvar_dados(self.controller.dados_config)

        self.entry_novo_nome.delete(0, "end")
        self.controller.entrar_no_perfil(novo_perfil)


class DashboardFrame(ctk.CTkFrame):
    """Painel Principal Dashboard Overlay."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG_SURFACE, corner_radius=12)
        self.controller = controller

        self._offset_x = 0
        self._offset_y = 0
        self.dynamic_accent_buttons = []
        self.icone_foto_temp = ""
        self.imagem_fundo_atual = None

        self.criar_interface()
        self.atualizar_monitor_sistema()

    def criar_interface(self):
        self.lbl_fundo_bg = ctk.CTkLabel(self, text="", fg_color="transparent")
        self.lbl_fundo_bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self.redimensionar_fundo_handler)

        self.header_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_CARD,
            corner_radius=12,
            border_color=COLOR_BORDER,
            border_width=1,
            height=60,
        )
        self.header_frame.pack(fill="x", padx=16, pady=(16, 8))

        self.header_frame.bind("<Button-1>", self.iniciar_arraste)
        self.header_frame.bind("<B1-Motion>", self.arrastar_janela)

        self.btn_avatar = ctk.CTkButton(
            self.header_frame,
            text="👤",
            width=40,
            height=40,
            corner_radius=20,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            font=("Segoe UI", 15),
            command=self.trocar_foto_perfil,
        )
        self.btn_avatar.pack(side="left", padx=(12, 8))

        self.lbl_titulo = ctk.CTkLabel(
            self.header_frame,
            text="OmniOverlay",
            font=("Segoe UI", 13, "bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_titulo.pack(side="left", padx=2)

        self.frame_hardware = ctk.CTkFrame(
            self.header_frame,
            fg_color=COLOR_BG_SURFACE,
            corner_radius=8,
            height=36
        )
        self.frame_hardware.pack(side="left", padx=16, pady=10)

        self.lbl_cpu = ctk.CTkLabel(
            self.frame_hardware,
            text="⚡ CPU: 0%",
            font=("Segoe UI", 10, "bold"),
            text_color=("#2563EB", "#60A5FA")
        )
        self.lbl_cpu.pack(side="left", padx=8)

        self.lbl_ram = ctk.CTkLabel(
            self.frame_hardware,
            text="💾 RAM: 0%",
            font=("Segoe UI", 10, "bold"),
            text_color=("#16A34A", "#4ADE80")
        )
        self.lbl_ram.pack(side="left", padx=(0, 8))

        btn_fechar = ctk.CTkButton(
            self.header_frame,
            text="✕",
            width=32,
            height=32,
            corner_radius=8,
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="#FFFFFF",
            command=self.controller.destroy,
        )
        btn_fechar.pack(side="right", padx=(4, 12))

        self.btn_tema = ctk.CTkButton(
            self.header_frame,
            text="☀️" if self.controller.modo_tema_atual == "dark" else "🌙",
            width=32,
            height=32,
            corner_radius=8,
            fg_color=COLOR_BG_SURFACE,
            hover_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            font=("Segoe UI", 12),
            command=self.controller.alternar_tema_global,
        )
        self.btn_tema.pack(side="right", padx=4)

        btn_trocar_conta = ctk.CTkButton(
            self.header_frame,
            text="🔄 Contas",
            width=85,
            height=32,
            corner_radius=8,
            fg_color=COLOR_BG_SURFACE,
            hover_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
            command=self.controller.abrir_seletor_perfis,
        )
        btn_trocar_conta.pack(side="right", padx=4)

        self.frame_busca = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_CARD,
            corner_radius=12,
            border_color=COLOR_BORDER,
            border_width=1,
        )
        self.frame_busca.pack(fill="x", padx=16, pady=4)

        self.entry_universal = ctk.CTkEntry(
            self.frame_busca,
            placeholder_text="Cole um Link Web ou o caminho de um Programa (.exe) para abrir...",
            height=38,
            corner_radius=8,
            fg_color=COLOR_INPUT_BG,
            text_color=COLOR_TEXT_PRIMARY,
            border_color=COLOR_BORDER,
            font=("Segoe UI", 11),
        )
        self.entry_universal.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        self.entry_universal.bind("<Return>", lambda e: self.executar_busca_universal())

        btn_procurar_arquivo = ctk.CTkButton(
            self.frame_busca,
            text="📁 Buscar App",
            width=100,
            height=38,
            fg_color=COLOR_BG_SURFACE,
            hover_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            command=self.selecionar_executavel_direto,
        )
        btn_procurar_arquivo.pack(side="right", padx=(0, 4), pady=8)

        btn_executar = ctk.CTkButton(
            self.frame_busca,
            text="Abrir 🚀",
            width=90,
            height=38,
            corner_radius=8,
            text_color="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            command=self.executar_busca_universal,
        )
        btn_executar.pack(side="right", padx=8, pady=8)
        self.dynamic_accent_buttons.append(btn_executar)

        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=12,
            fg_color=COLOR_BG_CARD,
            border_color=COLOR_BORDER,
            border_width=1,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.tabview.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        self.tab_hub = self.tabview.add("🚀 Central de Atalhos")
        self.tab_ia = self.tabview.add("🤖 Assistente IA")
        self.tab_video = self.tabview.add("🎬 Player de Vídeo")
        self.tab_config = self.tabview.add("⚙️ Configurações")

        self.montar_aba_hub()
        self.montar_aba_ia()
        self.montar_aba_player_video()
        self.montar_aba_config()

    def atualizar_fundo_tela(self, caminho_img):
        self.imagem_fundo_atual = None
        if caminho_img and os.path.exists(caminho_img):
            try:
                self.imagem_fundo_atual = Image.open(caminho_img)
                self.aplicar_imagem_fundo_redimensionada()
                self.lbl_fundo_bg.lower()
                return
            except Exception as e:
                print(f"[ERRO] Falha ao carregar fundo de tela: {e}")

        self.lbl_fundo_bg.configure(image="")

    def redimensionar_fundo_handler(self, event=None):
        if self.imagem_fundo_atual:
            self.aplicar_imagem_fundo_redimensionada()

    def aplicar_imagem_fundo_redimensionada(self):
        if not self.imagem_fundo_atual:
            return
        w = max(self.winfo_width(), 200)
        h = max(self.winfo_height(), 200)
        try:
            pil_resized = self.imagem_fundo_atual.resize((w, h), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=pil_resized, dark_image=pil_resized, size=(w, h))
            self.lbl_fundo_bg.configure(image=ctk_img)
        except Exception as e:
            print(f"[ERRO] Redimensionamento de fundo: {e}")

    def carregar_perfil(self, perfil):
        self.lbl_titulo.configure(text=f"OmniOverlay - {perfil['nome']}")
        self.aplicar_cor_acento(perfil.get("cor_acento", "azul"))
        self.atualizar_foto_avatar(perfil.get("foto_perfil", ""))
        self.atualizar_fundo_tela(perfil.get("fundo_imagem", ""))
        self.atualizar_atalhos_customizados()

    def atualizar_monitor_sistema(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()

            self.lbl_cpu.configure(text=f"⚡ CPU: {cpu_usage:.0f}%")
            self.lbl_ram.configure(text=f"💾 RAM: {ram.percent:.0f}%")

            if hasattr(self, 'bar_cpu_detalhada'):
                self.bar_cpu_detalhada.set(cpu_usage / 100.0)
                self.lbl_cpu_valor_detalhado.configure(text=f"{cpu_usage:.1f}%")

                self.bar_ram_detalhada.set(ram.percent / 100.0)
                ram_usada_gb = ram.used / (1024**3)
                ram_total_gb = ram.total / (1024**3)
                self.lbl_ram_valor_detalhado.configure(
                    text=f"{ram.percent:.1f}% ({ram_usada_gb:.1f} GB / {ram_total_gb:.1f} GB)"
                )

                cor_cpu = "#16A34A" if cpu_usage < 60 else ("#EAB308" if cpu_usage < 85 else "#EF4444")
                self.bar_cpu_detalhada.configure(progress_color=cor_cpu)

                cor_ram = "#16A34A" if ram.percent < 70 else ("#EAB308" if ram.percent < 88 else "#EF4444")
                self.bar_ram_detalhada.configure(progress_color=cor_ram)

        except Exception as e:
            print(f"[MONITOR] Erro: {e}")

        self.after(1500, self.atualizar_monitor_sistema)

    def atualizar_foto_avatar(self, foto_path):
        if foto_path and os.path.exists(foto_path):
            try:
                pil_img = Image.open(foto_path)
                img_avatar = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(32, 32))
                self.btn_avatar.configure(image=img_avatar, text="")
                return
            except Exception as e:
                print(f"[ERRO] Falha ao carregar avatar: {e}")

        self.btn_avatar.configure(image="", text="👤")

    def trocar_foto_perfil(self):
        caminho = filedialog.askopenfilename(
            title="Escolha sua Foto de Perfil",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.ico *.bmp")]
        )
        if caminho and self.controller.perfil_ativo:
            self.controller.perfil_ativo["foto_perfil"] = caminho
            AccountManager.salvar_dados(self.controller.dados_config)
            self.atualizar_foto_avatar(caminho)

    def aplicar_cor_acento(self, nome_cor):
        cor = COLOR_ACCENTS.get(nome_cor, COLOR_ACCENTS["azul"])
        for btn in self.dynamic_accent_buttons:
            btn.configure(fg_color=cor["primary"], hover_color=cor["hover"])

        if self.controller.perfil_ativo:
            self.controller.perfil_ativo["cor_acento"] = nome_cor
            AccountManager.salvar_dados(self.controller.dados_config)

    def iniciar_arraste(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def arrastar_janela(self, event):
        x = self.controller.winfo_x() + (event.x - self._offset_x)
        y = self.controller.winfo_y() + (event.y - self._offset_y)
        self.controller.geometry(f"+{x}+{y}")

    def toggle_visibilidade_overlay(self):
        """Oculta ou exibe o overlay ao pressionar o atalho global Alt + Z."""
        if self.winfo_viewable():
            self.controller.withdraw()
        else:
            self.controller.deiconify()
            self.controller.lift()
            self.controller.focus_force()

    def montar_aba_hub(self):
        frame_adicionar = ctk.CTkFrame(self.tab_hub, fg_color=COLOR_BG_SURFACE, corner_radius=10, border_color=COLOR_BORDER, border_width=1)
        frame_adicionar.pack(fill="x", pady=(4, 6), padx=4, ipady=4)

        ctk.CTkLabel(
            frame_adicionar,
            text="➕ Adicionar Novo Atalho ao Seu Perfil",
            font=("Segoe UI", 11, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(anchor="w", padx=12, pady=(6, 2))

        form_top = ctk.CTkFrame(frame_adicionar, fg_color="transparent")
        form_top.pack(fill="x", padx=8, pady=2)

        self.entry_nome_atalho = ctk.CTkEntry(
            form_top,
            placeholder_text="Nome do Atalho...",
            height=32,
            fg_color=COLOR_INPUT_BG,
            text_color=COLOR_TEXT_PRIMARY,
            border_color=COLOR_BORDER
        )
        self.entry_nome_atalho.pack(side="left", fill="x", expand=True, padx=4)

        self.entry_url_atalho = ctk.CTkEntry(
            form_top,
            placeholder_text="Link Web ou Caminho (.exe)...",
            height=32,
            fg_color=COLOR_INPUT_BG,
            text_color=COLOR_TEXT_PRIMARY,
            border_color=COLOR_BORDER
        )
        self.entry_url_atalho.pack(side="left", fill="x", expand=True, padx=4)

        btn_browse_app = ctk.CTkButton(
            form_top,
            text="💻 Buscar App",
            width=100,
            height=32,
            fg_color=COLOR_BG_CARD,
            hover_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            command=self.procurar_app_para_atalho,
        )
        btn_browse_app.pack(side="left", padx=4)

        form_bot = ctk.CTkFrame(frame_adicionar, fg_color="transparent")
        form_bot.pack(fill="x", padx=8, pady=(4, 6))

        ctk.CTkLabel(form_bot, text="Ícone:", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT_PRIMARY).pack(side="left", padx=4)

        self.combo_icone = ctk.CTkComboBox(
            form_bot,
            values=["🎮", "💻", "🚀", "🌐", "🎵", "⚡", "📂", "🛠️"],
            width=70,
            height=30,
            fg_color=COLOR_INPUT_BG,
            text_color=COLOR_TEXT_PRIMARY,
            dropdown_fg_color=COLOR_BG_CARD,
            dropdown_text_color=COLOR_TEXT_PRIMARY
        )
        self.combo_icone.pack(side="left", padx=4)
        self.combo_icone.set("🎮")

        self.btn_foto_atalho = ctk.CTkButton(
            form_bot,
            text="🖼️ Foto Custom",
            width=110,
            height=30,
            fg_color=COLOR_BG_CARD,
            hover_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            command=self.escolher_foto_icone_atalho,
        )
        self.btn_foto_atalho.pack(side="left", padx=4)

        btn_add_atalho = ctk.CTkButton(
            form_bot,
            text="+ Salvar Atalho",
            width=120,
            height=30,
            fg_color="#16A34A",
            hover_color="#15803D",
            text_color="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            command=self.adicionar_atalho_customizado,
        )
        btn_add_atalho.pack(side="right", padx=4)

        self.tabview_hub = ctk.CTkTabview(
            self.tab_hub,
            corner_radius=10,
            fg_color="transparent",
            text_color=COLOR_TEXT_PRIMARY
        )
        self.tabview_hub.pack(fill="both", expand=True, padx=4, pady=0)

        self.cat_custom = self.tabview_hub.add("⭐ Meus Atalhos")
        self.cat_media = self.tabview_hub.add("🎵 Mídia & Streaming")
        self.cat_games = self.tabview_hub.add("🎮 Jogos & Plataformas")
        self.cat_tools = self.tabview_hub.add("⚙️ Sistema & Ferramentas")

        self.scroll_custom = ctk.CTkScrollableFrame(self.cat_custom, fg_color="transparent")
        self.scroll_custom.pack(fill="both", expand=True)

        self.container_custom_items = ctk.CTkFrame(self.scroll_custom, fg_color="transparent")
        self.container_custom_items.pack(fill="x", pady=4)

        self.montar_categoria_estatica(self.cat_media, [
            ("🟢 Spotify", "https://open.spotify.com"),
            ("▶️ YouTube", "https://www.youtube.com"),
            ("🔴 Netflix", "https://www.netflix.com"),
            ("💜 Twitch", "https://www.twitch.tv"),
            ("📦 Prime Video", "https://www.primevideo.com"),
            ("💬 WhatsApp Web", "https://web.whatsapp.com"),
            ("🎵 Soundcloud", "https://soundcloud.com"),
            ("📺 Disney+", "https://www.disneyplus.com"),
        ])

        self.montar_categoria_estatica(self.cat_games, [
            ("🚀 Steam", "steam://open/main"),
            ("🛡️ Epic Games", "epicgames://"),
            ("💬 Discord", "https://discord.com/app"),
            ("🎮 Roblox", "https://www.roblox.com"),
            ("🔴 Roblox App", "roblox://"),
            ("🌐 Poki Jogos", "https://poki.com"),
        ])

        self.montar_categoria_estatica(self.cat_tools, [
            ("📁 Gerenciador de Arquivos", "explorer.exe"),
            ("⚙️ Configurações do Windows", "ms-settings:"),
            ("📝 Bloco de Notas", "notepad.exe"),
            ("🌐 Google Chrome", "https://www.google.com"),
            ("💻 Prompt de Comando", "cmd.exe"),
            ("⚡ Gerenciador de Tarefas", "taskmgr.exe"),
        ])

    def montar_categoria_estatica(self, container, lista_atalhos):
        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=4, pady=4)

        for nome, alvo in lista_atalhos:
            btn = ctk.CTkButton(
                scroll,
                text=nome,
                height=38,
                corner_radius=8,
                fg_color=COLOR_BG_SURFACE,
                hover_color=COLOR_BORDER,
                text_color=COLOR_TEXT_PRIMARY,
                border_color=COLOR_BORDER,
                border_width=1,
                font=("Segoe UI", 11, "bold"),
                anchor="w",
                command=lambda a=alvo: self.abrir_inteligente(a)
            )
            btn.pack(fill="x", pady=3, padx=4)

    def procurar_app_para_atalho(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o Executável",
            filetypes=[("Executáveis e Atalhos", "*.exe *.lnk *.bat *.cmd"), ("Todos os Arquivos", "*.*")]
        )
        if caminho:
            self.entry_url_atalho.delete(0, "end")
            self.entry_url_atalho.insert(0, caminho)
            if not self.entry_nome_atalho.get():
                nome_sugerido = os.path.splitext(os.path.basename(caminho))[0].capitalize()
                self.entry_nome_atalho.insert(0, nome_sugerido)

    def escolher_foto_icone_atalho(self):
        caminho = filedialog.askopenfilename(
            title="Escolha uma imagem para o ícone",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.ico *.bmp")]
        )
        if caminho:
            self.icone_foto_temp = caminho
            self.btn_foto_atalho.configure(text="✅ Foto OK")

    def adicionar_atalho_customizado(self):
        nome = self.entry_nome_atalho.get().strip()
        alvo = self.entry_url_atalho.get().strip()
        icone = self.combo_icone.get()

        if not nome or not alvo:
            return

        perfil = self.controller.perfil_ativo
        if perfil:
            novo_item = {
                "nome": nome,
                "alvo": alvo,
                "icone": icone,
                "foto_icone": self.icone_foto_temp
            }
            perfil["atalhos_custom"].append(novo_item)
            AccountManager.salvar_dados(self.controller.dados_config)

            self.entry_nome_atalho.delete(0, "end")
            self.entry_url_atalho.delete(0, "end")
            self.icone_foto_temp = ""
            self.btn_foto_atalho.configure(text="🖼️ Foto Custom")
            self.atualizar_atalhos_customizados()

    def remover_atalho_customizado(self, index):
        perfil = self.controller.perfil_ativo
        if perfil and 0 <= index < len(perfil["atalhos_custom"]):
            perfil["atalhos_custom"].pop(index)
            AccountManager.salvar_dados(self.controller.dados_config)
            self.atualizar_atalhos_customizados()

    def mover_atalho_posicao(self, index, direcao):
        perfil = self.controller.perfil_ativo
        if not perfil:
            return

        lista = perfil.get("atalhos_custom", [])
        novo_index = index + direcao

        if 0 <= novo_index < len(lista):
            lista[index], lista[novo_index] = lista[novo_index], lista[index]
            AccountManager.salvar_dados(self.controller.dados_config)
            self.atualizar_atalhos_customizados()

    def alterar_modo_layout(self, modo):
        perfil = self.controller.perfil_ativo
        if perfil:
            perfil["modo_layout"] = modo
            AccountManager.salvar_dados(self.controller.dados_config)
            self.atualizar_atalhos_customizados()

    def atualizar_atalhos_customizados(self):
        for widget in self.container_custom_items.winfo_children():
            widget.destroy()

        perfil = self.controller.perfil_ativo
        if not perfil:
            return

        lista = perfil.get("atalhos_custom", [])
        modo_layout = perfil.get("modo_layout", "grid")

        ctrl_frame = ctk.CTkFrame(self.container_custom_items, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=4, pady=(0, 6))

        ctk.CTkLabel(ctrl_frame, text="Modo de Exibição:", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT_SECONDARY).pack(side="left", padx=4)
        
        btn_grid = ctk.CTkButton(
            ctrl_frame, text="🪟 Grade", width=70, height=26,
            fg_color="#2563EB" if modo_layout == "grid" else COLOR_BG_SURFACE,
            text_color="#FFFFFF" if modo_layout == "grid" else COLOR_TEXT_PRIMARY,
            command=lambda: self.alterar_modo_layout("grid")
        )
        btn_grid.pack(side="left", padx=2)

        btn_list = ctk.CTkButton(
            ctrl_frame, text="📋 Lista", width=70, height=26,
            fg_color="#2563EB" if modo_layout == "lista" else COLOR_BG_SURFACE,
            text_color="#FFFFFF" if modo_layout == "lista" else COLOR_TEXT_PRIMARY,
            command=lambda: self.alterar_modo_layout("lista")
        )
        btn_list.pack(side="left", padx=2)

        if not lista:
            lbl_vazio = ctk.CTkLabel(
                self.container_custom_items,
                text="Nenhum atalho personalizado criado ainda.",
                text_color=COLOR_TEXT_SECONDARY,
                font=("Segoe UI", 11)
            )
            lbl_vazio.pack(anchor="w", padx=8, pady=12)
            return

        if modo_layout == "grid":
            grid_frame = ctk.CTkFrame(self.container_custom_items, fg_color="transparent")
            grid_frame.pack(fill="x", expand=True)

            cols = 2
            for idx, item in enumerate(lista):
                r = idx // cols
                c = idx % cols

                card_frame = ctk.CTkFrame(
                    grid_frame,
                    fg_color=COLOR_BG_SURFACE,
                    border_color=COLOR_BORDER,
                    border_width=1,
                    corner_radius=8
                )
                card_frame.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
                grid_frame.grid_columnconfigure(c, weight=1)

                foto_icon = item.get("foto_icone", "")
                img_obj = None
                if foto_icon and os.path.exists(foto_icon):
                    try:
                        pil_img = Image.open(foto_icon)
                        img_obj = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(20, 20))
                    except Exception:
                        img_obj = None

                prefixo_icone = item.get("icone", "🎮")
                texto_exibicao = f"{prefixo_icone} {item['nome']}" if not img_obj else f" {item['nome']}"

                btn_exec = ctk.CTkButton(
                    card_frame,
                    text=texto_exibicao,
                    image=img_obj,
                    compound="left",
                    height=38,
                    fg_color="transparent",
                    hover_color=COLOR_BORDER,
                    text_color=COLOR_TEXT_PRIMARY,
                    font=("Segoe UI", 11, "bold"),
                    anchor="w",
                    command=lambda a=item['alvo']: self.abrir_inteligente(a),
                )
                btn_exec.pack(side="left", fill="both", expand=True, padx=(8, 0))

                btn_del = ctk.CTkButton(
                    card_frame, text="🗑️", width=28, height=26,
                    fg_color="#EF4444", hover_color="#DC2626", text_color="#FFFFFF",
                    command=lambda i=idx: self.remover_atalho_customizado(i)
                )
                btn_del.pack(side="right", padx=4)

                btn_down = ctk.CTkButton(
                    card_frame, text="▼", width=22, height=26,
                    fg_color=COLOR_BG_CARD, text_color=COLOR_TEXT_PRIMARY,
                    command=lambda i=idx: self.mover_atalho_posicao(i, 1)
                )
                btn_down.pack(side="right", padx=2)

                btn_up = ctk.CTkButton(
                    card_frame, text="▲", width=22, height=26,
                    fg_color=COLOR_BG_CARD, text_color=COLOR_TEXT_PRIMARY,
                    command=lambda i=idx: self.mover_atalho_posicao(i, -1)
                )
                btn_up.pack(side="right", padx=2)

        else:
            for idx, item in enumerate(lista):
                card_frame = ctk.CTkFrame(
                    self.container_custom_items,
                    fg_color=COLOR_BG_SURFACE,
                    border_color=COLOR_BORDER,
                    border_width=1,
                    corner_radius=8,
                    height=44
                )
                card_frame.pack(fill="x", pady=3, padx=4)

                foto_icon = item.get("foto_icone", "")
                img_obj = None
                if foto_icon and os.path.exists(foto_icon):
                    try:
                        pil_img = Image.open(foto_icon)
                        img_obj = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(20, 20))
                    except Exception:
                        img_obj = None

                prefixo_icone = item.get("icone", "🎮")
                texto_exibicao = f"{prefixo_icone} {item['nome']}" if not img_obj else f" {item['nome']}"

                btn_exec = ctk.CTkButton(
                    card_frame,
                    text=texto_exibicao,
                    image=img_obj,
                    compound="left",
                    height=38,
                    fg_color="transparent",
                    hover_color=COLOR_BORDER,
                    text_color=COLOR_TEXT_PRIMARY,
                    font=("Segoe UI", 11, "bold"),
                    anchor="w",
                    command=lambda a=item['alvo']: self.abrir_inteligente(a),
                )
                btn_exec.pack(side="left", fill="both", expand=True, padx=(8, 0))

                btn_del = ctk.CTkButton(
                    card_frame, text="🗑️", width=28, height=26,
                    fg_color="#EF4444", hover_color="#DC2626", text_color="#FFFFFF",
                    command=lambda i=idx: self.remover_atalho_customizado(i)
                )
                btn_del.pack(side="right", padx=4)

                btn_down = ctk.CTkButton(
                    card_frame, text="▼", width=22, height=26,
                    fg_color=COLOR_BG_CARD, text_color=COLOR_TEXT_PRIMARY,
                    command=lambda i=idx: self.mover_atalho_posicao(i, 1)
                )
                btn_down.pack(side="right", padx=2)

                btn_up = ctk.CTkButton(
                    card_frame, text="▲", width=22, height=26,
                    fg_color=COLOR_BG_CARD, text_color=COLOR_TEXT_PRIMARY,
                    command=lambda i=idx: self.mover_atalho_posicao(i, -1)
                )
                btn_up.pack(side="right", padx=2)

    def selecionar_executavel_direto(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar Programa para Executar",
            filetypes=[("Executáveis", "*.exe *.lnk *.bat *.cmd"), ("Todos os Arquivos", "*.*")]
        )
        if caminho:
            self.entry_universal.delete(0, "end")
            self.entry_universal.insert(0, caminho)
            self.abrir_inteligente(caminho)

    def executar_busca_universal(self):
        texto = self.entry_universal.get().strip()
        if texto:
            self.abrir_inteligente(texto)
            self.entry_universal.delete(0, "end")

    def abrir_inteligente(self, alvo):
        try:
            if alvo.startswith("http://") or alvo.startswith("https://") or "://" in alvo:
                webbrowser.open(alvo)
            elif os.path.exists(alvo) or alvo.endswith((".exe", ".bat", ".cmd", ".lnk")):
                subprocess.Popen(alvo, shell=True)
            elif alvo.startswith("ms-settings:") or alvo.startswith("explorer.exe") or alvo.startswith("notepad.exe") or alvo.startswith("taskmgr.exe") or alvo.startswith("cmd.exe"):
                subprocess.Popen(alvo, shell=True)
            else:
                query = urllib.parse.quote(alvo)
                webbrowser.open(f"https://www.google.com/search?q={query}")
        except Exception as e:
            print(f"[ERRO] Falha ao abrir alvo '{alvo}': {e}")

    def montar_aba_ia(self):
        self.box_chat = ctk.CTkTextbox(
            self.tab_ia,
            fg_color=COLOR_BG_SURFACE,
            text_color=COLOR_TEXT_PRIMARY,
            font=("Segoe UI", 11),
            corner_radius=8,
            border_color=COLOR_BORDER,
            border_width=1
        )
        self.box_chat.pack(fill="both", expand=True, padx=4, pady=(4, 8))
        self.box_chat.insert("end", "🤖 Olá! Sou o seu Assistente IA do OmniOverlay. Posso te ajudar com dicas de jogos, comandos do Windows ou pesquisas rápidas. O que manda?\n\n")
        self.box_chat.configure(state="disabled")

        frame_envio = ctk.CTkFrame(self.tab_ia, fg_color="transparent")
        frame_envio.pack(fill="x", padx=4, pady=4)

        self.entry_ia = ctk.CTkEntry(
            frame_envio,
            placeholder_text="Digite sua pergunta para a IA...",
            height=38,
            fg_color=COLOR_INPUT_BG,
            text_color=COLOR_TEXT_PRIMARY,
            border_color=COLOR_BORDER
        )
        self.entry_ia.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.entry_ia.bind("<Return>", lambda e: self.enviar_mensagem_ia())

        btn_enviar = ctk.CTkButton(
            frame_envio,
            text="Enviar 🚀",
            width=90,
            height=38,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            command=self.enviar_mensagem_ia
        )
        btn_enviar.pack(side="right")
        self.dynamic_accent_buttons.append(btn_enviar)

    def enviar_mensagem_ia(self):
        pergunta = self.entry_ia.get().strip()
        if not pergunta:
            return

        self.box_chat.configure(state="normal")
        self.box_chat.insert("end", f"👤 Você: {pergunta}\n")
        self.box_chat.configure(state="disabled")
        self.entry_ia.delete(0, "end")

        p_lower = pergunta.lower()
        if "jogo" in p_lower or "jogar" in p_lower:
            resposta = "🤖 OmniAI: Para jogatina, verifique a aba 'Jogos & Plataformas' ou adicione atalhos personalizados direto na Central de Atalhos!"
        elif "computador" in p_lower or "cpu" in p_lower or "ram" in p_lower or "pc" in p_lower:
            resposta = "🤖 OmniAI: Você pode acompanhar o uso de hardware em tempo real diretamente no cabeçalho do overlay ou na aba Configurações."
        elif "olá" in p_lower or "tudo bem" in p_lower:
            resposta = "🤖 OmniAI: Olá! Tudo ótimo por aqui. Pronto para acelerar sua produtividade ou gameplay hoje."
        else:
            respostas_padrao = [
                f"🤖 OmniAI: Analisei sua solicitação sobre '{pergunta}'. Recomendo utilizar a barra de pesquisa universal para buscar conteúdos ou abrir aplicativos instantaneamente.",
                f"🤖 OmniAI: Entendido! Caso precise abrir páginas web rapidamente, você pode fixá-las nos favoritos da Central de Atalhos.",
                f"🤖 OmniAI: Ótima questão sobre '{pergunta}'! O OmniOverlay foi projetado para manter suas ferramentas favoritas acessíveis sem fechar sua tela cheia."
            ]
            resposta = random.choice(respostas_padrao)
        
        self.box_chat.configure(state="normal")
        self.box_chat.insert("end", f"{resposta}\n\n")
        self.box_chat.see("end")
        self.box_chat.configure(state="disabled")

    def montar_aba_player_video(self):
        frame_controles_video = ctk.CTkFrame(self.tab_video, fg_color=COLOR_BG_SURFACE, corner_radius=8, border_color=COLOR_BORDER, border_width=1)
        frame_controles_video.pack(fill="x", padx=4, pady=4)

        btn_abrir_video = ctk.CTkButton(
            frame_controles_video,
            text="📁 Selecionar Vídeo Local",
            height=32,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            command=self.carregar_video_local
        )
        btn_abrir_video.pack(side="left", padx=8, pady=8)
        self.dynamic_accent_buttons.append(btn_abrir_video)

        self.btn_play_pause = ctk.CTkButton(
            frame_controles_video,
            text="▶️ Play",
            width=80,
            height=32,
            fg_color=COLOR_BG_CARD,
            hover_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY,
            command=self.toggle_play_video
        )
        self.btn_play_pause.pack(side="left", padx=4, pady=8)

        self.frame_video_container = ctk.CTkFrame(self.tab_video, fg_color="#000000", corner_radius=8)
        self.frame_video_container.pack(fill="both", expand=True, padx=4, pady=4)

        try:
            self.videoplayer = TkinterVideo(master=self.frame_video_container, scaled=True)
            self.videoplayer.pack(fill="both", expand=True)
        except Exception as e:
            lbl_err = ctk.CTkLabel(
                self.frame_video_container,
                text=f"Erro ao inicializar TkinterVideo: {e}",
                text_color="#EF4444"
            )
            lbl_err.pack(expand=True)
            self.videoplayer = None

    def carregar_video_local(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar Arquivo de Vídeo",
            filetypes=[("Arquivos de Vídeo", "*.mp4 *.avi *.mkv *.mov *.webm"), ("Todos os Arquivos", "*.*")]
        )
        if caminho and self.videoplayer:
            try:
                self.videoplayer.load(caminho)
                self.btn_play_pause.configure(text="⏸️ Pause")
                self.videoplayer.play()
            except Exception as e:
                print(f"[ERRO] Falha ao reproduzir vídeo: {e}")

    def toggle_play_video(self):
        if not self.videoplayer:
            return
        try:
            if self.btn_play_pause.cget("text") == "▶️ Play":
                self.btn_play_pause.configure(text="⏸️ Pause")
                self.videoplayer.play()
            else:
                self.btn_play_pause.configure(text="▶️ Play")
                self.videoplayer.pause()
        except Exception:
            pass

    def montar_aba_config(self):
        scroll_config = ctk.CTkScrollableFrame(self.tab_config, fg_color="transparent")
        scroll_config.pack(fill="both", expand=True, padx=4, pady=4)

        card_fundo = ctk.CTkFrame(scroll_config, fg_color=COLOR_BG_SURFACE, corner_radius=10, border_color=COLOR_BORDER, border_width=1)
        card_fundo.pack(fill="x", pady=6, padx=4, ipady=4)

        ctk.CTkLabel(
            card_fundo,
            text="🖼️ Imagem de Fundo (Background Customizado)",
            font=("Segoe UI", 12, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(anchor="w", padx=12, pady=(8, 2))

        btn_escolher_fundo = ctk.CTkButton(
            card_fundo,
            text="Selecionar Imagem de Fundo",
            height=32,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            command=self.escolher_imagem_fundo_perfil
        )
        btn_escolher_fundo.pack(anchor="w", padx=12, pady=6)
        self.dynamic_accent_buttons.append(btn_escolher_fundo)

        btn_remover_fundo = ctk.CTkButton(
            card_fundo,
            text="Remover Fundo",
            height=32,
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="#FFFFFF",
            command=self.remover_imagem_fundo_perfil
        )
        btn_remover_fundo.pack(anchor="w", padx=12, pady=(0, 8))

        card_cores = ctk.CTkFrame(scroll_config, fg_color=COLOR_BG_SURFACE, corner_radius=10, border_color=COLOR_BORDER, border_width=1)
        card_cores.pack(fill="x", pady=6, padx=4, ipady=4)

        ctk.CTkLabel(
            card_cores,
            text="🎨 Tema de Cor do Perfil",
            font=("Segoe UI", 12, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(anchor="w", padx=12, pady=(8, 4))

        cores_frame = ctk.CTkFrame(card_cores, fg_color="transparent")
        cores_frame.pack(fill="x", padx=12, pady=(0, 8))

        for nome_cor in COLOR_ACCENTS.keys():
            b = ctk.CTkButton(
                cores_frame,
                text=nome_cor.capitalize(),
                width=90,
                height=32,
                fg_color=COLOR_ACCENTS[nome_cor]["primary"],
                hover_color=COLOR_ACCENTS[nome_cor]["hover"],
                text_color="#FFFFFF",
                command=lambda c=nome_cor: self.aplicar_cor_acento(c)
            )
            b.pack(side="left", padx=4)

        card_hw = ctk.CTkFrame(scroll_config, fg_color=COLOR_BG_SURFACE, corner_radius=10, border_color=COLOR_BORDER, border_width=1)
        card_hw.pack(fill="x", pady=6, padx=4, ipady=4)

        ctk.CTkLabel(
            card_hw,
            text="⚡ Monitoramento de Hardware Detalhado",
            font=("Segoe UI", 12, "bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(anchor="w", padx=12, pady=(8, 4))

        row_cpu = ctk.CTkFrame(card_hw, fg_color="transparent")
        row_cpu.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(row_cpu, text="Uso de CPU:", font=("Segoe UI", 11), text_color=COLOR_TEXT_SECONDARY).pack(side="left")
        self.lbl_cpu_valor_detalhado = ctk.CTkLabel(row_cpu, text="0.0%", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_PRIMARY)
        self.lbl_cpu_valor_detalhado.pack(side="right")

        self.bar_cpu_detalhada = ctk.CTkProgressBar(card_hw, height=12)
        self.bar_cpu_detalhada.pack(fill="x", padx=12, pady=(0, 6))
        self.bar_cpu_detalhada.set(0)

        row_ram = ctk.CTkFrame(card_hw, fg_color="transparent")
        row_ram.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(row_ram, text="Uso de Memória RAM:", font=("Segoe UI", 11), text_color=COLOR_TEXT_SECONDARY).pack(side="left")
        self.lbl_ram_valor_detalhado = ctk.CTkLabel(row_ram, text="0.0%", font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_PRIMARY)
        self.lbl_ram_valor_detalhado.pack(side="right")

        self.bar_ram_detalhada = ctk.CTkProgressBar(card_hw, height=12)
        self.bar_ram_detalhada.pack(fill="x", padx=12, pady=(0, 8))
        self.bar_ram_detalhada.set(0)

    def escolher_imagem_fundo_perfil(self):
        caminho = filedialog.askopenfilename(
            title="Escolha a Imagem de Fundo",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")]
        )
        if caminho and self.controller.perfil_ativo:
            self.controller.perfil_ativo["fundo_imagem"] = caminho
            AccountManager.salvar_dados(self.controller.dados_config)
            self.atualizar_fundo_tela(caminho)

    def remover_imagem_fundo_perfil(self):
        if self.controller.perfil_ativo:
            self.controller.perfil_ativo["fundo_imagem"] = ""
            AccountManager.salvar_dados(self.controller.dados_config)
            self.atualizar_fundo_tela("")


class App(ctk.CTk):
    """Classe controladora principal da aplicação OmniOverlay."""

    def __init__(self):
        super().__init__()

        self.dados_config = AccountManager.carregar_dados()
        self.modo_tema_atual = self.dados_config.get("modo_tema", "dark")
        ctk.set_appearance_mode(self.modo_tema_atual)
        ctk.set_default_color_theme("blue")

        self.title("OmniOverlay")
        self.geometry("920x800")
        self.overrideredirect(True)
        self.attributes("-alpha", 0.98)
        self.centralizar_janela(920, 800)

        self.perfil_ativo = None

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.profile_selector = ProfileSelectorFrame(self.container, self)
        self.dashboard = DashboardFrame(self.container, self)

        ultimo_id = self.dados_config.get("ultimo_perfil", "")
        perfil_encontrado = None
        for p in self.dados_config.get("perfis", []):
            if p["id"] == ultimo_id:
                perfil_encontrado = p
                break

        if perfil_encontrado:
            self.entrar_no_perfil(perfil_encontrado)
        else:
            self.abrir_seletor_perfis()

        self.iniciar_listener_teclado()

    def centralizar_janela(self, largura, altura):
        self.update_idletasks()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (largura // 2)
        y = (hs // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def abrir_seletor_perfis(self):
        self.dashboard.pack_forget()
        self.profile_selector.pack(fill="both", expand=True)
        self.profile_selector.atualizar_lista()

    def entrar_no_perfil(self, perfil):
        self.perfil_ativo = perfil
        self.dados_config["ultimo_perfil"] = perfil["id"]
        AccountManager.salvar_dados(self.dados_config)

        self.profile_selector.pack_forget()
        self.dashboard.pack(fill="both", expand=True)
        self.dashboard.carregar_perfil(perfil)

    def alternar_tema_global(self):
        self.modo_tema_atual = "light" if self.modo_tema_atual == "dark" else "dark"
        ctk.set_appearance_mode(self.modo_tema_atual)
        self.dados_config["modo_tema"] = self.modo_tema_atual
        AccountManager.salvar_dados(self.dados_config)

        if hasattr(self.dashboard, 'btn_tema'):
            self.dashboard.btn_tema.configure(text="☀️" if self.modo_tema_atual == "dark" else "🌙")

    def iniciar_listener_teclado(self):
        def acao_atalho_global():
            # Alterna a visibilidade (esconde / mostra o overlay) com segurança na thread principal
            self.after(0, self.dashboard.toggle_visibilidade_overlay)

        try:
            listener = keyboard.GlobalHotKeys({
                '<alt>+z': acao_atalho_global,
                '<alt>+Z': acao_atalho_global
            })
            listener.daemon = True
            listener.start()
        except Exception as e:
            print(f"[AVISO] Não foi possível iniciar o listener de teclado global: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()