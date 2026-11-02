"""Lay sound effects from sounds/sfx onto a reel at exact times.

The reel's own audio is replaced (base clips carry generator noise); trending music is
meant to be added inside Instagram on top of these effects.

Usage:
  python3 -I tools/sound_mix.py              # re-mix every reel listed in sounds/reel_sounds.json
  python3 -I tools/sound_mix.py 04 12        # only reels whose file name contains 04 or 12
Cue format (sounds/reel_sounds.json):  {"keep_reel_04_…": [{"sound": "horror-hit", "at": 2.8, "volume": 0.9}, …]}
"""
import json, os, subprocess, sys, tempfile, shutil

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SFX = os.path.join(ROOT, "sounds", "sfx")

def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout.strip())

def mix(video, cues, out):
    """Write `out`: the video stream of `video` (copied) + a new audio track built from `cues`."""
    dur = duration(video)
    args = ["ffmpeg", "-v", "error", "-y", "-i", video]
    parts = []
    for i, c in enumerate(cues):
        args += ["-i", os.path.join(SFX, c["sound"] + ".wav")]
        ms = int(round(float(c["at"]) * 1000))
        parts.append(f"[{i+1}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={c.get('volume', 0.85)},adelay={ms}|{ms}[s{i}]")
    if parts:
        labels = "".join(f"[s{i}]" for i in range(len(cues)))
        parts.append(f"{labels}amix=inputs={len(cues)}:normalize=0:duration=longest,apad,atrim=0:{dur:.3f},"
                     f"afade=t=out:st={max(0, dur - 0.4):.3f}:d=0.4,alimiter=limit=0.89[a]")
    else:
        parts.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{dur:.3f}[a]")
    args += ["-filter_complex", ";".join(parts), "-map", "0:v", "-map", "[a]", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]
    subprocess.run(args, check=True)

def main(only):
    plan = json.load(open(os.path.join(ROOT, "sounds", "reel_sounds.json")))
    for name, cues in plan.items():
        if only and not any(o in name for o in only):
            continue
        src = os.path.join(ROOT, "reels", name + ".mp4")
        tmp = tempfile.mktemp(suffix=".mp4")
        mix(src, cues, tmp)
        shutil.move(tmp, src)
        print("mixed", name, ", ".join(f"{c['sound']}@{c['at']}s" for c in cues))

if __name__ == "__main__":
    main(sys.argv[1:])
