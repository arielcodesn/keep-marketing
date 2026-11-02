"""Original sound-effects library for Keep reels, synthesised from scratch (no samples,
no third-party recordings), so every sound is free to use in ads and organic posts.

Run: python3 -I sounds/synth.py   -> writes sounds/sfx/<id>.wav and sounds/library.json
"""
import json, os
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sfx")
rng = np.random.default_rng(7)

def t(sec): return np.arange(int(SR * sec)) / SR
def env(n, a=0.005, d=0.3, s=0.0, total=None):
    """attack / exponential decay envelope"""
    x = np.arange(n) / SR
    e = np.minimum(1, x / max(a, 1e-4)) * np.exp(-np.maximum(0, x - a) / max(d, 1e-4))
    return np.maximum(e, s)
def lp(x, f): return sosfilt(butter(4, f, "low", fs=SR, output="sos"), x)
def hp(x, f): return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)
def reverb(x, sec=1.6, mix=0.3, bright=6000):
    n = int(SR * sec)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * (6.9 / sec))
    ir = lp(ir, bright); ir /= np.sqrt((ir ** 2).sum())
    wet = fftconvolve(x, ir)
    dry = np.concatenate([x, np.zeros(len(wet) - len(x))])
    return (1 - mix) * dry + mix * wet
def saw(f, tt, phase=0):
    ph = np.cumsum(np.broadcast_to(f, tt.shape) / SR) + phase
    return 2 * (ph % 1) - 1
def sine(f, tt): return np.sin(2 * np.pi * np.cumsum(np.broadcast_to(f, tt.shape) / SR))
def norm(x, peak=0.89):
    x = x - np.mean(x)
    return x / (np.max(np.abs(x)) + 1e-9) * peak
def fade(x, out=0.05, inn=0.003):
    n1, n2 = int(SR * inn), int(SR * out)
    x = x.copy(); x[:n1] *= np.linspace(0, 1, n1); x[-n2:] *= np.linspace(1, 0, n2); return x
def note(midi): return 440 * 2 ** ((midi - 69) / 12)

def boom():
    tt = t(1.4)
    f = 55 + 70 * np.exp(-tt * 18)
    body = sine(f, tt) * env(len(tt), 0.002, 0.45)
    click = hp(rng.standard_normal(len(tt)), 2000) * env(len(tt), 0.001, 0.012) * 0.5
    sub = sine(np.full_like(tt, 42), tt) * env(len(tt), 0.01, 0.6) * 0.6
    x = np.tanh(2.2 * (body + click + sub))
    return reverb(x, 1.2, 0.25, 3000)

def horror_hit():
    tt = t(2.6)
    cluster = sum(saw(note(m) * (1 + 0.003 * k), tt, rng.random()) for k, m in enumerate([45, 46, 51, 52, 57, 58]))
    strings = bp(cluster, 120, 5000) * env(len(tt), 0.004, 0.9)
    screech = saw(note(88) * (1 + 0.012 * np.sin(2 * np.pi * 9 * tt)), tt)
    screech = bp(screech, 1500, 9000) * env(len(tt), 0.003, 0.35) * 0.5
    low = sine(40 + 40 * np.exp(-tt * 10), tt) * env(len(tt), 0.002, 0.7)
    x = np.tanh(1.6 * (0.5 * strings + screech + 0.9 * low))
    return reverb(x, 2.2, 0.35, 7000)

def suspense_rise():
    tt = t(3.0)
    grow = (tt / tt[-1]) ** 2
    drone = sum(saw(note(m) * (1 + 0.004 * np.sin(2 * np.pi * (0.3 + k) * tt)), tt) for k, m in enumerate([33, 40, 45, 46]))
    drone = lp(drone, 900) * (0.15 + grow)
    shimmer = bp(rng.standard_normal(len(tt)), 3000, 8000) * grow * 0.15
    x = drone + shimmer
    return reverb(fade(x, 0.02), 1.5, 0.3)

def piano_note(midi, dur, vel=1.0):
    tt = t(dur)
    f = note(midi)
    partials = [(1, 1), (2, 0.45), (3, 0.22), (4, 0.12), (5, 0.06), (6, 0.03)]
    x = sum(a * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * tt) * np.exp(-tt * (1.4 + 0.9 * k)) for k, a in partials)
    hammer = bp(rng.standard_normal(len(tt)), 1500, 6000) * env(len(tt), 0.001, 0.01) * 0.15
    return (x * env(len(tt), 0.003, 2.5) + hammer) * vel

def place(dst, src, at):
    i = int(at * SR); dst[i:i + len(src)] += src[: max(0, len(dst) - i)]

def sad_piano():
    x = np.zeros(int(SR * 5.0))
    # A minor, slow and lonely: original phrase
    for at, m, v in [(0, 57, .6), (0, 64, .5), (0.55, 69, .7), (1.1, 72, .65), (1.65, 71, .6), (2.3, 69, .7), (2.3, 53, .5), (2.3, 60, .45), (3.1, 64, .6)]:
        place(x, piano_note(m, 2.2, v), at)
    return reverb(x, 2.5, 0.35, 5000)

def sad_violin():
    tt = t(3.2)
    f = note(76) * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * tt) * np.minimum(1, tt / 0.6))
    f = np.where(tt > 1.8, f * 2 ** (-1 / 12 * np.minimum(1, (tt - 1.8) / 0.25)), f)  # slides down a semitone
    x = saw(f, tt)
    x = bp(x, 400, 6000) + 0.3 * bp(x, 2500, 3500)
    x *= np.minimum(1, tt / 0.35) * np.minimum(1, (tt[-1] - tt) / 0.6)
    return reverb(x, 2.0, 0.35)

def sax_note(midi, dur, vel=1.0, bend=0.0):
    tt = t(dur)
    f = note(midi) * (1 + bend * np.exp(-tt * 12)) * (1 + 0.007 * np.sin(2 * np.pi * 5.2 * tt) * np.minimum(1, tt / 0.3))
    x = saw(f, tt) * 0.7 + np.sign(sine(f, tt)) * 0.15
    x = bp(x, 180, 3500) + 0.6 * bp(x, 900, 1500)
    breath = bp(rng.standard_normal(len(tt)), 1500, 5000) * 0.08
    e = np.minimum(1, tt / 0.04) * np.minimum(1, (dur - tt) / 0.08)
    return np.tanh(1.5 * (x + breath)) * e * vel

def smooth_sax():
    x = np.zeros(int(SR * 6.0))
    # original sultry phrase that keeps getting louder
    phrase = [(0.0, 62, .5, .25), (0.5, 65, .45, .3), (0.95, 67, .9, .35), (2.0, 70, .45, .45), (2.5, 69, .45, .5),
              (2.95, 67, .45, .6), (3.45, 65, 1.6, .85, -0.03)]
    for p in phrase:
        at, m, d, v = p[:4]; b = p[4] if len(p) > 4 else 0.02
        place(x, sax_note(m, d, v, b), at)
    return reverb(x, 1.8, 0.28)

def fail_trumpet():
    x = np.zeros(int(SR * 3.4))
    for i, (m, d) in enumerate([(58, .45), (57, .45), (56, .45), (55, 1.6)]):
        tt = t(d)
        wob = 1 + (0.025 * np.sin(2 * np.pi * 6 * tt) if i == 3 else 0)
        n = saw(note(m) * wob * (1 - 0.01 * tt), tt)
        n = bp(n, 200, 2500) * np.minimum(1, tt / 0.03) * np.minimum(1, (d - tt) / 0.06)
        place(x, np.tanh(2 * n) * 0.8, i * 0.5)
    return reverb(x, 1.2, 0.2)

def record_scratch():
    tt = t(0.7)
    rate = np.where(tt < 0.25, 1 + 4 * tt, np.maximum(0.05, 2 - 5 * (tt - 0.25)))
    nz = rng.standard_normal(len(tt))
    idx = np.clip(np.cumsum(rate).astype(int), 0, len(nz) - 1)
    x = bp(nz[idx], 300, 4000) * env(len(tt), 0.005, 0.25) + 0.4 * sine(200 * rate, tt) * env(len(tt), 0.005, 0.2)
    return fade(x, 0.05)

def whoosh():
    tt = t(0.6)
    nz = rng.standard_normal(len(tt))
    sweep = np.sin(np.pi * tt / tt[-1]) ** 2
    x = bp(nz, 400, 3000) * sweep
    return reverb(x, 0.6, 0.15)

def pop():
    tt = t(0.25)
    x = sine(900 * np.exp(-tt * 25) + 300, tt) * env(len(tt), 0.001, 0.05)
    return reverb(x, 0.4, 0.15)

def ding():
    tt = t(1.6)
    x = sum(a * np.sin(2 * np.pi * note(84) * r * tt) * np.exp(-tt * d) for r, a, d in [(1, 1, 2.5), (2.76, .4, 4), (5.4, .2, 6)])
    return reverb(x * env(len(tt), 0.002, 1.2), 1.2, 0.2)

def victory():
    x = np.zeros(int(SR * 2.2))
    for at, ms, d in [(0, (60, 64, 67), .18), (0.2, (60, 64, 67), .18), (0.4, (60, 64, 67), .18), (0.62, (65, 69, 72), 1.4)]:
        tt = t(d)
        ch = sum(saw(note(m), tt) for m in ms)
        ch = bp(ch, 250, 4000) * np.minimum(1, tt / 0.02) * np.minimum(1, (d - tt) / 0.05)
        place(x, np.tanh(1.2 * ch) * 0.6, at)
    place(x, ding() * 0.5, 0.62)
    return reverb(x, 1.4, 0.22)

def tick_tock():
    x = np.zeros(int(SR * 4.0))
    for i in range(8):
        tt = t(0.08)
        c = bp(rng.standard_normal(len(tt)), 2500 if i % 2 == 0 else 1800, 6000) * env(len(tt), 0.0005, 0.01)
        place(x, c, i * 0.5)
    return reverb(x, 0.8, 0.2)

LIBRARY = [
    ("boom", "Boom", boom, "Hit", "A deep, punchy boom. The classic meme punch on a punchline.", "Any punchline pop-in, exactly on the beat"),
    ("horror-hit", "Horror hit", horror_hit, "Horror", "Screeching strings and a low slam, like a jump scare.", "Shocked reveals: \"Photos: 118 GB 💀\", the ex in the photo"),
    ("suspense-rise", "Suspense rise", suspense_rise, "Horror", "A dark drone that swells for 3 seconds, ending where the hit should land.", "Start ~3 s before a horror hit or boom"),
    ("sad-piano", "Sad piano", sad_piano, "Sad", "A slow, lonely piano phrase in A minor.", "Crying, \"Storage Full\" at the best moment, deleting the ex"),
    ("sad-violin", "Sad violin", sad_violin, "Sad", "One long, wobbly violin note that sinks at the end.", "Defeated faces, \"I give up\", tiny violin moments"),
    ("smooth-sax", "Smooth sax, getting louder", smooth_sax, "Sax", "A sultry saxophone phrase that keeps getting louder.", "Strut, side-eye, smug or \"main character\" moments"),
    ("fail-trumpet", "Fail trumpet", fail_trumpet, "Fail", "Wah, wah, wah, waaah: four sinking notes.", "Picture fails, jump shots, \"it's a plastic bag\""),
    ("record-scratch", "Record scratch", record_scratch, "Hit", "A needle scratch that stops everything.", "\"Wait, what?\" moments; cut right before a reveal"),
    ("whoosh", "Whoosh", whoosh, "Transition", "A soft air swipe.", "Text sliding in, scene changes"),
    ("pop", "Pop", pop, "Transition", "A short bubbly pop.", "Small text pop-ins, emojis appearing"),
    ("ding", "Ding", ding, "Success", "A bright bell ding.", "\"Storage freed\" numbers, Keep logo moments"),
    ("victory", "Victory fanfare", victory, "Success", "A short brassy ta-da with a bell.", "Dance and cleanup payoff reels"),
    ("tick-tock", "Tick tock", tick_tock, "Tension", "A clock ticking for 4 seconds.", "Scrolling forever, \"weekend #87\", waiting moments"),
]

def main():
    os.makedirs(OUT, exist_ok=True)
    meta = []
    for sid, name, fn, cat, desc, use in LIBRARY:
        x = fade(norm(fn()), 0.08)
        wavfile.write(os.path.join(OUT, f"{sid}.wav"), SR, (x * 32767).astype(np.int16))
        meta.append(dict(id=sid, name=name, category=cat, description=desc, use=use,
                         seconds=round(len(x) / SR, 2), file=f"sfx/{sid}.wav"))
        print(f"{sid:15s} {len(x)/SR:4.1f}s")
    json.dump(meta, open(os.path.join(HERE, "library.json"), "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
