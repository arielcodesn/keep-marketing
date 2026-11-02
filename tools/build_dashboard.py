"""Builds the Keep reel studio dashboard (a single HTML page + media folder).

Usage: python3 -I tools/build_dashboard.py <out_dir>
Expects <out_dir>/media/{reels,clips,posters,sheets,bg} to already hold the preview media
(540px-wide re-encodes of reels/ and base-clips/, poster frames, contact sheets, backgrounds).
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "plan"))
from write_timelines import CLIPS as TIMELINES
from ideas import IDEAS, CLIPS as PLAN_CLIPS, PILLARS

OUT = sys.argv[1]

BG = {
    "snowy-mountain-dusk": ("Snowy mountain at dusk", "Pexels", "https://www.pexels.com/photo/photo-of-snow-capped-mountain-during-evening-2440024/"),
    "pier-sunset": ("Pier at sunset", "Unsplash (CC0)", "https://unsplash.com/photos/ces8_Bo7bhQ"),
    "lake-mountains": ("Lake and mountains", "Unsplash", "https://unsplash.com/photos/Dxod5pdRtsk"),
    "desert-dunes": ("Desert dunes", "Unsplash", "https://unsplash.com/photos/A9mr3TPoj0k"),
    "valley": ("Valley", "Unsplash", "https://unsplash.com/photos/M6XC789HLe8"),
    "snowy-summit": ("Snowy summit", "Unsplash (CC0)", "https://unsplash.com/photos/yrwpJwDNSHE"),
    "pink-flower": ("Pink flower on blue", "Unsplash", "https://unsplash.com/photos/iGrsa9rL11o"),
}

# file stem, pillar, hook, punchline, base clip, background key (None = original scene), plan id it fulfils
REELS = [
    ("keep_reel_01_concert_filming-47-minutes", "storage", "Me filming 47 minutes of a concert I'll never rewatch 🎤😭", "", "concert_excited-to-blissful_branded", None, None),
    ("keep_reel_02_concert_312-photos-of-stage", "fails", "Me taking 312 photos of a stage I can barely see 📸💀", "", "concert_excited-to-blissful_branded", None, None),
    ("keep_reel_03_concert_cleared-8gb-payoff", "storage", "When you cleared 8GB in 5 minutes and can film the WHOLE encore 🎶", "cleaned with Keep 🧹", "concert_excited-to-blissful_branded", None, None),
    ("keep_reel_04_living_118gb-photos", "storage", "2am, checking iPhone Storage…", "Photos: 118 GB 💀", "living-room_sleepy-to-shocked", None, "d02-storage"),
    ("keep_reel_05_living_airdrop-400-photos", "life", "When your friend AirDrops all 400 party photos…", "and you're in 3 of them 😐", "living-room_sleepy-to-shocked", None, None),
    ("keep_reel_06_living_2016-emo-phase", "funny", "Scrolling back to 2016 at 3am and finding your emo phase 💀", "", "living-room_sleepy-to-shocked", None, "d01-funny"),
    ("keep_reel_07_beach_icloud-full-day-1", "travel", "Day 1 of vacation:", "\"iCloud Storage Full\" 🌴💀", "beach_surprised", None, "d02-travel"),
    ("keep_reel_08_beach_1204-photos-3-good", "travel", "Trip album: 1,204 photos 📸", "Good ones: 3 💀", "beach_surprised", None, "d04-travel"),
    ("keep_reel_09_desk_find-id-in-38000-screenshots", "storage", "Trying to find ONE photo of my ID in 38,000 screenshots 😤", "I give up 💀", "desk_frustrated-to-defeated_branded", None, "d03-storage"),
    ("keep_reel_10_desk_icloud-upgrade-dog-pics", "storage", "iCloud asking me to upgrade AGAIN because I won't delete 14 blurry pics of my dog 💀", "", "desk_frustrated-to-defeated_branded", None, "d04-storage"),
    ("keep_reel_11_mountain_hiked-4-hours-600-photos", "travel", "Me after hiking 4 hours just to take 600 photos of the same mountain 🏔️📸", "", "concert_excited-to-blissful_branded", "snowy-mountain-dusk", "d14-travel"),
    ("keep_reel_12_pier_2941-photos-today", "travel", "Day 2 of vacation, checking my camera roll 🌅", "Photos taken today: 2,941 💀", "white_calm-to-shocked_fullbody", "pier-sunset", None),
    ("keep_reel_13_lake_dad-37-photos-of-thumb", "travel", "Asked my dad to take photos of me on our trip 📸", "37 photos of his thumb 😭", "white_calm-to-laughing_fullbody", "lake-mountains", "d01-travel"),
    ("keep_reel_14_dunes_52-pics-blinking", "fails", "Asked my friend for ONE nice desert pic 🏜️", "She sent 52. I'm blinking in all of them 💀", "white_calm-to-laughing_fullbody", "desert-dunes", "d01-fails"),
    ("keep_reel_15_valley_aesthetic-pics-posted-0", "travel", "Looking back at the \"aesthetic\" travel pics I swore I'd post 🏞️", "Posted: 0 · Storage used: 14 GB 😭", "white_calm-to-laughing_fullbody", "valley", None),
    ("keep_reel_16_dance_deleted-4000-screenshots", "storage", "Me after finally deleting the 4,000 screenshots I took \"for later\" 💃", "", "white_dance_fullbody", None, "d01-storage"),
    ("keep_reel_17_summit_deleted-4000-screenshots", "storage", "Me after finally deleting the 4,000 screenshots I took \"for later\" 💃", "", "white_dance_fullbody", "snowy-summit", "d01-storage"),
    ("keep_reel_18_flower_deleted-4000-screenshots", "storage", "Me after finally deleting the 4,000 screenshots I took \"for later\" 💃", "", "white_dance_fullbody", "pink-flower", "d01-storage"),
    ("keep_reel_19_pier_vacation-1-2gb-left", "travel", "Me walking into a 2-week vacation with 1.2 GB of storage left like it's enough 🧳", "", "green_strut-turn_fullbody", "pier-sunset", "d03-travel"),
]

# Base clips still to make: (emotion, why, priority, kind)
TO_MAKE = [
    ("Side-eye / suspicious", "Group photos, someone scrolling your phone, GC receipts", "Make first", "new"),
    ("Crying", "Storage Full at the best moment, deleting photos of an ex", "Make first", "new"),
    ("Panic, fast swiping", "Hiding photos before someone sees, boarding pass lost in memes", "Make first", "new"),
    ("Facepalm", "47 near-identical photos, zooming in on a plastic bag", "Make first", "new"),
    ("Laughing (green)", "Used 45× in the plan; the current clip is on white, so every reel needs the slow AI cutout", "Remake on green", "green"),
    ("Shocked (green)", "Used 23×; number-reveal punchlines", "Remake on green", "green"),
    ("Angry → gives up (green, full body)", "Used 17×; the current clip is stuck behind an office desk", "Remake on green", "green"),
    ("Sleepy → wide awake (green)", "Used 10×; the current clip is stuck in the living room and cuts out badly", "Remake on green", "green"),
    ("Dance (green)", "Used 12×; you may already have this in another session, so upload it to base-clips/", "Upload if you have it", "green"),
    ("Laughing, variation 2 (pointing at phone)", "So 45 laughing reels don't all look the same", "Nice to have", "variation"),
    ("Shocked, variation 2 (drops the phone)", "A bigger reaction for the biggest numbers", "Nice to have", "variation"),
]

PLAN_EMOTION_TO_CLIP = {k: v[0] for k, v in PLAN_CLIPS.items()}

def main():
    made = {}
    for r in REELS:
        if r[6]:
            made.setdefault(r[6], []).append(r[0])
    plan = []
    for d in range(30):
        for p in PILLARS:
            hook, punch, clip, bg, cta = IDEAS[p][d]
            pid = f"d{d+1:02d}-{p}"
            plan.append(dict(id=pid, day=d + 1, pillar=p, hook=hook, punch=punch,
                             emotion=clip.replace("NEW:", ""), new=clip.startswith("NEW:"),
                             clip=PLAN_EMOTION_TO_CLIP.get(clip) or "", beat=PLAN_CLIPS[clip][1],
                             bg=bg, cta=cta, made=made.get(pid, [])))
    emotion_need = {}
    for row in plan:
        emotion_need[row["emotion"]] = emotion_need.get(row["emotion"], 0) + 1
    clips = []
    for name, c in TIMELINES.items():
        bgtype = "green" if name.startswith("green") else "white" if name.startswith("white") else "scene"
        clips.append(dict(name=name, summary=c["summary"], background=c["background"], framing=c["framing"],
                          branding=c["branding"], cutout=c["cutout"], beat=c["beat"], use=c["use"],
                          bgtype=bgtype, rows=c["rows"],
                          reels=[r[0] for r in REELS if r[4] == name]))
    reels = [dict(file=r[0], num=r[0].split("_")[2], pillar=r[1], hook=r[2], punch=r[3], clip=r[4],
                  bg=r[5], bgname=BG[r[5]][0] if r[5] else "Original scene", plan=r[6]) for r in REELS]
    bgs = [dict(key=k, name=v[0], license=v[1], url=v[2], used=[r[0] for r in REELS if r[5] == k]) for k, v in BG.items()]
    data = dict(clips=clips, reels=reels, plan=plan, pillars=PILLARS, bgs=bgs,
                tomake=[dict(name=a, why=b, priority=c, kind=d) for a, b, c, d in TO_MAKE],
                emotion_need=emotion_need)
    tpl = open(os.path.join(HERE, "dashboard_template.html")).read()
    open(os.path.join(OUT, "index.html"), "w").write(tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False)))
    print("wrote", os.path.join(OUT, "index.html"))

if __name__ == "__main__":
    main()
