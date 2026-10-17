# JARVIS AI — Python (Termux)

Ye ek Termux terminal assistant hai. Text ya voice se baat karein, Gemini se jawab lein,
aur phone ke kuch kaam (torch, volume, YouTube, settings, alarm, dialer draft) karwaayein.

## 1. Termux setup (ek baar)

```bash
pkg update && pkg upgrade -y
pkg install -y python git termux-api
pip install -r requirements.txt
```

Play Store ya F-Droid se **Termux:API** app bhi install karein. Voice, torch, volume aur battery
ke liye ye zaroori hai. Phone me Termux:API ko Microphone aur baaki permissions dein.

## 2. Project chalana

```bash
cd ~/jarvis-ai          # zip extract karne ke baad wala folder
python main.py
```

## 3. Gemini API key (ek baar)

1. Google AI Studio (aistudio.google.com) se API key banayein.
2. JARVIS ke andar: `/setkey` likhein, key paste karein (screen par nahi dikhegi).
3. `/test` se check karein. `Connected` aana chahiye.

Key `~/.jarvis/secrets.json` me save hoti hai, aur file permission sirf aapke app user ke liye 600 hai.
Ye Android Keystore jaisi hardware encryption nahi hai. Personal use ke liye theek hai, lekin
key ko kisi ke saath share na karein. Aap chahein to `GEMINI_API_KEY` environment variable bhi set kar sakte hain.

Model galat ho to: `/set gemini_model gemini-2.5-flash` (ya jo model Google dikhaye).

## 4. Voice

- `v` likhkar Enter dabayein, phir bolein. Ye push-to-talk hai.
- Jawab bolkar sunaya jata hai. Band karne ke liye `/speak off`.
- Hindi bolne ke liye TTS language `hi-IN` hai. Agar Hindi voice install nahi hai to `/set tts_language en-US` karein.
- Bolte waqt Ctrl+C dabane se bolna ruk jata hai.

Wake-word (bina bole sunna) implement nahi hai. Termux me background mic chalana battery aur privacy ke liye
sahi nahi hai, isliye ye push-to-talk hi rakha gaya hai.

## 5. Kya-kya kar sakti hai

| Aap bolein | JARVIS kya karegi |
|---|---|
| "torch on karo" / "torch band" | Flashlight (Termux:API) |
| "volume badhao" / "volume kam karo" | Music volume badhana/kam karna |
| "battery kitni hai" | Battery % aur status |
| "wifi settings kholo" | Settings screen (`am start`) |
| "YouTube kholo" | YouTube app/site |
| "Arijit Singh ka romantic gaana chalao" | YouTube par search khulta hai |
| "camera kholo" | Camera app |
| "call 98765 43210 karo" | Pehle confirm, phir dialer me number bhar kar khulta hai (call aap dabayenge) |
| "message 98765 43210: kal milte hain" | Messages app me draft (send aap dabayenge) |
| "Connaught Place ka rasta dikhao" | Google Maps me directions |
| "kal subah 7 baje ka alarm" | Clock app me alarm pre-fill (save aap karenge) |
| "5 minute ka timer" | Clock app me timer |
| "time kya hai" / "aaj ki date" | Local time |
| "mausam kaisa hai in Mumbai" | Open-Meteo se live mausam aur baarish ki sambhavna |
| "news batao" / "AI news" | Google News se headlines |
| "100 USD to INR" | Frankfurter se live rate |
| "task add doodh lena" / "tasks dikhao" | Local task list |
| "yaad rakho mujhe chai pasand hai" | Preference memory me save |

Baaki sab baatein Gemini ke paas jaati hain.

## 6. Settings

`/settings` se dekhein, `/set <key> <value>` se badlein:
- `affection_level` 0–3 (neutral se affectionate)
- `response_length` short / medium / long
- `nickname`, `tts_language`, `speech_rate`
- `memory_enabled` on/off, `/memory clear` se sab memory delete
- `default_city`, `news_language`, `news_region`

Settings `~/.jarvis/config.json` me save hoti hain aur app band karne ke baad bhi rehti hain.

## 7. Tests

```bash
cd ~/jarvis-ai
python -m unittest discover -s tests -t . -v
```

## 8. Known limitations (sach)

- Gemini ka real response, Termux:API ke voice/torch aur live data (mausam, news, rate) internet aur
  permissions par depend karte hain. Ye sab maine sandbox me chalakar verify nahi kiya hai; pehli
  run par error aaye to `~/.jarvis/jarvis.log` dekhein.
- `am start` aur `monkey` kuch naye Android versions par block ho sakte hain. Tab JARVIS error bolega,
  "khul gaya" nahi bolega.
- Alarm aur timer app me sirf pre-fill hote hain; save aapko karna hota hai.
- Call aur message kabhi auto-send nahi hote; hamesha aap confirm/send karte hain.
- Gemini key Termux me file me save hoti hai (Keystore nahi). Production distribution ke liye backend chahiye.
- Hindi bolna device par installed TTS voice par depend karta hai.

## Troubleshooting

- `termux-torch: command not found` → Termux:API app aur `pkg install termux-api` dono zaroori hain.
- `API key galat ya band hai` → `/setkey` se naya key dalein; Google AI Studio me key active check karein.
- `Rate limit` → thodi der ruk kar try karein; free quota limited hota hai.
- Voice `Kuch sunai nahi diya` → Termux:API ko mic permission dein aur phir se `v` bolein.
- Logs: `cat ~/.jarvis/jarvis.log`
