"""
Configurações visuais, fontes e temas do aplicativo.
Suporta modo claro e escuro com persistência em JSON.
"""

import json
import os

# Arquivo de preferências do usuário
_PREFS_PATH = os.path.join(os.path.dirname(__file__), "preferencias.json")

# ── Paletas de cores ────────────────────────────────────────────────────────

TEMAS = {
    "claro": {
        "fundo":            "#FFFFFF",
        "fundo_secundario": "#F5F5F3",
        "fundo_terciario":  "#EEEDE9",
        "borda":            "#E0DED7",
        "texto":            "#1A1A18",
        "texto_suave":      "#888780",
        "texto_dica":       "#AAAAAA",

        "verde_fundo":      "#E1F5EE",
        "verde_texto":      "#0F6E56",
        "verde_ponto":      "#1D9E75",

        "amarelo_fundo":    "#FAEEDA",
        "amarelo_texto":    "#854F0B",
        "amarelo_ponto":    "#EF9F27",

        "vermelho_fundo":   "#FCEBEB",
        "vermelho_texto":   "#A32D2D",
        "vermelho_ponto":   "#E24B4A",

        "aba_ativa":        "#1A1A18",
        "aba_inativa":      "#888780",
        "botao_fundo":      "#1A1A18",
        "botao_texto":      "#FFFFFF",

        "foco_borda":       "#4A90D9",
        "botao_hover":      "#2D2D2A",
        "btn_secundario_hover": "#DDDBD5",
    },
    "escuro": {
        "fundo":            "#1C1C1E",
        "fundo_secundario": "#2C2C2E",
        "fundo_terciario":  "#3A3A3C",
        "borda":            "#48484A",
        "texto":            "#F2F2F7",
        "texto_suave":      "#AEAEB2",
        "texto_dica":       "#636366",

        "verde_fundo":      "#0D3B2E",
        "verde_texto":      "#30D158",
        "verde_ponto":      "#30D158",

        "amarelo_fundo":    "#3D2F00",
        "amarelo_texto":    "#FFD60A",
        "amarelo_ponto":    "#FFD60A",

        "vermelho_fundo":   "#3D0F0F",
        "vermelho_texto":   "#FF453A",
        "vermelho_ponto":   "#FF453A",

        "aba_ativa":        "#F2F2F7",
        "aba_inativa":      "#636366",
        "botao_fundo":      "#F2F2F7",
        "botao_texto":      "#1C1C1E",

        "foco_borda":       "#64B5F6",
        "botao_hover":      "#DADADE",
        "btn_secundario_hover": "#4A4A4C",
    },
}

# Referência mutável às cores ativas — todos os módulos importam CORES
CORES: dict = {}


# ── Fontes (escaladas dinamicamente em runtime) ─────────────────────────────

def _escala(base: int, fator: float) -> int:
    return max(8, round(base * fator))


def gerar_fontes(fator: float = 1.0) -> dict:
    return {
        "FONTE_MONO":    ("Courier New",  _escala(10, fator)),
        "FONTE_SANS":    ("Helvetica",    _escala(10, fator)),
        "FONTE_DISPLAY": ("Courier New",  _escala(52, fator), "normal"),
        "FONTE_MS":      ("Courier New",  _escala(28, fator), "normal"),
        "FONTE_TIMER":   ("Courier New",  _escala(52, fator), "normal"),
        "FONTE_BOTAO":   ("Helvetica",    _escala(13, fator), "bold"),
        "FONTE_LABEL":   ("Helvetica",    _escala(11, fator)),
        "FONTE_PEQUENA": ("Helvetica",    _escala(10, fator)),
        "FONTE_MINIMA":  ("Helvetica",    _escala(9,  fator)),
        "FONTE_STATUS":  ("Helvetica",    _escala(11, fator), "bold"),
        "FONTE_ABA":     ("Helvetica",    _escala(13, fator), "bold"),
        "FONTE_ABA_IN":  ("Helvetica",    _escala(13, fator)),
        "FONTE_TITULO":  ("Helvetica",    _escala(13, fator)),
    }


# Dicionário mutável — atualizado em runtime conforme resolução
FONTES: dict = gerar_fontes(1.0)


# ── Persistência de preferências ────────────────────────────────────────────

def _prefs_padrao() -> dict:
    return {"tema": "claro"}


def carregar_prefs() -> dict:
    try:
        with open(_PREFS_PATH, "r", encoding="utf-8") as f:
            dados = json.load(f)
        # Valida campos obrigatórios
        if dados.get("tema") not in TEMAS:
            dados["tema"] = "claro"
        return dados
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return _prefs_padrao()


def salvar_prefs(prefs: dict) -> None:
    try:
        with open(_PREFS_PATH, "w", encoding="utf-8") as f:
            json.dump(prefs, f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # Silencia erros de I/O (permissão, disco cheio etc.)


def aplicar_tema(nome: str) -> None:
    """Atualiza o dicionário CORES com a paleta do tema escolhido."""
    CORES.clear()
    CORES.update(TEMAS.get(nome, TEMAS["claro"]))


# Inicialização: carrega preferência salva e aplica tema
_prefs_iniciais = carregar_prefs()
aplicar_tema(_prefs_iniciais["tema"])
