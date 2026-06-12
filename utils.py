"""
Funções de apoio do projeto.
"""

import threading


def tocar_beep() -> None:
    """Som de aviso quando o tempo acaba."""
    def _tocar():
        try:
            import winsound
            winsound.Beep(880, 600)
        except Exception:
            try:
                import subprocess, math, wave, struct, tempfile, os
                f = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                w = wave.open(f, "w")
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100)
                for i in range(22050):
                    v = int(32767 * math.sin(2 * math.pi * 880 * i / 44100)
                            * max(0, 1 - i / 22050))
                    w.writeframes(struct.pack("<h", v))
                w.close()
                subprocess.call(["aplay", f.name],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
                os.unlink(f.name)
            except Exception:
                pass

    threading.Thread(target=_tocar, daemon=True).start()


def formatar_tempo(segundos: float) -> str:
    """Formata o tempo do cronômetro."""
    h = int(segundos) // 3600
    m = (int(segundos) % 3600) // 60
    s = int(segundos) % 60
    return f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"


def formatar_tempo_voltas(segundos: float) -> str:
    """Formata o tempo das voltas."""
    h  = int(segundos // 3600)
    m  = int((segundos % 3600) // 60)
    s  = int(segundos % 60)
    cs = int((segundos % 1) * 100)
    return f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}"


def calcular_fator_escala(largura_tela: int, altura_tela: int) -> float:
    """
    Ajusta o tamanho da interface conforme a resolução da tela.
    """
    area = largura_tela * altura_tela
    area_ref = 1920 * 1080
    fator = (area / area_ref) ** 0.35          
    return round(max(0.75, min(1.4, fator)), 3)
