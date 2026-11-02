"""Builds the Keep reel studio dashboard (a single HTML page + media folder).

Usage: python3 -I tools/build_dashboard.py <out_dir>
Content to edit: REELS and BG below, plan/ideas.py (30-day plan), plan/clip_prompts.py (clips to make + prompts),
tools/write_timelines.py (base clip timelines). Layout: tools/dashboard_template.html.
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
    "city-dusk-a": ("Japanese street at dusk", "Unsplash", "https://unsplash.com/photos/laQwB9ixkyk"),
    "airport-gate-b": ("Airport gate", "Unsplash", "https://unsplash.com/photos/3aoDO4XmRH0"),
    "house-party-a": ("Party with golden lights", "Unsplash", "https://unsplash.com/photos/bscyZhPghTY"),
    "bedroom-night-a": ("Bedside lamp at night", "Unsplash", "https://unsplash.com/photos/XhLdjyQQi2I"),
    "city-dusk-b": ("Japan street crossing at dusk", "Unsplash", "https://unsplash.com/photos/QWrtDkkfDY0"),
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
    ("keep_reel_20_city_one-good-trip-photo", "funny", "When ONE trip photo finally doesn't make me look like a potato 🥔", "Posting it everywhere ✨", "green_strut-turn_fullbody", "city-dusk-a", None),
    ("keep_reel_21_airport_freed-23gb-before-trip", "storage", "Me after freeing 23 GB the night before the trip ✈️", "Bring on the 4,000 sunset pics 🌅", "green_strut-turn_fullbody", "airport-gate-b", None),
    ("keep_reel_22_dunes_jump-shot-attempt-48", "fails", "Jump shot attempt #48 🏜️", "Finally nailed it. Retiring now 😌", "green_strut-turn_fullbody", "desert-dunes", None),
    ("keep_reel_23_party_only-good-group-photo", "life", "Walking away after taking the ONLY good group photo 📸", "Photographer of the year 🏆", "green_strut-turn_fullbody", "house-party-a", None),
    ("keep_reel_24_bedroom_deleted-200-photos-of-ex", "life", "Me after finally deleting 200 photos of my ex 🫡", "Storage: freed. Heart: also freed ✨", "green_strut-turn_fullbody", "bedroom-night-a", None),
    ("keep_reel_25_japan_steps-and-photos-day-3", "travel", "Day 1 in Tokyo with my girlfriend ⛩️ · Steps 31,204 · Photos 1,206", "Her: 1,204 photos · Him: 2. Both from behind. 😐", "green_couple-phones-swap_fullbody", "city-dusk-a", None),
    ("keep_reel_26_japan-crossing_600-identical-photos", "travel", "Shibuya crossing 🚦 Her: again, you blinked · Him: crossed it 6 times", "", "green_couple-phones-swap_fullbody", "city-dusk-b", None),
    ("keep_reel_27_airport_only-a-few-photos", "travel", "Japan trip, day 0. We're at the gate. ✈️", "Her camera roll already: 1,107 📸 · 214 are of the plane", "green_couple-phones-swap_fullbody", "airport-gate-b", None),
    ("keep_reel_28_pier_312-sunset-photos", "fails", "She took 312 photos of the sunset. The sunset was 4 minutes long. 🌅", "", "green_couple-phones-swap_fullbody", "pier-sunset", None),
    ("keep_reel_29_hotel_delete-bad-trip-photos", "storage", "Hotel, 1am. Let's delete the bad trip photos 🫠", "Him: deleted 212 · Her: deleted 0 · 38 Lawson egg sandwich photos: memories 🥪", "green_couple-phones-swap_fullbody", "bedroom-night-a", None),
]

from clip_prompts import CLIPS as TO_MAKE_CLIPS, REFERENCES, prompt_for

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
    snd = os.path.join(HERE, "..", "sounds")
    library = json.load(open(os.path.join(snd, "library.json")))
    cues = json.load(open(os.path.join(snd, "reel_sounds.json")))
    trending = json.load(open(os.path.join(snd, "trending_tracks.json")))
    for r in reels:
        r["sounds"] = cues.get(r["file"], [])
    for s_ in library:
        s_["reels"] = [r["num"] for r in reels if any(c["sound"] == s_["id"] for c in r["sounds"])]
    data = dict(clips=clips, reels=reels, sounds=library, trending=trending, plan=plan, pillars=PILLARS, bgs=bgs,
                tomake=[dict(id=c["id"], name=c["name"], why=c["why"], priority=c["priority"], kind=c["kind"],
                             beat=c["beat"], file=c["file"], prompt=prompt_for(c)) for c in TO_MAKE_CLIPS],
                refs=[dict(file=f, caption=cap) for f, cap in REFERENCES],
                emotion_need=emotion_need)
    # The page (index.html) is a fixed template; all content lives in data.json.
    # Viewer edits (status, prompt overrides, notes, posted/views) live in the dashboard's
    # own database, so rebuilding data.json never overwrites them.
    import shutil
    shutil.copy(os.path.join(HERE, "dashboard_template.html"), os.path.join(OUT, "index.html"))
    json.dump(data, open(os.path.join(OUT, "data.json"), "w"), ensure_ascii=False, indent=1)
    print("wrote", os.path.join(OUT, "index.html"), "and data.json")

if __name__ == "__main__":
    main()
