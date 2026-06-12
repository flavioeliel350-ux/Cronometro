
import tkinter as tk
import config as cfg
from config import CORES, FONTES, gerar_fontes, carregar_prefs, salvar_prefs, aplicar_tema
from componentes import Separador, BotaoTema
from cronometro import PainelCronometro
from temporizador import PainelTemporizador
from utils import calcular_fator_escala
from sons import som_tema


class Aplicacao(tk.Tk):

    # Largura de referência
    _LARGURA_REF = 480

    def __init__(self):
        super().__init__()
        self._prefs     = carregar_prefs()
        self._tema_nome = self._prefs.get("tema", "claro")

        self._calcular_escala()

        aplicar_tema(self._tema_nome)
        self._atualizar_fontes()

        self.title("Cronômetro e Temporizador")
        self.resizable(True, True)
        self.config(bg=CORES["fundo"])
        self.minsize(360, 500)

        self._aba_ativa = "cronometro"
        self._construir_janela()
        self._registrar_atalhos()

        self._resize_id = None

        self.update_idletasks()
        self._centralizar()

    #Escala e responsividade

    def _calcular_escala(self) -> None:
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self._fator = calcular_fator_escala(sw, sh)
        self._largura = max(360, round(self._LARGURA_REF * self._fator))

    def _atualizar_fontes(self) -> None:
        novas = gerar_fontes(self._fator)
        cfg.FONTES.clear()
        cfg.FONTES.update(novas)

    def _ao_redimensionar(self, evento) -> None:
        if evento.widget is not self:
            return
        if self._resize_id:
            self.after_cancel(self._resize_id)
        self._resize_id = self.after(500, self._reajustar_layout)

    def _reajustar_layout(self) -> None:
        w = self.winfo_width()
        h = self.winfo_screenheight()
        self._fator  = calcular_fator_escala(w * 2, h) 
        self._atualizar_fontes()
        self._propagar_tema()

    #Construção da janela

    def _construir_janela(self) -> None:
        self._frame_externo = tk.Frame(self, bg=CORES["borda"], padx=1, pady=1)
        self._frame_externo.pack(fill="both", expand=True)
        self._frame_interno = tk.Frame(self._frame_externo, bg=CORES["fundo"])
        self._frame_interno.pack(fill="both", expand=True)

        self._criar_barra_titulo(self._frame_interno)
        Separador(self._frame_interno).pack(fill="x")
        self._criar_abas(self._frame_interno)
        Separador(self._frame_interno).pack(fill="x")
        self._criar_paineis(self._frame_interno)
        self._mudar_aba("cronometro")

    def _criar_barra_titulo(self, pai) -> None:
        barra = tk.Frame(pai, bg=CORES["fundo"], pady=10)
        barra.pack(fill="x")
        dots = tk.Frame(barra, bg=CORES["fundo"])
        dots.pack(side="left", padx=14)
        for cor in ("#FF5F57", "#FEBC2E", "#28C840"):
            c = tk.Canvas(dots, width=13, height=13,
                          bg=CORES["fundo"], highlightthickness=0)
            c.create_oval(1, 1, 12, 12, fill=cor, outline="")
            c.pack(side="left", padx=2)
        self._lbl_titulo = tk.Label(
            barra, text="Cronômetro e Temporizador",
            font=FONTES["FONTE_TITULO"],
            fg=CORES["texto"], bg=CORES["fundo"],
        )
        self._lbl_titulo.pack(expand=True)

        # Botão de tema direita
        self._btn_tema = BotaoTema(barra, ao_alternar=self._alternar_tema)
        self._btn_tema.pack(side="right", padx=10)

    def _criar_abas(self, pai) -> None:
        self._barra_abas = tk.Frame(pai, bg=CORES["fundo"])
        self._barra_abas.pack(fill="x")

        self._btns_aba = {}
        abas = [("cronometro", "Cronômetro"), ("temporizador", "Temporizador")]
        for chave, rotulo in abas:
            btn = tk.Label(
                self._barra_abas, text=rotulo,
                font=FONTES["FONTE_ABA"],
                bg=CORES["fundo"], pady=12, padx=24,
                cursor="hand2",
                highlightthickness=2,
                highlightbackground=CORES["fundo"],
                highlightcolor=CORES["foco_borda"],
                takefocus=1,
            )
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, k=chave: self._mudar_aba(k))
            btn.bind("<Return>",   lambda e, k=chave: self._mudar_aba(k))
            btn.bind("<FocusIn>",  lambda e, w=btn: w.config(
                highlightbackground=CORES["foco_borda"]))
            btn.bind("<FocusOut>", lambda e, w=btn: w.config(
                highlightbackground=CORES["fundo"]))
            self._btns_aba[chave] = btn

    def _criar_paineis(self, pai) -> None:
        self._paineis = {
            "cronometro":   PainelCronometro(pai,  width=self._largura),
            "temporizador": PainelTemporizador(pai, width=self._largura),
        }

    #Navegação entre abas

    def _mudar_aba(self, chave: str) -> None:
        self._aba_ativa = chave
        for k, painel in self._paineis.items():
            if k == chave:
                painel.pack(fill="both", expand=True)
            else:
                painel.pack_forget()

        for k, btn in self._btns_aba.items():
            if k == chave:
                btn.config(
                    fg=CORES["aba_ativa"],
                    bg=CORES["fundo"],
                    highlightbackground=CORES["fundo"],
                    font=FONTES["FONTE_ABA"],
                )
            else:
                btn.config(
                    fg=CORES["aba_inativa"],
                    bg=CORES["fundo"],
                    highlightbackground=CORES["fundo"],
                    font=FONTES["FONTE_ABA_IN"],
                )

    #Atalhos de teclado

    def _registrar_atalhos(self) -> None:
        self.bind("<space>",  self._tecla_espaco)
        self.bind("r",        self._tecla_r)
        self.bind("R",        self._tecla_r)
        self.bind("l",        self._tecla_l)
        self.bind("L",        self._tecla_l)
        self.bind("<Escape>", self._tecla_esc)
        self.bind("<Control-t>", lambda e: self._alternar_tema())
        self.bind("<Control-Tab>",       self._proxima_aba)
        self.bind("<Control-Shift-Tab>", self._aba_anterior)

    def _tecla_espaco(self, evento) -> None:
        # Só aciona se o foco estiver na janela
        if evento.widget.winfo_class() in ("Entry", "Text"):
            return
        self._paineis[self._aba_ativa].alternar()

    def _tecla_r(self, evento) -> None:
        if evento.widget.winfo_class() in ("Entry", "Text"):
            return
        self._paineis[self._aba_ativa].resetar()

    def _tecla_l(self, evento) -> None:
        if evento.widget.winfo_class() in ("Entry", "Text"):
            return
        if self._aba_ativa == "cronometro":
            self._paineis["cronometro"].registrar_volta()

    def _tecla_esc(self, _) -> None:
        painel = self._paineis[self._aba_ativa]
        if getattr(painel, "_rodando", False):
            painel._pausar()

    def _proxima_aba(self, _) -> None:
        abas  = list(self._paineis.keys())
        idx   = abas.index(self._aba_ativa)
        self._mudar_aba(abas[(idx + 1) % len(abas)])

    def _aba_anterior(self, _) -> None:
        abas  = list(self._paineis.keys())
        idx   = abas.index(self._aba_ativa)
        self._mudar_aba(abas[(idx - 1) % len(abas)])

    #Tema

    def _alternar_tema(self) -> None:
        som_tema()
        self._tema_nome = "escuro" if self._tema_nome == "claro" else "claro"
        aplicar_tema(self._tema_nome)

        # Salva preferência
        self._prefs["tema"] = self._tema_nome
        salvar_prefs(self._prefs)

        self._propagar_tema()

    def _propagar_tema(self) -> None:
        self.config(bg=CORES["fundo"])
        self._frame_externo.config(bg=CORES["borda"])
        self._frame_interno.config(bg=CORES["fundo"])
        self._barra_abas.config(bg=CORES["fundo"])
        self._lbl_titulo.config(bg=CORES["fundo"], fg=CORES["texto"],
                                font=FONTES["FONTE_TITULO"])
        self._btn_tema.aplicar_tema()
        for w in self._frame_interno.winfo_children():
            try:
                if w.winfo_class() == "Frame":
                    w.config(bg=CORES["fundo"])
            except tk.TclError:
                pass
        self._mudar_aba(self._aba_ativa)

        # Painéis
        for painel in self._paineis.values():
            painel.aplicar_tema()

    def _centralizar(self) -> None:
        self.update_idletasks()
        w  = self.winfo_width()
        h  = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")


if __name__ == "__main__":
    app = Aplicacao()
    app.mainloop()
