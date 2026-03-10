# -*- coding: utf-8 -*-
import os
import sys
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
import webbrowser

from PIL import Image, ImageTk
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

APP_NAME = "Arte Preco Pro"

# =========================
# TEMA (VERDE OLIVA CLARO + FONTES MAIORES)
# =========================
# Fundo geral (tudo)
BG = "#DCE6D5"            # verde oliva bem claro (fundo do app inteiro)
# Cartões / seções (sem branco puro)
CARD = "#EEF3EA"          # um tom mais claro, mas ainda “oliva”
# Sidebar
ACCENT = "#6E8B57"        # oliva médio
ACCENT_DARK = "#4E6B3E"   # oliva escuro
# Textos
TEXT = "#1F1F1F"
MUTED = "#4F5A4A"
BTN_TEXT = "#FFFFFF"

# Fontes (aumentadas)
FONT_BASE = ("Arial", 12)
FONT_LABEL = ("Arial", 12)
FONT_BOLD = ("Arial", 12, "bold")
FONT_TITLE = ("Arial", 18, "bold")
FONT_SIDETITLE = ("Arial", 18, "bold")
FONT_BTN = ("Arial", 12, "bold")
FONT_RESULT = ("Arial", 22, "bold")

# ===== LICENÇA (CHAVE ÚNICA) =====
MASTER_LICENSE = "APP-ARTE-2026"


def app_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = app_base_dir()
CONFIG_DIR = os.path.join(BASE_DIR, "config")
PDF_DIR = os.path.join(BASE_DIR, "pdf")
LICENSE_FILE = os.path.join(CONFIG_DIR, "license.key")
LOGO_FILE = os.path.join(CONFIG_DIR, "logo.png")
DATA_FILE = os.path.join(CONFIG_DIR, "data.json")

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)


def to_float_br(value: str) -> float:
    s = (value or "").strip()
    if not s:
        return 0.0
    s = s.replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    return float(s)


def money_br(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def file_url(path: str) -> str:
    abs_path = os.path.abspath(path)
    return "file:///" + abs_path.replace("\\", "/")


# ====== Persistência (data.json) ======
def load_data() -> dict:
    default = {"next_orc": 1, "history": []}
    if not os.path.exists(DATA_FILE):
        return default
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("next_orc", 1)
        data.setdefault("history", [])
        return data
    except:
        return default


def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def format_orc(n: int) -> str:
    return f"ORC-{n:04d}"


# ===== LICENÇA =====
def license_is_valid() -> bool:
    if not os.path.exists(LICENSE_FILE):
        return False
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            saved = f.read().strip().upper()
        return saved == MASTER_LICENSE
    except:
        return False


def save_license(key: str):
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        f.write(key.strip().upper())


class LicenseWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Ativacao - Arte Preco Pro")
        self.geometry("560x250")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text="Ativacao do Sistema", bg=BG, fg=TEXT, font=("Arial", 16, "bold")).pack(pady=(16, 8))

        tk.Label(self, text="Digite sua chave de ativacao:", bg=BG, fg=TEXT, font=FONT_LABEL).pack(pady=(8, 4))
        self.key_entry = tk.Entry(self, width=36, font=("Consolas", 13))
        self.key_entry.pack(pady=8)
        self.key_entry.focus()

        btns = tk.Frame(self, bg=BG)
        btns.pack(pady=10)

        tk.Button(
            btns, text="Ativar", bg=ACCENT, fg=BTN_TEXT, relief="flat",
            padx=18, pady=10, command=self.activate, font=FONT_BTN
        ).pack(side="left", padx=10)

        tk.Button(
            btns, text="Sair", bg="#666666", fg="white", relief="flat",
            padx=18, pady=10, command=self.on_exit, font=FONT_BTN
        ).pack(side="left", padx=10)

        tk.Label(self, text="Exemplo: APP-ARTE-2026", bg=BG, fg=MUTED, font=FONT_LABEL).pack(pady=(8, 0))

    def activate(self):
        key = (self.key_entry.get() or "").strip().upper()
        if not key:
            messagebox.showerror("Erro", "Digite a chave.")
            return
        if key != MASTER_LICENSE:
            messagebox.showerror("Chave invalida", "A chave digitada nao confere.")
            return
        save_license(key)
        messagebox.showinfo("Ativado", "Ativacao concluida! O programa foi liberado.")
        self.destroy()

    def on_exit(self):
        self.master.destroy()


# ===== ScrollFrame (para não cortar observações) =====
class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg_color=BG):
        super().__init__(parent, bg=bg_color)

        self.canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)
        self.vscroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        self.vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=bg_color)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Scroll mouse (Windows)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_frame_configure(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# ===== Histórico =====
class HistoryWindow(tk.Toplevel):
    def __init__(self, master, data: dict):
        super().__init__(master)
        self.title("Historico de Orcamentos")
        self.geometry("860x480")
        self.configure(bg=BG)
        self.data = data

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=12, pady=10)

        tk.Label(top, text="Historico de Orcamentos", bg=BG, fg=TEXT, font=("Arial", 16, "bold")).pack(side="left")

        tk.Button(
            top, text="Abrir pasta PDF", bg=ACCENT, fg=BTN_TEXT, relief="flat",
            command=self.open_pdf_folder, font=FONT_BTN, padx=14, pady=8
        ).pack(side="right", padx=6)

        tk.Button(
            top, text="Limpar historico", bg="#666666", fg="white", relief="flat",
            command=self.clear_history, font=FONT_BTN, padx=14, pady=8
        ).pack(side="right", padx=6)

        mid = tk.Frame(self, bg=BG)
        mid.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.listbox = tk.Listbox(mid, font=("Consolas", 11))
        scroll = tk.Scrollbar(mid, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.listbox.bind("<Double-Button-1>", self.open_selected)

        self.refresh()
        tk.Label(self, text="Dica: dois cliques para abrir o PDF.", bg=BG, fg=MUTED, font=FONT_LABEL).pack(pady=(0, 10))

    def refresh(self):
        self.listbox.delete(0, "end")
        hist = list(self.data.get("history", []))
        hist.reverse()
        for item in hist:
            line = f"{item.get('orc',''):<9} | {item.get('date',''):<16} | {item.get('product','')[:28]:<28} | {item.get('final','')}"
            self.listbox.insert("end", line)
        self._hist_view = hist

    def open_selected(self, _event=None):
        idx = self.listbox.curselection()
        if not idx:
            return
        item = self._hist_view[idx[0]]
        path = item.get("pdf_path")
        if not path or not os.path.exists(path):
            messagebox.showerror("Erro", "PDF nao encontrado.")
            return
        webbrowser.open_new_tab(file_url(path))

    def open_pdf_folder(self):
        try:
            os.startfile(PDF_DIR)
        except:
            messagebox.showerror("Erro", "Nao consegui abrir a pasta PDF.")

    def clear_history(self):
        if not messagebox.askyesno("Confirmar", "Deseja apagar TODO o historico?"):
            return
        self.data["history"] = []
        save_data(self.data)
        self.refresh()


# ===== App =====
class ArtePrecoPro(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1080x800")
        self.minsize(900, 620)
        self.configure(bg=BG)

        # Fonte padrão do app inteiro (aumentada)
        self.option_add("*Font", FONT_BASE)

        # Se não estiver ativado, vai pedir
        if not license_is_valid():
            LicenseWindow(self)

        self.data = load_data()
        self.entries = {}
        self.logo_path = LOGO_FILE
        self.tk_img = None
        self.last_calc = None

        self._build_layout()
        self._load_logo_auto()

    def _build_layout(self):
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(container, bg=ACCENT_DARK, width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Arte Preco Pro", bg=ACCENT_DARK, fg="white",
                 font=FONT_SIDETITLE).pack(pady=(18, 6))
        tk.Label(sidebar, text="Sistema de Precificacao", bg=ACCENT_DARK, fg="#E6EFE1",
                 font=FONT_LABEL).pack(pady=(0, 14))

        self.logo_label = tk.Label(sidebar, bg=ACCENT_DARK)
        self.logo_label.pack(pady=12)

        tk.Button(sidebar, text="Selecionar Logo", command=self.select_logo,
                  bg=ACCENT, fg=BTN_TEXT, relief="flat", padx=12, pady=12,
                  font=FONT_BTN).pack(pady=8, padx=16, fill="x")

        tk.Button(sidebar, text="Calcular", command=self.calculate_price,
                  bg=ACCENT, fg=BTN_TEXT, relief="flat", padx=12, pady=12,
                  font=FONT_BTN).pack(pady=8, padx=16, fill="x")

        tk.Button(sidebar, text="Gerar PDF e Abrir", command=self.generate_pdf,
                  bg=ACCENT, fg=BTN_TEXT, relief="flat", padx=12, pady=12,
                  font=FONT_BTN).pack(pady=8, padx=16, fill="x")

        tk.Button(sidebar, text="Historico", command=self.open_history,
                  bg="#666666", fg="white", relief="flat", padx=12, pady=12,
                  font=FONT_BTN).pack(pady=8, padx=16, fill="x")

        self.result_sidebar = tk.Label(
            sidebar, text="", bg=ACCENT_DARK, fg="white",
            font=("Arial", 14, "bold"), wraplength=250, justify="left"
        )
        self.result_sidebar.pack(pady=18, padx=16, anchor="w")

        # Conteúdo com SCROLL
        sf = ScrollFrame(container, bg_color=BG)
        sf.pack(side="left", fill="both", expand=True)
        content = sf.inner

        # Dados empresa
        biz = tk.LabelFrame(content, text="Dados da Empresa (vai no PDF)", bg=CARD, fg=TEXT, padx=12, pady=12, font=FONT_BOLD)
        biz.pack(fill="x", pady=12, padx=18)
        self._field(biz, "Nome da Empresa", "empresa_nome", 62)
        self._field(biz, "Telefone / WhatsApp", "empresa_tel", 34)

        # Precificação
        form = tk.LabelFrame(content, text="Precificacao", bg=CARD, fg=TEXT, padx=12, pady=12, font=FONT_BOLD)
        form.pack(fill="x", pady=12, padx=18)
        self._field(form, "Nome do Produto", "produto", 62)
        self._field(form, "Custo do Material (R$)", "material", 26)
        self._field(form, "Horas Trabalhadas", "horas", 26)
        self._field(form, "Valor da Hora (R$)", "valor_hora", 26)
        self._field(form, "Despesas Extras (R$)", "despesas", 26)
        self._field(form, "Margem de Lucro (%)", "margem", 26)

        # Orçamento
        extra = tk.LabelFrame(content, text="Orcamento", bg=CARD, fg=TEXT, padx=12, pady=12, font=FONT_BOLD)
        extra.pack(fill="x", pady=12, padx=18)

        row = tk.Frame(extra, bg=CARD)
        row.pack(pady=8, padx=10, anchor="w")
        tk.Label(row, text="Validade (dias):", bg=CARD, fg=TEXT, font=FONT_LABEL).pack(side="left")
        self.entries["validade_dias"] = tk.Entry(row, width=10, font=("Arial", 12))
        self.entries["validade_dias"].insert(0, "7")
        self.entries["validade_dias"].pack(side="left", padx=10)

        tk.Label(extra, text="Observacoes (vai no PDF):", bg=CARD, fg=TEXT, font=FONT_LABEL).pack(anchor="w", padx=10)

        self.obs_text = tk.Text(extra, height=7, font=("Arial", 12), bg="#FFFFFF", fg=TEXT)
        self.obs_text.pack(padx=10, pady=8, fill="x")

        self.result_label = tk.Label(content, text="", font=FONT_RESULT, bg=BG, fg=ACCENT_DARK)
        self.result_label.pack(pady=14)

        tk.Label(content, text="", bg=BG).pack(pady=30)

    def _field(self, parent, label, key, width):
        row = tk.Frame(parent, bg=CARD)
        row.pack(pady=8, fill="x")
        tk.Label(row, text=label, bg=CARD, fg=TEXT, font=FONT_LABEL).pack()
        e = tk.Entry(row, width=width, font=("Arial", 12), bg="#FFFFFF", fg=TEXT)
        e.pack(pady=2)
        self.entries[key] = e

    def _load_logo_auto(self):
        if os.path.exists(self.logo_path):
            self._display_logo()

    def select_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Imagem", "*.png *.bmp")])
        if not path:
            return
        try:
            shutil.copy2(path, self.logo_path)
            self._display_logo()
            messagebox.showinfo("OK", "Logo salva! Da proxima vez abrira automaticamente.")
        except Exception as e:
            messagebox.showerror("Erro", f"Nao consegui salvar a logo.\n\n{e}")

    def _display_logo(self):
        img = Image.open(self.logo_path)
        img = img.resize((200, 200))
        self.tk_img = ImageTk.PhotoImage(img)
        self.logo_label.config(image=self.tk_img)

    def open_history(self):
        self.data = load_data()
        HistoryWindow(self, self.data)

    def calculate_price(self):
        try:
            produto = (self.entries["produto"].get() or "").strip()
            material = to_float_br(self.entries["material"].get())
            horas = to_float_br(self.entries["horas"].get())
            valor_hora = to_float_br(self.entries["valor_hora"].get())
            despesas = to_float_br(self.entries["despesas"].get())
            margem = to_float_br(self.entries["margem"].get())
            validade_dias = int((self.entries["validade_dias"].get() or "7").strip())
        except:
            messagebox.showerror("Erro", "Verifique os valores.")
            return

        if not produto:
            messagebox.showwarning("Atencao", "Informe o nome do produto.")
            return

        custo_mao_obra = horas * valor_hora
        custo_total = material + custo_mao_obra + despesas
        preco_final = custo_total + (custo_total * margem / 100.0)

        data_emissao = datetime.now()
        data_validade = data_emissao + timedelta(days=max(0, validade_dias))

        self.last_calc = {
            "produto": produto,
            "material": material,
            "horas": horas,
            "valor_hora": valor_hora,
            "custo_mao_obra": custo_mao_obra,
            "despesas": despesas,
            "custo_total": custo_total,
            "preco_final": preco_final,
            "data_emissao": data_emissao.strftime("%d/%m/%Y %H:%M"),
            "data_validade": data_validade.strftime("%d/%m/%Y"),
            "validade_dias": validade_dias,
            "obs": self.obs_text.get("1.0", "end").strip(),
            "empresa_nome": (self.entries["empresa_nome"].get() or "").strip(),
            "empresa_tel": (self.entries["empresa_tel"].get() or "").strip(),
        }

        msg = f"Preco Final: {money_br(preco_final)}"
        self.result_label.config(text=msg)

        try:
            self.result_sidebar.config(text=msg)
        except:
            pass

    def generate_pdf(self):
        if not self.last_calc:
            messagebox.showwarning("Atencao", "Clique em Calcular antes de gerar o PDF.")
            return

        self.data = load_data()
        orc_num = int(self.data.get("next_orc", 1))
        orc_code = format_orc(orc_num)

        c = self.last_calc

        safe_prod = "".join(ch for ch in c["produto"] if ch.isalnum() or ch in (" ", "_", "-")).strip().replace(" ", "_")
        safe_prod = safe_prod or "produto"

        file_name = f"{orc_code}_{safe_prod}.pdf"
        file_path = os.path.join(PDF_DIR, file_name)

        doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)

        title = ParagraphStyle(name="title", fontSize=18, leading=22)
        h2 = ParagraphStyle(name="h2", fontSize=13, leading=18)
        normal = ParagraphStyle(name="normal", fontSize=11, leading=15)

        elements = []
        elements.append(Paragraph(f"ORCAMENTO {orc_code}", title))
        elements.append(Paragraph(f"Emissao: {c['data_emissao']}", normal))
        elements.append(Paragraph(f"Valido ate: {c['data_validade']} ({c['validade_dias']} dias)", normal))
        elements.append(Spacer(1, 12))

        if os.path.exists(self.logo_path):
            try:
                elements.append(RLImage(self.logo_path, width=1.6 * inch, height=1.6 * inch))
                elements.append(Spacer(1, 10))
            except:
                pass

        if c["empresa_nome"] or c["empresa_tel"]:
            elements.append(Paragraph("Dados da Empresa", h2))
            if c["empresa_nome"]:
                elements.append(Paragraph(f"<b>Empresa:</b> {c['empresa_nome']}", normal))
            if c["empresa_tel"]:
                elements.append(Paragraph(f"<b>Contato:</b> {c['empresa_tel']}", normal))
            elements.append(Spacer(1, 10))

        elements.append(Paragraph("Produto", h2))
        elements.append(Paragraph(f"<b>Nome:</b> {c['produto']}", normal))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("Resumo de Custos", h2))
        elements.append(Paragraph(f"Material: {money_br(c['material'])}", normal))
        elements.append(Paragraph(
            f"Mao de obra: {c['horas']} h x {money_br(c['valor_hora'])} = {money_br(c['custo_mao_obra'])}",
            normal
        ))
        elements.append(Paragraph(f"Despesas extras: {money_br(c['despesas'])}", normal))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"<b>Custo total:</b> {money_br(c['custo_total'])}", normal))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph(f"<b>PRECO FINAL SUGERIDO:</b> {money_br(c['preco_final'])}", title))
        elements.append(Spacer(1, 12))

        if c["obs"]:
            elements.append(Paragraph("Observacoes", h2))
            for line in c["obs"].splitlines():
                elements.append(Paragraph(line, normal))

        doc.build(elements)

        hist_item = {
            "orc": orc_code,
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "product": c["produto"],
            "final": money_br(c["preco_final"]),
            "pdf_path": file_path,
        }
        self.data.setdefault("history", []).append(hist_item)
        self.data["next_orc"] = orc_num + 1
        save_data(self.data)

        messagebox.showinfo("Sucesso", f"PDF gerado:\n{file_name}")
        webbrowser.open_new_tab(file_url(file_path))

