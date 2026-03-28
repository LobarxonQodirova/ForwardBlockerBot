# 🚫📨 Telegram Forward Blocker Bot

Guruhingizni keraksiz forwardlardan himoya qiluvchi, avtomatik moderatsiya qiluvchi, kuchli va professional Telegram boti. U forward qilingan xabarlarni darhol o‘chiradi va qoidabuzarga bosqichma-bosqich cheklovlarni qo‘llaydi.

> **Nima uchun bu bot kerak?**
>
> Telegram guruhlarda forward qilingan xabarlar ko‘pincha spam, reklama yoki begona kanallardan keladi. Bu esa guruh muhitini buzadi, tartibni yo‘qotadi va ishtirokchilarga noqulaylik tug‘diradi. Ushbu bot yordamida siz guruhingizni avtomatik ravishda toza, tartibli va xavfsiz saqlaysiz. Har bir forward qilingan xabar darhol o‘chiriladi va qoidabuzar foydalanuvchi ogohlantiriladi, takroriy buzarlikda esa bosqichma-bosqich jazo kuchayadi. 
>
> **Botdan foydalangan holda siz:**
> - Guruhda tartibni avtomatik saqlaysiz
> - Spam va reklama tarqalishini oldini olasiz
> - Foydalanuvchilarni adolatli va shaffof jazolaysiz
> - Oson va tez sozlash orqali vaqt va asabni tejaysiz

---

## ✨ Nimalar qila oladi? (Features)
- 🧹 Forward qilingan har bir xabarni avtomatik O‘CHIRADI
- ⛔ Jazolar zanjiri (1 KUN ichida):
  - 1-marta forward → 🔇 5 daqiqa mute
  - 2-marta forward → 🔇 15 daqiqa mute
  - 3-marta forward → 🔇 30 daqiqa mute
  - 4-marta forward → 🚷 BAN (guruhdan chiqarish)
- 🧠 Har bir chat va foydalanuvchi bo‘yicha hisob-kitoblar SQLite bazada saqlanadi (kunlik)
- 🛡️ Admin/ownerlar jazolanmaydi (ammo forwardlari baribir o‘chiriladi)
- ⚙️ Polling (long-poll) bilan ishlaydi — server, webhook shart emas
- 📊 Statistika va monitoring uchun tayyor baza
- 🔔 Qisqa xabarlar orqali guruh a’zolarini ogohlantiradi
- 🏆 Minimal resurs, maksimal natija

---

## 🗂️ Loyiha tuzilmasi (Project Structure)
```text
.
├─ bot.py               # Aiogram v3 bot kodi: handlerlar, jazolar, polling
├─ requirements.txt     # Loyiha uchun kerakli kutubxonalar
├─ forwards.db          # SQLite ma’lumotlar bazasi (avtomatik yaratiladi)
└─ README.md            # Ushbu qo‘llanma
```

---

## 🚀 O‘rnatish (Installation)

### 1) Loyihani yuklab olish
```bash
git clone https://github.com/NodirUstoz/TelegramBlockerBot.git
cd TelegramBlockerBot
# yoki mavjud papkangizga o‘ting
cd D:\Downloads\TelegramBlockerBot
```

### 2) Virtual muhit (venv) yaratish va faollashtirish
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
```
> Agar faollashmasa, PowerShell Execution Policy sabab bo‘lishi mumkin: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` (Administrator PowerShell’da)

### 3) Kutubxonalarni o‘rnatish
```powershell
pip install -r requirements.txt
```

### 4) `.env` faylini yaratish va sozlash
Loyiha ildizida `.env` fayl yarating:
```env
BOT_TOKEN=123456789:ABCDEF...        # BotFather’dan olingan token
ADMIN_IDS=111111111,222222222        # (ixtiyoriy) adminlar ID ro‘yxati, vergul bilan
```
> Eslatma: `ADMIN_IDS` hozircha majburiy emas. Kelgusida admin komandalar/tahlillar uchun ishlatiladi.

---

## ▶️ Ishga tushirish (Usage)

### 1) Botni ishga tushirish
```powershell
python bot.py
```

### 2) Guruhga ulash
1. Botni guruhga qo‘shing
2. Botga quyidagi admin huquqlarini bering:
   - Delete messages
   - Restrict members
3. Tayyor! Bot forward xabarni o‘chiradi va qoidaga muvofiq jazo qo‘llaydi.

> Tavsiya: Guruh qoidalarida “forward taqiqlangan” degan bandni ham yozib qo‘ying ✅

---

## 🔧 Konfiguratsiya tafsilotlari
- `.env` fayli `python-dotenv` orqali avtomatik yuklanadi (`load_dotenv()`).
- `BOT_TOKEN` o‘qilmasa — bot ishga tushmaydi va aniq xabar bilan to‘xtaydi.
- Ma’lumotlar bazasi `forwards.db` faylida saqlanadi; har bir chat va foydalanuvchi bo‘yicha `count` oshirib boriladi.
- Kod to‘liq asinxron va zamonaviy Aiogram v3 handler/filtirlari asosida yozilgan.

---

## 🧩 Texnologiyalar (Tech Stack)
- 🐍 Python 3.11+
- 🤖 Aiogram v3 (modern handlerlar va filtrlar)
- 🗄️ SQLite + aiosqlite (async DB)
- 🔐 python-dotenv (.env konfiguratsiyasi)

---

## 🧭 Ishlash jarayoni (How It Works)
1. Forward qilingan xabar kelishi bilan handler ishga tushadi (`F.forward_origin`).
2. Xabar darhol o‘chiriladi (botda “Delete messages” ruxsati bo‘lishi kerak).
3. Foydalanuvchining forwardlar soni bazada oshiriladi.
4. Admin/owner bo‘lmasa va botda “Restrict members” ruxsati bo‘lsa, quyidagi jazo qo‘llanadi:
   - 1 → 5 daqiqa mute
   - 2 → 15 daqiqa mute
   - 3 → 30 daqiqa mute
   - 4 → Ban
5. Qisqa bildirish xabari bilan guruh xabardor qilinadi.

---

## 🧪 Tezkor tekshiruv ro‘yxati (Checklist)
- `.venv` faollashganmi? `(.venv)` belgisi terminalda ko‘rinadimi?
- `pip install -r requirements.txt` muvaffaqiyatli o‘tdimi?
- `.env` faylda `BOT_TOKEN` to‘g‘rimi?
- Bot guruhda adminmi? “Delete messages” va “Restrict members” berilganmi?
- Forward xabarni haqiqatan forward sifatida yuboryapsizmi (oddiy copy-paste emas)?

---

## 🛠️ Muammolar va yechimlar (Troubleshooting & FAQ)
**Q:** VS Code “Import ... could not be resolved” deydi.  
**A:** To‘g‘ri interpreterni tanlang: Ctrl+Shift+P → Python: Select Interpreter → `.venv\Scripts\python.exe`. So‘ng `pip install -r requirements.txt` ni aynan shu muhitda bajaring. Oynani Reload qiling.

**Q:** `BOT_TOKEN environment variable is not set` chiqdi.  
**A:** `.env` fayl loyihaning ildizida ekanini tekshiring. Tokenni to‘g‘ri yozganingizga ishonch hosil qiling. `python-dotenv` o‘rnatilgan bo‘lishi kerak (requirements.txt ichida bor).

**Q:** Forward aniqlanmayapti.  
**A:** Xabar haqiqatan “forward” bo‘lishi kerak. Telegram’ning “Forward” funksiyasi orqali yuboring; clientdan “copy-paste” qilingan xabar forward sanalmaydi.

**Q:** Bot xabarni o‘chirayapti, lekin jazo qo‘llamayapti.  
**A:** Botga “Restrict members” ruxsati ham berilganligiga ishonch hosil qiling.

**Q:** Tokenim oshkor bo‘lib qoldi.  
**A:** BotFather’dan tokenni yangilang (oldisini bekor qiling) va `.env` faylni faqat lokalda saqlang. Git’ga yubormang.

---

## 🗺️ Roadmap (Rejalashtirilgan imkoniyatlar)
- 🌐 Webhook rejimi (Docker, Cloud deploy)
- 🧑‍💼 Admin komandalar: statistikani ko‘rish, reset, whitelist/blacklist
- 📊 Oddiy web-panel / grafikli statistika
- 📁 CSV/Excel eksport
- 🧩 Forward manbasini filtrlash (faqat ruxsat berilgan kanallardan)

Agar g‘oya va fikrlaringiz bo‘lsa — Issue oching yoki PR yuboring!

---

## 🤝 Hissa qo‘shish (Contributing)
1. Reponi fork qiling
2. Feature branch yarating: `git checkout -b feature/your-feature`
3. O‘zgarishlarni kiriting va test qiling
4. Pull Request yuboring — qisqa tavsif va motivatsiya qo‘shing

---

## 🔒 Xavfsizlik tavsiyalari
- `.env` faylni hech qachon repoga qo‘shmang
- Tokenni faqat server/lokalda saqlang
- Token oshkor bo‘lsa — darhol yangilang

---

## 📜 Litsenziya (License)
MIT License — erkin foydalanish, nusxalash va o‘zgartirishga ruxsat beriladi. Mualliflik eslatmasini saqlang.

---

## 📫 Aloqa
Savollar va takliflar uchun Issues’dan foydalaning yoki PR yuboring. Botni yanada foydali qilishda birga harakat qilamiz! 🚀

