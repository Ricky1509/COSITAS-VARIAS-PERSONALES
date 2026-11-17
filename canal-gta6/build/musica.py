# -*- coding: utf-8 -*-
"""Música synthwave original generada por código (sin derechos de terceros)."""
import numpy as np

SR = 44100

def _nota(n):  # n = semitonos desde A4
    return 440.0 * 2 ** (n / 12)

def _saw(f, t):
    return 2 * ((t * f) % 1.0) - 1

def _lp(x, a):
    y = np.empty_like(x); acc = 0.0
    # filtro paso bajo de un polo (vectorizado por bloques sería más rápido; suficiente así)
    from scipy.signal import lfilter  # noqa
    return lfilter([a], [1, a - 1], x)

def pista(segundos, semilla=0, bpm=96):
    rng = np.random.default_rng(semilla)
    progresiones = [[-12, -16, -9, -14], [-14, -11, -16, -12], [-12, -7, -16, -9]]
    prog = progresiones[semilla % len(progresiones)]
    beat = 60.0 / bpm
    compas = beat * 4
    n = int(segundos * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    # pad: acorde menor/mayor por compás, sierra desafinada filtrada
    idx = (t // compas).astype(int) % 4
    for k, raiz in enumerate(prog):
        m = idx == k
        tt = t[m]
        for iv in (0, 3 if k % 2 == 0 else 4, 7, 12):
            f = _nota(raiz + iv)
            out[m] += 0.05 * (_saw(f, tt) + _saw(f * 1.004, tt))
    out = _lp(out, 0.06)
    # bajo en corcheas
    bajo = np.zeros(n)
    corchea = beat / 2
    for k, raiz in enumerate(prog):
        pass
    pos = (t % corchea) / corchea
    raizt = np.array(prog)[idx]
    f = 440.0 * 2 ** ((raizt - 24) / 12)
    fase = np.cumsum(f / SR)
    bajo = (2 * (fase % 1.0) - 1) * np.exp(-pos * 3.0) * 0.22
    out += _lp(bajo, 0.12)
    # batería
    def golpe(dur, gen):
        m = int(dur * SR); return gen(m)
    kick = golpe(0.35, lambda m: np.sin(2 * np.pi * np.cumsum(np.linspace(140, 45, m)) / SR) * np.exp(-np.linspace(0, 8, m)))
    snare = golpe(0.25, lambda m: rng.uniform(-1, 1, m) * np.exp(-np.linspace(0, 10, m)) * 0.5)
    hat = golpe(0.05, lambda m: rng.uniform(-1, 1, m) * np.exp(-np.linspace(0, 12, m)) * 0.15)
    nb = int(segundos / beat)
    for b in range(nb):
        s = int(b * beat * SR)
        def mezcla(x, s):
            e = min(n, s + len(x)); out[s:e] += x[: e - s]
        mezcla(kick * 0.6, s)
        if b % 2 == 1: mezcla(snare, s)
        mezcla(hat, s + int(beat / 2 * SR))
    # fundidos
    fi = int(2 * SR); fo = int(4 * SR)
    out[:fi] *= np.linspace(0, 1, fi)
    out[-fo:] *= np.linspace(1, 0, fo)
    out /= np.max(np.abs(out)) + 1e-9
    return (out * 0.8).astype(np.float32)
