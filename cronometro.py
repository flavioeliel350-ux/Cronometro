"""
Autores do modulo: Bruno teixeira e Marcos Vinicius
"""

import time
import tkinter as tk
from config import CORES, FONTES
from componentes import BotaoArredondado, BadgeStatus, Separador
from utils import formatar_tempo_voltas
from sons import som_iniciar, som_pausar, som_continuar, som_click, som_volta


class PainelCronometro(tk.Frame):

    def __init__(self, pai, **kwargs):
        super().__init__(pai, bg=CORES["fundo"], **kwargs)
        self._tempo_decorrido = 0.0
        self._rodando         = False
        self._ultimo_tick     = 0.0
        self._tick_id         = None
        self._voltas          = []
        self._inicio_volta    = 0.0
        self._construir_interface()


    def _construir_interface(self) -> None:
        self._criar_display()
        self._criar_botoes()
        self._criar_lista_voltas()
        self._criar_rodape()

    def _criar_display(self) -> None:
        display = tk.Frame(self, bg=CORES["fundo"])
        display.pack(fill="x", padx=32, pady=(28, 0))

        linha = tk.Frame(display, bg=CORES["fundo"])
        linha.pack()

        self._lbl_tempo = tk.Label(
            linha, text="00:00:00",
            font=FONTES["FONTE_DISPLAY"],
            fg=CORES["texto"], bg=CORES["fundo"],
        )
        self._lbl_tempo.pack(side="left")

        self._lbl_ms = tk.Label(
            linha, text=".00",
            font=FONTES["FONTE_MS"],
            fg=CORES["texto_suave"], bg=CORES["fundo"],
        )
        self._lbl_ms.pack(side="left", anchor="s", pady=(0, 6))

        self._status = BadgeStatus(display)
        self._status.pack(pady=(10, 0))

    def _criar_botoes(self) -> None:
        frame = tk.Frame(self, bg=CORES["fundo"])
        frame.pack(fill="x", padx=32, pady=(18, 0))
        for col in range(3):
            frame.columnconfigure(col, weight=1)

        self._btn_resetar = BotaoArredondado(
            frame, "↺  Resetar",
            comando=self.resetar, largura=130, altura=42,
        )
        self._btn_resetar.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self._btn_resetar.desabilitar(True)

        self._btn_iniciar = BotaoArredondado(
            frame, "▶  Iniciar",
            comando=self.alternar, estilo="primario", largura=130, altura=42,
        )
        self._btn_iniciar.grid(row=0, column=1, padx=5, sticky="ew")

        self._btn_volta = BotaoArredondado(
            frame, "⚑  Volta",
            comando=self.registrar_volta, largura=130, altura=42,
        )
        self._btn_volta.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        self._btn_volta.desabilitar(True)

    def _criar_lista_voltas(self) -> None:
        Separador(self).pack(fill="x", pady=(20, 0))

        cabecalho = tk.Frame(self, bg=CORES["fundo"])
        cabecalho.pack(fill="x", padx=32, pady=(12, 4))

        tk.Label(
            cabecalho, text="VOLTAS",
            font=FONTES["FONTE_MINIMA"], fg=CORES["texto_dica"],
            bg=CORES["fundo"],
        ).pack(side="left")

        self._lbl_total_voltas = tk.Label(
            cabecalho, text="",
            font=FONTES["FONTE_MINIMA"], fg=CORES["texto_dica"],
            bg=CORES["fundo"],
        )
        self._lbl_total_voltas.pack(side="right")

        container = tk.Frame(self, bg=CORES["fundo"])
        container.pack(fill="both", expand=True, padx=32)

        self._canvas_voltas = tk.Canvas(
            container, bg=CORES["fundo"],
            highlightthickness=0, height=170,
        )
        self._scroll_voltas = tk.Scrollbar(
            container, orient="vertical",
            command=self._canvas_voltas.yview,
        )
        self._frame_voltas = tk.Frame(self._canvas_voltas, bg=CORES["fundo"])
        self._frame_voltas.bind(
            "<Configure>",
            lambda e: self._canvas_voltas.configure(
                scrollregion=self._canvas_voltas.bbox("all")
            ),
        )
        self._canvas_voltas.create_window(
            (0, 0), window=self._frame_voltas, anchor="nw"
        )
        self._canvas_voltas.configure(yscrollcommand=self._scroll_voltas.set)
        self._canvas_voltas.pack(side="left", fill="both", expand=True)
        self._scroll_voltas.pack(side="right", fill="y")

        tk.Label(
            self._frame_voltas, text="Nenhuma volta registrada",
            font=FONTES["FONTE_PEQUENA"], fg=CORES["texto_dica"],
            bg=CORES["fundo"], pady=20,
        ).pack()

    def _criar_rodape(self) -> None:
        Separador(self).pack(fill="x", pady=(8, 0))
        tk.Label(
            self,
            text="Espaço: Iniciar/Pausar  ·  R: Resetar  ·  L: Volta",
            font=FONTES["FONTE_MINIMA"], fg=CORES["texto_dica"],
            bg=CORES["fundo"],
        ).pack(pady=8)


    def alternar(self) -> None:
        if self._rodando:
            self._pausar()
        else:
            self._iniciar()

    def _iniciar(self) -> None:
        som_iniciar()
        self._rodando     = True
        self._ultimo_tick = time.perf_counter() - self._tempo_decorrido
        self._atualizar()
        self._btn_iniciar.atualizar_texto("⏸  Pausar")
        self._btn_volta.desabilitar(False)
        self._btn_resetar.desabilitar(False)
        self._status.definir_estado("rodando")
        self._lbl_tempo.config(fg=CORES["verde_texto"])
        self._lbl_ms.config(fg=CORES["verde_ponto"])

    def _pausar(self) -> None:
        som_pausar()
        self._rodando = False
        if self._tick_id:
            self.after_cancel(self._tick_id)
        self._btn_iniciar.atualizar_texto("▶  Continuar")
        self._status.definir_estado("pausado")
        self._lbl_tempo.config(fg=CORES["texto"])
        self._lbl_ms.config(fg=CORES["texto_suave"])

    def resetar(self) -> None:
        som_click()
        self._rodando = False
        if self._tick_id:
            self.after_cancel(self._tick_id)
        self._tempo_decorrido = 0.0
        self._inicio_volta    = 0.0
        self._voltas          = []
        self._exibir_tempo()
        self._exibir_voltas()
        self._btn_iniciar.atualizar_texto("▶  Iniciar")
        self._btn_resetar.desabilitar(True)
        self._btn_volta.desabilitar(True)
        self._status.definir_estado("parado")
        self._lbl_tempo.config(fg=CORES["texto"])
        self._lbl_ms.config(fg=CORES["texto_suave"])

    def registrar_volta(self) -> None:
        som_volta()
        duracao = self._tempo_decorrido - self._inicio_volta
        self._voltas.insert(0, {
            "numero": len(self._voltas) + 1,
            "volta":  duracao,
            "total":  self._tempo_decorrido,
        })
        self._inicio_volta = self._tempo_decorrido
        self._exibir_voltas()

    def _atualizar(self) -> None:
        if not self._rodando:
            return
        self._tempo_decorrido = time.perf_counter() - self._ultimo_tick
        self._exibir_tempo()
        self._tick_id = self.after(30, self._atualizar)

    def _exibir_tempo(self) -> None:
        t  = self._tempo_decorrido
        h  = int(t // 3600)
        m  = int((t % 3600) // 60)
        s  = int(t % 60)
        cs = int((t % 1) * 100)
        self._lbl_tempo.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self._lbl_ms.config(text=f".{cs:02d}")

    def _exibir_voltas(self) -> None:
        for w in self._frame_voltas.winfo_children():
            w.destroy()

        if not self._voltas:
            self._lbl_total_voltas.config(text="")
            tk.Label(
                self._frame_voltas, text="Nenhuma volta registrada",
                font=FONTES["FONTE_PEQUENA"], fg=CORES["texto_dica"],
                bg=CORES["fundo"], pady=20,
            ).pack()
            return

        n = len(self._voltas)
        self._lbl_total_voltas.config(
            text=f"{n} volta{'s' if n > 1 else ''}"
        )

        tempos       = [v["volta"] for v in self._voltas]
        mais_rapida  = min(tempos) if n > 1 else None
        mais_lenta   = max(tempos) if n > 1 else None

        for volta in self._voltas:
            eh_rapida = mais_rapida is not None and volta["volta"] == mais_rapida
            eh_lenta  = mais_lenta  is not None and volta["volta"] == mais_lenta
            self._criar_linha_volta(volta, eh_rapida, eh_lenta)

    def _criar_linha_volta(self, volta: dict, eh_rapida: bool, eh_lenta: bool) -> None:
        linha = tk.Frame(self._frame_voltas, bg=CORES["fundo"])
        linha.pack(fill="x", pady=1)
        Separador(linha).pack(fill="x", side="bottom")

        esquerda = tk.Frame(linha, bg=CORES["fundo"])
        esquerda.pack(side="left", pady=8)

        tk.Label(
            esquerda, text=f"Volta {volta['numero']}",
            font=FONTES["FONTE_PEQUENA"], fg=CORES["texto_suave"],
            bg=CORES["fundo"],
        ).pack(side="left")

        if eh_rapida:
            tk.Label(
                esquerda, text="↑ rápida",
                font=FONTES["FONTE_MINIMA"],
                fg=CORES["verde_texto"], bg=CORES["verde_fundo"],
                padx=6, pady=2,
            ).pack(side="left", padx=6)
        elif eh_lenta:
            tk.Label(
                esquerda, text="↓ lenta",
                font=FONTES["FONTE_MINIMA"],
                fg=CORES["vermelho_texto"], bg=CORES["vermelho_fundo"],
                padx=6, pady=2,
            ).pack(side="left", padx=6)

        cor_tempo = (
            CORES["verde_texto"]    if eh_rapida else
            CORES["vermelho_texto"] if eh_lenta  else
            CORES["texto"]
        )
        tk.Label(
            linha,
            text=formatar_tempo_voltas(volta["volta"]),
            font=("Courier New", FONTES["FONTE_PEQUENA"][1] + 3),
            fg=cor_tempo, bg=CORES["fundo"],
        ).pack(side="right", pady=8, padx=4)


    def aplicar_tema(self) -> None:
        self.config(bg=CORES["fundo"])
        self._atualizar_cores_display()
        self._status.aplicar_tema()
        for btn in (self._btn_resetar, self._btn_iniciar, self._btn_volta):
            btn.aplicar_tema()
        self._exibir_voltas()         
        self._atualizar_cor_fundo_recursivo(self)

    def _atualizar_cores_display(self) -> None:
        em_execucao = self._rodando
        fg_tempo    = CORES["verde_texto"] if em_execucao else CORES["texto"]
        fg_ms       = CORES["verde_ponto"] if em_execucao else CORES["texto_suave"]
        self._lbl_tempo.config(fg=fg_tempo, bg=CORES["fundo"])
        self._lbl_ms.config(fg=fg_ms, bg=CORES["fundo"])
        self._canvas_voltas.config(bg=CORES["fundo"])
        self._frame_voltas.config(bg=CORES["fundo"])

    def _atualizar_cor_fundo_recursivo(self, widget) -> None:
        for filho in widget.winfo_children():
            try:
                cls = filho.winfo_class()
                if cls in ("Frame", "Label"):
                    filho.config(bg=CORES["fundo"])
            except tk.TclError:
                pass
            self._atualizar_cor_fundo_recursivo(filho)
