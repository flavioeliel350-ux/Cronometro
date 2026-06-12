"""
Autor do modulo: Miguel Artur.
"""

import tkinter as tk
from config import CORES, FONTES



def _anel_foco(widget: tk.Widget, ativo: bool) -> None:
    cor = CORES["foco_borda"] if ativo else CORES["borda"]
    try:
        widget.config(highlightbackground=cor, highlightthickness=2 if ativo else 1)
    except tk.TclError:
        pass



class BotaoArredondado(tk.Frame):

    def __init__(self, pai, texto: str, comando=None,
                 estilo: str = "secundario",
                 largura: int = 120, altura: int = 40,
                 **kwargs):
        kwargs.pop("width", None)
        kwargs.pop("height", None)
        super().__init__(pai, bg=CORES["fundo"], **kwargs)

        self.comando       = comando
        self.estilo        = estilo
        self.texto         = texto
        self.largura       = largura
        self.altura        = altura
        self._desabilitado = False
        self._hover        = False
        self._pressionado  = False

        self._label = tk.Label(
            self,
            text=texto,
            font=FONTES["FONTE_BOTAO"],
            width=largura  // 8,
            height=altura  // 20,
            cursor="hand2",
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
        )
        self._label.pack(fill="both", expand=True)
        self._aplicar_cores()

        for w in (self, self._label):
            w.bind("<Enter>",           self._ao_entrar)
            w.bind("<Leave>",           self._ao_sair)
            w.bind("<ButtonPress-1>",   self._ao_pressionar)
            w.bind("<ButtonRelease-1>", self._ao_soltar)

        self._label.config(takefocus=1)
        self._label.bind("<FocusIn>",  lambda e: _anel_foco(self, True))
        self._label.bind("<FocusOut>", lambda e: _anel_foco(self, False))
        self._label.bind("<Return>",   self._ativar_por_teclado)
        self._label.bind("<space>",    self._ativar_por_teclado)


    def _obter_cores(self):
        if self._desabilitado:
            return "#E0E0E0", "#AAAAAA", "#CCCCCC"

        if self.estilo == "primario":
            fundo = CORES["botao_hover"] if self._hover else CORES["botao_fundo"]
            return fundo, CORES["botao_texto"], fundo

        if self.estilo == "perigo":
            fundo = CORES["vermelho_fundo"]
            if self._hover:
                fundo = CORES.get("btn_secundario_hover", CORES["fundo_terciario"])
            return fundo, CORES["vermelho_texto"], CORES["vermelho_texto"]

        fundo = (CORES.get("btn_secundario_hover", CORES["fundo_terciario"])
                 if self._hover else CORES["fundo_secundario"])
        return fundo, CORES["texto"], CORES["borda"]

    def _aplicar_cores(self) -> None:
        fundo, fg, borda = self._obter_cores()
        self.config(bg=fundo, highlightbackground=borda, highlightthickness=1)
        self._label.config(bg=fundo, fg=fg,
                           cursor="arrow" if self._desabilitado else "hand2")

    def aplicar_tema(self) -> None:
        self.config(bg=CORES["fundo"])
        self._aplicar_cores()


    def atualizar_texto(self, novo_texto: str) -> None:
        self.texto = novo_texto
        self._label.config(text=novo_texto)

    def desabilitar(self, valor: bool) -> None:
        self._desabilitado = valor
        self._hover = False
        self._aplicar_cores()


    def _ao_entrar(self, _):
        if not self._desabilitado:
            self._hover = True
            self._aplicar_cores()

    def _ao_sair(self, _):
        self._hover = False
        self._pressionado = False
        self._aplicar_cores()

    def _ao_pressionar(self, _):
        if not self._desabilitado:
            self._pressionado = True
            self._aplicar_cores()

    def _ao_soltar(self, _):
        if not self._desabilitado and self._pressionado:
            self._pressionado = False
            self._aplicar_cores()
            if self.comando:
                self.comando()

    def _ativar_por_teclado(self, _):
        if not self._desabilitado and self.comando:
            self.comando()



class BadgeStatus(tk.Frame):

    ESTADOS = {
        "parado":     ("fundo_secundario", "texto_suave",    "texto_suave",    "Parado"),
        "rodando":    ("verde_fundo",      "verde_texto",    "verde_ponto",    "Rodando"),
        "pausado":    ("amarelo_fundo",    "amarelo_texto",  "amarelo_ponto",  "Pausado"),
        "concluido":  ("vermelho_fundo",   "vermelho_texto", "vermelho_ponto", "Concluído!"),
        "aguardando": ("fundo_secundario", "texto_suave",    "texto_suave",    "Aguardando"),
    }

    def __init__(self, pai, **kwargs):
        super().__init__(pai, bg=CORES["fundo"], **kwargs)
        self._canvas_ponto = tk.Canvas(self, width=10, height=10,
                                       bg=CORES["fundo"], highlightthickness=0)
        self._canvas_ponto.pack(side="left", padx=(8, 4), pady=5)
        self._rotulo = tk.Label(self, font=FONTES["FONTE_STATUS"], bg=CORES["fundo"])
        self._rotulo.pack(side="left", padx=(0, 10), pady=5)
        self._pulso_id     = None
        self._pulso_ativo  = True
        self._estado_atual = "parado"
        self.definir_estado("parado")

    def definir_estado(self, estado: str) -> None:
        self._parar_pulso()
        self._estado_atual = estado
        chave_fundo, chave_fg, chave_ponto, rotulo = self.ESTADOS.get(
            estado, self.ESTADOS["parado"]
        )
        fundo      = CORES[chave_fundo]
        fg         = CORES[chave_fg]
        cor_ponto  = CORES[chave_ponto]

        self.config(bg=fundo, relief="flat",
                    highlightbackground=CORES["borda"],
                    highlightthickness=1)
        self._canvas_ponto.config(bg=fundo)
        self._rotulo.config(bg=fundo, fg=fg, text=rotulo)
        self._cor_ponto    = cor_ponto
        self._fundo_ponto  = fundo
        self._desenhar_ponto(True)
        if estado == "rodando":
            self._iniciar_pulso()

    def aplicar_tema(self) -> None:
        self.config(bg=CORES["fundo"])
        self._canvas_ponto.config(bg=CORES["fundo"])
        self._rotulo.config(bg=CORES["fundo"])
        self.definir_estado(self._estado_atual)

    def _desenhar_ponto(self, visivel: bool) -> None:
        self._canvas_ponto.delete("all")
        cor = self._cor_ponto if visivel else self._fundo_ponto
        self._canvas_ponto.create_oval(1, 1, 9, 9, fill=cor, outline="")

    def _iniciar_pulso(self) -> None:
        self._pulso()

    def _pulso(self) -> None:
        self._pulso_ativo = not self._pulso_ativo
        self._desenhar_ponto(self._pulso_ativo)
        self._pulso_id = self.after(600, self._pulso)

    def _parar_pulso(self) -> None:
        if self._pulso_id:
            self.after_cancel(self._pulso_id)
            self._pulso_id = None



class BarraProgresso(tk.Canvas):

    def __init__(self, pai, **kwargs):
        super().__init__(pai, height=4,
                         bg=CORES["fundo_secundario"],
                         highlightthickness=0, **kwargs)
        self._percentual = 1.0
        self.bind("<Configure>", lambda e: self._desenhar())

    def definir_percentual(self, pct: float) -> None:
        self._percentual = max(0.0, min(1.0, pct))
        self._desenhar()

    def aplicar_tema(self) -> None:
        self.config(bg=CORES["fundo_secundario"])
        self._desenhar()

    def _desenhar(self) -> None:
        self.delete("all")
        largura = self.winfo_width()
        if largura < 2:
            return
        cor   = CORES["vermelho_ponto"] if self._percentual < 0.2 else CORES["verde_ponto"]
        barra = int(largura * self._percentual)
        if barra > 0:
            self.create_rectangle(0, 0, barra, 4, fill=cor, outline="")



class Separador(tk.Frame):

    def __init__(self, pai, **kwargs):
        super().__init__(pai, height=1, bg=CORES["borda"], **kwargs)

    def aplicar_tema(self) -> None:
        self.config(bg=CORES["borda"])



class BotaoTema(tk.Label):

    def __init__(self, pai, ao_alternar, **kwargs):
        super().__init__(pai, cursor="hand2", relief="flat", bd=0,
                         padx=6, pady=4, **kwargs)
        self._ao_alternar = ao_alternar
        self._hover = False
        self._atualizar_icone()

        self.bind("<Button-1>",   self._clicar)
        self.bind("<Enter>",      lambda e: self._set_hover(True))
        self.bind("<Leave>",      lambda e: self._set_hover(False))
        self.bind("<FocusIn>",    lambda e: _anel_foco(self, True))
        self.bind("<FocusOut>",   lambda e: _anel_foco(self, False))
        self.bind("<Return>",     self._clicar)
        self.config(takefocus=1)

    def _atualizar_icone(self) -> None:

        tema_atual = _tema_atual()
        icone = "☾" if tema_atual == "claro" else "☀"
        titulo = "Modo escuro" if tema_atual == "claro" else "Modo claro"
        self.config(text=icone, font=FONTES["FONTE_LABEL"])
        try:
            self.config(tooltip=titulo)         
        except tk.TclError:                     
            pass

    def aplicar_tema(self) -> None:
        self._set_hover(False)
        self._atualizar_icone()

    def _set_hover(self, estado: bool) -> None:
        self._hover = estado
        bg = CORES["fundo_terciario"] if estado else CORES["fundo"]
        self.config(bg=bg, fg=CORES["texto"])

    def _clicar(self, _=None) -> None:
        self._ao_alternar()
        self._atualizar_icone()


def _tema_atual() -> str:
    from config import TEMAS
    return "escuro" if CORES.get("fundo") == TEMAS["escuro"]["fundo"] else "claro"
