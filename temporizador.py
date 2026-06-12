"""
Autor do módulo: Flávio Eliel P. Lima
"""

import tkinter as tk
from config import CORES, FONTES
from componentes import BotaoArredondado, BadgeStatus, BarraProgresso, Separador
from utils import tocar_beep
from sons import som_iniciar, som_pausar, som_click


class PainelTemporizador(tk.Frame):

    PRESETS = [
        ("1 hora",  1, 0,  0),
        ("30 min",  0, 30, 0),
        ("10 min",  0, 10, 0),
        ("5 min",   0, 5,  0),
        ("1 min",   0, 1,  0),
    ]

    def __init__(self, pai, **kwargs):
        super().__init__(pai, bg=CORES["fundo"], **kwargs)
        self._restante = 0
        self._total    = 0
        self._rodando  = False
        self._tick_id  = None
        self._construir_interface()
        self._sincronizar_display()


    def _construir_interface(self) -> None:
        self._criar_entradas()
        self._criar_presets()
        Separador(self).pack(fill="x", pady=(20, 0))
        self._criar_display()
        self._criar_barra_progresso()
        self._criar_botoes()
        self._criar_rodape()

    def _criar_entradas(self) -> None:
        frame = tk.Frame(self, bg=CORES["fundo"])
        frame.pack(pady=(24, 0))

        tk.Label(
            frame, text="Defina o tempo",
            font=FONTES["FONTE_PEQUENA"], fg=CORES["texto_suave"],
            bg=CORES["fundo"],
        ).pack(pady=(0, 10))

        linha = tk.Frame(frame, bg=CORES["fundo"])
        linha.pack()

        self._var_h = tk.StringVar(value="0")
        self._var_m = tk.StringVar(value="5")
        self._var_s = tk.StringVar(value="0")

        self._inp_h = self._criar_campo(linha, self._var_h, "horas", 99, 0)
        self._sep_entrada(linha, col=1)
        self._inp_m = self._criar_campo(linha, self._var_m, "min",   59, 2)
        self._sep_entrada(linha, col=3)
        self._inp_s = self._criar_campo(linha, self._var_s, "seg",   59, 4)

    def _sep_entrada(self, pai, col: int) -> None:
        tk.Label(
            pai, text=":",
            font=("Courier New", FONTES["FONTE_MS"][1]),
            fg=CORES["texto_suave"], bg=CORES["fundo"],
        ).grid(row=0, column=col, padx=4, pady=(0, 16))

    def _criar_campo(self, pai, var, rotulo: str, max_val: int, col: int):
        frame = tk.Frame(pai, bg=CORES["fundo"])
        frame.grid(row=0, column=col, padx=4)

        validar = pai.register(lambda v: self._validar(v, max_val))
        entrada = tk.Entry(
            frame, textvariable=var, width=3,
            font=("Courier New", FONTES["FONTE_DISPLAY"][1] // 2),
            justify="center", relief="flat", bd=0,
            bg=CORES["fundo_secundario"],
            fg=CORES["texto"],
            insertbackground=CORES["texto"],
            validate="key",
            validatecommand=(validar, "%P"),
            highlightthickness=2,
            highlightbackground=CORES["borda"],
            highlightcolor=CORES["foco_borda"],
        )
        entrada.pack(ipady=10, ipadx=4)
        entrada.bind("<FocusOut>", lambda e, v=var: self._ao_perder_foco(v))
        entrada.bind("<Return>",   lambda e: self._sincronizar_display())
        entrada.bind("<Tab>",      lambda e: None)  

        tk.Label(
            frame, text=rotulo,
            font=FONTES["FONTE_MINIMA"], fg=CORES["texto_dica"],
            bg=CORES["fundo"],
        ).pack()
        return entrada

    def _criar_presets(self) -> None:
        frame = tk.Frame(self, bg=CORES["fundo"])
        frame.pack(pady=(12, 0))
        self._btns_preset = []

        for rotulo, h, m, s in self.PRESETS:
            btn = tk.Label(
                frame, text=rotulo,
                font=FONTES["FONTE_MINIMA"],
                fg=CORES["texto_suave"], bg=CORES["fundo_secundario"],
                padx=10, pady=4, cursor="hand2", relief="flat", bd=0,
                highlightthickness=2,
                highlightbackground=CORES["fundo_secundario"],
                highlightcolor=CORES["foco_borda"],
                takefocus=1,
            )
            btn.pack(side="left", padx=3)
            btn.bind("<Button-1>",
                     lambda e, hh=h, mm=m, ss=s: self._aplicar_preset(hh, mm, ss))
            btn.bind("<Return>",
                     lambda e, hh=h, mm=m, ss=s: self._aplicar_preset(hh, mm, ss))
            btn.bind("<Enter>",  lambda e, w=btn: self._hover_preset(w, True))
            btn.bind("<Leave>",  lambda e, w=btn: self._hover_preset(w, False))
            btn.bind("<FocusIn>",  lambda e, w=btn: w.config(
                highlightbackground=CORES["foco_borda"]))
            btn.bind("<FocusOut>", lambda e, w=btn: w.config(
                highlightbackground=CORES["fundo_secundario"]))
            self._btns_preset.append(btn)

    def _hover_preset(self, widget, ativo: bool) -> None:
        bg = CORES["fundo_terciario"] if ativo else CORES["fundo_secundario"]
        widget.config(bg=bg)

    def _criar_display(self) -> None:
        display = tk.Frame(self, bg=CORES["fundo"])
        display.pack(pady=(20, 0))

        self._lbl_tempo = tk.Label(
            display, text="05:00",
            font=FONTES["FONTE_TIMER"],
            fg=CORES["texto"], bg=CORES["fundo"],
        )
        self._lbl_tempo.pack()

        self._status = BadgeStatus(display)
        self._status.pack(pady=(8, 0))
        self._status.definir_estado("aguardando")

    def _criar_barra_progresso(self) -> None:
        frame = tk.Frame(self, bg=CORES["fundo"])
        frame.pack(fill="x", padx=32, pady=(14, 0))
        self._progresso = BarraProgresso(frame)
        self._progresso.pack(fill="x")

    def _criar_botoes(self) -> None:
        linha = tk.Frame(self, bg=CORES["fundo"])
        linha.pack(fill="x", padx=32, pady=(16, 0))
        linha.columnconfigure(0, weight=1)
        linha.columnconfigure(1, weight=1)

        self._btn_resetar = BotaoArredondado(
            linha, "↺  Resetar",
            comando=self.resetar, largura=190, altura=42,
        )
        self._btn_resetar.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self._btn_resetar.desabilitar(True)

        self._btn_iniciar = BotaoArredondado(
            linha, "▶  Iniciar",
            comando=self.alternar, estilo="primario", largura=190, altura=42,
        )
        self._btn_iniciar.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _criar_rodape(self) -> None:
        Separador(self).pack(fill="x", pady=(20, 0))
        tk.Label(
            self, text="Espaço: Iniciar/Pausar  ·  R: Resetar",
            font=FONTES["FONTE_MINIMA"], fg=CORES["texto_dica"],
            bg=CORES["fundo"],
        ).pack(pady=8)


    @staticmethod
    def _validar(valor: str, max_val: int) -> bool:
        if valor == "":
            return True
        try:
            return 0 <= int(valor) <= max_val
        except ValueError:
            return False

    def _ao_perder_foco(self, var: tk.StringVar) -> None:
        try:
            var.set(str(max(0, int(var.get()))))
        except ValueError:
            var.set("0")
        self._sincronizar_display()

    def _sincronizar_display(self) -> None:
        if not self._rodando and self._restante == 0:
            self._total = self._obter_segundos()
            self._renderizar(self._total)
            self._progresso.definir_percentual(1.0)

    def _obter_segundos(self) -> int:
        h = int(self._var_h.get() or 0)
        m = int(self._var_m.get() or 0)
        s = int(self._var_s.get() or 0)
        return h * 3600 + m * 60 + s

    def _aplicar_preset(self, h: int, m: int, s: int) -> None:
        if self._rodando:
            return
        self._var_h.set(str(h))
        self._var_m.set(str(m))
        self._var_s.set(str(s))
        self._restante = 0
        self._sincronizar_display()


    def alternar(self) -> None:
        if self._rodando:
            self._pausar()
        else:
            self._iniciar()

    def _iniciar(self) -> None:
        som_iniciar()
        if self._restante == 0:
            self._total = self._obter_segundos()
            if self._total == 0:
                return
            self._restante = self._total
        self._rodando = True
        self._habilitar_entradas(False)
        self._btn_resetar.desabilitar(False)
        self._btn_iniciar.atualizar_texto("⏸  Pausar")
        self._status.definir_estado("rodando")
        self._lbl_tempo.config(fg=CORES["verde_texto"])
        self._tick()

    def _pausar(self) -> None:
        som_pausar()
        self._rodando = False
        if self._tick_id:
            self.after_cancel(self._tick_id)
        self._btn_iniciar.atualizar_texto("▶  Continuar")
        self._status.definir_estado("pausado")
        self._lbl_tempo.config(fg=CORES["texto"])

    def resetar(self) -> None:
        som_click()
        self._rodando = False
        if self._tick_id:
            self.after_cancel(self._tick_id)
        self._restante = 0
        self._habilitar_entradas(True)
        self._sincronizar_display()
        self._btn_iniciar.atualizar_texto("▶  Iniciar")
        self._btn_iniciar.desabilitar(False)
        self._btn_resetar.desabilitar(True)
        self._status.definir_estado("aguardando")
        self._lbl_tempo.config(fg=CORES["texto"])
        self._progresso.definir_percentual(1.0)

    def _tick(self) -> None:
        if not self._rodando:
            return
        self._restante -= 1
        self._renderizar(self._restante)
        pct = self._restante / self._total if self._total > 0 else 0
        self._progresso.definir_percentual(pct)
        if self._restante <= 0:
            self._rodando = False
            self._status.definir_estado("concluido")
            self._btn_iniciar.desabilitar(True)
            self._lbl_tempo.config(fg=CORES["vermelho_texto"])
            tocar_beep()
            return
        self._tick_id = self.after(1000, self._tick)

    def _renderizar(self, segundos: int) -> None:
        h = segundos // 3600
        m = (segundos % 3600) // 60
        s = segundos % 60
        texto = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
        self._lbl_tempo.config(text=texto)

    def _habilitar_entradas(self, habilitado: bool) -> None:
        estado  = "normal" if habilitado else "disabled"
        cursor  = "hand2"  if habilitado else "arrow"
        for campo in (self._inp_h, self._inp_m, self._inp_s):
            campo.config(state=estado)
        for btn in self._btns_preset:
            btn.config(cursor=cursor)


    def aplicar_tema(self) -> None:
        self.config(bg=CORES["fundo"])
        self._lbl_tempo.config(bg=CORES["fundo"], fg=CORES["texto"])
        self._status.aplicar_tema()
        self._progresso.aplicar_tema()
        for btn in (self._btn_resetar, self._btn_iniciar):
            btn.aplicar_tema()
        for btn in self._btns_preset:
            btn.config(
                bg=CORES["fundo_secundario"],
                fg=CORES["texto_suave"],
                highlightbackground=CORES["fundo_secundario"],
            )
    
        for campo in (self._inp_h, self._inp_m, self._inp_s):
            campo.config(
                bg=CORES["fundo_secundario"],
                fg=CORES["texto"],
                insertbackground=CORES["texto"],
                highlightbackground=CORES["borda"],
            )
        self._atualizar_cor_fundo_recursivo(self)

    def _atualizar_cor_fundo_recursivo(self, widget) -> None:
        for filho in widget.winfo_children():
            try:
                cls = filho.winfo_class()
                if cls in ("Frame", "Label"):
                    filho.config(bg=CORES["fundo"])
            except tk.TclError:
                pass
            self._atualizar_cor_fundo_recursivo(filho)
