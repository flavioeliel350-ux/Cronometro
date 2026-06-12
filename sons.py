import math
import struct
import threading
import wave
import tempfile
import os
import subprocess


_RATE = 44100


def _wav_bytes(amostras: list[int]) -> bytes:
    import io
    buf = io.BytesIO()
    w = wave.open(buf, "w")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(_RATE)
    for s in amostras:
        w.writeframes(struct.pack("<h", s))
    w.close()
    return buf.getvalue()


def _envelope(i: int, total: int, ataque: int = 200, release: int = 800) -> float:
    if i < ataque:
        return i / ataque
    if i > total - release:
        return (total - i) / release
    return 1.0


def _sine(freq: float, t: float) -> float:
    return math.sin(2 * math.pi * freq * t)


def _gerar_tone(freq_inicio: float, freq_fim: float, duracao_ms: int,
                volume: float = 0.28) -> list[int]:
    n = int(_RATE * duracao_ms / 1000)
    amostras = []
    for i in range(n):
        t   = i / _RATE
        pct = i / n
        freq = freq_inicio + (freq_fim - freq_inicio) * pct
        env  = _envelope(i, n, ataque=int(n * 0.08), release=int(n * 0.35))
        v    = int(32767 * volume * env * _sine(freq, t))
        amostras.append(max(-32767, min(32767, v)))
    return amostras


def _gerar_dois_tons(f1: float, dur1: int, f2: float, dur2: int,
                     volume: float = 0.25) -> list[int]:
    n1 = int(_RATE * dur1 / 1000)
    n2 = int(_RATE * dur2 / 1000)
    amostras = []
    for i in range(n1):
        t   = i / _RATE
        env = _envelope(i, n1, ataque=int(n1 * 0.1), release=int(n1 * 0.3))
        amostras.append(int(32767 * volume * env * _sine(f1, t)))
    for i in range(n2):
        t   = i / _RATE
        env = _envelope(i, n2, ataque=int(n2 * 0.05), release=int(n2 * 0.45))
        amostras.append(int(32767 * volume * env * _sine(f2, t)))
    return amostras


def _tocar_amostras(amostras: list[int]) -> None:
    data = _wav_bytes(amostras)
    try:
        import winsound, io
        winsound.PlaySound(data, winsound.SND_MEMORY)
    except Exception:
        try:
            f = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            f.write(data)
            f.close()
            subprocess.call(["aplay", f.name],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
            os.unlink(f.name)
        except Exception:
            pass


def _play(amostras: list[int]) -> None:
    threading.Thread(target=_tocar_amostras, args=(amostras,), daemon=True).start()



def som_click() -> None:
    """Som curto para os botões resetar e volta."""
    _play(_gerar_tone(820, 780, 65, volume=0.22))


def som_iniciar() -> None:
    """Som para quando inicia a contagem."""
    _play(_gerar_tone(580, 920, 95, volume=0.26))


def som_pausar() -> None:
    """Som para quando pausar."""
    _play(_gerar_tone(880, 560, 95, volume=0.24))


def som_continuar() -> None:
    """som para retomar depois que pausa."""
    _play(_gerar_tone(620, 880, 85, volume=0.24))


def som_volta() -> None:
    """Som para cada volta registrada."""
    _play(_gerar_dois_tons(700, 55, 1000, 60, volume=0.22))


def som_tema() -> None:
    """Som para quando trocar entre o modo claro e escuro."""
    _play(_gerar_tone(900, 750, 70, volume=0.18))
