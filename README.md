# নিজের খাতা · Nijer Khata (Self Ledger, mj-ahmad)

শেখা, কাজ, স্বাস্থ্য, ইমান ও আত্মবিশ্লেষণের একটি শান্ত, উত্তরাধিকারযোগ্য খাতা।
কোনো বিল্ড স্টেপ নেই। বাংলা, English ও العربية তিন ভাষায় চলে।

## শুরু করুন

```bash
./khata doctor            # ফাইলগুলো ঠিক আছে কি না দেখুন
./khata start             # ডেটা যাচাই করে http://127.0.0.1:8000 এ ড্যাশবোর্ড চালু করুন
```

## কমান্ড (khata)

| কাজ | কমান্ড |
|---|---|
| সার্ভ ও খোলা | `./khata start [PORT]` · `./khata open` |
| অগ্রগতি লেখা | `./khata log "আজকের পড়া" --category learning --mood 4` |
| পূর্ণ এন্ট্রি | `./khata add "Heading" "Description" --body-file notes.md --tag a,b` |
| ফাইল যুক্ত | `./khata add "Heading" "Desc" --add-file ./proof.pdf` |
| শেষ এন্ট্রি | `./khata list --limit 10` |
| অবস্থা ও সারসংক্ষেপ | `./khata status` |
| সময় (ঢাকা + UTC) | `./khata time` |
| শেখার বিষয় | `./khata learn list` · `./khata learn open geojson` |
| শেখার পেজ তৈরি | `./khata learn build` |
| শেয়ার লিংক বদলান | `./khata url https://your-address/nijer-khata` |
| ব্যাকআপ | `./khata backup` |
| সাহায্য | `./khata help` |

## ফোল্ডারের গঠন

```
index.html          ড্যাশবোর্ড (splash + হোম পেজ, লাইভ ঢাকা ঘড়ি, last update)
khata               কমান্ড শেল
life.py             এন্ট্রি, ID, চেকসাম, ভ্যালিডেশন
data.json           সব এন্ট্রি (নতুনটা আগে)
registry.json       LIFE ও REG ID কাউন্টার
site.json           শেয়ার লিংকের মূল ঠিকানা
learn/              শেখার হাব
  subjects.json     বিষয় ও ধাপের তালিকা (এটি সম্পাদনা করুন)
  build.py          subjects.json থেকে পেজ তৈরি করে
  index.html        শেখার হাব
  <slug>/index.html প্রতিটি বিষয়ের আলাদা পেজ
terminal/           ব্রাউজার টার্মিনাল (help, time, status, open …)
attachments/        --add-file দিয়ে যুক্ত ফাইল
assets/             লোগো, আইকন, OG ছবি (সব branding ফাইল এখানে)
```

## নতুন বিষয় যোগ করা

1. `learn/subjects.json` এর `subjects` তালিকায় একটি ব্লক যোগ করুন (`slug`, `group`, `name`, `summary`, `phases`)।
2. `./khata learn build` চালান। নতুন পেজ `learn/<slug>/` এ তৈরি হবে এবং হাবে দেখা যাবে।
3. শেখার অগ্রগতি লিখতে: `./khata log "..." --category learning --tag <slug>`

গ্রুপ বদলাতে বা নতুন গ্রুপ যোগ করতে `groups` অংশটি সম্পাদনা করুন।

## শেয়ার প্রিভিউ (WhatsApp, Messenger, Telegram)

প্রিভিউ ছবি `assets/branding/og/og-1200x630.png`। সম্পূর্ণ ঠিকানা লাগে বলে প্রথমবার আপনার আসল ঠিকানা দিন:

```bash
./khata url https://mj-ahmad.github.io/mj/nijer-khata
```

এটি `index.html` ও সব `learn/` পেজের লিংক বদলে দেয়।

## MJ Ahmad সাইটের সাথে সম্পর্ক

এই ফোল্ডারটি `mj` সাইটের ভেতরে `nijer-khata/` নামে রাখা হয়েছে। তাই mj সাইটের প্রজেক্ট কার্ড থেকে এখানে আসা যায়, আর এখান থেকে "← MJ Ahmad" লিংকে ফেরা যায়। আলাদা জায়গায় রাখলে `learn/build.py` ও `index.html` এর মূল-সাইট লিংক (`../`) ঠিক করে নিতে হবে।

## আসল Bash টার্মিনাল (Ubuntu)

ব্রাউজারের `terminal/` পেজ একটি **ডেমো**। সেখানে শুধু কয়েকটি কমান্ড চলে, আসল bash চলে না। আসল shell পেতে দুটি পথ আছে।

### পথ ১: নিজের কম্পিউটারে (Ubuntu বা WSL)

Windows হলে আগে Ubuntu ইন্সটল করুন (PowerShell, administrator হিসেবে):

```powershell
wsl --install -d Ubuntu
```

তারপর Ubuntu-র ভেতরে প্রজেক্টে যান (Windows ড্রাইভ `/mnt/c/...` হিসেবে থাকে) এবং:

```bash
./khata setup              # git, Python 3 + pip + venv + pipx, Node.js LTS, .NET SDK 8
./khata doctor             # কোন টুল আছে তার তালিকা
./khata shell              # প্রজেক্ট ফোল্ডারে bash শেল
./khata start              # ড্যাশবোর্ড চালু করুন
```

`khata setup` বারবার চালালেও সমস্যা নেই। .NET অন্য ভার্সনে চাইলে: `DOTNET_CHANNEL=9.0 ./khata setup --no-node`।

### পথ ২: Docker দিয়ে ব্রাউজারে Ubuntu bash

এটি একটি আলাদা Ubuntu 24.04 কন্টেইনার বানায় এবং ttyd দিয়ে ব্রাউজারে bash দেখায়। আপনার computer-এই শুধু চলে।

```bash
cd setup
cp .env.example .env       # TTYD_PASS-এ লম্বা পাসওয়ার্ড দিন
docker compose up -d --build
```

- ব্রাউজারে খুলুন: `http://127.0.0.1:7681` (TTYD_USER / TTYD_PASS দিয়ে লগইন)
- কন্টেইনারের ভেতরে `./khata setup` দিলে সব টুল ইন্সটল হবে।
- ড্যাশবোর্ড: কন্টেইনারে `./khata start`, তারপর `http://127.0.0.1:8000`।
- প্রজেক্ট ফোল্ডার কন্টেইনারের `/root/nijer-khata`-এ mount করা, তাই `data.json` ও `attachments/` আপনার কম্পিউটারেই থাকে।

**নিরাপত্তা:** এই শেল পুরো কন্টেইনারের নিয়ন্ত্রণ দেয়। পোর্ট শুধু `127.0.0.1`-এ খোলা থাকে। এটি কখনো public ইন্টারনেটে বা GitHub Pages-এর লিংকে দেবেন না। দূর থেকে ব্যবহার করতে হলে SSH tunnel ব্যবহার করুন (`ssh -L 7681:127.0.0.1:7681 user@server`)। `setup/.env` কখনো git-এ commit করবেন না।

GitHub Pages স্ট্যাটিক সাইট, তাই সেখানে আসল shell চালানো যায় না। ওয়েবসাইটে শুধু ডেমো টার্মিনাল থাকবে।

## ইনহেরিট করা

সম্পূর্ণ ফোল্ডার কপি করুন। `data.json`, `registry.json` ও `attachments/` একসাথে রাখতে হবে। `./khata backup` দিয়ে সময়-সিলযুক্ত আর্কাইভ বানানো যায়।

Plain files, no build step, Bangla · English · Arabic.
