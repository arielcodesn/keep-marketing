"""Video-generator prompts for the base clips still to make.

Every prompt = CHARACTER + SETUP + the clip's own ACTION timeline + AVOID.
Edit CHARACTER / SETUP / AVOID once and every prompt updates. The dashboard also
lets you override a single prompt (stored in the dashboard, not here).
"""

REFERENCES = [
    ("01_front_fullbody_green.jpg", "Front, full body, on green: the target framing and size"),
    ("02_side_profile_green.jpg", "Side profile: body shape and cap from the side"),
    ("03_back_view.jpg", "Back view: plain black tee and cap from behind"),
    ("04_front_holding_phone.jpg", "Front, holding the phone at chest height"),
    ("05_cap_logo_closeup.jpg", "Cap logo close-up: two stacked white photo frames, black mountains, red heart"),
    ("06_shirt_keep_closeup.jpg", "Shirt close-up: white \"Keep\" lettering"),
]

CHARACTER = """CHARACTER (keep identical in every clip — match the reference images exactly):
A chubby, round golden-orange Syrian hamster, Pixar-style 3D animation, soft fluffy fur with a cream-white belly, cheeks and muzzle, small pink nose, pink inner ears, large glossy dark-brown eyes with white catchlights, tiny pink paws and feet. Stands upright on its hind legs like a person, about 2.5 heads tall, short stubby legs.
Wears a black baseball cap, brim facing forward, with the Keep logo centred on the front panel: two slightly offset stacked white photo frames with a black mountain silhouette inside and a small red heart at the top-right corner of the frames.
Wears a plain black crew-neck t-shirt with the word "Keep" printed across the chest in white, bold, rounded sans-serif lettering (capital K, lowercase eep). The back of the shirt is plain black.
When it holds a phone: a black smartphone with a triple rear camera, held in both paws at chest height, screen facing the hamster."""

SETUP = """SETUP:
Vertical 9:16, 1080x1920, 24 fps, exactly 10 seconds, one continuous shot.
Solid flat chroma-key green background and floor (#00FF00), evenly lit, no gradient, no shadows or reflections on the green, no props.
Full body in frame: hamster centred, feet at about 85% of the frame height, top of the cap at about 25%, a clear gap of green on every side. Same size and position as reference 01.
Locked-off camera at the hamster's chest height: no camera movement, no zoom, no cuts.
Soft, even studio lighting from the front. Minimal motion blur, crisp fur edges."""

AVOID = """AVOID:
No text, captions, watermarks or extra logos. Don't change the logo or the "Keep" lettering. No green tint on the hamster. No other characters or objects. Don't let the hamster leave the frame or touch the edges. No camera shake."""

CLIPS = [
    dict(id="sideeye", name="Side-eye / suspicious", file="green_side-eye_fullbody.mp4",
         priority="Make first", kind="new", beat="4.0s",
         why="Group photos, someone scrolling your phone, GC receipts",
         action="""ACTION (beat at 4.0s):
0–2s: Holds the phone at chest height, scrolling calmly with one thumb, neutral face.
2–4s: Scrolling slows; the hamster pauses, eyebrows begin to lower.
4.0s: BEAT. Without turning its head, it slowly slides its eyes to the side toward the camera: a suspicious side-eye with one eyebrow raised and lips pressed flat.
4–8s: Holds the side-eye, slowly leaning back a little, lowering the phone a few centimetres.
8–10s: A tiny slow head tilt while keeping the unimpressed side-eye. Ends still and holding the expression."""),
    dict(id="crying", name="Crying", file="green_crying_fullbody.mp4",
         priority="Make first", kind="new", beat="3.0s",
         why="Storage Full at the best moment, deleting photos of an ex",
         action="""ACTION (beat at 3.0s):
0–2s: Holds the phone at chest height, looking at it hopefully, small smile.
2–3s: Smile fades, bottom lip starts to wobble, eyes get shiny.
3.0s: BEAT. Bursts into dramatic cartoon crying: eyes squeezed shut, mouth open in a wail, big tears streaming down both cheeks.
3–8s: Keeps sobbing, shoulders shaking, hugs the phone to its chest.
8–10s: Lifts the phone and looks at the screen again through tears, sniffling, chin trembling."""),
    dict(id="panic", name="Panic, fast swiping", file="green_panic_fullbody.mp4",
         priority="Make first", kind="new", beat="2.0s",
         why="Hiding photos before someone sees, boarding pass lost in memes",
         action="""ACTION (beat at 2.0s):
0–2s: Holds the phone at chest height, scrolling casually, relaxed face.
2.0s: BEAT. Freezes, eyes go wide, ears flatten back in alarm, as if someone is coming.
2–7s: Frantically swipes and taps the screen with both thumbs at high speed, glancing nervously left and right, sweat drop on the forehead.
7–8.5s: Quickly hides the phone behind its back.
8.5–10s: Stands stiffly, smiling a big fake innocent smile at the camera."""),
    dict(id="facepalm", name="Facepalm", file="green_facepalm_fullbody.mp4",
         priority="Make first", kind="new", beat="4.0s",
         why="47 near-identical photos, zooming in on a plastic bag",
         action="""ACTION (beat at 4.0s):
0–3s: Holds the phone at chest height, scrolling with a hopeful, concentrating face.
3–4s: Stops scrolling, stares at the screen in disbelief, mouth flat.
4.0s: BEAT. Lowers the phone in one paw and slowly brings the other paw up to cover its face in a big facepalm.
4–8s: Holds the facepalm, shaking its head slowly inside the paw, a long exasperated sigh.
8–10s: Peeks out between its fingers at the phone, then closes the fingers again."""),
    dict(id="laugh-green", name="Laughing (green)", file="green_calm-to-laughing_fullbody.mp4",
         priority="Remake on green", kind="green", beat="5.5s",
         why="Used 45× in the plan; the current clip is on white, so every reel needs the slow AI cutout",
         action="""ACTION (beat at 5.5s), same performance as the existing white laughing clip:
0–3s: Holds the phone at chest height, looking at it with a small amused smile.
3–5s: The smile grows, cheeks puff, eyes squint, trying to hold back a laugh.
5.5s: BEAT. Bursts out laughing: eyes squeezed shut, mouth wide open showing the two front teeth, head tilting back slightly.
5.5–10s: Keeps laughing hard, little body bouncing, still holding the phone, never covering the shirt lettering."""),
    dict(id="shocked-green", name="Shocked (green)", file="green_calm-to-shocked_fullbody.mp4",
         priority="Remake on green", kind="green", beat="4.5s",
         why="Used 23×; number-reveal punchlines",
         action="""ACTION (beats at 4.5s and 6.5s), same performance as the existing white shocked clip:
0–4s: Looks down at the phone at chest height, scrolling calmly, neutral face.
4.5s: BEAT 1. Eyes widen, mouth opens slightly, a small gasp.
4.5–6.5s: Stares at the screen, frozen.
6.5s: BEAT 2. Looks up at the camera with a full jaw-drop: mouth in a round O, eyes huge.
6.5–10s: Holds the shocked face, ears perked straight up, completely still apart from a tiny blink."""),
    dict(id="angry-green", name="Angry → gives up (green, full body)", file="green_angry-to-defeated_fullbody.mp4",
         priority="Remake on green", kind="green", beat="5.5s",
         why="Used 17×; the current clip is stuck behind an office desk",
         action="""ACTION (beats at 2.5s, 5.5s and 8.5s):
0–2s: Holds the phone at chest height, scrolling, slightly frowning.
2.5s: BEAT 1. Gets angry: eyebrows down, gritting teeth, jabbing the screen hard with one finger.
2.5–5s: Jabs and swipes furiously, little growl, stamping one foot.
5.5s: BEAT 2. Throws both arms down in frustration, letting the phone dangle from one paw at its side.
5.5–8s: Glares at the camera, breathing hard.
8.5s: BEAT 3. Shoulders slump, ears droop, a defeated sad face looking down at the floor.
8.5–10s: Stays slumped and defeated."""),
    dict(id="sleepy-green", name="Sleepy → wide awake (green)", file="green_sleepy-to-wide-awake_fullbody.mp4",
         priority="Remake on green", kind="green", beat="3.0s",
         why="Used 10×; the current clip is stuck in the living room and cuts out badly",
         action="""ACTION (beats at 2.0s and 3.0s):
0–2s: Holds the phone at chest height, eyelids heavy, swaying slightly, nodding off.
2.0s: BEAT 1. Eyes fully close, head drops forward, dozing on its feet.
3.0s: BEAT 2. Jolts awake: eyes snap wide open, ears shoot up, staring at the phone.
3–6s: Brings the phone closer to its face, wide-eyed and alarmed.
6–10s: Stays wide awake, staring in disbelief at the screen, a slow blink at 8s."""),
    dict(id="dance-green", name="Dance (green)", file="green_dance_fullbody.mp4",
         priority="Upload if you have it", kind="green", beat="6.5s",
         why="Used 12×; you may already have this in another session, so upload it to base-clips/ before generating a new one",
         action="""ACTION (spin at 6.0–7.5s), same performance as the existing white dance clip, no phone:
0–6s: Happy little celebration dance on the spot: bouncing, swinging both fists side to side, small hops, big smile.
6.0–7.5s: BEAT. Does a full 360° spin on the spot (back to camera at 6.5s).
7.5–10s: Faces the camera again, grinning with teeth showing, fists up, still bopping."""),
    dict(id="laugh-point", name="Laughing, variation 2 (pointing at phone)", file="green_laughing-pointing_fullbody.mp4",
         priority="Nice to have", kind="variation", beat="4.5s",
         why="So 45 laughing reels don't all look the same",
         action="""ACTION (beat at 4.5s):
0–3s: Looks at the phone at chest height, eyebrows raised, curious.
3–4.5s: Snorts, smile spreading.
4.5s: BEAT. Turns the phone screen toward the camera and points at it with the other paw, laughing out loud, eyes squeezed shut.
4.5–10s: Keeps pointing at the screen and laughing, bending forward slightly, wiping a tear with the pointing paw at 8s."""),
    dict(id="shock-drop", name="Shocked, variation 2 (drops the phone)", file="green_shocked-drops-phone_fullbody.mp4",
         priority="Nice to have", kind="variation", beat="4.0s",
         why="A bigger reaction for the biggest numbers",
         action="""ACTION (beat at 4.0s):
0–3.5s: Holds the phone at chest height, scrolling calmly, neutral face.
4.0s: BEAT. Huge shock: eyes bulge, jaw drops, both paws fly up beside its face and the phone falls to the floor in front of its feet.
4–7s: Frozen with paws at its cheeks, staring at the camera, mouth wide open.
7–10s: Slowly looks down at the phone on the floor, then back up at the camera, still shocked."""),
]


def prompt_for(c):
    return "\n\n".join([
        f"10-second video of the Keep hamster mascot: {c['name'].lower()}. Use the attached reference images for the character, cap logo and shirt lettering.",
        CHARACTER, SETUP, c["action"], AVOID,
    ])
