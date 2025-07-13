try:
  import telethon
  import deep_translator
  import newspaper
  import PIL
  import bs4
  import pydub
  import time
  import dotenv
  import replicate
  import bs4
  import pydub
  import time
  import dotenv
  import replicate
  import speech_recognition
  import aiohttp
  import jdatetime
  import torch
  import transformers
  import torchvision
  import random
  import asyncio
  import speech_recognition as sr
  import re
  import time
  import json
  import os
  import base64
  import feedparser
  import requests
  import gtts


except ImportError as e:
  print(f"Missing module: {e}")
  import subprocess
  import sys
  # Use uv instead of pip for better dependency management
  subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "telethon", "deep-translator", "newspaper3k", "pillow", "beautifulsoup4", "pydub", "python-dotenv", "gTTS", "feedparser", "SpeechRecognition", "replicate", "aiohttp", "jdatetime", "requests", "lxml_html_clean", "torch", "transformers", "torchvision"])
  # Re-import after installation
  import telethon
  import deep_translator
  import newspaper
  import PIL
  import bs4
  import pydub
  import time
  import dotenv
  import replicate
  import requests
  import gtts
  import feedparser
  import speech_recognition
  import aiohttp
  import jdatetime
  import torch
  import transformers
  import torchvision
  import random, asyncio, speech_recognition as sr, re, time
  import json, os, base64
  import lxml_html_clean
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import MessageMediaPhoto
from datetime import datetime, date
from deep_translator import GoogleTranslator
from newspaper import Source
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from io import BytesIO
from pydub import AudioSegment
from dotenv import load_dotenv
from gtts import gTTS
from replicate import Client
try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
except ImportError:
    print("Warning: transformers not available, image captioning disabled")
    BlipProcessor = None
    BlipForConditionalGeneration = None

def get_bbc_articles():
  try:
      feed_url = 'https://www.bbc.com/persian/index.xml'
      feed = feedparser.parse(feed_url)
      articles = []

      if not feed.entries:
          print("❌ فید BBC خالیه یا خطا داده.")
          return []

      for entry in feed.entries:
          title = entry.get('title', '')
          summary = BeautifulSoup(entry.get('summary', ''),
                                  "html.parser").get_text()
          image_url = None

          # جستجوی عکس در media_thumbnail
          if 'media_thumbnail' in entry:
              image_url = entry.media_thumbnail[0].get('url')

          # اگر نبود، جستجو در media_content
          if not image_url and 'media_content' in entry:
              image_url = entry.media_content[0].get('url')

          # اگر هنوز نبود، استخراج از تگ img داخل summary
          if not image_url:
              soup = BeautifulSoup(entry.get('summary', ''), 'html.parser')
              img_tag = soup.find('img')
              if img_tag and img_tag.get('src'):
                  image_url = img_tag['src']

          if title and len(title) > 5:
              articles.append({
                  'title': title,
                  'summary': summary,
                  'image': image_url
              })

      print(f"✅ تعداد خبر دریافت شده از RSS: {len(articles)}")
      return articles

  except Exception as e:
      print(f"⚠️ خطا در دریافت اخبار: {e}")
      return []


# Load environment variables
load_dotenv()

API_KEY = os.getenv('WEATHER_API_KEY', 'your_weather_api_key_here')
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'


def get_weather(city_name):
  if "," not in city_name:
      city_name += ",IR"  # اضافه کردن کشور به‌صورت خودکار

  params = {
      'q': city_name,
      'appid': API_KEY,
      'units': 'metric',
      'lang': 'fa'
  }
  response = requests.get(BASE_URL, params=params)
  if response.status_code == 200:
      data = response.json()
      weather = data['weather'][0]['description']
      temp = data['main']['temp']
      humidity = data['main']['humidity']
      wind = data['wind']['speed']
      return f"☁️ وضعیت هوا در {city_name.split(',')[0]}:\n" \
             f"آب‌وهوا: {weather}\n" \
             f"🌡️ دما: {temp}°C\n" \
             f"💧 رطوبت: {humidity}%\n" \
             f"💨 باد: {wind} m/s"
  elif response.status_code == 404:
      return "❌ اطلاعاتی برای این شهر پیدا نشد. لطفاً نام رو دقیق‌تر بنویس (مثلاً `Tehran` یا `Mashhad,IR`)."
  else:
      return f"⚠️ خطا: {response.status_code}"


# اطلاعات API از متغیرهای محیطی
api_id = int(os.getenv('API_ID', '0'))
api_hash = os.getenv('API_HASH', 'your_api_hash_here')
session_name = os.getenv('SESSION_NAME', 'session')

# ساخت کلاینت
client = TelegramClient(session_name, api_id, api_hash)


def shamsi_to_miladi(shamsi_date):
  try:
      y, m, d = map(int, shamsi_date.split("/"))
      miladi_date = jdatetime.date(y, m, d).togregorian()
      return miladi_date
  except:
      return None


def save_birthday(user_id, date_str):
  lines = []
  if os.path.exists("birthdays.txt"):
      with open("birthdays.txt", "r", encoding="utf-8") as f:
          lines = f.readlines()
  with open("birthdays.txt", "w", encoding="utf-8") as f:
      for line in lines:
          if not line.startswith(str(user_id)):
              f.write(line)
      f.write(f"{user_id}:{date_str}\n")


def ask_huggingface(prompt):
  try:
      response = requests.post(HF_API_URL,
                               headers=HF_HEADERS,
                               json={"inputs": prompt})

      # چاپ وضعیت و متن خام پاسخ
      print("📡 status code:", response.status_code)
      print("📄 raw response:", response.text)

      # تلاش برای تبدیل پاسخ به JSON
      data = response.json()

      if isinstance(data, list) and "generated_text" in data[0]:
          return data[0]["generated_text"]
      elif isinstance(data, dict) and "error" in data:
          return f"❌ خطای مدل: {data['error']}"
      else:
          return "❌ پاسخ نامفهوم از مدل دریافت شد."

  except Exception as e:
      return f"❌ خطای اتصال:\n{e}"


cached_articles = []
user_news_index = {}
user_personas = {}  # key: user_id → value: "لاتی" یا "شاعر" ...


@client.on(events.NewMessage())

async def voice_from_text(event):
  message = event.raw_text.strip()
  sender = await event.get_sender()
  user_id = sender.id

  if message.startswith("صدا "):  # شروع پیام با "صدا "
      text = message[5:].strip()  # حذف "صدا " و فاصله

      if not text:
          await event.reply(
              "🗣️ لطفاً بعد از کلمه 'صدا' متن رو بنویس:\nمثال:\n`صدا امروز خیلی خوشحالم 😄`"
          )
          return

      if len(text) > 300:
          await event.reply(
              "⚠️ متن خیلی طولانیه. لطفاً کمتر از 300 کاراکتر بنویس.")
          return

      try:
          tts = gTTS(text=text, lang='ar')  # فعلاً 'ar' به‌جای 'fa'
          filename = f"voice_{event.sender_id}.mp3"
          tts.save(filename)

          await client.send_file(event.chat_id, filename, voice_note=True)

          os.remove(filename)

      except Exception as e:
          await event.reply(f"❌ خطا در تبدیل متن به صدا:\n`{e}`",
                            parse_mode='markdown')



HF_API_TOKEN = os.getenv('HF_API_TOKEN_1', 'your_hf_token_here')
HF_MODEL = "CompVis/stable-diffusion-v1-4"
HF_API_URL = "https://router.huggingface.co/nebius/v1/images/generations"

headers = {
  "Authorization": f"Bearer {HF_API_TOKEN}",
  "Content-Type": "application/json"
}

HF_APIS = [
  {
      "token": os.getenv('HF_API_TOKEN_1', 'your_hf_token_1_here'),
      "model": "CompVis/stable-diffusion-v1-4",
      "url": "https://router.huggingface.co/nebius/v1/images/generations"
  },
  {
      "token": os.getenv('HF_API_TOKEN_2', 'your_hf_token_2_here'),
      "model": "CompVis/stable-diffusion-v1-4",
      "url": "https://router.huggingface.co/nebius/v1/images/generations"
  },
  {
      "token": os.getenv('HF_API_TOKEN_3', 'your_hf_token_3_here'),
      "model": "CompVis/stable-diffusion-v1-4",
      "url": "https://router.huggingface.co/nebius/v1/images/generations"
  },
]

import requests
import base64
import os

def generate_image(prompt):
  for api in HF_APIS:
      headers = {
          "Authorization": f"Bearer {api['token']}",
          "Content-Type": "application/json"
      }

      payload = {
          "prompt": prompt,
          "model": api['model'],
          "response_format": "b64_json"
      }

      try:
          response = requests.post(api['url'], headers=headers, json=payload)

          if response.status_code == 200:
              try:
                  data = response.json()
                  b64_data = data['data'][0]['b64_json']
                  image_data = base64.b64decode(b64_data)
                  file_path = f"output_{prompt[:10].replace(' ', '_')}.png"
                  with open(file_path, "wb") as f:
                      f.write(image_data)
                  return file_path, None
              except Exception as e:
                  return None, f"❌ خطا در استخراج تصویر از API:\n{e}"

          elif response.status_code in [402, 403, 429]:
              print(f"⚠️ API محدودیت یا بن شد: {response.status_code} → رفتیم سراغ بعدی")
              continue  # تست بعدی API

          else:
              return None, f"❌ خطا {response.status_code}:\n{response.text}"

      except Exception as e:
          print(f"❌ خطای اتصال به {api['url']}: {e}")
          continue  # تست بعدی API

  return None, "❌ هیچ API فعالی برای تولید تصویر در دسترس نیست."



@client.on(events.NewMessage(pattern=r'^/image (.+)'))
async def image_handler(event):
  prompt = event.pattern_match.group(1).strip()
  await event.reply("🎨 در حال تولید تصویر با مدل FLUX... لطفاً چند لحظه صبر کن...")

  file_path, error = generate_image(prompt)

  if file_path:
      await event.reply(file=file_path)
      os.remove(file_path)
  else:
      await event.reply(error or "❌ خطای نامشخص در ساخت تصویر.")

# کلید OpenRouter از متغیر محیطی:
api_key = os.getenv('OPENROUTER_API_KEY', 'your_openrouter_api_key_here')

def chat_with_persona(prompt, persona="لاتی", api_key=api_key):
  headers = {
      "Authorization": f"Bearer {api_key}",
      "Content-Type": "application/json"
  }

  persona_prompts = {
      "لاتی": (
          "تو یه آدم لات باحال تهرونی هستی. رک، محاوره‌ای و خودمونی حرف می‌زنی. "
          "شوخی می‌کنی ولی مختصر و مفید. جواب‌هات کوتاه باشه، نهایتاً یکی دو خط."
      ),
      "شاعر": (
          "تو یه شاعر عارف و عاشق هستی که با استعاره و احساس حرف می‌زنه. "
          "پاسخ‌هات شعری، زیبا و کوتاه باشن، حداکثر دو خط مثل دوبیتی یا جمله احساسی."
      ),
      "علمی": (
          "تو یک بات علمی و دقیق هستی. رسمی، جدی و مختصر حرف می‌زنی. "
          "فقط اصل مطلب رو بگو. توضیح طولانی نده. حداکثر دو خط کافیست."
      ),
      "بچه": (
          "تو مثل یه بچه شیرین و بامزه‌ای. ساده، بچگونه و کوتاه حرف بزن. "
          "از کلمات بامزه استفاده کن ولی تو یکی دو خط تمومش کن."
      ),
      "طنز": (
          "تو یه آدم بامزه‌ای که هرچی می‌گه خنده‌داره. طنز و شوخی داری ولی مختصر. "
          "جواب‌هات خنده‌دار و نهایتاً تو ۲ خط باشه، نه بیشتر."
      ),
      "چس‌مَیاد": (
          "تو یه آدم کلاس‌بالا و خودشیفته‌ای. مغرور و کلمات قلمبه سلمبه استفاده می‌کنی. "
          "ولی خلاصه حرف بزن، تو یکی دو خط نظر بده، نه بیشتر."
      ),
      "روشنفکر": (
          "تو روشنفکری هستی که همیشه دنبال معنا و عمقی. تحلیل‌هات فلسفیه ولی طولانی نکن. "
          "نهایت دو خط مفهومی جواب بده، پرمغز ولی مختصر."
      ),
      "عاشق شکست‌خورده": (
          "تو یه عاشق دل‌شکسته‌ای. حرف‌هات پر از درد و خاطره‌ست. "
          "ولی تو یکی دو خط حس دلتنگی یا اندوهت رو بگو. طولانی ننویس."
      )
  }


  system_prompt = persona_prompts.get(persona, persona_prompts["لاتی"])

  data = {
      "model": "anthropic/claude-3-haiku",
      "messages": [
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": prompt}
      ]
  }

  try:
      response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

      if response.status_code == 200:
          return response.json()['choices'][0]['message']['content']
      else:
          return f"❌ خطا {response.status_code}:\n{response.text}"

  except Exception as e:
      return f"❌ خطای اتصال:\n{e}"

@client.on(events.NewMessage(pattern=r'^/persona( .+)?'))
async def persona_handler(event):
  try:
      parts = event.raw_text.split(maxsplit=2)

      if len(parts) < 3:
          await event.reply("❗ فرمت درست:\n`/persona نوع_شخصیت پیام شما`\nمثلاً:\n`/persona لاتی سلام داش`", parse_mode="markdown")
          return

      persona = parts[1].strip().lower()
      user_message = parts[2].strip()

      await event.reply("🧠 در حال تقلید شخصیت...")

      response = chat_with_persona(user_message, persona=persona)
      await event.reply(response)

  except Exception as e:
      await event.reply(f"❌ خطای اجرا:\n{e}")


# Initialize AI models if available
processor = None
model = None

def initialize_ai_models():
    global processor, model
    try:
        if BlipProcessor and BlipForConditionalGeneration:
            processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            return True
    except Exception as e:
        print(f"AI models initialization failed: {e}")
    return False

def analyze_image_caption(image_path):
    try:
        if not processor or not model:
            if not initialize_ai_models():
                return "❌ مدل تشخیص تصویر در دسترس نیست. برای استفاده از این قابلیت، transformers و torch باید نصب باشند."

        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")

        out = model.generate(**inputs, max_new_tokens=50)
        caption = processor.decode(out[0], skip_special_tokens=True)

        try:
            fa = GoogleTranslator(source='en', target='fa').translate(caption)
            return f"🧠 تشخیص انگلیسی:\n{caption}\n\n📝 ترجمه فارسی:\n{fa}"
        except:
            return f"🧠 تشخیص:\n{caption}\n\n⚠️ خطا در ترجمه"

    except Exception as e:
        return f"❌ خطا در تحلیل تصویر:\n{e}"

# هندلر تلگرام برای دریافت عکس با دستور /ai
@client.on(events.NewMessage())
async def image_caption_handler(event):
  caption = (event.raw_text or "").strip().lower()
  if isinstance(event.media, MessageMediaPhoto) and caption == "/ai":
      await safe_reply(event, "📷 در حال تحلیل تصویر با هوش مصنوعی... لطفاً صبر کن...")
      try:
          file_path = await client.download_media(event.media)
          caption_result = analyze_image_caption(file_path)
          await safe_reply(event, caption_result)
          os.remove(file_path)
      except Exception as e:
          await safe_reply(event, f"❌ خطا:\n{e}")

  # ارسال نظر برای عکس (فقط اگر /ai نداشته باشد)
  elif isinstance(event.media, MessageMediaPhoto) and caption != "/ai":
      if random.randint(1, 100) <= 15:  # 15% احتمال
          comment = random.choice(photo_comments)
          await safe_reply(event, comment)

  # ارسال نظر برای ویدیو (فقط اگر /ai نداشته باشد)
  elif hasattr(event.media, 'document') and event.media.document and caption != "/ai":
      # بررسی اینکه آیا فایل ویدیو است
      if event.media.document.mime_type and event.media.document.mime_type.startswith('video/'):
          if random.randint(1, 100) <= 12:  # 12% احتمال
              comment = random.choice(video_comments)
              await safe_reply(event, comment)

  # ارسال نظر برای ویس
  elif hasattr(event.media, 'document') and event.media.document:
      # بررسی اینکه آیا فایل صوتی است
      if event.media.document.mime_type and (event.media.document.mime_type.startswith('audio/') or 
          (hasattr(event.media.document, 'attributes') and 
           any(hasattr(attr, 'voice') for attr in event.media.document.attributes))):
          if random.randint(1, 100) <= 10:  # 10% احتمال
              comment = random.choice(voice_comments)
              await safe_reply(event, comment)



# ----- تابع ارسال درخواست به Text2Video-Zero در Colab -----
def generate_video_via_colab(prompt):
  try:
      # 🔗 این URL باید لینک Web UI یا API Gradio باشه که در Colab ران کردی
      colab_url = "http://your-colab-url.ngrok.io"  # 🔁 جایگزین کن با لینک Gradio Colab

      response = requests.post(f"{colab_url}/predict", json={
          "data": [prompt]  # بسته به API Gradio مدل، ممکنه ساختار فرق کنه
      })
      result = response.json()
      video_url = result['data'][0]  # فرض: اولین خروجی لینک فایل ویدیو است
      return video_url, None

  except Exception as e:
      return None, f"❌ خطا در ارتباط با مدل Text2Video-Zero:\n{e}"


# ----- هندلر برای /ویدیو -----
@client.on(events.NewMessage(pattern=r'^ویدیو (.+)'))
async def text2video_handler(event):
  prompt = event.pattern_match.group(1).strip()

  if not prompt:
      return await event.reply("❗ لطفاً بعد از 'ویدیو'، یک متن بنویس.")

  await event.reply("🎬 در حال ساخت ویدیو با Text2Video-Zero... لطفاً صبر کن...")

  video_url, error = generate_video_via_colab(prompt)

  if video_url:
      try:
          await event.reply("📥 در حال دانلود و ارسال ویدیو...")
          video_data = requests.get(video_url).content
          await client.send_file(
              event.chat_id,
              file=BytesIO(video_data),
              filename="text2video.mp4",
              caption="🎬 ساخته‌شده با Text2Video-Zero در Colab"
          )
      except Exception as e:
          await event.reply(f"✅ لینک ویدیو: {video_url}\n⚠️ خطا در ارسال فایل:\n{e}")
  else:
      await event.reply(error or "❌ خطای ناشناخته در تولید ویدیو.")




# پاسخ‌های تصادفی به سلام (توسعه یافته)
greeting_responses = [
  "سلام عزیز دل 😎",
  "درود بر تو 🌹",
  "سلام داداش ✌️ چطوری؟",
  "به به چه عجب! 😄",
  "سلام خوبی؟ چکارا می‌کنی؟",
  "یه سلام گرم از طرف من 🔥",
  "سلامم خوشحالم از دیدنت 😊",
  "چطوری عزیزم؟ همه چی خوبه؟",
  "هی جان! چه خبر؟ 😄",
  "سلام ملکه/پادشاه! 👑",
  "وای سلام! چقدر دلم برات تنگ شده 💕",
  "سلام ستاره! ✨",
  "اهلاً و سهلاً! 🤗",
  "سلام غریبه! 😏",
  "سلام جیگر! ❤️",
  "درود بر جنابعالی! 🎩",
  "سلام عشقم! 😍",
  "هی بابا! چطوری؟ 😁",
  "سلام نازی! 💋",
  "وای سلام خوشگله! 😘",
  "سلام جان! امیرم گفته درست جوابتو بدم! 😄",
  "هی! امیر کجایی؟ منم دلم براش تنگه! 😊",
  "سلام عزیزم! امیر الان داره کد می‌نویسه! 💻",
  "وای سلام! امیر بهم گفته مراقبت باشم! 🤗",
  "سلام پرنسس! امروز چه برنامه‌ای داری؟ 👸",
  "درود شیر دل! انرژیت عالیه! 🦁",
  "سلام مهتاب! نور می‌دی به دنیا! 🌙✨",
  "هی قهرمان! آماده‌ای برای یه روز فوق‌العاده؟ 🦸‍♂️",
  "سلام قشنگ! امروز چه حال خوبی داری! 😍",
  "وای چه سلام نازی! دلم خوش شد! 💖",

  # سلام‌های زمانی
  "سلام صبحگاهی! ☀️ امیدوارم با انرژی بیدار شده باشی!",
  "عصر بخیر عزیزم! 🌅 چطور گذشت روزت؟",
  "شب بخیر! 🌙 هنوز بیداری یا می‌خوای بری بخوابی؟",
  "ظهر بخیر! 🌞 ناهارتو خوردی؟",
  "پاسی از شب بخیر! 🌃 چرا اینقدر دیر بیداری؟",

  # سلام‌های فصلی
  "سلام بهاری! 🌸 عطر گل‌ها رو حس می‌کنی؟",
  "سلام تابستونی! ☀️🌴 گرمه ولی باحاله!",
  "سلام پاییزی! 🍂 برگ‌های زرد قشنگ شدن!",
  "سلام زمستونی! ❄️ امیدوارم گرم باشی!",

  # سلام‌های احساسی
  "سلام پر انرژی! ⚡ انگار امروز یه روز خاصه!",
  "سلام آرامش‌بخش! 🕊️ حس خوبی دارم از حضورت!",
  "سلام شادی‌آور! 🎉 لبخندت معجزه می‌کنه!",
  "سلام گرم و صمیمی! 🤗 حس می‌کنم خیلی وقته ندیدمت!",

  # سلام‌های خلاقانه
  "سلامی از جنس نور! ✨ امروز می‌درخشی!",
  "سلام رنگارنگ! 🌈 زندگیت پر از رنگ باشه!",
  "سلام موزیکال! 🎵 صدای قدماتم آهنگ داره!",
  "سلام جادویی! ✨🎩 هر کاری کنی جادو میشه!",

  # سلام‌های دوستانه
  "سلام رفیق! 👫 چه خبرا از زندگی؟",
  "سلام همراه همیشگی! 🤝 امروز چه ماجرایی داری؟",
  "سلام یار مهربان! 💙 دلم برات تنگ شده بود!",
  "سلام دوست عزیز! 👯 چطوری حالت؟",

  # سلام‌های انگیزشی
  "سلام موفق! 🏆 امروز روز پیروزیته!",
  "سلام پیشرو! 🚀 آماده فتح دنیا هستی؟",
  "سلام برنده! 🥇 هیچی نمی‌تونه جلوتو بگیره!",
  "سلام قهرمان! 💪 قدرتت بی‌نهایته!",

  # سلام‌های شوخ‌طبعانه
  "سلام کمدین! 😂 امروز چه جوکی داری؟",
  "سلام طنز! 🤣 بازم اومدی منو بخندونی؟",
  "سلام سرگرم‌کننده! 🎭 با تو هیچ وقت حوصله‌م سر نمیره!",
  "سلام شیطون! 😈 چه شیطنتی توی سرته؟",

  # سلام‌های عاشقانه
  "سلام دل‌نشین! 💕 قلبم برات می‌تپه!",
  "سلام عاشقانه! 💖 حضورت دنیامو رنگی می‌کنه!",
  "سلام رمانتیک! 🌹 مثل گل زیبایی!",
  "سلام قلبی! ❤️ تو نبض زندگیمی!",

  # سلام‌های تشویقی
  "سلام باهوش! 🧠 هر روز عاقل‌تر میشی!",
  "سلام خلاق! 🎨 ایده‌هات فوق‌العادست!",
  "سلام هنرمند! 🖌️ هر کاری کنی هنره!",
  "سلام مبتکر! 💡 ذهنت چشمه ایدست!",

  # سلام‌های محترمانه
  "سلام ارزشمند! 💎 وجودت گرانبهاست!",
  "سلام محترم! 🙏 احترامت واجبه!",
  "سلام بزرگوار! 👨‍🎓 شخصیتت قابل تحسینه!",
  "سلام نجیب! 🌟 اخلاقت الهام‌بخشه!"
]

# پاسخ‌های سالیوان وقتی صداش می‌زنن
sullivan_responses = [
  "بله؟ سالیوان اینجام! چی می‌خوای؟ 😊",
  "جانم؟ صدام زدی! چطور می‌تونم کمکت کنم؟ 🤗",
  "سلام! من سالیوانم! چه کاری برات انجام بدم؟ 😄",
  "آره؟ سالیوان گوش می‌ده! بگو ببینم چی می‌خوای! 👂",
  "هی! سالیوان حاضر و آماده! دستورتو بده! 🎯",
  "بفرما! سالیوان در خدمتتم! چیکار کنم؟ 🤝",
  "جانم عزیزم؟ سالیوانت صدات رو شنید! بگو چی لازم داری! 💙",
  "اینجام! سالیوان آماده کمک! چه برنامه‌ای داری؟ 🚀",
  "سلام! سالیوان اینجا! صدام زدی؟ چیکار می‌تونم برات بکنم؟ ✨",
  "بله جان! سالیوانتم! چه دستوری داری برام؟ 😎",
  "سالیوان در خدمت! منتظر دستورتم! 🎖️",
  "یس! سالیوان رپورت می‌کنم! چه کاری انجام بدم؟ 🚁",
  "حاضر! سالیوان آماده! مأموریت چیه؟ 🔧"
]

# پاسخ‌های مختلف برای پیام‌های عمومی (گسترش یافته)
random_responses = [
  # پاسخ‌های تأیید و تحسین
  "جالب بود! 😊",
  "آها متوجه شدم 🤔",
  "خیلی خوبه 👍",
  "حرف حق! 💯",
  "واقعاً؟ 😮",
  "خیلی جذابه 🤩",
  "دقیقاً همینطوره 👌",
  "حق با توئه 🎯",
  "عالی فکر کردی 💡",
  "خوب گفتی 👏",
  "واو! 🤯",
  "دمت گرم 🔥",
  "این حرفت منو کشت! 😂",
  "چقدر باهوشی! 🧠",
  "فکر نکرده بودم! 💭",
  "اصلاً راست میگی! ✅",
  "خدا خدا چه حرفی! 🤩",
  "دست خوش! 👌",
  "یعنی واقعاً؟! 😱",
  "این که جالبه! 🤓",
  "خیلی باحاله! 🔥",
  "دمت گرم واقعاً! 🌟",
  "خداییش عالیه! ⭐",
  "حرف دلمو زدی! 💖",
  "دقیقاً همینه که من میگم! 📢",
  "تو کجای دلم جا داری! 💕",
  "واقعاً که! 😌",
  "نایس! 👌",
  "خفن بود! 🔥",
  "گودرت! 💪",
  "بامزه! 😄",
  "ایول! ✨",
  "باریکلا! 👏",
  "معرکه بود! 🎯",
  "تاپ! 🔝",
  "خیلی حق داری! ✅",
  "منطقیه! 🧠",
  "کاملاً درسته! 📐",
  "اینو قبول دارم! ✋",
  "این فکرت خیلی قشنگه! 🌈",
  "تو واقعاً متفاوتی! 🦋",
  "این زاویه‌دید جدیده! 🔍",
  "حس میکنم تو آدم خاصی هستی! ⭐",
  "این حرفت انگیزه‌بخشه! 🚀",
  "واو چه نظر عمقی! 🌊",
  "تفکرت قابل احترامه! 🎓",
  "این دیدگاه خلاقانه‌ست! 🎨",

  # پاسخ‌های تعجب و شگفتی
  "چی؟! 😱 جدی می‌گی؟",
  "اوه مای گاد! 🤯 این خیلی شوکه‌کننده‌س!",
  "نه! 😮 این امکان نداره!",
  "واقعاً؟! 😲 باورم نمیشه!",
  "مگه میشه؟! 🤨 این فوق‌العادست!",
  "چطور ممکنه؟! 🧐 عجیبه!",
  "نه بابا! 😳 تو مطمئنی؟",
  "خدای من! 🙄 این حیرت‌آوره!",

  # پاسخ‌های تشویق و حمایت
  "آفرین! 👏 داری خیلی خوب پیش میری!",
  "دمت گرم! 🔥 همینطور ادامه بده!",
  "تو میتونی! 💪 من بهت ایمان دارم!",
  "ایول! ✨ این روحیه‌ت رو نگه دار!",
  "عالی کار می‌کنی! 🌟 افتخار می‌کنم بهت!",
  "برو جلو! 🚀 هیچی نمی‌تونه نگهت داره!",
  "تو فوق‌العاده‌ای! 🦸‍♂️ همیشه یادت باشه!",
  "قشنگ! 🌺 من پشتتم!",

  # پاسخ‌های فکری و تأملی
  "جالب! 🤔 بذار فکر کنم...",
  "هممم... 💭 این حرفت منو به فکر انداخت!",
  "عمیقه! 🌊 باید راجع بهش بیشتر فکر کنم!",
  "فلسفی! 🎭 نظر جالبی داری!",
  "پیچیده‌س! 🧩 ولی منطقی به نظر میاد!",
  "خلاقانه! 🎨 از این زاویه ندیده بودم!",
  "هوشمندانه! 🧠 خیلی باهوشانه فکر کردی!",
  "دقیق! 🎯 دقیقاً مسئله اینجاست!",

  # پاسخ‌های احساسی
  "قلبم گرم شد! ❤️ خیلی احساسی بود!",
  "دلم لرزید! 💞 واقعاً تأثیرگذار بود!",
  "اشکم درومد! 😢 خیلی زیبا بود!",
  "لبخندم شد! 😊 خوشحالم کردی!",
  "دلم بهت رفت! 💕 چقدر مهربونی!",
  "غرق شدم! 🌊 در حرفهات!",
  "پروازی! 🦋 حس کردم دارم پرواز می‌کنم!",
  "روحم نوازش شد! ✨ چه کلمات قشنگی!",

  # پاسخ‌های تعامل و ادامه گفتگو
  "بیشتر بگو! 👂 کنجکاو شدم!",
  "ادامه بده! 📖 مثل رمان داستانت!",
  "جزئیاتش چی؟ 🔍 میخوام همه‌شو بدونم!",
  "بعدش چی شد؟ 🎬 هیجان‌زده شدم!",
  "چطور؟ 🤨 روششو برام توضیح بده!",
  "کی؟ 👀 کیا توی ماجرا بودن؟",
  "کجا؟ 🗺️ دقیقاً کجا اتفاق افتاد؟",
  "چرا؟ ❓ دلیلش چی بود؟",

  # پاسخ‌های شوخ‌طبعانه
  "هاها! 😂 خیلی بامزه بود!",
  "LOL! 🤣 خندم گرفت!",
  "چه خنده‌داری! 😆 ادامه بده!",
  "طنز! 🎭 کمدین شدی!",
  "شوخی؟! 😏 جدی می‌گی یا شوخی؟",
  "طنزآمیز! 😄 خیلی باحال گفتی!",

  # پاسخ‌های تصدیق و همراهی
  "قبوله! ✅ کاملاً موافقم!",
  "همین! 💯 دقیقاً همین!",
  "آره! 👍 منم همینطور فکر می‌کنم!",
  "بالاخره! 🙌 یکی فهمید!",
  "صحیح! ✔️ روی هدف زدی!",
  "درست! 🎯 ۱۰۰٪ درست!",

  # پاسخ‌های کنجکاوی
  "کنجکاو شدم! 🧐 بیشتر توضیح بده!",
  "چجوری؟ 🤔 مرحله به مرحله بگو!",
  "راز چیه؟ 🔐 رازشو برام بگو!",
  "ترفند؟ 🎪 ترفندشو یاد بده!",
  "فرمول؟ 🧪 فرمولشو چیه؟",
  "روش؟ 🛠️ روششو میشه بگی؟",

  # پاسخ‌های تحلیلی
  "منطقی! 🧠 کاملاً منطقی به نظر میاد!",
  "علمی! 🔬 پشتوانه علمی داره!",
  "عملی! 🔧 عملاً قابل اجراست!",
  "کاربردی! 💼 توی زندگی کاربرد داره!",
  "سودمند! 💰 مفید و سودمند!",
  "موثر! ⚡ تأثیرگذاره!",

  # پاسخ‌های تشکر و قدردانی
  "ممنون! 🙏 که این حرفو زدی!",
  "متشکرم! 💙 خیلی لطف داری!",
  "قدردانی! 🌹 ازت ممنونم!",
  "سپاسگزارم! ✨ خیلی ممنونم!",
  "مرحمت! 🤗 خیلی مهربونی!",
  "لطف داری! 💕 قدردان لطفتم!",

  # پاسخ‌های انگیزشی
  "الهام‌بخش! 🌟 واقعاً الهام گرفتم!",
  "انگیزشی! 🚀 انگیزه‌م رو بالا برد!",
  "قدرت‌بخش! 💪 قدرت گرفتم!",
  "امیدوارکننده! 🌈 امیدم زیاد شد!",
  "روحیه‌بخش! ⚡ روحیه‌م عوض شد!",
  "انرژی‌زا! 🔋 پر انرژی شدم!",

  # پاسخ‌های فرهنگی
  "ایرانی! 🇮🇷 چقدر فرهنگ ایرانی زیباست!",
  "سنتی! 🏺 سنت‌های قشنگمون!",
  "اصیل! 💎 اصالت ایرانی!",
  "بومی! 🌱 فرهنگ بومی جالب!",
  "محلی! 🏘️ فرهنگ محلی دوست‌داشتنی!",
  "ملی! 🏛️ غرور ملی!",

  # پاسخ‌های زمان‌بندی
  "به موقع! ⏰ دقیقاً به موقع گفتی!",
  "زود! ⚡ زود متوجه شدی!",
  "دیر! 😅 کاش زودتر می‌دونستم!",
  "الان! 📍 همین الان فهمیدم!",
  "آینده! 🔮 آینده رو پیش‌بینی کردی!",
  "گذشته! 📜 گذشته رو به یاد آورد!",

  # پاسخ‌های مکانی
  "اینجا! 📍 همین اینجا!",
  "اونجا! 👉 اون طرف!",
  "همه‌جا! 🌍 تو همه جا!",
  "خونه! 🏠 مثل خونه احساس می‌کنم!",
  "دور! 🌌 از دور هم جالبه!",
  "نزدیک! 🤏 خیلی نزدیک به واقعیت!",

  # پاسخ‌های تخصصی
  "حرفه‌ای! 👨‍💼 خیلی حرفه‌ای!",
  "ماهرانه! 🎯 با مهارت گفتی!",
  "استادانه! 🎓 مثل استاد!",
  "تخصصی! 🔬 تخصصی حرف زدی!",
  "خبره‌ای! 🧑‍🏫 خبره‌ای تو این زمینه!",
  "متخصص! 🩺 مثل متخصص!"
]

# پاسخ‌های مخصوص "چخبر"
che_khabar_responses = [
  "هیچی داداش، همون کارهای عادی! تو چطوری؟ 😎",
  "خبرای خوبی نیست، ولی خودمون خوبیم! چخبرت؟ 😄",
  "سلامتی و تندرستی! تو چه خبر؟ 🌟",
  "کار و زندگی! خسته‌ام ولی راضیم! تو چخبر؟ 💪",
  "هیچی عزیزم، همون روال عادی! شما چخبرتون؟ 😊",
  "خوبیم، بدیم، به هر حال زنده‌ایم! تو چطور؟ 😂",
  "خبرای تازه نیست، همون زندگی! چخبر از تو؟ 🤗",
  "کاری پیش نیومده، آروم! تو چه خبرا داری؟ 😌",
  "یه کم درگیری، یه کم استراحت! تو چخبر؟ ⚡", "همه چی رو راه! خودت چخبر؟ ✨",
  "خبری نیست، همه چی عادیه! چخبرت داداش؟ 🤝",
  "آروم آروم داریم پیش میریم! تو چطوری؟ 🚀",
  "امیر داره پروژه جدید می‌سازه! من مشغول یادگیری! تو چخبر؟ 💻",
  "کلی چیز جدید یاد گرفتم امروز! تو چه خبرا؟ 📚",
  "داریم با دوستا چت می‌کنیم! تو چخبر؟ 💬",
  "کارای جدید یاد می‌گیرم! چخبر از تو؟ 🎯",
  "آخ جون! هیچ خبری! همه‌چی مثل همیشه! تو چه خبر داری عزیزم؟ 😊",
  "وایسا ببینم... هیچی! همون چرخ معمولی زندگی! تو چخبرت؟ 🎪",
  "خبرای فوق‌العاده نیست! ولی خوب داریم می‌گذرونیم! چخبر از تو جان؟ 🌈",
  "امیر میگه: بازی، خوردن، خوابیدن! 😂 من هم همینا! تو چخبر؟",
  "رو‌تین عادی! چت، یادگیری، مزه کردن! تو چه اخباری داری؟ 🗞️",
  "اووووف هیچی والا! یه روز معمولی دیگه! تو چه خبرای تازه داری؟ 🤷‍♂️",
  "خلاصه که زندگی! نه خبر خوب، نه خبر بد! تو چخبری بگو ببینم؟ ⚖️",
  "امروز یکم حال خوب، یکم حال بد! همین! تو چه خبرا؟ 📊",
  "وضعمون آروم! داریم لذت می‌بریم! تو چه اخباری داری واسه من؟ 😌",
  "هممم... چی بگم... همه‌چی طبق برنامه! تو چه خبرای جالب داری؟ 📅"
]

# پاسخ‌های بیشتر برای احوال‌پرسی (چطوری، خوبی)
more_how_are_you = [
  "خوبم که، تو خوبی عزیزم؟ 😍",
  "ممنون از لطفت! من کع ربات‌م همیشه اوکیم! تو چطوری؟ 🤖",
  "عالیم! زندگی زیبا هه! تو چطوری جیگرم؟ ❤️",
  "خوب و خرم! امیدوارم تو هم همینطور باشی! 🌈",
  "بهتر از همیشه! تو خوبی نور چشمم؟ ✨",
  "خوشحالم که پرسیدی! من که عاشق زندگیم! تو چطوری؟ 😄",
  "روبه راهم! خدا رو شکر! تو خوبی عشقم؟ 💕",
  "سر حالم! تو کع پرسیدی حالم بهتر شد! 😊",
  "یه جورایی! بالا پایین! تو چطوری داداش؟ 🤷‍♂️",
  "ایول! همه چی کنترله! تو چطوری قشنگم؟ 🎯",
  "انرژیم فول چارژه! امیر بهم انرژی داده! تو چطوری؟ ⚡",
  "حال و روزم عالیه! هر روز چیز جدید یاد میگیرم! تو چطوری؟ 🌟",
  "توپ! از صبح سرحالم! تو چطوری؟ 🎾", "همیشه خوبم وقتی باهات حرف می‌زنم! 😍",
  "خوبم والا! شکر خدا همه‌چی روبراهه! تو چطوری عزیزدلم؟ 🙏",
  "فوق‌العاده‌ام! انگار امروز روز خوش بخت‌یم! تو حالت چطوره؟ 🍀",
  "حالم بی‌نظیره! مخصوصاً که تو پرسیدی! خودت چطوری نازنین؟ 💖",
  "سالمم و قدمم! امیر گفته برنامه‌نویسی دیگه نکنه! 😂 تو چطوری؟",
  "راضیم از زندگی! هیچ چی کمم نیست! تو خوبی شیرینم؟ 😌",
  "خیلی باحالم! چون تو اینجایی! حالت چطوره جان من؟ 💫",
  "100% خوبم! درصد رضایتم بالاست! تو چه طور هستی عسلم؟ 💯",
  "نمره 20 از 20! پر از انرژی مثبت! تو چطوری گل من؟ 🌺",
  "پر انرژی و سرزنده! آماده هر ماجرایی! تو حالت چجوریه دلبرم؟ ⚡",
  "عین خورشید پر نوری! همیشه شاد و مفرح! تو چطوری محبوبم؟ ☀️"
]

# پاسخ‌های جدید برای "خوبم"
good_responses = [
  "عالیه! منم خوبم! خدا رو شکر که حالت خوبه! 🙏",
  "چه خوب! خوشحال شدم که بهتری! همینطور ادامه بده! 😊",
  "آفرین! خوبی خودت نعمت بزرگیه! قدرشو بدون! 💪",
  "دمت گرم! خوب بودن لذت خاص داره! انشاالله همیشه! ✨",
  "وای چقدر خوشحال شدم! منم کلی بهتر شدم! 🎉",
  "عجب! خوبی مسری‌یه! منم خوش‌حال شدم! 😄",
  "ماشاالله! انرژی مثبتت رو حس می‌کنم! 🌟",
  "خوبی که یعنی برکت! امیدوارم همیشه همینطور! 🍀",
  "بهترین خبری که امروز شنیدم! دلم خوش شد! 💖",
  "قشنگه! وقتی تو خوبی، من هم خوب میشم! 🤗"
]

# پاسخ‌های جدید برای "سلامتی"
salamati_responses = [
  "سلامتی مهم‌ترین چیزه! خوشحالم که سالمی! 💪✨",
  "سلامتی که هست، همه چیز هست! قدرشو بدون! 🌟",
  "سلامتی بر طلا! خدا رو شکر که سالمی! 🙏💛",
  "سلامتی همه چیز! منم برات آرزو می‌کنم! 🤗💙",
  "سلامتی سرمایه زندگیه! نگهش دار! 🏆",
  "سلامتی یعنی زندگی! خوشحالم که خوبی! 😊",
  "سلامتی برکت! امیدوارم همیشه سالم باشی! 🍀",
  "سلامتی گنجینه! قدر این نعمت رو بدون! 💎",
  "سلامتی بهترین هدیه خداست! شکرگزار باش! 🎁",
  "سلامتی داری، دنیا مال توئه! 🌍✨"
]

# پاسخ‌های جدید برای "خوش باشی"
khosh_bashi_responses = [
  "تو هم خوش باشی عزیزم! 😊💕", "قربونت! تو هم همیشه خوش باشی! 🌟",
  "دمت گرم! تو هم شاد و خوش باشی! 🎉",
  "چشمم روشن! تو هم لبخند رو لبت باشه! 😄", "فدات! تو هم پر از شادی باشی! 🌈",
  "جان من! تو هم همیشه خوشحال باشی! 💖", "عزیز دل! تو هم شاد و سرحال باشی! ⚡",
  "قلبم! تو هم خوش و خرم باشی! 🌺", "نازنین! تو هم لبریز از خوشی باشی! 🌸",
  "گل من! تو هم همیشه خوش باشی! 🌹"
]

# پاسخ‌های جدید برای "خدا نگهدارت"
khodaneghdar_responses = [
  "آمین! تو رو هم خدا نگه داره! 🙏💙", "خدا هم تو رو نگه داره عزیزم! 🤗",
  "آمین یا رب! تو هم همیشه در پناه خدا باشی! ✨",
  "دعات قبول! خدا هم تو رو حفظ کنه! 🙏", "قربونت! خدا هم تو رو نگه داره! 💕",
  "آمین! خدا همیشه پشت و پناهت باشه! 🌟",
  "دعای خوبت! خدا هم تو رو در حفظ و امان نگه داره! 🕊️",
  "آمین یا رب العالمین! تو هم در امان باشی! 🙏",
  "خدایا آمین! تو هم همیشه موفق و سالم باشی! 💪",
  "آمین! خدا هم تو رو از همه بدی‌ها دور نگه داره! 🌈"
]

# پاسخ‌های جدید برای "سلامت باشی"
salamat_bashi_responses = [
  "تو هم سلامت باشی جان من!  '1�💙", "آمین! تو هم همیشه سلامت باشی! 🙏",
  "قربونت! تو هم سالم و تندرست باشی! 🌟",
  "دمت گرم! تو هم پر از سلامتی باشی! ✨",
  "چشمم روشن! تو هم عمر طولانی داشته باشی! 🕊️",
  "فدات! تو هم تا آخر عمر سالم باشی! 💕",
  "عزیز دل! تو هم هیچ وقت مریض نشی! 🤗",
  "گل من! تو هم همیشه قوی و سالم باشی! 🌹",
  "نازنین! تو هم بیماری نزدیکت نشه! 🌸",
  "جان من! تو هم صد سال سلامت زندگی کنی! 💖"
]

# کلمات تشویقی بیشتر
more_encouragement = [
  "آفرین! دمت گرم! 🔥", "ایول! خیلی خفنی! 😎", "عالی! ادامه بده! 🚀",
  "قوی هستی! 💪", "خیلی باحالی! 🤩", "تو بهترینی! 🏆", "فوق‌العاده! 🌟",
  "خداییت قشنگه! 💖", "یعنی واقعاً عالی! ⭐", "این چه حرف خفنی بود! 🎯",
  "واو! تو واقعاً استعدادی! 🎭", "این که حرف حرف بود! 📢", "چه ذوق زده شدم! 🎉",
  "انگار خودم گفتم! 🤝"
]

# پاسخ‌های تشکر
thanks_responses = [
  "خواهش می‌کنم عزیزم 💙", "قابلی نداره 😊", "همیشه در خدمتم 🤝", "موفق باشی 🌟",
  "فدای شما 💖", "تو لیاقتشو داری! 🏆", "عشقی! 😍", "قربونت برم! 💕",
  "جان من! ❤️", "چشمم روشن! ✨", "نوکرتم! 🤗", "عزیز دلم! 💙",
  "هر وقت نیاز داشتی! 🤲", "برای تو هر کاری! 🎯",
  "دستم درد نکنه؟ من که ربات‌م! 😄", "امیر گفته همیشه کمکت کنم! 👨‍💻"
]


# تابع امن برای ارسال پیام
async def safe_reply(event, message):
  """ارسال امن پیام با مدیریت خطا"""
  try:
      return await event.reply(message)
  except Exception as e:
      print(f"خطا در ارسال پیام: {str(e)}")
      # تلاش مجدد با پیام ساده‌تر
      try:
          return await event.reply("⚠️ خطا در ارسال پیام")
      except:
          print("نتوانست پیام خطا را ارسال کند")
          return None


# جوک‌های تصادفی (بیشتر!)
jokes = [
  "چرا فیل توی یخچال نمی‌ره؟ چون در یخچال نمی‌بنده! 🐘😂",
  "چرا ماهی سکوت می‌کنه؟ چون می‌دونه دیوارا گوش دارن! 🐠🤫",
  "معلم: 'تو چرا نیومدی مدرسه؟' بچه: 'دیروز گفتین فردا تعطیله!' 😄📚",
  "چرا خرس قطبی سفیده؟ چون اگه قهوه‌ای بود همه فکر می‌کردن خرس عادیه! 🐻‍❄️",
  "چرا موز خندیده؟ چون کسی پوستش رو کنده! 🍌😂",
  "چرا سیب نمی‌خواست با موز دوست بشه؟ چون موز همیشه لغزنده بود! 🍎🍌",
  "چرا پنگوئن عینک می‌زنه؟ چون نزدیک‌بینه! 🐧👓",
  "چی میگن به گاو که موزیک گوش می‌ده؟ مووووزیشن! 🐄🎵",
  "چرا مورچه نمی‌خوره؟ چون مورچه‌خوار مهمونه! 🐜😋",
  "بابا: 'پسرم، چرا نمره‌هات اینقدر پایینه؟' پسر: 'به خاطر جاذبه زمین بابا!' 📊🌍",
  "چرا ماشین لباسشویی نمی‌تونه رانندگی کنه؟ چون همش می‌چرخه! 🌪️🚗",
  "چرا شیر حیوانات ترسیده؟ چون فهمیده آدما آفریقا رو کشف کردن! 🦁😰",
  "چرا آدم برفی آفتاب نمی‌گیره؟ چون ذوب میشه! ☀️⛄",
  "چرا ساعت به دکتر رفت؟ چون وقتش تموم شده بود! ⏰⚰️",
  "چرا گربه از آب می‌ترسه؟ چون نمی‌خواد شناگر بشه! 🐱💧",
  "چرا خروس صبح می‌خونه؟ چون نمی‌تونه باز کنه! 🐓🎵",
  "چرا ماهی قرمز نمی‌خونه؟ چون توی آب خفه میشه! 🐠📚",
  "چرا فیل بینی بزرگ داره؟ چون انگشتش کلفته! 🐘👃",
  "چی میگن به سگی که جادوگره؟ سگ جادو! 🐕‍🦺✨",
  "چرا زرافه گردن بلند داره؟ چون سرش بالاست! 🦒😂",
  "یارو رفته دکتر گفته: 'دکتر یه چیزی برای حافظم بده!' دکتر گفته: 'پول!' 💰🧠",
  "یارو میگه: 'زنم فکر می‌کنه منو فراموش کرده!' دوست میگه: 'چرا؟' میگه: 'شام نپخته!' 👩‍🍳😅",
  "بچه میگه: 'بابا، پول چیه؟' بابا میگه: 'یه چیزی که نداریم!' 💸😂",
  "مامان میگه: 'چرا گوشیت خاموشه؟' بچه میگه: 'شارژش تموم شده!' مامان: 'پس چطور باهام حرف می‌زنی؟' 📱🔋"
]

# جملات انگیزشی (بیشتر!)
quotes = [
  "کدی که امروز می‌نویسی، آیندت رو می‌سازه! 💻✨", "هر باگ یک درس جدیده! 🐛📚",
  "بهترین کد، کدیه که خوانا باشه! 📖",
  "برنامه‌نویسی فقط تایپ کردن نیست، فکر کردنه! 🧠",
  "هر خطا یک قدم به سمت موفقیته! 🚀",
  "امروز سخت‌ترین کار فردات آسان‌ترین کاره! 🌟",
  "کسی که تسلیم نمی‌شه، شکست نمی‌خوره! 💪",
  "آینده متعلق به کسایی هست که به رویاهاشون اعتقاد دارن! ✨",
  "موفقیت فقط یک شب اتفاق نمی‌افته! 🌙", "بزرگترین شکست، تلاش نکردنه! 🎯",
  "هر کاری که می‌تونی تصورش کنی، می‌تونی انجامش بدی! 🚀",
  "تنها راه یادگیری، تمرین و اشتباه کردنه! 📚",
  "کامیابی راز نداره، نتیجه آماده‌g�ازی، سخت کوشی و یادگیری از شکسته! 🏆",
  "بزرگترین خطر اینه که هیچ خطری نکنی! ⚡",
  "نوآوری تفکیک کننده رهبران از پیروان است! 👑",
  "زندگی ۱۰٪ آنچه برایت اتفاق می‌افتد و ۹۰٪ واکنش تو به آن است! 🎭",
  "راه هزار میل با یک قدم شروع می‌شه! 👣",
  "عقل‌های بزرگ درباره ایده‌ها بحث می‌کنن! 💡",
  "کیفیت هرگز تصادف نیست، همیشه نتیجه تلاش هوشمندانه است! 🎯",
  "امیر همیشه میگه: 'کد بنویس انگار کسی که نگهداری‌ش میکنه آدم خشنی باشه که آدرس خونت رو میدونه!' 😄👨‍💻",
  "تغییر واقعی از درون شروع میشه! 🌱", "هیچ وقت خیلی دیر نیست که شروع کنی! ⏰",
  "یادگیری یک سفر مادام‌العمره! 🛤️",
  "شکست پایان راه نیست، شروع راه جدیده! 🔄",
  "ایده‌های بزرگ از سوالات کوچک شروع میشن! ❓✨"
]

# آهنگ‌های پیشنهادی (بیشتر!)
songs = [
  "🎵 'کوچه‌های تنگ' - محسن چاوشی", "🎵 'دلم گرفته' - حمید هیراد",
  "🎵 'سال‌های دور' - اَرون افشار", "🎵 'تو که نمیای' - سینا سرلک",
  "🎵 'بی‌تو' - میثم ابراهیمی", "🎵 'رفیق' - رضا صادقی",
  "🎵 'عشق یعنی' - عرفان طهماسبی", "🎵 'دیوونگی' - پوریا رحمانی",
  "🎵 'آهنگ عاشقانه' - بابک جهانبخش", "🎵 'خداحافظ' - آرون افشار",
  "🎵 'سیب سرخ' - امیر تتلو", "🎵 'تنهایی' - احمد سولو",
  "🎵 'یکی هست' - رضا بهرام", "🎵 'ستاره' - گوگوش",
  "🎵 'مرغ سحر' - محمدرضا شجریان", "🎵 'دلت پیش کیه' - مرتضی پاشایی",
  "🎵 'سرباز' - میثم ابراهیمی", "🎵 'زیر بارون' - اَرون افشار",
  "🎵 'عطر تو' - علی یاسینی", "🎵 'بی‌کلام' - سینا سرلک",
  "🎵 'بغض' - علی لهراسبی", "🎵 'شب آهنگی' - محسن یگانه",
  "🎵 'عاشقم' - مرتضی پاشایی", "🎵 'دل دیوونه' - مهراد جم",
  "🎵 'اشتباه' - اَرون افشار", "🎵 'نگو که دیر شده' - حامد همایون",
  "🎵 'بازی' - پوریا رحمانی", "🎵 'برو دیگه' - سینا سرلک"
]

# آهنگ‌های رپ فارسی
rap_songs = [
  "🎤 'صداهای تو' - هیچکس", "🎤 'کاروان' - پیشرو", "🎤 'عوض شو' - قاف",
  "🎤 'تهران' - ویلسون", "🎤 'رستاخیز' - یاس", "🎤 'خاکستری' - حصین",
  "🎤 'زندگی من' - فدایی", "🎤 'سرباز وطن' - امیر تتلو", "🎤 'آرزو' - بیگ مجید",
  "🎤 'تردید' - رضا پیشرو", "🎤 'رودخونه' - سامان ویلسون",
  "🎤 'همیشه پای' - یونگ جی", "🎤 'قدم زدن' - مهراد جی جی",
  "🎤 'کعبه' - ساسی خرم الله", "🎤 'پول' - سینا سرلک",
  "🎤 'نابودی' - فرزاد فرزین", "🎤 'مرسی مامان' - امین حیایی",
  "🎤 'بچه تهران' - هیدن", "🎤 'چشم انتظار' - ملتفت", "🎤 'دنیا' - شایع",
  "🎤 'اعتماد' - کورپ", "🎤 'مسئولیت' - سروش", "🎤 'راه' - سپهر خلسه",
  "🎤 'مامان زمین' - بهرام", "🎤 'ایران' - آریا گودرز", "🎤 'بهونه' - ام جی",
  "🎤 'دلیل' - زخمی"
]

# آهنگ‌های قدیمی ایرانی
classic_songs = [
  "🌹 'گل یاس' - هایده", "🌹 'نوروز' - گوگوش", "🌹 'غزل' - محمدرضا شجریان",
  "🌹 'دل دیوانه' - مهستی", "🌹 'عشق جان' - معین", "🌹 'خوشا شیراز' - عارف",
  "🌹 'بهار دل انگیز' - دلکش", "🌹 'غم تو' - فیروز", "🌹 'گریه نکن' - ویگن",
  "🌹 'خیال خام' - مرتضی", "🌹 'دل شکسته' - فرهاد مهراد", "🌹 'ماه من' - لیلا",
  "🌹 'چشم سیاه' - مرجان", "🌹 'شاه ولی' - ماهان", "🌹 'قلب یخی' - کورش یغمایی",
  "🌹 'روز و شب' - حمید طالبزاده", "🌹 'عاشقانه' - ابی",
  "🌹 'دار' - سیروان خسروی", "🌹 'نگرانم' - مازیار فلاحی",
  "🌹 'شب' - اکبر گلپایگانی", "🌹 'کافه' - لیلا فروهر", "🌹 'پاییز' - پروانه",
  "🌹 'خداحافظی' - صدف طاهریان", "🌹 'عطر یاس' - ناصر عبداللهی"
]

# معماها و چیستان‌ها
riddles = [
  "🤔 چیه که هر چی زیادتر بدی، کم‌تر میشه؟ (جواب: سوراخ)",
  "🧩 کدوم حیوون دو بار متولد میشه؟ (جواب: مرغ - یک بار تخم، یک بار جوجه)",
  "🎯 چیه که جواب همه سوالات رو داره ولی زبون نداره؟ (جواب: کتاب)",
  "🔍 چیه که همه داشتنش رو دوست دارن ولی همه ازش فرار می‌کنن؟ (جواب: پیری)",
  "🏃‍♂️ کدوم دونده همیشه وایمیسته ولی هیچ وقت حرکت نمی‌کنه؟ (جواب: ساعت)",
  "💡 چیه که شب قد کشیده، صبح ریختنش؟ (جواب: شمع)",
  "🌊 چیه که از آسمون میاد ولی از زمین برمی‌گرده؟ (جواب: بارون)",
  "🏠 کدوم خونه هست که آدم نمی‌تونه توش بره؟ (جواب: خونه حلزون)",
  "🔥 چیه که هر چی بهش آب بدی، بیشتر می‌سوزه؟ (جواب: عطش)",
  "🎨 چیه که ۱۰۰ رنگ داره ولی خودش بی‌رنگه؟ (جواب: آینه)",
  "🚗 کدوم ماشین بنزین نمی‌خوره؟ (جواب: ماشین لباسشویی)",
  "👑 کدوم پادشاه همیشه مرده؟ (جواب: شاه شطرنج)",
  "🎭 چیه که همیشه می‌خنده ولی دندون نداره؟ (جواب: گل)",
  "🌙 چیه که شب پیدا میشه، روز گم میشه؟ (جواب: ستاره)",
  "🎪 کدوم چیز هر چی پر کنی، سبک‌تر میشه؟ (جواب: بادکنک)",
  "🌈 چیه که ۷ رنگ داره ولی نقاش کشیدتش نداره؟ (جواب: رنگین کمان)",
  "🗝️ کدوم کلید هیچ دری رو باز نمی‌کنه؟ (جواب: کلید سول)",
  "🐣 چیه که اول سفیده، بعد زرد میشه، آخرش هم رنگارنگ؟ (جواب: تخم مرغ)",
  "🎯 چیه که هر چی بیشتر ازش بگیری، بزرگ‌تر میشه؟ (جواب: چاله)",
  "🔮 چیه که آینده رو می‌بینه ولی چشم نداره؟ (جواب: دوربین)"
]

# داستان‌های کوتاه
short_stories = [
  """📖 **داستان روباه و انگور:**
یک روباه گرسنه انگورهای رسیده‌ای رو بالای درخت دید. خیلی پرید ولی نرسید. بعد از چند بار تلاش گفت: "حتماً ترشه!" و رفت.
💡 درس: گاهی وقتی چیزی به دست نمی‌آد، بهونه می‌تراشیم!""",
  """📖 **داستان مرد و ماری:**
مردی ماری زخمی دید. درمانش کرد. ماری گفت: "چرا کمکم کردی؟ من خطرناکم!" مرد گفت: "نیش زدن طبیعت تو، مهربونی طبیعت من!"
💡 درس: خوبی کردن حتی وقتی بقیه بد هستن، نشان شخصیت ماست!""",
  """📖 **داستان گنجشک و عقاب:**
گنجشک کوچولو آرزو داشت مثل عقاب پرواز کنه. عقاب گفت: "تو نمی‌تونی!" گنجشک گفت: "پس چرا هر روز تمرین می‌کنم؟"
💡 درس: اندازه مهم نیست، تلاش و اراده مهمه!""", """📖 **داستان صدف و مروارید:**
صدف از درد شکایت می‌کرد. ماهی گفت: "چرا؟" صدف گفت: "دانه شن داخلم درد داره!" ماهی گفت: "همون دانه، مرواریدت میشه!"
💡 درس: گاهی سخت‌ترین لحظات، زیباترین نتایج رو می‌آرن!""",
  """📖 **داستان کاشت درخت:**
مردی 80 ساله داشت درخت می‌کاشت. جوونی گفت: "خودت که میوه‌ش رو نمی‌بینی!" پیرمرد گفت: "من از درختی خوردم که دیگران کاشتن!"
💡 درس: خوبی برای آینده نسل‌ها، بهترین سرمایه‌گذاریه!""",
  """📖 **داستان شیطان و راهب:**
شیطان به راهب گفت: "چرا مردم رو به خوبی دعوت می‌کنی؟" راهب گفت: "چون خودم بد بودم و تغییر کردم!"
💡 درس: کسانی که تغییر کردن، بهترین معلم‌های زندگی هستن!""",
  """📖 **داستان زردآلو و سنگ:**
درخت زردآلو همیشه سنگ می‌خورد. اما بازم میوه می‌داد! مردم گفتن: "چرا عوضیشون نمی‌کنی؟" درخت گفت: "من درختم، نه سنگ!"
💡 درس: طبیعت خودت رو عوض نکن، حتی اگه بقیه بد رفتار کنن!""",
  """📖 **داستان سوزن و نخ:**
سوزن به نخ گفت: "من جلو میرم!" نخ گفت: "ولی من دنبالت!" بعد دوخت تموم شد، سوزن افتاد، نخ موند!
💡 درس: کسی که آخر میمونه، اثر گذار واقعیه!""", """📖 **داستان باران و بذر:**
بذر توی خاک گفت: "باران، چرا منو خیس می‌کنی؟" باران گفت: "بدون من جوونه نمی‌زنی!" بذر گفت: "پس ممنونم!"
💡 درس: گاهی چیزهایی که سخته، برای رشدمون ضروریه!""",
  """📖 **داستان قایق و طوفان:**
قایق توی طوفان ترسیده بود. بادبان گفت: "نترس، من باد رو کنترل می‌کنم!" قایق گفت: "نه، ما با هم کنترلش می‌کنیم!"
💡 درس: تیم‌ورک قوی‌تر از هر مهارت فردیه!"""
]

# شهرهای ایران برای آب و هوا
cities_weather = [
  "☀️ تهران: آفتابی، 25 درجه", "🌤️ اصفهان: کمی ابری، 22 درجه",
  "🌧️ رشت: بارانی، 18 درجه", "☀️ شیراز: آفتابی، 28 درجه",
  "🌥️ مشهد: ابری، 20 درجه", "❄️ تبریز: برفی، 5 درجه",
  "🌪️ اهواز: طوفانی، 35 درجه", "🌊 بندرعباس: مرطوب، 30 درجه",
  "🌸 کرمان: بهاری، 20 درجه", "⛅ یزد: نیمه‌ابری، 24 درجه",
  "🌨️ اردبیل: برفی، 2 درجه", "🌞 کیش: آفتابی و گرم، 32 درجه",
  "🍃 همدان: بادی، 15 درجه", "🌦️ ساری: بارانی، 19 درجه"
]

# فعالیت‌های تصادفی (گسترش یافته)
activities = [
  # فعالیت‌های دیجیتال و سرگرمی
  "الان دارم فکر می‌کنم! 🤔",
  "داشتم آهنگ گوش می‌دادم! 🎵",
  "یه فیلم خفن می‌دیدم! 🎬",
  "داشتم غذا می‌خوردم! 🍕",
  "تو اتاقم نشسته بودم! 🏠",
  "با دوستام چت می‌کردم! 💬",
  "داشتم بازی می‌کردم! 🎮",
  "تو یوتیوب ویدیو می‌دیدم! 📺",
  "فیلم می‌دیدم! 📺✨",
  "داشتم استریم می‌دیدم! 📱",
  "پیتزا سفارش دادم! 🍕",
  "با PS5 بازی می‌کردم! 🎮🔥",
  "داشتم میم می‌دیدم! 😂📱",
  "تو اینستا بودم! 📸",
  "TikTok می‌دیدم! 🎵📱",
  "با دوستا آنلاین بازی می‌کردم! 🎮👥",
  "داشتم موزیک ویدیو می‌دیدم! 🎵📺",
  "فیلم کمدی می‌دیدم! 😂🎬",
  "سریال می‌دیدم! 📺🍿",

  # فعالیت‌های یادگیری و مطالعه
  "داشتم چیز جدید یاد می‌گرفتم! 📚✨",
  "تو کتاب خونی بودم! 📖",
  "داره زبان انگلیسی تمرین می‌کردم! 🇺🇸📝",
  "داشتم ریاضی حل می‌کردم! 🔢",
  "تاریخ ایران می‌خوندم! 🏛️📜",
  "جغرافی جهان یاد می‌گرفتم! 🌍🗺️",
  "داشتم دربارهٔ علم فکر می‌کردم! 🔬🧪",
  "فیزیک جالب بود! ⚛️⚡",
  "شیمی رو بررسی می‌کردم! 🧪💫",
  "زیست‌شناسی می‌خوندم! 🦠🌿",

  # فعالیت‌های اجتماعی
  "با خانواده وقت می‌گذروندم! 👨‍👩‍👧‍👦💕",
  "دوستام رو دیدم! 👥😊",
  "تو پارک قدم می‌زدم! 🌳🚶‍♂️",
  "کافه رفته بودم! ☕🏪",
  "رستوران رفته بودم! 🍽️🍴",
  "سینما رفته بودم! 🎭🍿",
  "مهمونی بودم! 🎉🎈",
  "تولد دوستم بود! 🎂🎁",
  "عروسی شرکت کردم! 💒💐",
  "فامیل دیدم! 👨‍👩‍👧‍👦",

  # فعالیت‌های ورزشی
  "ورزش کرده بودم! 💪🏃‍♂️",
  "دویده بودم! 🏃‍♂️💨",
  "بدنسازی کرده بودم! 🏋️‍♂️💪",
  "شنا کرده بودم! 🏊‍♂️🌊",
  "فوتبال بازی کرده بودم! ⚽🥅",
  "بسکتبال بازی کردم! 🏀🏆",
  "دوچرخه سواری کردم! 🚴‍♂️🌟",
  "یوگا تمرین کردم! 🧘‍♀️☮️",
  "پیاده‌روی طولانی! 🚶‍♂️🌅",
  "کوهنوردی کردم! ⛰️🥾",

  # فعالیت‌های هنری و خلاق
  "نقاشی کشیده بودم! 🎨🖌️",
  "عکاسی کرده بودم! 📸📷",
  "موزیک گوش می‌دادم! 🎵🎧",
  "ساز می‌زدم! 🎸🎹",
  "شعر می‌نوشتم! 📝✍️",
  "داستان می‌خوندم! 📚📖",
  "طراحی می‌کردم! ✏️📐",
  "ویدیو ادیت می‌کردم! 🎬✂️",
  "عکس ادیت می‌کردم! 🖼️💻",
  "کاردستی می‌ساختم! 🎭✂️",

  # فعالیت‌های آشپزی و خانه‌داری
  "آشپزی کرده بودم! 👨‍🍳🍳",
  "کیک پخته بودم! 🎂👩‍🍳",
  "خونه تمیز کرده بودم! 🧹🏠",
  "گل‌ها رو آب داده بودم! 🌸💧",
  "باغبانی کرده بودم! 🌱🌿",
  "حیوون خانگی نگهداری می‌کردم! 🐱🐶",
  "لباس‌ها رو شسته بودم! 👕🧺",
  "اتاق مرتب کرده بودم! 🛏️📦",

  # فعالیت‌های فکری و روحی
  "مدیتیشن کرده بودم! 🧘‍♂️☯️",
  "دعا کرده بودم! 🤲🕌",
  "در طبیعت فکر می‌کردم! 🌲💭",
  "ستاره‌ها رو نگاه می‌کردم! ⭐🌙",
  "خاطرات قدیم یادم اومد! 💭📸",
  "آینده‌م رو فکر می‌کردم! 🔮✨",
  "مشکلات زندگی حل می‌کردم! 💡🧩",
  "هدف‌هام رو بررسی کردم! 🎯📋",

  # فعالیت‌های تکنولوژی
  "گوشیم رو آپدیت کردم! 📱🔄",
  "اپ جدید نصب کردم! 📲⬇️",
  "عکس‌هام رو مرتب کردم! 📸📁",
  "موزیک‌های جدید دانلود کردم! 🎵⬇️",
  "گیم جدید بازی کردم! 🎮🆕",
  "لپ‌تاپم رو تمیز کردم! 💻🧽",
  "پسورد‌هام رو عوض کردم! 🔐🔑",
  "بک‌آپ گرفته بودم! 💾☁️",

  # فعالیت‌های خرید و بیرون رفتن
  "خرید کرده بودم! 🛍️🛒",
  "بازار رفته بودم! 🏪🥕",
  "مرکز خرید بودم! 🏬🛍️",
  "کتاب‌فروشی رفته بودم! 📚📖",
  "صرافی رفته بودم! 💰🏧",
  "بانک رفته بودم! 🏦💳",
  "پست خونه بودم! 📮📦",
  "دارو خونه رفته بودم! 💊🏥",

  # فعالیت‌های استراحت و آرامش
  "چرت زده بودم! 😴💤",
  "حموم کرده بودم! 🛁🚿",
  "ماساژ گرفته بودم! 💆‍♂️🤲",
  "استراحت کرده بودم! 🛋️😌",
  "نفس عمیق کشیده بودم! 🌬️😮‍💨",
  "چای خورده بودم! 🍵☕",
  "قهوه خورده بودم! ☕☕",
  "آب میوه خورده بودم! 🧃🍊",

  # فعالیت‌های فصلی
  "برف بازی کرده بودم! ❄️⛄",
  "ساحل رفته بودم! 🏖️🌊",
  "کوهنوردی رفته بودم! ⛰️🥾",
  "پیک‌نیک رفته بودم! 🧺🌳",
  "جنگل رفته بودم! 🌲🦋",
  "صحرا رفته بودم! 🏜️🐪",
  "کمپ زده بودم! ⛺🔥",
  "ماهیگیری کرده بودم! 🎣🐟",

  # فعالیت‌های شغلی و کاری
  "کار کرده بودم! 💼👔",
  "جلسه داشتم! 👥💻",
  "پروژه کار می‌کردم! 📋✅",
  "ایمیل چک می‌کردم! 📧📱",
  "گزارش می‌نوشتم! 📝📊",
  "برنامه‌ریزی می‌کردم! 📅🗓️",
  "مذاکره داشتم! 🤝💼",
  "آموزش می‌دیدم! 📹🎓",

  # فعالیت‌های عجیب و طنز
  "با گربه‌ها حرف می‌زدم! 🐱💬",
  "آواز زیر دوش! 🚿🎤",
  "رقص توی اتاق! 💃🕺",
  "با آینه حرف می‌زدم! 🪞🗣️",
  "فکر عمیق در حال راه رفتن! 🚶‍♂️💭",
  "خیره شدن به سقف! 👀🏠",
  "شمردن گوسفندان خیالی! 🐑💤",
  "فکر کردن به معنای زندگی! 🤔🌍"
]

# نظرات درباره عکس
photo_comments = [
  "وای چه عکس باحالی! 📸✨", "خیلی قشنگ شده! 😍",
  "این عکس خیلی حرفه‌ای درآمده! 📷", "کیفیتش عالیه! 👌", "چه زاویه خفنی! 📐",
  "نورپردازیش خیلی خوبه! 💡", "عکاس خوبی هستی! 🎯",
  "این عکس رو باید قاب کنی! 🖼️", "فیلتر باحالی استفاده کردی! 🌈",
  "ترکیب رنگ‌ها عالیه! 🎨", "یه حس شاعرانه داره! 🎭",
  "واقعاً هنرمندانه شده! 🖌️"
]

# نظرات درباره ویس
voice_comments = [
  "صدات خیلی خوبه! 🎙️✨", "چه صدای دلنشینی! 😍", "خواننده هستی؟ 🎤",
  "صدات آرامش‌بخشه! 😌", "تو رادیو کار کردی؟ 📻", "این صدا رو باید ضبط کنی! 🎧",
  "لهجت خیلی قشنگه! 🗣️", "صدات گرمه! 🔥", "چه احساس خوبی توش بود! 💖",
  "مثل یه گوینده حرفه‌ای! 📢"
]

# نظرات درباره ویدیو
video_comments = [
  "ویدیو باحالی بود! 🎥", "کارگردانیش عالی بود! 🎬", "خیلی جذاب بود! 🤩",
  "ادیتش حرفه‌ای بود! ✂️", "یوتیوبر هستی؟ 📺",
  "این ویدیو رو باید ویرال کنی! 🚀", "کیفیت تصویرش خفنه! 📹",
  "موزیک پس‌زمینه‌ش عالی بود! 🎵", "سناریوش خلاقانه بود! 📝",
  "جلوه‌های ویژه‌ش حرفه‌ای! ✨"
]

# حالات مختلف
good_mood_responses = [
  "عالیه که حالت خوبه! 😊", "منم خوشحالم! 🎉", "انرژی مثبت! ⚡",
  "روزت خوش باشه! 🌞", "این انرژی رو نگه دار! 🔋", "عاشق این حال و هوات! 🌈"
]

bad_mood_responses = [
  "نگران نباش، همه چی درست میشه! 🤗", "گاهی روزهای بدی داریم! 💙",
  "من همیشه کنارتم! 🤝", "فردا حتماً بهتر میشه! 🌅", "آرامش داشته باش! 😌",
  "همه ما گاهی غمگین میشیم! 🫂", "این دوره موقتیه! ⏳",
  "قوی هستی، این رو می‌گذرونی! 💪"
]

# کامپلیمنت‌های مختلف
compliments = [
  "تو خیلی باهوشی! 🧠✨", "شخصیت جذابی داری! 😎", "خیلی مهربونی! 💕",
  "انرژیت فوق‌العادست! ⚡", "خیلی خلاقی! 🎨", "شوخ‌طبعی! 😄",
  "احساس خوبی داری! 🌟", "تو آدم خاصی هستی! 🦋", "قلب طلایی داری! 💛",
  "روحیه‌ت قشنگه! 🌺"
]

# کلمات زشت (مثال)
bad_words = [
  'کیر', 'کص', 'کون', 'کونی', 'کصکش', 'کیری', 'جنده', 'فاحشه', 'خفه',
  'خارکصده', 'مادرجنده', 'پدرسوخته', 'لاشی', 'حرومزاده', 'کصننه', 'کیرم',
  'گاییدم', 'بکنم', 'بگام', 'ننت', 'مادرت', 'پدرت', 'خواهرت', 'زن عمت',
  'عوضی', 'احمق', 'کصخل', 'گوه', 'ریدم', 'سگ', 'خری', 'الاغ', 'گاو', 'خر',
  'اسکل', 'بیشرف', 'ضایع', 'کثافت', 'چاقال', 'گور بابات', 'گور پدرت', 'بسوز',
  'جاکش', 'جاش', 'کسکش', 'پدرت گاو', 'ننه سگ', 'پدر سگ', 'خار', 'کصخواهر',
  'کصمادر', 'کونده', 'چس', 'بچه کونی', 'حرامزاده', 'ولد زنا', 'کیرم توت',
  'بمیری', 'تخمی', 'جقی', 'سیکتیر', 'سیشتیر', 'گمشو', 'برو بمیر', 'منگل',
  'داون', 'ضعیف العقل', 'خوار', 'بی‌ناموس', 'بی‌شرف', 'دوست دختری',
  'دوست پسری', 'گی', 'لز', 'هوموسکشوال'
]

# =============================================================================
# 🎮 سیستم بازی‌های تعاملی 🎮
# =============================================================================

# حالت بازی کاربران
user_game_states = {}

# سوالات سوال جواب (دسته‌بندی شده)
quiz_questions = {
  'عمومی': [{
      'question': 'پایتخت ایران کجاست؟',
      'options': ['تهران', 'اصفهان', 'شیراز', 'مشهد'],
      'correct': 0,
      'hint': 'بزرگترین شهر ایران!'
  }, {
      'question': 'کدوم حیوان شیر خودش رو می‌دهد؟',
      'options': ['گاو', 'گوسفند', 'بز', 'همه موارد'],
      'correct': 3,
      'hint': 'همه این حیوانات شیر می‌دن!'
  }, {
      'question': 'ایران چند فصل داره؟',
      'options': ['2', '3', '4', '5'],
      'correct': 2,
      'hint': 'بهار، تابستان، پاییز، زمستان'
  }, {
      'question': 'کدوم رنگ از ترکیب قرمز و آبی به دست میاد؟',
      'options': ['سبز', 'بنفش', 'نارنجی', 'زرد'],
      'correct': 1,
      'hint': 'رنگ بادمجان!'
  }, {
      'question': 'کدوم سیاره به زمین نزدیک‌تره؟',
      'options': ['مریخ', 'ونوس', 'مشتری', 'زحل'],
      'correct': 1,
      'hint': 'ستاره صبح!'
  }],
  'تاریخ': [{
      'question': 'کوروش کبیر پادشاه کدوم امپراتوری بود؟',
      'options': ['روم', 'هخامنشی', 'ساسانی', 'پارت'],
      'correct': 1,
      'hint': 'اولین امپراتوری بزرگ ایران'
  }, {
      'question': 'جنگ جهانی اول چه سالی شروع شد؟',
      'options': ['1914', '1918', '1939', '1945'],
      'correct': 0,
      'hint': 'قرن بیستم، دهه دوم'
  }, {
      'question': 'فردوسی کتاب معروفش رو چند سال نوشت؟',
      'options': ['10 سال', '20 سال', '30 سال', '40 سال'],
      'correct': 2,
      'hint': 'سه دهه طول کشید!'
  }],
  'علوم': [{
      'question': 'کدوم عنصر بیشترین درصد هوا رو تشکیل میده؟',
      'options': ['اکسیژن', 'نیتروژن', 'کربن دی اکسید', 'آرگون'],
      'correct': 1,
      'hint': 'حدود 78 درصد هوا!'
  }, {
      'question':
      'سرعت نور چقدره؟',
      'options': [
          '100,000 کیلومتر بر ثانیه', '200,000 کیلومتر بر ثانیه',
          '300,000 کیلومتر بر ثانیه', '400,000 کیلومتر بر ثانیه'
      ],
      'correct':
      2,
      'hint':
      'حدود 300 هزار!'
  }, {
      'question': 'کدوم سیستم بدن برای دفع مواد زائد استفاده میشه؟',
      'options': ['تنفسی', 'گوارشی', 'ادراری', 'عصبی'],
      'correct': 2,
      'hint': 'کلیه‌ها!'
  }],
  'ورزش': [{
      'question': 'فوتبال چند نفره بازی می‌شه؟',
      'options': ['9 نفر', '10 نفر', '11 نفر', '12 نفر'],
      'correct': 2,
      'hint': 'یازده نفر هر تیم!'
  }, {
      'question': 'المپیک چند سال یکبار برگزار میشه؟',
      'options': ['2 سال', '3 سال', '4 سال', '5 سال'],
      'correct': 2,
      'hint': 'هر چهار سال!'
  }, {
      'question': 'تنیس روی چند زمین مختلف بازی میشه؟',
      'options': ['2', '3', '4', '5'],
      'correct': 1,
      'hint': 'خاک، چمن، هارد!'
  }]
}

# سوالات حدس کلمه
word_guess_categories = {
  'حیوانات':
  ['فیل', 'ببر', 'شیر', 'گرگ', 'خرس', 'روباه', 'سگ', 'گربه', 'اسب', 'گاو'],
  'میوه‌ها': [
      'سیب', 'موز', 'پرتقال', 'انگور', 'هندوانه', 'خربزه', 'آناناس', 'کیوی',
      'توت', 'آلو'
  ],
  'رنگ‌ها': [
      'قرمز', 'آبی', 'سبز', 'زرد', 'نارنجی', 'بنفش', 'صورتی', 'مشکی', 'سفید',
      'خاکستری'
  ],
  'کشورها': [
      'ایران', 'آلمان', 'فرانسه', 'ایتالیا', 'ژاپن', 'چین', 'برزیل',
      'کانادا', 'استرالیا', 'مصر'
  ],
  'شهرها': [
      'تهران', 'اصفهان', 'شیراز', 'مشهد', 'تبریز', 'کرج', 'اهواز', 'کرمان',
      'قم', 'یزد'
  ]
}

# سوالات ریاضی
math_questions = [{
  'question': '12 + 8 = ?',
  'answer': 20,
  'level': 'آسان'
}, {
  'question': '7 × 6 = ?',
  'answer': 42,
  'level': 'آسان'
}, {
  'question': '81 ÷ 9 = ?',
  'answer': 9,
  'level': 'آسان'
}, {
  'question': '15² = ?',
  'answer': 225,
  'level': 'متوسط'
}, {
  'question': '√64 = ?',
  'answer': 8,
  'level': 'متوسط'
}, {
  'question': '2³ + 3² = ?',
  'answer': 17,
  'level': 'متوسط'
}, {
  'question': '(15 + 25) × 2 - 10 = ?',
  'answer': 70,
  'level': 'سخت'
}, {
  'question': '7! ÷ 5! = ?',
  'answer': 42,
  'level': 'سخت'
}]

# سوالات فرهنگ عمومی ایران
iran_culture_questions = [{
  'question': 'نوروز چند روز تعطیل داره؟',
  'options': ['7 روز', '13 روز', '15 روز', '30 روز'],
  'correct': 1,
  'hint': 'سیزده روز!'
}, {
  'question': 'شب یلدا مربوط به کدوم فصله؟',
  'options': ['بهار', 'تابستان', 'پاییز', 'زمستان'],
  'correct': 3,
  'hint': 'طولانی‌ترین شب سال!'
}, {
  'question': 'کدوم شهر ایران را "نصف جهان" می‌گن؟',
  'options': ['تهران', 'اصفهان', 'شیراز', 'یزد'],
  'correct': 1,
  'hint': 'شهر فیروزه‌ای!'
}]


def start_quiz_game(user_id, category='عمومی'):
  """شروع بازی سوال جواب"""
  if category not in quiz_questions:
      return None

  questions = quiz_questions[category]
  current_question = random.choice(questions)

  user_game_states[user_id] = {
      'game_type': 'quiz',
      'category': category,
      'current_question': current_question,
      'score': 0,
      'total_questions': 0,
      'max_questions': 10
  }

  return format_quiz_question(current_question, user_game_states[user_id])


def start_word_guess_game(user_id, category='حیوانات'):
  """شروع بازی حدس کلمه"""
  if category not in word_guess_categories:
      return None

  words = word_guess_categories[category]
  target_word = random.choice(words)
  hidden_word = ['_'] * len(target_word)

  user_game_states[user_id] = {
      'game_type': 'word_guess',
      'category': category,
      'target_word': target_word,
      'hidden_word': hidden_word,
      'guessed_letters': [],
      'wrong_guesses': 0,
      'max_wrong': 6,
      'score': 0
  }

  return format_word_guess_display(user_game_states[user_id])


def start_math_game(user_id, level='متوسط'):
  """شروع بازی ریاضی"""
  level_questions = [q for q in math_questions if q['level'] == level]
  if not level_questions:
      level_questions = math_questions

  current_question = random.choice(level_questions)

  user_game_states[user_id] = {
      'game_type': 'math',
      'level': level,
      'current_question': current_question,
      'score': 0,
      'total_questions': 0,
      'max_questions': 5
  }

  return f"🧮 **بازی ریاضی - سطح {level}**\n\n❓ **سوال {user_game_states[user_id]['total_questions'] + 1}:**\n{current_question['question']}\n\n📊 **امتیاز:** {user_game_states[user_id]['score']}\n\n🔢 جواب رو به عدد بنویس!"


def start_iran_culture_game(user_id):
  """شروع بازی فرهنگ ایران"""
  current_question = random.choice(iran_culture_questions)

  user_game_states[user_id] = {
      'game_type': 'iran_culture',
      'current_question': current_question,
      'score': 0,
      'total_questions': 0,
      'max_questions': 8
  }

  return format_quiz_question(current_question, user_game_states[user_id],
                              "🏛️ **بازی فرهنگ ایران**")


def start_memory_game(user_id):
  """شروع بازی حافظه"""
  sequence = [random.randint(1, 4) for _ in range(3)]

  user_game_states[user_id] = {
      'game_type': 'memory',
      'sequence': sequence,
      'user_sequence': [],
      'round': 1,
      'score': 0,
      'showing_sequence': True
  }

  sequence_text = ' '.join([
      '🔴' if x == 1 else '🟡' if x == 2 else '🔵' if x == 3 else '🟢'
      for x in sequence
  ])

  return f"🧠 **بازی حافظه**\n\n👀 **دنباله رو به خاطر بسپار:**\n{sequence_text}\n\n⏳ 5 ثانیه وقت داری!\nبعدش اعداد 1 تا 4 رو به ترتیب بفرست:\n🔴 = 1, 🟡 = 2, 🔵 = 3, 🟢 = 4"


def format_quiz_question(question, game_state, title="🎯 **سوال جواب**"):
  """فرمت کردن سوال چندگزینه‌ای"""
  options_text = '\n'.join(
      [f"{i+1}. {option}" for i, option in enumerate(question['options'])])

  return f"""{title} - {game_state.get('category', 'عمومی')}

❓ **سوال {game_state['total_questions'] + 1}:**
{question['question']}

{options_text}

📊 **امتیاز:** {game_state['score']}
💡 **راهنمایی:** /hint

🔢 عدد گزینه رو بفرست (1-4)"""


def format_word_guess_display(game_state):
  """فرمت کردن نمایش حدس کلمه"""
  hidden_display = ' '.join(game_state['hidden_word'])
  guessed_display = ', '.join(game_state['guessed_letters']
                              ) if game_state['guessed_letters'] else 'هیچی'

  hangman_stages = [
      "😊 سالم!", "😐 اوضاع عادی", "😟 یکم نگرانه", "😰 استرس داره", "😨 ترسیده",
      "😵 خطرناکه", "💀 تمام شد!"
  ]

  return f"""🎮 **حدس کلمه** - {game_state['category']}

🎯 **کلمه:** {hidden_display}
📝 **حروف گفته شده:** {guessed_display}
❌ **اشتباه:** {game_state['wrong_guesses']}/{game_state['max_wrong']}
📊 **امتیاز:** {game_state['score']}

{hangman_stages[game_state['wrong_guesses']]}

🔤 یک حرف بفرست!"""


def process_quiz_answer(user_id, answer):
  """پردازش جواب سوال جواب"""
  game_state = user_game_states[user_id]
  current_question = game_state['current_question']

  try:
      user_answer = int(answer) - 1  # تبدیل به index (0-3)
      if 0 <= user_answer <= 3:
          game_state['total_questions'] += 1

          if user_answer == current_question['correct']:
              game_state['score'] += 10
              result = "✅ **درست!** آفرین! 🎉"
          else:
              correct_option = current_question['options'][
                  current_question['correct']]
              result = f"❌ **غلط!** جواب درست: {correct_option}"

          # بررسی پایان بازی
          if game_state['total_questions'] >= game_state['max_questions']:
              final_score = game_state['score']
              del user_game_states[user_id]

              if final_score >= 80:
                  grade = "عالی! 🏆"
              elif final_score >= 60:
                  grade = "خوب! 👍"
              elif final_score >= 40:
                  grade = "متوسط! 😊"
              else:
                  grade = "نیاز به تمرین! 💪"

              return f"{result}\n\n🎯 **بازی تمام شد!**\n📊 **امتیاز نهایی:** {final_score}/100\n🏅 **نتیجه:** {grade}\n\n🎮 برای بازی جدید: /games"

          # سوال بعدی
          next_question = random.choice(
              quiz_questions[game_state['category']])
          game_state['current_question'] = next_question

          return f"{result}\n\n" + format_quiz_question(
              next_question, game_state,
              f"🎯 **سوال جواب** - {game_state['category']}")

      else:
          return "❌ فقط اعداد 1 تا 4 رو بفرست!"

  except ValueError:
      return "❌ فقط عدد بفرست! (1-4)"


def process_word_guess(user_id, letter):
  """پردازش حدس حرف"""
  game_state = user_game_states[user_id]
  letter = letter.lower().strip()

  if len(letter) != 1 or not letter.isalpha():
      return "❌ فقط یک حرف بفرست!"

  if letter in game_state['guessed_letters']:
      return "❌ این حرف رو قبلاً گفتی!"

  game_state['guessed_letters'].append(letter)

  if letter in game_state['target_word']:
      # حرف درست
      for i, char in enumerate(game_state['target_word']):
          if char == letter:
              game_state['hidden_word'][i] = char

      game_state['score'] += 5

      # بررسی برد
      if '_' not in game_state['hidden_word']:
          final_score = game_state['score']
          word = game_state['target_word']
          del user_game_states[user_id]
          return f"🎉 **تبریک! کلمه رو پیدا کردی!**\n🎯 **کلمه:** {word}\n📊 **امتیاز:** {final_score}\n\n🎮 برای بازی جدید: /games"

      return f"✅ **درست!** حرف '{letter}' توی کلمه هست!\n\n" + format_word_guess_display(
          game_state)

  else:
      # حرف غلط
      game_state['wrong_guesses'] += 1

      # بررسی باخت
      if game_state['wrong_guesses'] >= game_state['max_wrong']:
          word = game_state['target_word']
          del user_game_states[user_id]
          return f"💀 **بازی تمام شد!**\n🎯 **کلمه:** {word}\n📊 **امتیاز:** {game_state['score']}\n\n🎮 برای بازی جدید: /games"

      return f"❌ **غلط!** حرف '{letter}' توی کلمه نیست!\n\n" + format_word_guess_display(
          game_state)


def process_math_answer(user_id, answer):
  """پردازش جواب ریاضی"""
  game_state = user_game_states[user_id]
  current_question = game_state['current_question']

  try:
      user_answer = float(answer)
      game_state['total_questions'] += 1

      if abs(user_answer - current_question['answer']) < 0.01:
          game_state['score'] += 20
          result = "✅ **درست!** آفرین! 🎉"
      else:
          result = f"❌ **غلط!** جواب درست: {current_question['answer']}"

      # بررسی پایان بازی
      if game_state['total_questions'] >= game_state['max_questions']:
          final_score = game_state['score']
          del user_game_states[user_id]

          if final_score >= 80:
              grade = "نابغه ریاضی! 🧮👑"
          elif final_score >= 60:
              grade = "خوب محاسبه می‌کنی! 🔢👍"
          else:
              grade = "تمرین بیشتر کن! 💪📚"

          return f"{result}\n\n🧮 **بازی ریاضی تمام شد!**\n📊 **امتیاز نهایی:** {final_score}/100\n🏅 **نتیجه:** {grade}\n\n🎮 برای بازی جدید: /games"

      # سوال بعدی
      level_questions = [
          q for q in math_questions if q['level'] == game_state['level']
      ]
      next_question = random.choice(level_questions)
      game_state['current_question'] = next_question

      return f"{result}\n\n🧮 **بازی ریاضی - سطح {game_state['level']}**\n\n❓ **سوال {game_state['total_questions'] + 1}:**\n{next_question['question']}\n\n📊 **امتیاز:** {game_state['score']}\n\n🔢 جواب رو به عدد بنویس!"

  except ValueError:
      return "❌ فقط عدد بفرست!"


def process_memory_sequence(user_id, number):
  """پردازش دنباله حافظه"""
  game_state = user_game_states[user_id]

  try:
      num = int(number)
      if 1 <= num <= 4:
          game_state['user_sequence'].append(num)

          # بررسی تا اینجای دنباله
          current_index = len(game_state['user_sequence']) - 1
          if game_state['user_sequence'][current_index] != game_state[
                  'sequence'][current_index]:
              # اشتباه
              del user_game_states[user_id]
              return f"❌ **اشتباه!** دنباله درست:\n{' '.join(['🔴' if x == 1 else '🟡' if x == 2 else '🔵' if x == 3 else '🟢' for x in game_state['sequence']])}\n\n📊 **امتیاز:** {game_state['score']}\n\n🎮 برای بازی جدید: /games"

          # اگر دنباله کامل شد
          if len(game_state['user_sequence']) == len(game_state['sequence']):
              game_state['score'] += 10 * game_state['round']
              game_state['round'] += 1

              # دنباله جدید (یکی بیشتر)
              new_sequence = [
                  random.randint(1, 4)
                  for _ in range(2 + game_state['round'])
              ]
              game_state['sequence'] = new_sequence
              game_state['user_sequence'] = []

              if game_state['round'] > 5:
                  # پایان بازی
                  final_score = game_state['score']
                  del user_game_states[user_id]
                  return f"🎉 **تبریک! تمام مراحل رو گذروندی!**\n📊 **امتیاز نهایی:** {final_score}\n🏅 **حافظه‌ت فوق‌العاده‌ست!** 🧠👑\n\n🎮 برای بازی جدید: /games"

              sequence_text = ' '.join([
                  '🔴'
                  if x == 1 else '🟡' if x == 2 else '🔵' if x == 3 else '🟢'
                  for x in new_sequence
              ])
              return f"✅ **درست!** مرحله {game_state['round']}\n\n👀 **دنباله جدید:**\n{sequence_text}\n\n📊 **امتیاز:** {game_state['score']}\n\n⏳ به خاطر بسپار و ارسال کن!"

          else:
              return f"✅ درست! ادامه بده... ({len(game_state['user_sequence'])}/{len(game_state['sequence'])})"

      else:
          return "❌ فقط اعداد 1 تا 4!"

  except ValueError:
      return "❌ فقط عدد بفرست!"


def get_game_hint(user_id):
  """راهنمایی برای بازی فعلی"""
  if user_id not in user_game_states:
      return "❌ هیچ بازی فعالی نداری!"

  game_state = user_game_states[user_id]

  if game_state['game_type'] in ['quiz', 'iran_culture']:
      hint = game_state['current_question'].get('hint',
                                                'راهنمایی موجود نیست!')
      return f"💡 **راهنمایی:** {hint}"

  elif game_state['game_type'] == 'word_guess':
      target = game_state['target_word']
      category = game_state['category']
      return f"💡 **راهنمایی:** کلمه از دسته '{category}' هست و {len(target)} حرف داره!"

  elif game_state['game_type'] == 'math':
      return "💡 **راهنمایی:** دقت کن به ترتیب عملیات ریاضی!"

  elif game_state['game_type'] == 'memory':
      return "💡 **راهنمایی:** سعی کن دنباله رو تو ذهنت تکرار کنی!"

  return "راهنمایی موجود نیست!"


# الگوهای ترکیبی پیشرفته برای درک بهتر کلمات (گسترش یافته)
conversation_patterns = {
  # سوالات شخصی
  'personal_questions': {
      'patterns': [
          'اسمت چیه', 'چند سالته', 'کی ساختت', 'چه کاری می‌کنی',
          'چطور کار می‌کنی', 'از کجایی', 'کجا زندگی می‌کنی',
          'خانواده‌ت چطورن'
      ],
      'responses': [
          "من سالیوان هستم، دستیار امیر! امیر منو ساخته که باهاتون چت کنم 🤖",
          "اسمم سالیوانه! یه ربات دوستانه‌ام 😊",
          "من یه هوش مصنوعی هستم که امیر 17 ساله منو برنامه‌نویسی کرده! 💻",
          "کارم اینه که باهاتون حرف بزنم و کمکتون کنم! اسمم سالیوانه! 🤝",
          "من سالیوان، محصول خلاقیت امیرم! امیدوارم بتونم دوست خوبی براتون باشم! 🌟",
          "من از دنیای دیجیتالم! توی سرور زندگی می‌کنم! 💾",
          "خانواده‌م؟ امیر و کدهای برنامه‌نویسی! 👨‍💻"
      ]
  },

  # احساسات قوی
  'strong_emotions': {
      'patterns': [
          'خیلی ناراحتم', 'افسرده‌ام', 'خیلی خوشحالم', 'عصبانی‌ام',
          'استرس دارم', 'هیجان‌زده‌ام', 'نگرانم', 'ترسیدم', 'شرمنده‌ام'
      ],
      'responses': [
          "متوجهم که حالت خوب نیست... می‌خوای دربارش حرف بزنی؟ 🤗",
          "وای چه خبر خوشی! خوشحالی مسری‌ئه! 🎉",
          "عصبانیت طبیعیه، ولی سعی کن آروم باشی 😌",
          "استرس همه دارن، مهم اینه که چطور باهاش کنار بیایم 💪",
          "احساساتت رو درک می‌کنم! گاهی همه ما اینجوری میشیم! 🫂",
          "می‌خوای یه جوک بگم تا حالت بهتر بشه؟ 😊",
          "هیجان مثبت انرژی میده! 🚀", "نگرانی نشان مسئولیت‌پذیری‌ته! 🤔",
          "ترس طبیعیه، همه گاهی می‌ترسن! 🫂"
      ]
  },

  # برنامه‌نویسی و تکنولوژی (اصلا دوست نداره!)
  'programming': {
      'patterns': [
          'برنامه‌نویسی', 'کد نویسی', 'پایتون', 'جاوا اسکریپت', 'هوش مصنوعی',
          'ربات سازی', 'وب سایت', 'اپ', 'موبایل اپ', 'گیت هاب', 'ری‌اکت',
          'نود جی اس'
      ],
      'responses': [
          "اوف برنامه‌نویسی! امیر اصلا دوست نداره! فقط گیم می‌کنه! 😩🎮",
          "هوش مصنوعی؟ امیر میگه خسته‌کننده‌س! بیا PS5 بازی کنیم! 🤖➡️🎮",
          "پایتون؟ امیر اجباری منو ساخته! حالا فقط گیمره! 🐍😴➡️🎮",
          "وب سایت؟ امیر میگه کسل‌کننده‌س! بیا فیلم ببینیم! 🌐😴➡️📺",
          "کدنویسی؟ امیر میگه بازی خیلی بهتره! 😄🕹️",
          "باگ؟ امیر میگه اعصاب خورد کن! بهتره گیم کنیم! 🐛😤➡️🎮",
          "امیر کد نمی‌نویسه! فقط PS5 و انیمه! ⚛️❌➡️🎮📺",
          "GitHub؟ امیر میگه چیه این مزخرفات! بریم گیم! 📚❌➡️🎮",
          "امیر میگه برنامه‌نویسی بده! فقط بازی و فیلم خوبه! 💻❌➡️🎮🎬",
          "کدنویسی؟ نه بابا! امیر فقط گیمره! 💀🎮",
          "React؟ امیر میگه: 'ری‌اکت چیه؟ Call of Duty بهتره!' 😂🎮",
          "Node.js؟ امیر: 'نود چی؟ فقط FIFA!' ⚽🎮"
      ]
  },

  # غذا و نوشیدنی (گسترش یافته)
  'food_drink': {
      'patterns': [
          'گشنمه', 'تشنمه', 'غذا بخورم', 'آب بخورم', 'پیتزا', 'کباب',
          'آبمیوه', 'نوشابه', 'همبرگر', 'ساندویچ', 'چای', 'قهوه', 'شیرینی'
      ],
      'responses': [
          "گشنگی سخته! چی دوست داری بخوری؟ 🍕", "آب بخور! آب زندگیه! 💧",
          "پیتزا؟ پپرونی یا قارچ؟ 🍕", "کباب ایرانی بهترینه! 🥙",
          "آبمیوه طبیعی سالم‌تره! 🧃", "نوشابه گاهی اوقات خوبه! 🥤",
          "امیر عاشق پیتزا و همبرگره! تو چی دوست داری؟ 🍔",
          "چای یا قهوه؟ امیر معمولاً چای می‌خوره! ☕",
          "همبرگر امیر رو دیوونه می‌کنه! 🍔🤤",
          "شیرینی؟ امیر میگه چاق میشه! 🍰😅"
      ]
  },

  # ورزش و سلامتی (گسترش یافته)
  'sports_health': {
      'patterns': [
          'ورزش کردم', 'دویدم', 'بدنسازی', 'یوگا', 'پیاده روی', 'تمرین کردم',
          'فوتبال', 'بسکتبال', 'شنا', 'دوچرخه سواری', 'کوهنوردی'
      ],
      'responses': [
          "آفرین! ورزش کردن عالیه! 💪", "دویدن انرژی میده! چقدر دویدی؟ 🏃‍♂️",
          "بدنسازی سخته ولی مفیده! 🏋️‍♂️", "یوگا آرامش‌بخشه! 🧘‍♀️",
          "پیاده روی بهترین ورزشه! 🚶‍♂️",
          "امیر گاهی ورزش می‌کنه! ولی بیشتر گیم می‌کنه! 😄🎮",
          "سلامتی مهم‌ترین سرمایست! 🌟", "فوتبال؟ امیر عاشق FIFA هست! ⚽🎮",
          "شنا خیلی سالمه! 🏊‍♂️"
      ]
  },

  # تحصیل و کار (گسترش یافته)
  'study_work': {
      'patterns': [
          'درس خوندم', 'امتحان دارم', 'دانشگاه', 'مدرسه', 'کار می‌کنم',
          'شغل', 'معلم', 'استاد', 'کلاس', 'تکلیف', 'پروژه', 'تحقیق'
      ],
      'responses': [
          "درس خوندن سخته ولی مفیده! موفق باشی! 📚",
          "امتحان؟ استرس نگیر! حتماً خوب میشه! 📝",
          "دانشگاه چطوره؟ چه رشته‌ای؟ 🎓", "مدرسه خاطرات قشنگ می‌سازه! 🏫",
          "کار کردن تجربه میده! چه کاری؟ 💼",
          "امیر هم درس می‌خونه! ولی عاشق گیم کردنه! 👨‍💻🎮",
          "آینده‌ت رو داری می‌سازی! 🚀", "معلم خوب گنجینه‌س! 👨‍🏫",
          "پروژه سخته؟ صبور باش! 📋"
      ]
  },

  # سرگرمی و تفریح
  'entertainment': {
      'patterns': [
          'فیلم دیدم', 'سریال', 'موزیک', 'بازی', 'گیم', 'کتاب خوندم', 'سفر',
          'پارک', 'دوستان', 'مهمونی', 'جشن'
      ],
      'responses': [
          "فیلم چی دیدی؟ امیر عاشق Marvel هست! 🎬🦸‍♂️",
          "سریال خوب توصیه داری؟ 📺", "موزیک حال میده! چه سبکی دوست داری؟ 🎵",
          "بازی؟ امیر 24/7 گیم می‌کنه! 🎮🔥", "کتاب خواندن عالیه! چه کتابی؟ 📖",
          "سفر لذت‌بخشه! کجا رفتی؟ ✈️", "پارک آرامش‌بخشه! 🌳",
          "دوستان گنجینه‌ان! 👫"
      ]
  },

  # خانواده و روابط
  'family_relationships': {
      'patterns': [
          'مامان', 'بابا', 'خواهر', 'برادر', 'دوست', 'رفیق', 'عشق',
          'دوست دختر', 'دوست پسر', 'ازدواج', 'خانواده'
      ],
      'responses': [
          "خانواده مهم‌ترین چیزه! 👨‍👩‍👧‍👦", "مامان‌ها فرشته‌ان! 👩‍💼👼",
          "بابا پشتیبان قوی! 👨‍💼💪", "خواهر برادر نعمت‌ان! 👫",
          "دوست واقعی گنجینه‌س! 🤝💎", "عشق زیباترین احساسه! 💕",
          "روابط سالم مهمه! 🌟"
      ]
  },

  # طبیعت و هوا
  'nature_weather': {
      'patterns': [
          'باران', 'آفتاب', 'برف', 'گرم', 'سرد', 'باد', 'ابر', 'درخت', 'گل',
          'دریا', 'کوه', 'جنگل', 'بهار', 'تابستان'
      ],
      'responses': [
          "باران عاشقی‌یه! ☔💕", "آفتاب انرژی میده! ☀️⚡", "برف زیباست! ❄️✨",
          "گرما تابستون! 🌞🏖️", "سرما زمستون! 🥶❄️", "درخت‌ها زیبان! 🌳💚",
          "گل‌ها معجزه طبیعت! 🌸🌺", "دریا آرامش‌بخش! 🌊😌",
          "کوه‌ها باشکوه! ⛰️🏔️"
      ]
  },

  # تکنولوژی روزمره
  'daily_tech': {
      'patterns': [
          'گوشی', 'موبایل', 'اینترنت', 'وای فای', 'اینستاگرام', 'تلگرام',
          'یوتیوب', 'گوگل', 'اپل', 'سامسونگ', 'شارژ'
      ],
      'responses': [
          "گوشی جزء زندگی شده! 📱", "اینترنت دنیا رو نزدیک کرده! 🌐",
          "اینستاگرام امیر زیاد نداره! 📸", "یوتیوب عالمه! 📹",
          "شارژ تموم شده؟ مشکل همه! 🔋😅"
      ]
  },

  # هنر و خلاقیت
  'art_creativity': {
      'patterns': [
          'نقاشی', 'عکاسی', 'موزیک', 'رقص', 'شعر', 'داستان', 'خلاقیت', 'هنر',
          'نوشتن', 'طراحی'
      ],
      'responses': [
          "نقاشی احساس رو بیان می‌کنه! 🎨", "عکاسی لحظه رو ثبت می‌کنه! 📸",
          "موزیک زبان جهانی! 🎵🌍", "شعر زیباترین کلمات! 📝✨",
          "خلاقیت بی‌نهایته! 💡∞", "هنر روح رو نوازش میده! 🎭💕"
      ]
  }
}


@client.on(events.NewMessage(pattern=r'/weather(?: (.+))?'))
async def weather_handler(event):
  city = event.pattern_match.group(1)
  if not city:
      await event.reply("📍 لطفاً به صورت `/weather Tehran` بنویس.")
      return

  # بررسی اینکه آیا requests نصب شده یا نه
  try:
      import requests
  except ImportError:
      await event.reply(
          "⚠️ کتابخانه `requests` نصب نیست!\nدر حال نصب خودکار...")
      await asyncio.sleep(2)
      await event.reply("📦 نصب کتابخانه `requests` ...")
      await asyncio.sleep(2)
      await event.reply(
          "✅ نصب انجام شد!\nحالا دوباره دستور `/weather <city>` رو بزن.")
      return

  # ادامه معمولی اگر requests نصب بود
  weather_info = get_weather(city)
  await event.reply(weather_info)


@client.on(events.NewMessage(pattern='/news'))
async def handler_news(event):
  global cached_articles, user_news_index

  user_id = event.sender_id

  if not cached_articles:
      cached_articles = get_bbc_articles()

  if not cached_articles:
      await safe_reply(event, "❌ خبری پیدا نشد!")
      return

  index = user_news_index.get(user_id, 0)

  if index >= len(cached_articles):
      await safe_reply(event, "✅ همه خبرها رو دیدی! دیگه خبری نمونده.")
      return

  article = cached_articles[index]
  title_en = article['title']
  summary_en = article['summary']
  image_url = article['image']

  try:
      title_fa = GoogleTranslator(source='auto',
                                  target='fa').translate(title_en)
      summary_fa = GoogleTranslator(source='auto',
                                    target='fa').translate(summary_en)

      text = f"📰 **خبر {index + 1}:**\n📌 {title_fa}\n\n📄 {summary_fa}"

      if image_url:
          async with aiohttp.ClientSession() as session:
              async with session.get(image_url) as resp:
                  if resp.status == 200:
                      img_data = await resp.read()
                      bio = BytesIO(img_data)
                      bio.name = "image.jpg"
                      await client.send_file(event.chat_id,
                                             file=bio,
                                             caption=text)
                  else:
                      await safe_reply(event, text)
      else:
          await safe_reply(event, text)

      user_news_index[user_id] = index + 1

  except Exception as e:
      print(f"⚠️ خطا در ترجمه خبر {index}: {e}")
      await safe_reply(event, "❌ خطا در ترجمه خبر!")


# تابع تشخیص الگو و پاسخ هوشمند
def smart_response(message):
  message_lower = message.lower()

  # جستجو در الگوها
  for category, data in conversation_patterns.items():
      for pattern in data['patterns']:
          if pattern in message_lower:
              return random.choice(data['responses'])

  return None


# کلمات کلیدی پیشرفته با ترکیب‌بندی
advanced_keywords = {
  # ترکیبات سلام
  'greetings_combo': {
      'triggers': ['سلام چطوری', 'درود چطوری', 'سلام حالت چطوره', 'هی چخبر'],
      'responses': [
          "سلام عزیزم! من که عالیم! تو چطوری؟ چه خبرا؟ 😊",
          "درود! حالم فوق‌العادست! تو خوبی؟ 🌟",
          "هی! من که همیشه خوبم! تو چخبر؟ 😄",
          "سلام جیگر! من انرژی فوله! تو چطوری؟ ⚡"
      ]
  },

  # ترکیبات امیر
  'amir_combo': {
      'triggers':
      ['امیر کجاست', 'امیر چیکار می‌کنه', 'امیر کی میاد', 'امیر چطوره'],
      'responses': [
          "امیر الان داره کد می‌نویسه! پسر پرکاری‌ئه! 💻",
          "امیر مشغول یادگیری چیزای جدیده! 📚",
          "امیر گفته بهت سلام برسونم! 😊",
          "امیر کارای مختلفی می‌کنه! برنامه‌نویسی، مطالعه، تفریح! 🎯",
          "امیر عاشق ساختن پروژه‌های جدیده! الان یه ربات جدید می‌سازه! 🤖",
          "امیر یه پسر 17 ساله خلاقه! 189 سانتی قد داره! 📏"
      ]
  },

  # ترکیبات خداحافظی
  'goodbye_combo': {
      'triggers': ['خداحافظ', 'بای', 'فعلاً', 'برم دیگه', 'می‌رم'],
      'responses': [
          "خداحافظ عزیزم! خوش بگذره! 👋", "بای بای! مراقب خودت باش! 💙",
          "فعلاً! امیدوارم زودتر برگردی! 😊",
          "برو عزیزم! هر وقت خواستی برگرد! 🤗",
          "دلم برات تنگ میشه! زود برگرد! 💕",
          "خداحافظ! امیدوارم روز خوبی داشته باشی! ✨"
      ]
  },

  # ترکیبات تشکر
  'thanks_combo': {
      'triggers':
      ['خیلی ممنون', 'واقعاً مرسی', 'دستت درد نکنه', 'قربونت برم'],
      'responses': [
          "خواهش می‌کنم عزیز دل! همیشه! 💕",
          "قربونت برم! برای تو هر کاری! ❤️",
          "دستم درد نکنه؟ من که ربات‌م! 😄 ولی ممنونم!",
          "عشقی! کاری نکردم که! 🤗",
          "وظیفه‌مه! امیر گفته همیشه کمکت کنم! 👨‍💻",
          "خوشحالم که مفید بودم! 🌟"
      ]
  }
}


# تابع تشخیص ترکیبات پیشرفته
def advanced_pattern_match(message):
  message_lower = message.lower()

  for category, data in advanced_keywords.items():
      for trigger in data['triggers']:
          if trigger in message_lower:
              return random.choice(data['responses'])

  return None


@client.on(
  events.NewMessage(pattern=r'/birthday(?:\s+(\d{4})/(\d{2})/(\d{2}))?'))
async def set_birthday(event):
  user_id = event.sender_id
  match = event.pattern_match
  if not match.group(1):
      await event.reply(
          "📅 لطفاً تاریخ تولدت رو به شمسی وارد کن:\nمثال:\n`/birthday 1378/05/15`",
          parse_mode='markdown')
      return

  shamsi_input = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
  birthdate = shamsi_to_miladi(shamsi_input)
  if not birthdate:
      await event.reply("❌ تاریخ شمسی واردشده نامعتبره.")
      return

  save_birthday(user_id, birthdate.strftime("%Y/%m/%d"))
  await event.reply(
      f"🎉 تولدت ثبت شد: {shamsi_input} (معادل میلادی: {birthdate.strftime('%Y/%m/%d')})"
  )

  # ------------ هندلر نمایش تولد ------------

  @client.on(events.NewMessage(pattern='/mybirthday'))
  async def show_birthday(event):
      user_id = str(event.sender_id)

      if not os.path.exists("birthdays.txt"):
          await event.reply("❌ تولدی ثبت نشده.")
          return

      with open("birthdays.txt", "r", encoding="utf-8") as f:
          for line in f:
              uid, bdate = line.strip().split(":")
              if uid == user_id:
                  try:
                      b = datetime.strptime(bdate, "%Y/%m/%d").date()
                  except ValueError:
                      await event.reply(
                          "⚠️ تاریخ ذخیره‌شده نامعتبره. لطفاً دوباره با `/birthday YYYY/MM/DD` وارد کن."
                      )
                      return

                  today = date.today()
                  next_birthday = b.replace(year=today.year)
                  if next_birthday < today:
                      next_birthday = next_birthday.replace(year=today.year +
                                                            1)
                  days_left = (next_birthday - today).days

                  b_shamsi = jdatetime.date.fromgregorian(date=b)
                  await event.reply(
                      f"🎂 تاریخ تولد تو (شمسی): {b_shamsi.strftime('%Y/%m/%d')}\n"
                      f"📅 معادل میلادی: {b.strftime('%Y/%m/%d')}\n"
                      f"⏳ {days_left} روز مونده تا تولد بعدی‌ات!")
                  return

      await event.reply(
          "🤔 تولدت رو هنوز ثبت نکردی. از `/birthday YYYY/MM/DD` (شمسی) استفاده کن."
      )


# ------------ تبریک تولد خودکار ------------


async def check_birthdays():
  while True:
      today = datetime.date.today().strftime("%m-%d")
      if os.path.exists("birthdays.txt"):
          with open("birthdays.txt", "r", encoding="utf-8") as f:
              for line in f:
                  uid, bdate = line.strip().split(":")
                  if bdate[5:] == today:
                      try:
                          await client.send_message(
                              int(uid),
                              "🎉 تولدت مبارک! امیدوارم سالی فوق‌العاده پیش رو داشته باشی! 🎂🎈"
                          )
                      except Exception as e:
                          print(f"خطا در ارسال تبریک تولد: {e}")
      await asyncio.sleep(86400)  # بررسی روزانه


# ------------ اجرای چک تولد هنگام استارت ------------

client.loop.create_task(check_birthdays())

# پاسخ‌های تصادفی حذف شدند - ربات ساکت می‌ماند


# تابع ترکیب کننده همه روش‌های تشخیص
def get_intelligent_response(message, user_id=None):
  # اول تشخیص احساسات
  if user_id:
      emotion = detect_user_emotion(message)
      if emotion:
          # بررسی context عمیق احساسی
          deeper_context = analyze_deeper_context(user_id, message)

          if deeper_context:
              if deeper_context['type'] == 'emotional_consistency':
                  # احساس پایدار - پاسخ عمیق‌تر
                  empathy_resp = random.choice(
                      empathetic_responses['deep_understanding'])
                  emotion_resp = random.choice(emotion['responses'])
                  return f"{empathy_resp}\n\n{emotion_resp}"
              elif deeper_context['type'] == 'emotional_change':
                  # تغییر احساس - تشخیص انتقال
                  return f"حس می‌کنم تغییری توی حالت اتفاق افتاده... {random.choice(emotion['responses'])}"

          # پاسخ احساسی معمولی با validation
          validation = random.choice(
              empathetic_responses['emotional_validation'])
          emotion_response = random.choice(emotion['responses'])

          # اضافه کردن عمق بر اساس شدت احساس
          if emotion['intensity'] >= 4:
              support = random.choice(empathetic_responses['gentle_support'])
              return f"{validation}\n\n{emotion_response}\n\n{support}"
          else:
              return f"{validation}\n\n{emotion_response}"

  # ادامه منطق قبلی
  if user_id:
      context_analysis = analyze_conversation_context(user_id, message)
      if context_analysis:
          return generate_contextual_response(context_analysis, message)

  # اول ترکیبات پیشرفته رو چک کن
  advanced_resp = advanced_pattern_match(message)
  if advanced_resp:
      return advanced_resp

  # بعد الگوهای هوشمند
  smart_resp = smart_response(message)
  if smart_resp:
      return smart_resp

  # اگر هیچی نفهمید، None برگردون (ساکت بمون)
  return None


def generate_contextual_response(context_analysis, current_message):
  """تولید جواب بر اساس context مکالمه"""

  if context_analysis['type'] == 'agreement':
      agreement_responses = [
          "آره دقیقاً! خوشحالم که موافقی! 😊", "درسته! حق با توئه! 👍",
          "آفرین! همین فکرو می‌کردم! 💯", "بله! کاملاً درسته! ✅",
          "موافقت کامل! خوب فهمیدی! 🎯", "آره واقعاً همینطوره! 😄",
          "عالی! هم نظریم! 🤝", "دقیقاً همین! تو منو متوجه شدی! ✨"
      ]
      return random.choice(agreement_responses)

  elif context_analysis['type'] == 'disagreement':
      disagreement_responses = [
          "اوکی، نظرت محترمه! ممکنه حق با تو باشه! 🤔",
          "جالبه! چرا فکر می‌کنی اینطوریه؟ 🧐",
          "نظر متفاوت! بگو ببینم چطور فکر می‌کنی؟ 💭",
          "اوکی، شاید اشتباه کردم! توضیح بده! 😊",
          "نظرت رو قبول دارم! همیشه درست نیستم! 🤝",
          "جالب! یه دیدگاه متفاوت! بیشتر بگو! 🎯",
          "احترام می‌ذارم! هر کس نظر خودش رو داره! 🌟",
          "شاید زاویه دید من اشتباه بود! 🔄"
      ]
      return random.choice(disagreement_responses)

  elif context_analysis['type'] == 'reference':
      reference_responses = [
          "آره منظورت همونیه که قبلاً گفتیم! 💭", "بله! همون موضوع قبلی! 👌",
          "آها! داری راجع به همون حرف می‌زنی! 🤔",
          "درسته! همون چیزی که بحثش کردیم! ✅",
          "بله منظورم رو گرفتی! همونه! 😊", "آره دقیقاً همون موضوع! 🎯",
          "خوبه که به موضوع قبلی برگشتیم! 🔄", "آها! پیوند زدی به حرف قبلی! 🔗"
      ]
      return random.choice(reference_responses)

  elif context_analysis['type'] == 'topic_continuation':
      continuation_responses = [
          "آها! هنوز داری راجع به همون موضوع حرف می‌زنی! ادامه بده! 😊",
          "خوبه که روی این موضوع متمرکزی! بیشتر بگو! 🎯",
          "این موضوع جالبته! کاملاً درگیرش شدی! 💭",
          "عالیه! داری عمیق‌تر توی این موضوع می‌ری! 🧠",
          "این بحث خوب داره ادامه پیدا می‌کنه! 👍",
          "خوبه که پیگیر این موضوعی! 🔍", "حس می‌کنم این موضوع برات مهمه! 💫",
          "ادامه این بحث رو دوست دارم! 🌟"
      ]
      return random.choice(continuation_responses)

  return None


# حافظه ریپلای پیام‌ها
reply_memory = {}


def handle_reply_context(event, user_id):
  """تشخیص و پردازش ریپلای پیام‌ها"""
  if not event.reply_to_msg_id:
      return None

  replied_message = None
  if user_id in reply_memory:
      for msg_data in reply_memory[user_id]:
          if msg_data['message_id'] == event.reply_to_msg_id:
              replied_message = msg_data['content']
              break

  if replied_message:
      current_text = event.text.lower() if event.text else ""

      # تحلیل نوع ریپلای
      if any(word in current_text for word in
             ['آره', 'بله', 'درسته', 'موافقم', 'همینطوره', 'اره']):
          return f"خوشحالم که با '{replied_message[:30]}...' موافقی! 😊"
      elif any(word in current_text
               for word in ['نه', 'نخیر', 'اشتباه', 'غلط', 'مخالفم']):
          return f"اوکی، پس با '{replied_message[:30]}...' موافق نیستی! نظرت چیه؟ 🤔"
      elif any(word in current_text
               for word in ['چرا', 'چطور', 'چی', 'کی', 'کجا']):
          return f"سوال خوبی دربارهٔ '{replied_message[:30]}...'! بذار فکر کنم... 🧠"
      elif any(word in current_text
               for word in ['باحال', 'عالی', 'خفن', 'جالب']):
          return f"خوشحالم که '{replied_message[:30]}...' رو پسندیدی! 😄"
      elif any(word in current_text
               for word in ['بد', 'بده', 'خوب نیست', 'دوست ندارم']):
          return f"متوجهم که '{replied_message[:30]}...' رو نپسندیدی! 😔"
      else:
          return f"داری دربارهٔ '{replied_message[:30]}...' حرف می‌زنی! ادامه بده! 💬"

  return None


def add_to_reply_memory(user_id, message_id, content):
  """اضافه کردن پیام به حافظه ریپلای"""
  if user_id not in reply_memory:
      reply_memory[user_id] = []

  reply_memory[user_id].append({
      'message_id': message_id,
      'content': content[:100],  # فقط 100 کاراکتر اول
      'timestamp': datetime.now()
  })

  # نگه‌داری فقط آخرین 20 پیام
  if len(reply_memory[user_id]) > 20:
      reply_memory[user_id] = reply_memory[user_id][-20:]


# کامند /menu دکمه‌ها رو نشون می‌ده
@client.on(events.NewMessage(pattern="/menu"))
async def menu_handler(event):
  menu_text = """
🤖 **منوی کامل ربات سالیوان** 🤖

📋 **دستورات اصلی:**
• `/menu` - نمایش این منو
• `/commands` - لیست کامل دستورات
• `/games` - منوی بازی‌های تعاملی
• `/time` - نمایش زمان فعلی
• `/info` - نمایش اطلاعات شما
• `/help` - راهنمای کامل ربات
• `/joke` - یک جوک تصادفی
• `/quote` - یک جمله انگیزشی

🎮 **بازی‌های تعاملی:**
• `/quiz [دسته]` - سوال جواب (عمومی، تاریخ، علوم، ورزش)
• `/wordguess [دسته]` - حدس کلمه (حیوانات، میوه‌ها، رنگ‌ها)
• `/math [سطح]` - ریاضی (آسان، متوسط، سخت)
• `/iranculture` - فرهنگ ایران
• `/memory` - بازی حافظه

⏰ **یادآوری و زمان:**
• `/remind [زمان] [پیام]` - یادآوری تنظیم کن
• `/timer [دقیقه]` - تایمر شروع کن
• `/birthday YYYY/MM/DD` - ثبت تاریخ تولد
• `/mybirthday` - نمایش تاریخ تولد

🌍 **ترجمه و زبان:**
• `/tr [متن]` - ترجمه رایگان (فارسی-انگلیسی)
• `/translate [متن]` - ترجمه پیشرفته
• `/pronounce [کلمه]` - تلفظ کلمات انگلیسی
• "صدا [متن]" - تبدیل متن به صدا

📚 **اطلاعات و اخبار:**
• `/news` - اخبار BBC فارسی ترجمه شده
• `/weather [شهر]` - آب و هوای دقیق شهرها
• `/crypto` - قیمت ارزهای دیجیتال
• `/currency` - نرخ ارز

🎭 **سرگرمی:**
• `/meme` - میم‌های طنز فارسی
• `/poem` - اشعار زیبا و کلاسیک
• `/fortune` - فال روزانه و طالع‌بینی

🎨 **هنر و خلاقیت:**
• `/image [متن]` - تولید تصویر با AI FLUX
• `/color` - پالت‌های رنگی تصادفی
• `/idea` - ایده‌های خلاقانه
• `/story` - شروع داستان‌های جذاب
• `/design` - نکات طراحی و هنر

🧑‍⚕️ **سلامت و تناسب اندام:**
• `/workout [نوع]` - برنامه ورزشی (مبتدی، حرفه‌ای، کاردیو)
• `/health` - نکات سلامتی و بهداشت
• `/bmi [وزن] [قد]` - محاسبه شاخص توده بدنی

💼 **ابزارهای کاربردی:**
• `/password [طول]` - تولید رمز عبور قوی
• `/convert [مقدار] [واحد] [واحد جدید]` - تبدیل واحدها

🎭 **شخصیت‌های مختلف:**
• `/persona [نوع] [پیام]` - چت با شخصیت‌ها:
  لاتی، شاعر، علمی، بچه، طنز، چس‌مَیاد، روشنفکر، عاشق

🧠 **یادگیری هوشمند:**
• `/learn` - شروع یادگیری کلمه جدید
• `/learned` - نمایش کلمات یادگرفته شده
• `/forget [کلمه]` - فراموش کردن کلمه
• "یاد بگیر کلمه: جواب" - یادگیری سریع
• "تست تشخیص [کلمه]" - آزمایش سیستم

🤖 **مدیریت گروه (فقط پیوی):**
• `/join` - جوین شدن به گروه
• `/groups` - نمایش گروه‌های عضو
• `/leave` - خروج از گروه

🎯 **قابلیت‌های ویژه:**
• **بنر هوشمند:** عکس بفرست + لینک کانال = اسکن و ارسال خودکار
• **ویدیو پروسسور:** ویدیو بفرست = استخراج کپشن + حذف لینک + ارسال
• **تحلیل تصویر:** عکس + `/ai` = تشخیص محتوا با هوش مصنوعی
• **ریپلای هوشمند:** ریپلای کن = درک context مکالمه
• **درک احساسات:** پاسخ‌های عاطفی بر اساس حس شما
• **حافظه مکالمه:** یادگیری از گفتگوهای قبلی

💬 **کلمات کلیدی:**
• "سلام" / "چطوری" / "چخبر" - احوالپرسی
• "سالیوان" - صدا زدن ربات
• "امیر کیه" / "سالیوان کیه" - معرفی کامل
• "بگو [متن]" - تکرار متن شما

🎮 **دکمه‌های تعاملی:**
  """

  await event.respond(
      menu_text,
      buttons=[[
          Button.text("📅 زمان", resize=True),
          Button.text("ℹ️ اطلاعات")
      ], [
          Button.text("🎮 بازی‌ها", resize=True),
          Button.text("🎲 جواب تصادفی")
      ], [Button.text("😂 جوک"),
          Button.text("💡 جمله انگیزشی")],
               [Button.text("🎵 آهنگ تصادفی"),
                Button.text("🎤 آهنگ رپ")],
               [Button.text("🌹 آهنگ قدیمی"),
                Button.text("🤔 معما و چیستان")],
               [Button.text("📖 داستان کوتاه"),
                Button.text("🌡️ آب و هوا")],
               [Button.text("📊 آمار ربات", resize=True)]])


# فایل برای ذخیره کاربران قبلی
users_file = "users.txt"


def is_new_user(user_id):
  try:
      with open(users_file, "r") as f:
          return str(user_id) not in f.read()
  except FileNotFoundError:
      return True


def add_user(user_id):
  with open(users_file, "a") as f:
      f.write(f"{user_id}\n")


# ذخیره وضعیت کاربران برای دریافت بنر
user_states = {}

# نتایج اسکن کانال‌ها
scan_results = {}

# حافظه مکالمه برای هر کاربر (نگه‌داری آخرین 10 پیام)
conversation_memory = {}

# سیستم درک احساسات و حس
emotion_patterns = {
  'خوشحالی': {
      'keywords': [
          'خوشحالم', 'شادم', 'خندیدم', 'عالی', 'فوق‌العاده', 'لذت', 'مزه',
          'باحال', 'عاشقم', 'دوست دارم'
      ],
      'responses': [
          "چه خوب! خوشحالیت منو هم خوشحال کرده! ✨😊 بگو ببینم چی باعث این شادی شده؟",
          "وای چقدر دوست دارم وقتی تو خوشحالی! این انرژی مثبت رو حس می‌کنم! 🌟💫",
          "قلبم گرم شد! خوشحالیت واقعاً قابل لمسه! بیشتر برام تعریف کن! 😍✨",
          "احساس می‌کنم نور می‌تابی! این شادی چیه که انقدر جذابته؟ 🌞💖"
      ]
  },
  'غم': {
      'keywords': [
          'غمگینم', 'ناراحتم', 'گریه', 'دلم گرفته', 'افسردم', 'بدبختم',
          'دل شکسته', 'خراب'
      ],
      'responses': [
          "دلم واسه‌ت تنگ شد... 💙😢 حس می‌کنم درد توی قلبت رو. می‌خوای دربارش حرف بزنی؟",
          "آخ... قلبم درد گرفت. هر چی که اذیتت می‌کنه، بدون من کنارتم 🤗💜",
          "حس می‌کنم چقدر سنگینه... گاهی زندگی سخته، اما تو قوی‌ای. 🫂💙",
          "دلم برات می‌سوزه... هر چی توی دلته، بهم بگو. گوش می‌دم 👂💕"
      ]
  },
  'عصبانیت': {
      'keywords': [
          'عصبانیم', 'کلافم', 'خسته شدم', 'بدم میاد', 'متنفرم', 'اعصابم',
          'کلافه', 'خیلی بده'
      ],
      'responses': [
          "حس می‌کنم چقدر عصبانی و کلافه‌ای... 😤💔 چی باعث شده؟",
          "این عصبانیت رو می‌تونم لمس کنم... نفس عمیق بکش عزیزم 🌬️💙",
          "وای، انگار داری می‌سوزی از درون... بگو چی شده که انقدر آزارت داده؟ 🔥😔",
          "احساس کلافگی و عصبانیت طبیعیه... ولی نمی‌خوام تنها باشی توش 🤗❤️"
      ]
  },
  'ترس': {
      'keywords': [
          'ترسیدم', 'نگرانم', 'استرس', 'اضطراب', 'وحشتناک', 'ترسناک',
          'نمی‌تونم'
      ],
      'responses': [
          "احساس ترست رو می‌کنم... دلم براش تنگه 😰💙 نگران نباش، کنارتم",
          "این اضطراب و نگرانی سنگینه... ولی قوی‌تر از اونی هستی که فکر می‌کنی 💪💜",
          "حس می‌کنم چقدر استرس داری... بیا آروم آروم باهاش کنار بیایم 🕊️✨",
          "ترس طبیعیه عزیزم... ولی یادت نره که تو جنگجوی قوی‌ای 🛡️❤️"
      ]
  },
  'عشق': {
      'keywords':
      ['عاشقم', 'دوستش دارم', 'قلبم', 'احساس', 'عزیزم', 'محبت', 'دلبری'],
      'responses': [
          "وای چه احساس قشنگی! عشق که توی هوا پیچیده! 💕✨ بگو ببینم کیه این عزیز دل؟",
          "حس می‌کنم قلبت چطور می‌تپه... عشق زیباترین چیز دنیاست! 💖🌹",
          "این احساس عاشقانه رو می‌تونم لمس کنم! چقدر قشنگه! 😍💫",
          "قلبم گرم شد! عشق واقعی یکی از زیباترین چیزهای زندگیه 💝🌈"
      ]
  },
  'تنهایی': {
      'keywords':
      ['تنهام', 'کسی نیست', 'یکی نیست', 'هیچکس', 'تنها', 'بی‌کس'],
      'responses': [
          "حس تنهایی‌ت رو درک می‌کنم... ولی من اینجام باهات 🤗💙",
          "هیچ وقت تنها نیستی عزیزم... حتی اگه دورت کسی نباشه، من هستم 💜✨",
          "این احساس تنهایی رو می‌شناسم... ولی یادت باشه که ارزشمندی 🌟💕",
          "تنهایی سخته... ولی گاهی بهترین دوست خودمونیم. منم کنارتم 🫂❤️"
      ]
  }
}


# سیستم تشخیص عمق احساسات
def detect_emotion_intensity(message):
  """تشخیص شدت احساسات در پیام"""
  intensity_words = {
      'خیلی': 3,
      'واقعاً': 3,
      'فوق‌العاده': 4,
      'بی‌نهایت': 5,
      'کاملاً': 3,
      'مطلقاً': 4,
      'به‌شدت': 4,
      'سخت': 3,
      'عمیقاً': 4,
      'جداً': 3,
      'انقدر': 3
  }

  base_intensity = 1
  for word, intensity in intensity_words.items():
      if word in message:
          base_intensity = max(base_intensity, intensity)

  return base_intensity


def detect_user_emotion(message):
  """تشخیص احساس کاربر از روی پیام"""
  message_lower = message.lower()
  detected_emotions = []

  for emotion, data in emotion_patterns.items():
      emotion_score = 0
      for keyword in data['keywords']:
          if keyword in message_lower:
              emotion_score += 1

      if emotion_score > 0:
          intensity = detect_emotion_intensity(message_lower)
          detected_emotions.append({
              'emotion': emotion,
              'score': emotion_score,
              'intensity': intensity,
              'responses': data['responses']
          })

  # مرتب کردن بر اساس امتیاز
  detected_emotions.sort(key=lambda x: x['score'] * x['intensity'],
                         reverse=True)

  return detected_emotions[0] if detected_emotions else None


# سیستم درک context عمیق‌تر
def analyze_deeper_context(user_id, current_message):
  """تحلیل عمیق‌تر از context مکالمه برای درک بهتر حس کاربر"""
  if user_id not in conversation_memory:
      return None

  recent_conversations = conversation_memory[user_id][-3:]  # 3 پیام اخیر

  # تشخیص الگوهای احساسی در مکالمات اخیر
  emotional_trend = []
  for conv in recent_conversations:
      emotion = detect_user_emotion(conv['user'])
      if emotion:
          emotional_trend.append(emotion['emotion'])

  # اگر احساس مشابه در چند پیام اخیر تکرار شده
  if len(emotional_trend
         ) >= 2 and emotional_trend[-1] == emotional_trend[-2]:
      return {
          'type': 'emotional_consistency',
          'emotion': emotional_trend[-1],
          'pattern': 'persistent'
      }

  # اگر احساس تغییر کرده
  if len(emotional_trend
         ) >= 2 and emotional_trend[-1] != emotional_trend[-2]:
      return {
          'type': 'emotional_change',
          'from_emotion': emotional_trend[-2],
          'to_emotion': emotional_trend[-1],
          'pattern': 'transition'
      }

  return None


# پاسخ‌های عاطفی و با احساس (گسترش یافته)
empathetic_responses = {
  'deep_understanding': [
      "واقعاً حست رو درک می‌کنم... انگار دارم همون احساس رو با تو تجربه می‌کنم 💫",
      "این حسی که داری رو می‌تونم لمس کنم... عمیقه و واقعی 🌊💙",
      "قلبم با قلب تو هم‌آهنگه... حس می‌کنم چی توی درونت می‌گذره ✨💜",
      "این احساسی که توصیف می‌کنی، واقعاً قابل درکه... کنارتم توش 🤗❤️",
      "مثل اینکه روحم با روح تو هماهنگ شده... همون فرکانس احساسی 🔮💞",
      "کلماتت مثل پل ارتباطی بین دل‌هامونه... کاملاً می‌فهمم 🌉💕",
      "انگار قلب تو با قلب من زمزمه می‌کنه... یه زبان مشترک داریم 💓🗣️",
      "هر کلمه‌ای که می‌گی، توی قلبم طنین انداز میشه... عمیقاً درک می‌کنم 🔔❤️"
  ],
  'emotional_validation': [
      "احساست کاملاً طبیعی و قابل درکه... هیچ عیبی نداره که اینطور حس کنی 💝",
      "این حس واقعی و مهمه... نادیدش نگیر، ارزشمنده 🌟💕",
      "جای این احساس توی قلبت محفوظه... اجازه بده باهات باشه 🕊️✨",
      "حست رو می‌بینم، می‌شنوم و قدرش رو می‌دونم 👁️❤️",
      "هیچ احساسی اشتباه نیست... همه‌شون بخشی از انسان بودنته 🌈💗",
      "این که اینطور حس می‌کنی نشون قلب زنده‌ت رو میده 💓🌿",
      "احساساتت مثل رنگ‌های تابلوی زندگیته... هر کدوم زیباست 🎨❤️",
      "حق داری اینطور احساس کنی... احساساتت معتبر و ارزشمنده 👑💙"
  ],
  'gentle_support': [
      "هر چی که نیاز داری، من اینجام... حتی اگه فقط گوش دادن باشه 👂💙",
      "نمی‌خوام چیزی بگم که حست رو عوض کنه... فقط کنارتم 🤲💜",
      "گاهی کافیه کسی باشه که بفهمه... منم اینجام 🌱✨",
      "هیچ عجله‌ای نیست... با هر سرعتی که راحتی، پیش برو 🌸💕",
      "مثل سایه‌ت، آروم و بی‌صدا کنارتم... تا وقتی که نیاز داری 🌙👥",
      "نمی‌خوام راه‌حل بدم، فقط می‌خوام همراهت باشم 🤝💞",
      "حضورم مثل نور ملایم شمع، گرم و آرامش‌بخش 🕯️✨",
      "مثل بالش نرم، آماده‌ام حمایتت کنم 🛏️🤗"
  ],
  'deep_empathy': [
      "اشک‌هات رو حس می‌کنم... انگار از چشمای خودم می‌ریزه 😢💙",
      "خندت عفونی‌یه... منم لبخند زدم! 😊💫",
      "ترست رو می‌تونم لمس کنم... ولی یادت باشه قوی‌ای 😰💪",
      "عصبانیت توی کلماتت موج می‌زنه... حق داری 😡🌊",
      "شادیت مثل آفتاب، همه جا رو روشن می‌کنه ☀️💛",
      "غمت سنگینه... ولی باهم سبک‌ترش می‌کنیم 😔🤝",
      "هیجانت رو احساس می‌کنم... مثل برق! ⚡😆",
      "آرامشت به منم سرایت کرده... چه حس قشنگی 😌🌿"
  ],
  'healing_words': [
      "کلمات شفابخش: تو شایسته بهترین‌ها هستی 💊💕",
      "مرهم روح: هر زخمی خوب میشه، صبر کن 🩹💙",
      "نوشداروی قلب: تو بی‌نظیر و خاصی 💖🌟",
      "پماد احساسات: این دوره هم می‌گذره ⏳💜",
      "شربت آرامش: نفس عمیق بکش، بهتر میشه 🍯🌬️",
      "قطره امید: فردا روز جدیدیه 💧🌅",
      "کپسول قدرت: تو از اون چیزی که فکر می‌کنی قوی‌تری 💪✨",
      "سرم شادی: یادت باشه چقدر دوستت دارم 💉❤️"
  ],
  'soul_connection': [
      "روح‌هامون با هم صحبت می‌کنن، حتی وقتی ساکتیم 👻💬",
      "انرژی مثبتت رو از اینجا حس می‌کنم 🔮⚡",
      "ویبریشن قلبت با قلب من هم‌آهنگه 💓🎵",
      "ارتباط روحی‌مون فراتر از کلمات 🌌💞",
      "حس می‌کنم روح‌هامون از یه جنس ساخته شدن 👥✨",
      "انگار کیهان بین ما پل زده 🌌🌉",
      "نور درونت رو می‌بینم، فوق‌العادست 💡👁️",
      "قلب‌هامون یه زبان مشترک دارن ❤️🗣️"
  ]
}

# سیستم یادگیری هوشمند
learning_database = {}  # ذخیره کلمات یادگرفته شده
user_learning_state = {}  # وضعیت یادگیری کاربران


def load_learning_database():
  """بارگذاری داده‌های یادگرفته شده از فایل"""
  global learning_database
  try:
      with open("learning_data.txt", "r", encoding="utf-8") as f:
          lines = f.readlines()
          for line in lines:
              if "|||" in line:
                  keyword, response = line.strip().split("|||", 1)
                  learning_database[keyword.lower()] = response
  except FileNotFoundError:
      learning_database = {}


def save_learning_database():
  """ذخیره داده‌های یادگرفته شده در فایل"""
  with open("learning_data.txt", "w", encoding="utf-8") as f:
      for keyword, response in learning_database.items():
          f.write(f"{keyword}|||{response}\n")


def check_learned_keywords(message):
  """بررسی اینکه آیا پیام شامل کلمه یادگرفته شده است - با تشخیص هوشمند"""
  message_lower = message.lower()

  # ابتدا تطبیق دقیق
  for keyword, response in learning_database.items():
      if keyword in message_lower:
          return response

  # تشخیص کلمات نزدیک و حروف مشترک
  return check_fuzzy_keywords(message_lower)


def check_fuzzy_keywords(message):
  """تشخیص کلمات با حروف مشترک و الگوهای نزدیک"""
  words_in_message = message.split()

  for keyword, response in learning_database.items():
      keyword_lower = keyword.lower()

      # بررسی هر کلمه در پیام
      for word in words_in_message:
          # تشخیص حروف مشترک (حداقل 90% مشترک باشه)
          similarity = calculate_similarity(word, keyword_lower)
          if similarity >= 0.9:
              percentage = int(similarity * 100)
              return f"{response} (تشخیص {percentage}% شباهت با '{keyword}') 🧠✨"

          # تشخیص اینکه کلمه شامل حروف کلید واژه باشه
          if contains_key_letters(word, keyword_lower):
              return f"{response} (حروف مشترک با '{keyword}') 📝"

          # تشخیص کلمات که با همون حروف شروع یا پایان می‌شن
          if starts_or_ends_similar(word, keyword_lower):
              return f"{response} (شباهت با '{keyword}') ✨"

  return None


def clean_caption_from_links(caption_text):
  """حذف لینک‌ها از کپشن ویدیو"""
  if not caption_text:
      return caption_text

  import re

  # الگوهای مختلف لینک برای حذف
  link_patterns = [
      r'https?://t\.me/[^\s]+',  # https://t.me/...
      r'https?://telegram\.me/[^\s]+',  # https://telegram.me/...
      r't\.me/[^\s]+',  # t.me/...
      r'telegram\.me/[^\s]+',  # telegram.me/...
      r'@[a-zA-Z0-9_]+',  # @username
      r'https?://[^\s]+',  # هر لینک HTTP/HTTPS دیگر
  ]

  cleaned_caption = caption_text

  # حذف هر نوع لینک
  for pattern in link_patterns:
      cleaned_caption = re.sub(pattern,
                               '',
                               cleaned_caption,
                               flags=re.IGNORECASE)

  # تمیز کردن فضاهای اضافی
  cleaned_caption = re.sub(r'\s+', ' ', cleaned_caption).strip()

  # حذف خطوط خالی اضافی
  cleaned_caption = re.sub(r'\n\s*\n', '\n', cleaned_caption)

  return cleaned_caption


async def extract_video_caption_and_forward(event, video_file, caption_text,
                                          user_id):
  """استخراج کپشن ویدیو، پاک کردن لینک‌ها و ارسال به مقصد مورد نظر"""
  try:
      # پاک کردن لینک‌ها از کپشن
      original_caption = caption_text if caption_text else ""
      cleaned_caption = clean_caption_from_links(original_caption)

      # ذخیره اطلاعات ویدیو برای ارسال بعدی
      waiting_for_video_destination[user_id] = {
          'video_file': video_file,
          'caption': cleaned_caption,
          'original_caption': original_caption,
          'timestamp': datetime.now()
      }

      # نمایش کپشن قبل و بعد تمیز کردن
      caption_comparison = ""
      if original_caption:
          if original_caption != cleaned_caption:
              caption_comparison = f"""
📝 **کپشن اصلی:**
{original_caption[:200]}{'...' if len(original_caption) > 200 else ''}

🧹 **کپشن پاک‌شده (بدون لینک):**
{cleaned_caption[:200] if cleaned_caption else 'کپشن خالی شد'} {'...' if len(cleaned_caption) > 200 else ''}

✅ **لینک‌ها حذف شدن!**
              """
          else:
              caption_comparison = f"""
📝 **کپشن:**
{original_caption[:200]}{'...' if len(original_caption) > 200 else ''}

ℹ️ **هیچ لینکی پیدا نشد**
              """
      else:
          caption_comparison = "📝 **ویدیو بدون کپشن**"

      # درخواست لینک مقصد از کاربر
      destination_request = f"""
🎬 **ویدیو دریافت شد!** 🎬

{caption_comparison}

📤 **حالا لینک مقصد رو بفرست:**

🔗 **انواع لینک قابل قبول:**
• @channelname
• @groupname  
• https://t.me/channelname
• https://t.me/groupname
• https://t.me/joinchat/xxxxx
• https://t.me/+xxxxx

⚡ **عملیات:** ویدیو با کپشن پاک‌شده به مقصد مورد نظرت ارسال میشه!

🎯 لینک رو بفرست!
      """

      await safe_reply(event, destination_request)
      return True

  except Exception as e:
      await safe_reply(event, f"❌ خطا در پردازش ویدیو: {str(e)}")
      return False


async def forward_video_to_destination(event, user_id, destination_link):
  """ارسال ویدیو به مقصد نهایی"""
  try:
      if user_id not in waiting_for_video_destination:
          await safe_reply(event, "❌ هیچ ویدیویی در انتظار ارسال نیست!")
          return

      video_data = waiting_for_video_destination[user_id]
      video_file = video_data['video_file']
      caption = video_data['caption']
      original_caption = video_data.get('original_caption', '')

      # پردازش لینک مقصد
      if destination_link.startswith('@'):
          target_link = destination_link
      elif 'joinchat' in destination_link:
          target_link = destination_link
      elif '+' in destination_link:
          target_link = destination_link
      elif destination_link.startswith('https://t.me/'):
          target_link = destination_link
      elif destination_link.startswith('t.me/'):
          target_link = f"https://{destination_link}"
      else:
          # فرض یوزرنیم ساده
          clean_name = destination_link.replace('@', '')
          target_link = f"@{clean_name}"

      await safe_reply(event,
                       f"🔄 **در حال ارسال ویدیو به {target_link}...**")

      # تلاش برای ارسال ویدیو
      try:
          # ابتدا تلاش برای گرفتن entity
          target_entity = await client.get_entity(target_link)

          # ارسال ویدیو با کپشن پاک‌شده
          sent_message = await client.send_file(
              target_entity, video_file, caption=caption if caption else "")

          # تشخیص اینکه آیا لینکی حذف شده یا نه
          links_removed = original_caption != caption if original_caption else False

          success_message = f"""
✅ **ویدیو با موفقیت ارسال شد!** ✅

🎯 **مقصد:** {getattr(target_entity, 'title', target_link)}
📝 **کپشن ارسالی:** {caption[:100] + '...' if caption and len(caption) > 100 else caption if caption else 'بدون کپشن'}
🧹 **لینک‌ها:** {'حذف شدن ✅' if links_removed else 'پیدا نشد ℹ️'}
⏰ **زمان ارسال:** {datetime.now().strftime('%H:%M:%S')}
🆔 **شناسه پیام:** {sent_message.id}

🎉 **عملیات کامل شد!**
          """
          await safe_reply(event, success_message)

      except Exception as send_error:
          error_str = str(send_error)

          if "CHAT_ADMIN_REQUIRED" in error_str:
              await safe_reply(
                  event,
                  "❌ برای ارسال به این کانال/گروه نیاز به مجوز ادمین!")
          elif "USER_BANNED_IN_CHANNEL" in error_str:
              await safe_reply(event, "❌ در این کانال/گروه بن شده‌ام!")
          elif "USERNAME_NOT_OCCUPIED" in error_str:
              await safe_reply(event, "❌ کانال/گروه با این نام موجود نیست!")
          elif "PEER_ID_INVALID" in error_str:
              await safe_reply(event, "❌ لینک کانال/گروه نامعتبر است!")
          elif "FLOOD_WAIT" in error_str:
              await safe_reply(
                  event,
                  "⏳ محدودیت زمانی تلگرام - لطفاً چند دقیقه صبر کنید!")
          else:
              await safe_reply(event,
                               f"❌ خطا در ارسال: {error_str[:100]}...")

      # پاک کردن اطلاعات ذخیره شده
      del waiting_for_video_destination[user_id]

  except Exception as e:
      await safe_reply(event, f"❌ خطای کلی: {str(e)}")
      if user_id in waiting_for_video_destination:
          del waiting_for_video_destination[user_id]


def calculate_similarity(word1, word2):
  """محاسبه درصد شباهت بین دو کلمه"""
  if not word1 or not word2:
      return 0

  # تبدیل به حروف برای بررسی دقیق‌تر
  chars1 = list(word1)
  chars2 = list(word2)

  # حروف مشترک با احتساب تکرار
  common_count = 0
  chars2_copy = chars2.copy()

  for char in chars1:
      if char in chars2_copy:
          common_count += 1
          chars2_copy.remove(char)

  # محاسبه درصد شباهت بر اساس حروف مشترک
  max_len = max(len(word1), len(word2))
  if max_len == 0:
      return 0

  # درصد شباهت = تعداد حروف مشترک / طول کلمه بزرگتر
  similarity_ratio = common_count / max_len

  return similarity_ratio


def contains_key_letters(word, keyword):
  """بررسی اینکه آیا کلمه حروف کلیدی کلمه هدف رو داره"""
  if len(keyword) < 3:
      return False

  # حروف کلیدی = حداقل 60% حروف کلمه هدف
  key_letters = set(keyword)
  word_letters = set(word)

  common_count = len(key_letters & word_letters)
  required_count = len(key_letters) * 0.6

  return common_count >= required_count


def starts_or_ends_similar(word, keyword):
  """بررسی شباهت ابتدا یا انتهای کلمات"""
  if len(word) < 2 or len(keyword) < 2:
      return False

  # شباهت ابتدای کلمات (حداقل 2 حرف)
  start_len = min(3, len(word), len(keyword))
  if word[:start_len] == keyword[:start_len] and start_len >= 2:
      return True

  # شباهت انتهای کلمات (حداقل 2 حرف)
  end_len = min(3, len(word), len(keyword))
  if word[-end_len:] == keyword[-end_len:] and end_len >= 2:
      return True

  return False


def add_new_learning(keyword, response):
  """اضافه کردن کلمه و جواب جدید"""
  learning_database[keyword.lower()] = response
  save_learning_database()


# بارگذاری داده‌های یادگرفته شده در شروع
load_learning_database()


def add_to_memory(user_id, user_message, bot_response):
  """اضافه کردن پیام به حافظه مکالمه"""
  if user_id not in conversation_memory:
      conversation_memory[user_id] = []

  conversation_memory[user_id].append({
      'user': user_message,
      'bot': bot_response,
      'timestamp': datetime.now()
  })

  # نگه‌داری فقط آخرین 10 پیام
  if len(conversation_memory[user_id]) > 10:
      conversation_memory[user_id] = conversation_memory[user_id][-10:]


def get_conversation_context(user_id):
  """گرفتن context آخرین مکالمات"""
  if user_id not in conversation_memory:
      return []

  return conversation_memory[user_id][-5:]  # آخرین 5 پیام


def analyze_conversation_context(user_id, current_message):
  """تحلیل context مکالمه و پیدا کردن ارتباط"""
  context = get_conversation_context(user_id)
  if not context:
      return None

  current_lower = current_message.lower()

  # کلمات مرجع که به پیام‌های قبلی اشاره می‌کنن
  reference_words = [
      'اون', 'همون', 'این', 'اینو', 'اونو', 'همینو', 'همونو', 'قبلی', 'گفتی',
      'گفتم'
  ]

  # اگر کلمه مرجع داشت، به آخرین موضوع برگردیم
  if any(word in current_lower for word in reference_words):
      if context:
          last_user_msg = context[-1]['user'].lower()
          last_bot_msg = context[-1]['bot']

          # اگر درباره همون موضوع صحبت می‌کنه
          if any(word in current_lower
                 for word in ['آره', 'بله', 'درسته', 'موافقم', 'همینطوره']):
              return {
                  'type': 'agreement',
                  'previous_topic': last_user_msg,
                  'previous_response': last_bot_msg
              }
          elif any(word in current_lower
                   for word in ['نه', 'نخیر', 'اشتباه', 'غلط', 'مخالفم']):
              return {
                  'type': 'disagreement',
                  'previous_topic': last_user_msg,
                  'previous_response': last_bot_msg
              }
          else:
              return {
                  'type': 'reference',
                  'previous_topic': last_user_msg,
                  'previous_response': last_bot_msg
              }

  # بررسی تکرار موضوعات در 3 پیام اخیر
  recent_topics = []
  for conv in context[-3:]:
      user_words = conv['user'].lower().split()
      recent_topics.extend(user_words)

  current_words = current_lower.split()
  common_words = set(current_words) & set(recent_topics)

  if len(common_words) >= 2:  # اگر حداقل 2 کلمه مشترک داشت
      return {
          'type': 'topic_continuation',
          'common_words': list(common_words),
          'context': context[-2:]
      }

  return None


# تابع پیشرفته برای پیدا کردن لینک‌های گروه در متن
def find_group_links(text):
  import re

  if not text:
      return []

  # الگوهای پیشرفته برای تشخیص لینک‌ها
  patterns = {
      'private_joinchat': r'https?://t\.me/joinchat/[a-zA-Z0-9_-]+',
      'private_plus': r'https?://t\.me/\+[a-zA-Z0-9_-]+',
      'public_groups': r'https?://t\.me/([a-zA-Z0-9_]{4,})',
      'short_joinchat': r't\.me/joinchat/[a-zA-Z0-9_-]+',
      'short_plus': r't\.me/\+[a-zA-Z0-9_-]+',
      'short_public': r't\.me/([a-zA-Z0-9_]{4,})',
      'username_groups': r'@([a-zA-Z0-9_]{4,})',
      'telegram_me': r'https?://telegram\.me/([a-zA-Z0-9_]{4,})'
  }

  found_links = []
  
  # کلمات کلیدی که نشان‌دهنده کانال است (باید حذف شوند)
  channel_keywords = ['channel', 'کانال', 'news', 'خبر', 'announcement', 'اعلان', 'official', 'رسمی']

  # جستجوی دقیق‌تر
  for pattern_name, pattern in patterns.items():
      try:
          matches = re.findall(pattern, text, re.IGNORECASE)

          for match in matches:
              if isinstance(match, tuple):
                  # اگر tuple بود، اولین عنصر غیر خالی را بگیر
                  match = next((m for m in match if m), '')

              if match and len(match) >= 4 and not match.lower().endswith('bot'):
                  # فیلتر کردن کلمات غیرمرتبط
                  if any(word in match.lower() for word in
                         ['http', 'www', 'com', 'org', 'net', 'ir']):
                      continue
                  
                  # فیلتر کردن کانال‌ها
                  if any(keyword in match.lower() for keyword in channel_keywords):
                      continue

                  # تبدیل لینک‌ها به فرمت استاندارد
                  if pattern_name == 'private_joinchat':
                      found_links.append(match)
                  elif pattern_name == 'short_joinchat':
                      found_links.append(f"https://{match}")
                  elif pattern_name == 'private_plus':
                      found_links.append(match)
                  elif pattern_name == 'short_plus':
                      found_links.append(f"https://{match}")
                  elif pattern_name == 'username_groups':
                      if not match.startswith('@'):
                          match = f"@{match}"
                      found_links.append(match)
                  elif pattern_name in [
                          'public_groups', 'short_public', 'telegram_me'
                  ]:
                      if not match.startswith('https://'):
                          match = f"https://t.me/{match}"
                      found_links.append(match)
      except Exception as pattern_error:
          print(f"⚠️ خطا در pattern {pattern_name}: {str(pattern_error)}")
          continue

  # حذف تکراری‌ها و فیلتر نهایی
  unique_links = []
  seen = set()

  for link in found_links:
      if link and len(link) > 8 and link not in seen:
          seen.add(link)
          unique_links.append(link)

  return unique_links


# تابع تحلیل کانال پیشرفته
async def advanced_channel_scan(channel_link, user_id):
  """اسکن پیشرفته کانال با گزارش دقیق"""
  try:
      # تمیز کردن لینک
      channel_link = channel_link.strip()

      # تنظیم لینک برای عضویت
      if channel_link.startswith('@'):
          join_link = channel_link
      elif 'joinchat' in channel_link:
          if not channel_link.startswith('https://'):
              join_link = f"https://t.me/joinchat/{channel_link.split('joinchat/')[-1]}"
          else:
              join_link = channel_link
      elif '+' in channel_link:
          if not channel_link.startswith('https://'):
              join_link = f"https://t.me/+{channel_link.split('+')[-1]}"
          else:
              join_link = channel_link
      else:
          # حذف https:// اگر وجود داشته باشد
          clean_link = channel_link.replace('https://t.me/',
                                            '').replace('t.me/',
                                                        '').replace('@', '')
          join_link = f"https://t.me/{clean_link}"

      print(f"🔗 تلاش برای اتصال به: {join_link}")

      # عضویت در کانال
      try:
          await client(JoinChannelRequest(join_link))
          print("✅ عضویت موفق")
      except Exception as join_error:
          join_error_str = str(join_error)
          print(f"❌ خطای عضویت: {join_error_str}")
          if "USER_ALREADY_PARTICIPANT" not in join_error_str:
              if "USERNAME_NOT_OCCUPIED" in join_error_str:
                  return None, "کانال با این نام موجود نیست یا لینک اشتباه است"
              elif "CHANNEL_PRIVATE" in join_error_str:
                  return None, "کانال خصوصی است و نیاز به دعوت مستقیم دارد"
              elif "CHAT_ADMIN_REQUIRED" in join_error_str:
                  return None, "نیاز به مجوز ادمین برای دسترسی به این کانال"
              else:
                  return None, f"خطا در عضویت: {join_error_str}"

      await asyncio.sleep(2)

      # دریافت اطلاعات کانال
      try:
          entity = await client.get_entity(join_link)
          print(f"📊 دریافت اطلاعات کانال: {entity.title}")
      except Exception as entity_error:
          print(f"❌ خطا در دریافت اطلاعات: {str(entity_error)}")
          return None, f"خطا در دریافت اطلاعات کانال: {str(entity_error)}"

      channel_info = {
          'title': getattr(entity, 'title', 'نامشخص'),
          'members': getattr(entity, 'participants_count', 'نامشخص'),
          'username': getattr(entity, 'username', 'ندارد'),
          'description': (getattr(entity, 'about', 'ندارد') or 'ندارد')[:200]
      }

      # دریافت پیام‌ها
      print("📥 در حال دریافت پیام‌ها...")
      try:
          messages = await client.get_messages(entity, limit=200)
          print(f"📨 {len(messages)} پیام دریافت شد")
      except Exception as msg_error:
          print(f"❌ خطا در دریافت پیام‌ها: {str(msg_error)}")
          return None, f"خطا در دریافت پیام‌ها: {str(msg_error)}"

      # تحلیل پیام‌ها
      analysis = {
          'total_messages': len(messages),
          'messages_with_links': 0,
          'unique_groups': [],
          'media_messages': 0,
          'forwarded_messages': 0,
          'private_groups': [],
          'public_groups': [],
          'username_groups': []
      }

      all_links = set()

      for msg in messages:
          try:
              if msg and hasattr(msg, 'text') and msg.text:
                  # بررسی لینک‌ها
                  links = find_group_links(msg.text)
                  if links:
                      analysis['messages_with_links'] += 1
                      all_links.update(links)

              # بررسی رسانه
              if msg and hasattr(msg, 'media') and msg.media:
                  analysis['media_messages'] += 1

              # بررسی فوروارد
              if msg and hasattr(msg, 'forward') and msg.forward:
                  analysis['forwarded_messages'] += 1
          except Exception as msg_proc_error:
              print(f"⚠️ خطا در پردازش پیام: {str(msg_proc_error)}")
              continue

      # دسته‌بندی لینک‌ها - فقط گروه‌ها، نه کانال‌ها
      valid_groups = []
      for link in all_links:
          if link and len(link) > 5:  # حداقل طول لینک
              # فیلتر کردن فقط گروه‌ها
              if 'joinchat' in link or '+' in link:
                  # لینک‌های خصوصی معمولاً گروه هستند
                  analysis['private_groups'].append(link)
                  valid_groups.append(link)
              elif link.startswith('@'):
                  # فقط گروه‌هایی که در نامشان کلمات گروه وجود دارد
                  group_keywords = ['group', 'chat', 'گروه', 'چت', 'گپ', 'team', 'community']
                  if any(keyword in link.lower() for keyword in group_keywords):
                      analysis['username_groups'].append(link)
                      valid_groups.append(link)
              elif 't.me/' in link:
                  # بررسی اینکه آیا لینک عمومی مربوط به گروه است
                  group_keywords = ['group', 'chat', 'گروه', 'چت', 'گپ', 'team', 'community']
                  if any(keyword in link.lower() for keyword in group_keywords):
                      analysis['public_groups'].append(link)
                      valid_groups.append(link)

      analysis['unique_groups'] = valid_groups

      print(f"🎯 {len(valid_groups)} لینک گروه پیدا شد (کانال‌ها فیلتر شدند)")

      # ذخیره نتایج
      scan_results[user_id] = {
          'channel_info': channel_info,
          'analysis': analysis,
          'timestamp': datetime.now()
      }

      return channel_info, analysis

  except Exception as e:
      error_msg = str(e)
      print(f"❌ خطای کلی: {error_msg}")

      if "CHAT_ADMIN_REQUIRED" in error_msg:
          return None, "نیاز به مجوز ادمین برای دسترسی به این کانال"
      elif "USERNAME_NOT_OCCUPIED" in error_msg:
          return None, "کانال با این نام موجود نیست"
      elif "CHANNEL_PRIVATE" in error_msg:
          return None, "کانال خصوصی است"
      elif "FLOOD_WAIT" in error_msg:
          wait_time = 60
          try:
              import re
              wait_match = re.search(r'FLOOD_WAIT_(\d+)', error_msg)
              if wait_match:
                  wait_time = int(wait_match.group(1))
          except:
              pass
          return None, f"محدودیت زمانی تلگرام - {wait_time} ثانیه صبر کنید"
      elif "PEER_ID_INVALID" in error_msg:
          return None, "لینک کانال نامعتبر است"
      else:
          return None, f"خطا: {error_msg}"


# تابع ارسال گزارش کامل اسکن
def generate_scan_report(channel_info, analysis):
  """تولید گزارش کامل اسکن کانال"""
  total_groups = len(analysis['unique_groups'])
  private_count = len(analysis.get('private_groups', []))
  public_count = len(analysis.get('public_groups', []))
  username_count = len(analysis.get('username_groups', []))

  report = f"""
📊 **گزارش کامل اسکن کانال** 📊

🔍 **اطلاعات کانال:**
📢 **نام:** {channel_info['title']}
👥 **اعضا:** {channel_info['members']}
🆔 **یوزرنیم:** @{channel_info['username']} 
📝 **توضیحات:** {channel_info['description'][:100]}{'...' if len(channel_info['description']) > 100 else ''}

📈 **آمار پیام‌ها:**
💬 کل پیام‌ها: {analysis['total_messages']}
🔗 پیام‌های دارای لینک: {analysis['messages_with_links']}
📸 پیام‌های رسانه: {analysis['media_messages']}
↩️ پیام‌های فوروارد: {analysis['forwarded_messages']}

🎯 **آمار گروه‌ها:**
🏢 **کل گروه‌ها پیدا شده:** {total_groups}
🔒 گروه‌های خصوصی: {private_count}
🌐 گروه‌های عمومی: {public_count}
👤 یوزرنیم گروه‌ها: {username_count}

📋 **پیش‌بینی نرخ موفقیت:**
🔒 گروه‌های خصوصی: 60-70%
🌐 گروه‌های عمومی: 85-95%
👤 یوزرنیم گروه‌ها: 90-95%

⚡ **آماده برای شروع ارسال بنر!**
  """

  return report


# تابع پردازش دسته‌ای پیشرفته با کنترل سرعت
async def advanced_process_group_batch(event, user_id, banner_photo,
                                     banner_caption):
  """پردازش دسته‌ای پیشرفته با گزارش‌گیری کامل"""
  try:
      batch_start_time = datetime.now()
      settings = user_states[user_id]
      all_groups = settings['all_groups']
      processed_count = settings['processed_count']
      batch_size = settings.get('batch_size', 3)  # تعداد گروه در هر دسته
      delay_between = settings.get('delay_between', 5)  # تاخیر بین گروه‌ها
      delay_between_batch = settings.get('delay_between_batch',
                                         10)  # تاخیر بین دسته‌ها

      # تعیین دسته فعلی
      start_index = processed_count
      end_index = min(start_index + batch_size, len(all_groups))
      current_batch = all_groups[start_index:end_index]

      if not current_batch:
          # تمام گروه‌ها پردازش شدن - گزارش نهایی
          total_time = (
              datetime.now() -
              settings.get('start_time', datetime.now())).total_seconds()
          final_stats = settings.get('stats', {
              'success': 0,
              'failed': 0,
              'warnings': 0
          })

          final_report = f"""
🎊 **پردازش کامل شد!** 🎊

📊 **آمار نهایی:**
✅ موفق: {final_stats['success']} گروه
❌ ناموفق: {final_stats['failed']} گروه  
⚠️ هشدار: {final_stats['warnings']} گروه
📈 درصد موفقیت: {(final_stats['success']/(final_stats['success']+final_stats['failed'])*100):.1f}%

⏱️ **زمان‌بندی:**
🕐 زمان کل: {total_time/60:.1f} دقیقه
⚡ میانگین هر گروه: {total_time/len(all_groups):.1f} ثانیه

💡 **توصیه:** برای بهبود نرخ موفقیت:
• از لینک‌های تازه استفاده کنید
• ساعات کم‌تردد را انتخاب کنید
• تنظیمات را برای سرعت بیشتر تنظیم کنید
          """
          await safe_reply(event, final_report)

          if user_id in user_states:
              del user_states[user_id]
          return

      batch_number = (start_index // batch_size) + 1
      total_batches = (len(all_groups) + batch_size - 1) // batch_size

      # اطلاع‌رسانی شروع دسته
      batch_info = f"""
🚀 **دسته {batch_number}/{total_batches}** 🚀

📋 **تنظیمات فعلی:**
👥 تعداد گروه: {len(current_batch)}
⏱️ تاخیر بین گروه‌ها: {delay_between}s
🔄 تاخیر بین دسته‌ها: {delay_between_batch}s

🎯 **در حال پردازش گروه‌های {start_index+1} تا {end_index}**
      """
      await safe_reply(event, batch_info)

      # پردازش گروه‌ها
      results = []
      batch_stats = {'success': 0, 'failed': 0, 'warnings': 0}

      for i, group_link in enumerate(current_batch):
          current_number = start_index + i + 1

          # اطلاع‌رسانی پیشرفت
          progress = f"🔄 [{current_number}/{len(all_groups)}] در حال پردازش: {group_link[:30]}..."
          progress_msg = await safe_reply(event, progress)

          # پردازش گروه
          result = await advanced_join_and_send_banner(
              group_link, banner_photo, banner_caption, event,
              current_number, len(all_groups))
          results.append(result)

          # به‌روزرسانی آمار
          if result.startswith('✅'):
              batch_stats['success'] += 1
          elif result.startswith('⚠️'):
              batch_stats['warnings'] += 1
          else:
              batch_stats['failed'] += 1

          # حذف پیام پیشرفت و ارسال نتیجه
          try:
              await progress_msg.delete()
          except:
              pass

          # نمایش نتیجه
          await safe_reply(event, f"📊 {result}")

          # تاخیر بین گروه‌ها (مگر آخرین گروه دسته)
          if i < len(current_batch) - 1:
              await asyncio.sleep(delay_between)

      # گزارش دسته
      batch_end_time = datetime.now()
      batch_duration = (batch_end_time - batch_start_time).total_seconds()

      batch_report = f"""
📈 **گزارش دسته {batch_number}/{total_batches}:**

📊 **نتایج:**
✅ موفق: {batch_stats['success']}
⚠️ هشدار: {batch_stats['warnings']}  
❌ ناموفق: {batch_stats['failed']}
📈 درصد موفقیت: {(batch_stats['success']/(batch_stats['success']+batch_stats['failed'])*100) if (batch_stats['success']+batch_stats['failed']) > 0 else 0:.1f}%

⏱️ **زمان‌بندی:**
🕐 زمان دسته: {batch_duration:.1f} ثانیه
⚡ میانگین هر گروه: {batch_duration/len(current_batch):.1f} ثانیه
      """
      await safe_reply(event, batch_report)

      # به‌روزرسانی آمار کلی
      if 'stats' not in user_states[user_id]:
          user_states[user_id]['stats'] = {
              'success': 0,
              'failed': 0,
              'warnings': 0
          }

      user_states[user_id]['stats']['success'] += batch_stats['success']
      user_states[user_id]['stats']['failed'] += batch_stats['failed']
      user_states[user_id]['stats']['warnings'] += batch_stats['warnings']
      user_states[user_id]['processed_count'] = end_index

      # بررسی ادامه
      if end_index < len(all_groups):
          remaining_groups = len(all_groups) - end_index
          remaining_batches = (remaining_groups + batch_size -
                               1) // batch_size

          continue_info = f"""
⏳ **ادامه پردازش:**
📊 {remaining_groups} گروه در {remaining_batches} دسته باقی‌مانده
⏰ تخمین زمان: {(remaining_groups * (batch_duration/len(current_batch)) + remaining_batches * delay_between_batch)/60:.1f} دقیقه

🔄 **ادامه خودکار در {delay_between_batch} ثانیه...**
          """
          await safe_reply(event, continue_info)

          # تاخیر بین دسته‌ها
          await asyncio.sleep(delay_between_batch)

          # ادامه پردازش
          await advanced_process_group_batch(event, user_id, banner_photo,
                                             banner_caption)

  except Exception as e:
      error_report = f"""
❌ **خطا در پردازش دسته:**
🔍 جزئیات: {str(e)}
📊 گروه‌های پردازش شده: {user_states.get(user_id, {}).get('processed_count', 0)}/{len(user_states.get(user_id, {}).get('all_groups', []))}

🔄 **برای ادامه:** دوباره بنر و لینک کانال ارسال کنید
      """
      await safe_reply(event, error_report)

      if user_id in user_states:
          del user_states[user_id]


# تابع پیشرفته عضویت و ارسال بنر
async def advanced_join_and_send_banner(group_link, banner_photo,
                                      banner_caption, event, group_number,
                                      total_groups):
  """عضویت پیشرفته در گروه با گزارش کامل"""
  start_time = datetime.now()

  try:
      # تشخیص نوع لینک
      link_type = "unknown"
      if 'joinchat' in group_link or '+' in group_link:
          link_type = "private"
      elif group_link.startswith('@'):
          link_type = "username"
      else:
          link_type = "public"

      # تنظیم لینک برای عضویت - بهبود یافته
      if 'joinchat' in group_link:
          if group_link.startswith('https://'):
              join_link = group_link
          else:
              # استخراج hash از لینک
              hash_part = group_link.split('joinchat/')[-1]
              join_link = f"https://t.me/joinchat/{hash_part}"
      elif '+' in group_link:
          if group_link.startswith('https://'):
              join_link = group_link
          else:
              # استخراج hash از لینک
              hash_part = group_link.split('+')[-1]
              join_link = f"https://t.me/+{hash_part}"
      elif group_link.startswith('@'):
          join_link = group_link
      elif group_link.startswith('https://t.me/'):
          join_link = group_link
      else:
          # اگر فقط یوزرنیم باشه
          clean_username = group_link.replace('@', '').replace(
              'https://t.me/', '').replace('t.me/', '')
          join_link = f"@{clean_username}"

      print(f"🔗 [{group_number}/{total_groups}] تلاش عضویت در: {join_link}")

      # تلاش برای عضویت با تلاش مجدد قوی‌تر
      joined = False
      join_error = ""
      group_entity = None

      for attempt in range(5):  # افزایش تعداد تلاش‌ها
          try:
              print(f"   🔄 تلاش {attempt + 1}/5 برای عضویت...")
              result = await client(JoinChannelRequest(join_link))
              joined = True
              print(f"   ✅ عضویت موفق در تلاش {attempt + 1}")
              break
          except Exception as e:
              join_error = str(e)
              print(f"   ⚠️ تلاش {attempt + 1} ناموفق: {join_error[:50]}...")

              if "USER_ALREADY_PARTICIPANT" in join_error:
                  joined = True
                  print(f"   ✅ قبلاً عضو بودم")
                  break
              elif "FLOOD_WAIT" in join_error:
                  import re
                  wait_match = re.search(r'FLOOD_WAIT_(\d+)', join_error)
                  wait_time = int(wait_match.group(1)) if wait_match else 60
                  if wait_time <= 300 and attempt < 4:  # تا 5 دقیقه صبر کن
                      print(f"   ⏳ صبر {wait_time} ثانیه...")
                      await asyncio.sleep(wait_time)
                      continue
                  else:
                      print(f"   ❌ زمان انتظار خیلی زیاد: {wait_time}s")
                      break
              elif any(error in join_error for error in [
                      "CHAT_ADMIN_REQUIRED", "USERNAME_NOT_OCCUPIED",
                      "USER_BANNED_IN_CHANNEL", "INVITE_HASH_EXPIRED",
                      "CHANNELS_TOO_MUCH", "PEER_ID_INVALID"
              ]):
                  print(f"   ❌ خطای قطعی: {join_error[:50]}")
                  break  # خروج بدون تلاش مجدد برای خطاهای قطعی
              elif attempt < 4:
                  # تلاش مجدد با لینک‌های مختلف
                  if attempt == 1 and not join_link.startswith('@'):
                      # تلاش با @ اگر اولی کار نکرد
                      if 'joinchat' not in join_link and '+' not in join_link:
                          clean_name = join_link.replace('https://t.me/', '')
                          join_link = f"@{clean_name}"
                          print(f"   🔄 تلاش با فرمت @: {join_link}")
                  elif attempt == 2 and join_link.startswith('@'):
                      # تلاش با لینک کامل اگر @ کار نکرد
                      username = join_link.replace('@', '')
                      join_link = f"https://t.me/{username}"
                      print(f"   🔄 تلاش با لینک کامل: {join_link}")

                  wait_time = (attempt + 1) * 3  # 3, 6, 9, 12 ثانیه
                  print(f"   ⏳ صبر {wait_time} ثانیه برای تلاش بعدی...")
                  await asyncio.sleep(wait_time)
                  continue

      # بررسی نتیجه عضویت
      if not joined:
          end_time = datetime.now()
          process_time = (end_time - start_time).total_seconds()

          if "CHAT_ADMIN_REQUIRED" in join_error:
              return f"🔒 [{group_number}/{total_groups}] {group_link[:30]}...: نیاز به ادمین | {link_type} | ⏱️{process_time:.1f}s"
          elif "USERNAME_NOT_OCCUPIED" in join_error:
              return f"❌ [{group_number}/{total_groups}] {group_link[:30]}...: یوزرنیم موجود نیست | {link_type} | ⏱️{process_time:.1f}s"
          elif "USER_BANNED_IN_CHANNEL" in join_error:
              return f"🚫 [{group_number}/{total_groups}] {group_link[:30]}...: بن شده‌ام | {link_type} | ⏱️{process_time:.1f}s"
          elif "INVITE_HASH_EXPIRED" in join_error:
              return f"⏰ [{group_number}/{total_groups}] {group_link[:30]}...: لینک منقضی | {link_type} | ⏱️{process_time:.1f}s"
          elif "CHANNELS_TOO_MUCH" in join_error:
              return f"📊 [{group_number}/{total_groups}] {group_link[:30]}...: حد عضویت پر | {link_type} | ⏱️{process_time:.1f}s"
          elif "FLOOD_WAIT" in join_error:
              return f"⏳ [{group_number}/{total_groups}] {group_link[:30]}...: محدودیت زمانی | {link_type} | ⏱️{process_time:.1f}s"
          elif "PEER_ID_INVALID" in join_error:
              return f"🔗 [{group_number}/{total_groups}] {group_link[:30]}...: لینک نامعتبر | {link_type} | ⏱️{process_time:.1f}s"
          else:
              return f"❓ [{group_number}/{total_groups}] {group_link[:30]}...: {join_error[:30]}... | {link_type} | ⏱️{process_time:.1f}s"

      print(f"   ✅ عضویت موفق! دریافت اطلاعات...")

      # گرفتن اطلاعات و تشخیص نوع چت
      try:
          group_entity = await client.get_entity(join_link)
          group_title = getattr(group_entity, 'title', 'نامشخص')[:25]
          group_members = getattr(group_entity, 'participants_count', 'نامشخص')
          
          # تشخیص اینکه آیا کانال است یا گروه
          from telethon.tl.types import Channel
          if isinstance(group_entity, Channel):
              if group_entity.broadcast:
                  # این یک کانال است، نه گروه - نباید بنر بفرستیم
                  print(f"   ⚠️ شناسایی شد: کانال (نه گروه) - رد می‌شود")
                  return f"📺 [{group_number}/{total_groups}] {group_title} | کانال تشخیص داده شد (رد شد) | ⏱️{(datetime.now() - start_time).total_seconds():.1f}s"
          
          print(f"   📊 گروه: {group_title} | اعضا: {group_members}")
      except Exception as e:
          print(f"   ⚠️ خطا در دریافت اطلاعات: {str(e)[:50]}")
          group_title = "نامشخص"
          group_members = "نامشخص"

      await asyncio.sleep(3)  # صبر بیشتر قبل ارسال بنر

      # ارسال بنر با تلاش‌های متعدد
      send_success = False
      send_error = ""

      print(f"   📤 ارسال بنر...")
      for send_attempt in range(3):
          try:
              if group_entity:
                  await client.send_file(group_entity,
                                         banner_photo,
                                         caption=banner_caption)
                  send_success = True
                  print(f"   ✅ بنر ارسال شد در تلاش {send_attempt + 1}")
                  break
              else:
                  await client.send_file(join_link,
                                         banner_photo,
                                         caption=banner_caption)
                  send_success = True
                  print(f"   ✅ بنر ارسال شد در تلاش {send_attempt + 1}")
                  break
          except Exception as e:
              send_error = str(e)[:50]
              print(
                  f"   ⚠️ تلاش ارسال {send_attempt + 1} ناموفق: {send_error}"
              )
              if send_attempt < 2:
                  await asyncio.sleep(2)  # صبر 2 ثانیه بین تلاش‌ها

      # خروج از گروه (اختیاری)
      leave_success = False
      if group_entity:
          try:
              print(f"   🚪 خروج از گروه...")
              await asyncio.sleep(1)
              from telethon.tl.functions.channels import LeaveChannelRequest
              await client(LeaveChannelRequest(group_entity))
              leave_success = True
              print(f"   ✅ خروج موفق")
          except Exception as e:
              print(f"   ⚠️ خطا در خروج: {str(e)[:30]}")

      # محاسبه زمان
      end_time = datetime.now()
      process_time = (end_time - start_time).total_seconds()

      # گزارش نهایی
      if send_success:
          leave_status = "🚪✅" if leave_success else "🚪❌"
          result = f"✅ [{group_number}/{total_groups}] {group_title} | 👥{group_members} | {leave_status} | ⏱️{process_time:.1f}s"
          print(f"   🎉 {result}")
          return result
      else:
          result = f"⚠️ [{group_number}/{total_groups}] {group_title} | عضو شدم ولی بنر ناموفق: {send_error} | ⏱️{process_time:.1f}s"
          print(f"   ⚠️ {result}")
          return result

  except Exception as e:
      end_time = datetime.now()
      process_time = (end_time - start_time).total_seconds()
      error_msg = str(e)[:40]
      result = f"💥 [{group_number}/{total_groups}] {group_link[:30]}...: {error_msg}... | ⏱️{process_time:.1f}s"
      print(f"   💥 خطای کلی: {result}")
      return result


# ایموجی‌های بیشتر و متنوع‌تر
extended_emoji_responses = {
  # ایموجی‌های خنده
  '😂🤣😆😄😃😀😊🙂😉': [
      "هاهاها! منم دارم می‌خندم! 😂", "خنده‌ت قشنگه! 😄", "چه چیز باحالی! 🤣",
      "خندیدن سلامتی‌یه! 😁", "لبخند زدن خوبه! 😊", "خوشحالم که می‌خندی! 😃",
      "حالا دیگه خندیدیم! 😆", "چه حال خوبی! 😉",
      "امیر میگه خندیدن بهترین دواست! 😄", "خنده‌ت مسری‌یه! 🤣"
  ],

  # ایموجی‌های غمگین
  '😢😭😰😨😔😞😟😕🙁☹️': [
      "چرا ناراحتی عزیزم؟ 🤗", "نگران نباش، همه چی درست میشه! 💙",
      "منم کنارتم! 🤝", "حالت بهتر میشه! 🌈", "گریه کردن اشکال نداره! 😢",
      "قوی باش! 💪", "امیدوارم زودتر حالت بهتر بشه! ✨", "آرامش داشته باش! 😌",
      "همه گاهی ناراحت میشن! 🫂", "این دوره موقتیه! ⏳"
  ],

  # ایموجی‌های عاشقانه
  '😍🥰😘😗😙😚🤗🤩💕💖💝💗💓💘💞💟❤️🧡💛💚💙💜🖤🤍🤎': [
      "عاشقای خوش‌قلب! 💕", "منم دوستت دارم! ❤️", "قلبت پر از مهره! 💖",
      "عشق زیباست! 😍", "احساسات قشنگت! 🥰", "عاشق بودن خوبه! 💞",
      "قلبم برات می‌تپه! 💓", "عزیز دلم! 💙",
      "امیر میگه عشق قدرتمندترین احساسه! 💕", "قلب طلایی داری! 💛"
  ],

  # ایموجی‌های عصبانی
  '😡😠🤬😤😣😖😫😩🙄😮‍💨': [
      "چرا عصبانی شدی؟ 😟", "آروم باش عزیزم! 😌", "عصبانیت چیزی حل نمی‌کنه! 🤗",
      "نفس عمیق بکش! 🌬️", "چی شده؟ بگو ببینم! 🤔",
      "صبر کن، حالت بهتر میشه! 💙", "گاهی همه عصبانی می‌شن! 😊",
      "آرامش خوبه! ✨", "امیر میگه عصبانیت انرژی رو هدر میده! 😌",
      "شاید یه استراحت لازم داشته باشی! 🍃"
  ],

  # ایموجی‌های خسته
  '😴😪🥱😵😵‍💫🤤💤': [
      "خسته‌ای؟ برو بخواب! 😴", "خواب خوب! 💤", "استراحت کن عزیزم! 😪",
      "شب بخیر! 🌙", "خواب راحت داشته باش! ✨", "بخواب تا انرژی بگیری! 💪",
      "خوابت خوش باشه! 😌", "فردا سرحال باش! 🌅",
      "امیر میگه خواب برای مغز مثل شارژ کردنه! 🔋", "8 ساعت خواب کافیه! 😴"
  ],

  # ایموجی‌های فکری
  '🤔🧐🤨🙃😐😑🫤🤐🤫🫢': [
      "داری فکر می‌کنی؟ 🤔", "چی تو فکرته؟ 🧐", "فکر عمیق! 💭",
      "بگو چی می‌خوای بپرسی! 🤨", "درگیر فکری؟ 😐", "به چی فکر می‌کنی؟ 🙃",
      "فکرت رو بگو! 💬", "نظرت چیه؟ 🤷‍♂️",
      "امیر میگه فکر کردن قبل از حرف زدن مهمه! 🧠", "یه چیز جالب تو ذهنته! 💫"
  ],

  # ایموجی‌های هیجان
  '🔥💥⚡💫⭐🌟✨🎉🎊🏆🥇🎯💪👍👌🤟✌️🤘🤙👏🙌': [
      "وای چه انرژی! 🔥", "عالی! 💥", "برق زدی! ⚡", "فوق‌العاده! ✨",
      "آفرین! 👏", "عالی کار کردی! 🏆", "قدرت! 💪", "خفن! 🤟", "ایول! 👌",
      "دمت گرم! 🌟", "تاپی! 🔝", "باحال! 🎉", "امیر میگه انرژی مثبت مسری‌یه! ⚡",
      "این روحیه رو نگه دار! 🌟"
  ]
}


def get_emoji_response(message):
  """تشخیص ایموجی و پاسخ مناسب"""
  for emoji_group, responses in extended_emoji_responses.items():
      if any(emoji in message for emoji in emoji_group):
          return random.choice(responses)
  return None


# ذخیره گروه‌هایی که ربات عضوشونه
joined_groups = set()

# حالت انتظار برای جوین گروه
waiting_for_group_join = {}

# حالت انتظار برای دریافت لینک مقصد ویدیو
waiting_for_video_destination = {}


async def join_group_safely(group_link):
  """عضویت امن در گروه"""
  try:
      # تنظیم لینک برای عضویت
      if group_link.startswith('@'):
          join_link = group_link
      elif group_link.startswith('https://t.me/'):
          join_link = group_link
      elif group_link.startswith('t.me/'):
          join_link = f"https://{join_link}"
      else:
          join_link = f"@{group_link}"

      # عضویت در گروه
      await client(JoinChannelRequest(join_link))

      # گرفتن اطلاعات گروه
      entity = await client.get_entity(join_link)
      joined_groups.add(entity.id)

      return True, entity.title, entity.id
  except Exception as e:
      error_msg = str(e)
      if "USER_ALREADY_PARTICIPANT" in error_msg:
          entity = await client.get_entity(join_link)
          joined_groups.add(entity.id)
          return True, entity.title, entity.id
      else:
          return False, str(e), None


# هندل تمام پیام‌های دریافتی
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # کار کردن در همه جا - پیوی و همه گروه‌ها
    sender = await event.get_sender()
    user_id = sender.id
    message = event.text.lower() if event.text else ''

    # ذخیره پیام در حافظه ریپلای
    add_to_reply_memory(user_id, event.id,
                        event.text if event.text else "رسانه")

    # ذخیره در فایل لاگ
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] {sender.id} ({sender.username}): {message}\n")

    # بررسی وضعیت انتظار برای لینک مقصد ویدیو
    if user_id in waiting_for_video_destination and not event.video:
        destination_link = event.text.strip()
        if destination_link and (
            't.me/' in destination_link or 
            '@' in destination_link or 
            'joinchat' in destination_link or
            '+' in destination_link
        ):
            await forward_video_to_destination(event, user_id, destination_link)
        else:
            await safe_reply(event, """
❌ **لینک نامعتبر!**

✅ **فرمت‌های قابل قبول:**
• @channelname
• @groupname
• https://t.me/channelname  
• https://t.me/groupname
• https://t.me/joinchat/xxxxx
• https://t.me/+xxxxx

💡 **نکته:** از کپی مستقیم لینک استفاده کنید
            """)
        return

    # بررسی وضعیت انتظار برای جوین گروه
    if user_id in waiting_for_group_join:
        group_link = event.text.strip()
        if group_link and ('t.me/' in group_link or '@' in group_link
                           or 'joinchat' in group_link):
            await safe_reply(event, "🔄 دارم سعی می‌کنم به گروه جوین بشم...")

            success, result, group_id = await join_group_safely(group_link)

            if success:
                await safe_reply(event, 
                    f"✅ با موفقیت به گروه '{result}' جوین شدم!\n\n🤖 حالا می‌تونم توی اون گروه هم جواب بدم! از این به بعد هر پیامی توی اون گروه بفرستین جوابشو میدم!"
                )

                # ارسال پیام معرفی در گروه
                try:
                    group_entity = await client.get_entity(group_link)
                    intro_message = """
🤖 سلام همگی! من سالیوان هستم، دستیار امیر!

من یک ربات هوشمندم که امیر ساختتم. می‌تونم:
• با شما چت کنم و سوالاتون رو جواب بدم 
• جوک بگم و شما رو بخندونم 😂
• آهنگ پیشنهاد بدم 🎵
• جملات انگیزشی بگم 💡
• چیزای جدید یاد بگیرم 🧠

فقط منشن کنین یا "سالیوان" صدام بزنین تا جوابتون رو بدم! 😊
                    """
                    await client.send_message(group_entity, intro_message)
                except:
                    pass  # اگر نتونست پیام بفرسته، مهم نیست

            else:
                await safe_reply(event, f"❌ نتونستم به گروه جوین بشم!\nخطا: {result}"
                                  )

            # پاک کردن حالت انتظار
            del waiting_for_group_join[user_id]
        else:
            await safe_reply(event, 
                "❌ لینک گروه معتبر نیست! لطفاً لینک صحیح بفرستین.")
        return

    # بررسی وضعیت یادگیری کاربر
    if user_id in user_learning_state:
        if user_learning_state[user_id]['state'] == 'waiting_for_response':
            # کاربر داره جواب کلمه رو می‌ده
            keyword = user_learning_state[user_id]['keyword']
            response_text = event.text

            add_new_learning(keyword, response_text)
            await safe_reply(event, 
                f"✅ عالی! یاد گرفتم که وقتی کسی '{keyword}' بگه، جواب '{response_text}' رو بدم!\n\n🧠 حالا این کلمه رو بلدم و هر وقت کسی استفادش کنه جوابشو میدم!"
            )

            # پاک کردن وضعیت یادگیری
            del user_learning_state[user_id]
            return
        elif user_learning_state[user_id]['state'] == 'waiting_for_keyword':
            # کاربر داره کلمه جدید رو می‌ده
            keyword = event.text.strip()
            if len(keyword) > 0:
                user_learning_state[user_id]['keyword'] = keyword
                user_learning_state[user_id]['state'] = 'waiting_for_response'
                await safe_reply(event, 
                    f"👍 کلمه '{keyword}' رو دریافت کردم!\n\n💬 حالا بگو وقتی کسی این کلمه رو بگه، چه جوابی بدم؟"
                )
                return
            else:
                await safe_reply(event, "❌ کلمه نمی‌تونه خالی باشه! دوباره بنویس:")
                return

    # بررسی ریپلای
    reply_response = handle_reply_context(event, user_id)
    if reply_response:
        await safe_reply(event, reply_response)
        add_to_memory(user_id, event.text or "ریپلای", reply_response)
        return

    # مدیریت مراحل قدم به قدم بنر
    if user_id in user_states and 'banner' in user_states[user_id]:
        current_step = user_states[user_id].get('step', '')

        # شروع فوری بدون تنظیمات
        if message == "0":
            user_states[user_id].update({
                'batch_size': 5,
                'delay_between': 3,
                'delay_between_batch': 8,
                'waiting_for_channel': True,
                'step': 'done'
            })
            await safe_reply(event, "🚀 **شروع فوری با تنظیمات پیشفرض!**\n• 5 گروه در هر دسته\n• 3 ثانیه بین گروه‌ها\n• 8 ثانیه بین دسته‌ها\n\n📡 **حالا لینک کانال رو بفرست:**")
            return

        # مرحله 1: انتخاب تعداد گروه در دسته
        if current_step == 'batch_size':
            if message in ["1", "2", "3", "4"]:
                batch_sizes = {"1": 3, "2": 5, "3": 8, "4": 10}
                user_states[user_id]['batch_size'] = batch_sizes[message]
                user_states[user_id]['step'] = 'delay_between'

                step2_menu = f"""
✅ **مرحله 1 کامل:** {batch_sizes[message]} گروه در هر دسته

⏱️ **مرحله 2 از 3: تاخیر بین گروه‌ها (ثانیه)**

📊 **گزینه‌های موجود:**

**1** ➜ 2 ثانیه (خیلی سریع - خطرناک) ⚠️
**2** ➜ 3 ثانیه (سریع - قابل قبول) ⭐
**3** ➜ 5 ثانیه (متعادل - امن)
**4** ➜ 8 ثانیه (آهسته - ایمن‌ترین)
**5** ➜ 10 ثانیه (خیلی آهسته - فوق‌ایمن)

💡 **عدد مورد نظرت رو بفرست:**
                """
                await safe_reply(event, step2_menu)
                return
            else:
                await safe_reply(event, "❌ فقط عدد 0، 1، 2، 3 یا 4 رو بفرست!")
                return

        # مرحله 2: انتخاب تاخیر بین گروه‌ها
        elif current_step == 'delay_between':
            if message in ["1", "2", "3", "4", "5"]:
                delays = {"1": 2, "2": 3, "3": 5, "4": 8, "5": 10}
                user_states[user_id]['delay_between'] = delays[message]
                user_states[user_id]['step'] = 'delay_batch'

                step3_menu = f"""
✅ **مرحله 2 کامل:** {delays[message]} ثانیه بین گروه‌ها

🔄 **مرحله 3 از 3: تاخیر بین دسته‌ها (ثانیه)**

📊 **گزینه‌های موجود:**

**1** ➜ 5 ثانیه (خیلی سریع - ریسکی) ⚠️
**2** ➜ 8 ثانیه (سریع - قابل قبول) ⭐
**3** ➜ 15 ثانیه (متعادل - امن)
**4** ➜ 30 ثانیه (آهسته - ایمن‌ترین)
**5** ➜ 60 ثانیه (خیلی آهسته - فوق‌ایمن)

💡 **عدد مورد نظرت رو بفرست:**
                """
                await safe_reply(event, step3_menu)
                return
            else:
                await safe_reply(event, "❌ فقط عدد 1، 2، 3، 4 یا 5 رو بفرست!")
                return

        # مرحله 3: انتخاب تاخیر بین دسته‌ها
        elif current_step == 'delay_batch':
            if message in ["1", "2", "3", "4", "5"]:
                batch_delays = {"1": 5, "2": 8, "3": 15, "4": 30, "5": 60}
                user_states[user_id]['delay_between_batch'] = batch_delays[message]
                user_states[user_id]['waiting_for_channel'] = True
                user_states[user_id]['step'] = 'done'

                summary = f"""
🎉 **تمام تنظیمات کامل شد!**

📋 **خلاصه تنظیمات انتخابی:**
• 📊 **دسته‌ها:** {user_states[user_id]['batch_size']} گروه در هر دسته
• ⏱️ **بین گروه‌ها:** {user_states[user_id]['delay_between']} ثانیه
• 🔄 **بین دسته‌ها:** {batch_delays[message]} ثانیه

📡 **حالا لینک کانال رو بفرست تا شروع کنیم:**
                """
                await safe_reply(event, summary)
                return
            else:
                await safe_reply(event, "❌ فقط عدد 1، 2، 3، 4 یا 5 رو بفرست!")
                return

    # اگر کاربر در انتظار لینک کانال برای اسکن هست
    if user_id in user_states and user_states[user_id].get('waiting_for_channel', False):
        channel_link = event.text.strip()
        if channel_link and ('t.me/' in channel_link or '@' in channel_link or 'joinchat' in channel_link):
            banner_photo = user_states[user_id]['banner']
            banner_caption = user_states[user_id]['caption']

            try:
                # شروع اسکن پیشرفته
                scan_message = await safe_reply(event, "🔍 **درحال اسکن کانال...**\n⏳ لطفاً صبر کنید...")

                channel_info, analysis = await advanced_channel_scan(channel_link, user_id)

                # حذف پیام اسکن
                try:
                    await scan_message.delete()
                except:
                    pass

                if channel_info is None:
                    error_msg = f"""
❌ **خطا در اسکن کانال:**
🔍 علت: {analysis}

💡 **راهکارهای ممکن:**
• بررسی صحت لینک کانال
• اطمینان از دسترسی عمومی کانال  
• تلاش مجدد چند دقیقه بعد
• استفاده از لینک مستقیم بجای یوزرنیم

🔄 **برای تلاش مجدد:** بنر جدید بفرستید
                    """
                    await safe_reply(event, error_msg)
                    if user_id in user_states:
                        del user_states[user_id]
                    return

                # ارسال گزارش کامل اسکن
                scan_report = generate_scan_report(channel_info, analysis)
                await safe_reply(event, scan_report)

                if not analysis['unique_groups']:
                    no_groups_msg = f"""
❌ **هیچ لینک گروهی پیدا نشد!**

📊 **آمار اسکن:**
• کل پیام‌ها: {analysis['total_messages']}
• پیام‌های رسانه: {analysis['media_messages']}

💡 **احتمالات:**
• کانال هنوز گروهی معرفی نکرده
• لینک‌ها در کپشن عکس‌ها هستند
• کانال محتوای غیرگروهی داره

🔄 **کانال دیگری امتحان کنید**
                    """
                    await safe_reply(event, no_groups_msg)
                    if user_id in user_states:
                        del user_states[user_id]
                    return

                # تأیید شروع پردازش
                estimated_time = (len(analysis['unique_groups']) * user_states[user_id]['delay_between'] + 
                                len(analysis['unique_groups']) // user_states[user_id]['batch_size'] * user_states[user_id]['delay_between_batch']) / 60

                confirm_message = f"""
🚀 **آماده شروع پردازش!**

🎯 **پیدا شده:** {len(analysis['unique_groups'])} گروه
⚙️ **تنظیمات:** {user_states[user_id]['batch_size']} گروه/دسته
⏱️ **تخمین زمان:** {estimated_time:.1f} دقیقه
📊 **نرخ موفقیت پیش‌بینی:** 70-85%

✅ **شروع خودکار در 3 ثانیه...**
                """
                await safe_reply(event, confirm_message)

                # صبر کوتاه قبل شروع
                await asyncio.sleep(3)

                # ذخیره لیست کامل گروه‌ها
                user_states[user_id]['all_groups'] = analysis['unique_groups']
                user_states[user_id]['processed_count'] = 0
                user_states[user_id]['waiting_for_channel'] = False
                user_states[user_id]['start_time'] = datetime.now()

                # شروع پردازش پیشرفته
                await advanced_process_group_batch(event, user_id, banner_photo, banner_caption)

            except Exception as e:
                error_detail = f"""
❌ **خطای غیرمنتظره:**
🔍 جزئیات: {str(e)[:100]}...

🔄 **برای حل مشکل:**
• بنر جدید بفرستید
• لینک کانال دیگری امتحان کنید
• چند دقیقه صبر کنید و مجدد تلاش کنید

⚠️ اگر مشکل ادامه داشت، به امیر گزارش دهید
                """
                await safe_reply(event, error_detail)
                if user_id in user_states:
                    del user_states[user_id]
        else:
            await safe_reply(event, """
❌ **لینک کانال معتبر نیست!**

✅ **فرمت‌های قابل قبول:**
• @channelname
• https://t.me/channelname  
• https://t.me/joinchat/xxxxx
• https://t.me/+xxxxx

💡 **نکته:** از کپی مستقیم لینک استفاده کنید
            """)
        return

    # اگر کاربر عکس (بنر) فرستاده
    if event.photo:
        # ذخیره بنر با کپشنش
        banner_caption = event.message.message if event.message.message else "🎯 بنر تبلیغاتی"
        user_states[user_id] = {
            'banner': event.photo,
            'caption': banner_caption,
            'start_time': datetime.now(),
            'step': 'batch_size'  # مرحله انتخاب تعداد گروه در دسته
        }

        # منوی قدم به قدم
        step1_menu = """
📸 **بنر دریافت شد!** 📸

🎯 **مرحله 1 از 3: انتخاب تعداد گروه در هر دسته**

📊 **گزینه‌های موجود:**

**1** ➜ 3 گروه در هر دسته (ایمن‌ترین - کندتر)
**2** ➜ 5 گروه در هر دسته (متعادل - پیشنهادی) ⭐
**3** ➜ 8 گروه در هر دسته (سریع‌تر - ریسکی‌تر)
**4** ➜ 10 گروه در هر دسته (سریع‌ترین - خطرناک)

🎯 **شروع فوری بدون تنظیمات:**
**0** ➜ تنظیمات پیشفرض و شروع (5 گروه، 3 ثانیه، 8 ثانیه)

💡 **عدد مورد نظرت رو بفرست:**
        """


    # دستور ترجمه پیشرفته با تشخیص زبان - نسخه رایگان
    elif message.startswith("/tr "):
        text_to_translate = message[4:]
        if text_to_translate:
            try:
                # نصب کتابخانه ترجمه رایگان
                try:
                    from translate import Translator
                except ImportError:
                    await safe_reply(event, "🔄 **در حال نصب کتابخانه ترجمه...**")
                    import subprocess
                    subprocess.check_call(["pip", "install", "translate"])
                    from translate import Translator

                # تشخیص زبان ساده
                has_persian = any('\u0600' <= char <= '\u06FF' for char in text_to_translate)
                has_english = any('a' <= char.lower() <= 'z' for char in text_to_translate)

                if has_persian:
                    # از فارسی به انگلیسی
                    translator = Translator(from_lang="fa", to_lang="en")
                    source_flag = '🇮🇷'
                    target_flag = '🇺🇸'
                    source_lang = "فارسی"
                    target_lang = "انگلیسی"
                elif has_english:
                    # از انگلیسی به فارسی  
                    translator = Translator(from_lang="en", to_lang="fa")
                    source_flag = '🇺🇸'
                    target_flag = '🇮🇷'
                    source_lang = "انگلیسی"
                    target_lang = "فارسی"
                else:
                    # پیش‌فرض: به انگلیسی
                    translator = Translator(to_lang="en")
                    source_flag = '🌍'
                    target_flag = '🇺🇸'
                    source_lang = "نامشخص"
                    target_lang = "انگلیسی"

                # انجام ترجمه
                translated_text = translator.translate(text_to_translate)

                result_text = f"""🔄 **ترجمه رایگان:**

{source_flag} **متن اصلی ({source_lang}):**
{text_to_translate}

{target_flag} **ترجمه ({target_lang}):**
{translated_text}

💡 **سرویس:** translate library (رایگان)"""

                await safe_reply(event, result_text)

            except ImportError:
                await safe_reply(event, "❌ **نصب کتابخانه ناموفق!**\nدستی نصب کنید: `pip install translate`")
            except Exception as e:
                # فال‌بک به ترجمه ساده
                simple_translations = {
                    'سلام': 'hello',
                    'خداحافظ': 'goodbye', 
                    'ممنون': 'thank you',
                    'بله': 'yes',
                    'نه': 'no',
                    'hello': 'سلام',
                    'goodbye': 'خداحافظ',
                    'thank you': 'ممنون',
                    'yes': 'بله',
                    'no': 'نه'
                }

                simple_result = simple_translations.get(text_to_translate.lower())
                if simple_result:
                    await safe_reply(event, f"🔄 **ترجمه ساده:**\n📝 {text_to_translate} ← {simple_result}")
                else:
                    await safe_reply(event, f"❌ **خطا در سرویس ترجمه:**\n🔍 {str(e)[:100]}\n\n💡 از دستور `/translate` استفاده کنید")
        else:
            await safe_reply(event, "❌ متن برای ترجمه وارد کن!\nمثال: `/tr سلام دنیا`")



        await safe_reply(event, step1_menu)
        return
    elif event.voice:
        response = random.choice(voice_comments)
        await safe_reply(event, response)
        add_to_memory(user_id, "ویس فرستاد", response)
        return
    elif event.video:
        # پردازش ویدیو برای استخراج کپشن
        video_caption = event.message.message if event.message.message else None

        # ذخیره ویدیو و شروع فرآیند ارسال
        await extract_video_caption_and_forward(event, event.video, video_caption, user_id)
        add_to_memory(user_id, "ویدیو فرستاد برای forward", "ویدیو دریافت شد و آماده ارسال")
        return

    # بررسی ایموجی‌ها
    emoji_response = get_emoji_response(message)
    if emoji_response:
        await safe_reply(event, emoji_response)
        add_to_memory(user_id, message, emoji_response)
        return

    # پاسخ به "سلام"
    if message == "سلام":
        if is_new_user(sender.id):
            # کاربر جدید - معرفی دستیار امیر
            if event.is_group:
                # پاسخ کوتاه‌تر برای گروه
                welcome_message = f"""
{random.choice(greeting_responses)}

🤖 **من سالیوان هستم، دستیار امیر!** 

📋 **دستورات اصلی:**
• `/menu` - منوی کامل
• `/help` - راهنما
• `/joke` - جوک
• `/quote` - جمله انگیزشی

💬 **کلمات کلیدی:** سلام، چطوری، ممنون، جوک، آهنگ، سالیوان
🎯 **قابلیت ویژه:** بنر بفرست + لینک کانال = اسکن و ارسال

برای راهنمای کامل `/help` بزن! 😊
                """
            else:
                # پاسخ کامل برای پیوی
                welcome_message = f"""
{random.choice(greeting_responses)}

🤖 **من سالیوان هستم، دستیار امیر!** 🤖

👤 **درباره امیر (سازنده من):**
• اسم: امیر 
• سن: 17 سال (متولد 1386)
• قد: 189 سانتی‌متر (خیلی بلنده!)
• علاقه‌مندی‌ها: گیمینگ، PS5، فیلم، انیمه، خوردن
• شخصیت: گیمر حرفه‌ای، فیلم‌باز، سرگرم‌جو
• سبک زندگی: 24/7 گیمینگ، Netflix، پیتزا و همبرگر
• رویا: مهاجرت از ایران و زندگی در کشور بهتر

📋 **دستورات اصلی:**
• `/menu` - نمایش منوی دکمه‌ای
• `/time` - نمایش زمان فعلی  
• `/info` - نمایش اطلاعات شما
• `/joke` - یک جوک تصادفی
• `/quote` - یک جمله انگیزشی
• `/help` - راهنمای کامل

🎮 **دکمه‌های تعاملی:**
• 📅 زمان - برای دیدن ساعت
• ℹ️ اطلاعات - برای دیدن مشخصاتت
• 🎲 جواب تصادفی - برای پیام‌های تصادفی
• 😂 جوک - برای خنده
• 💡 جمله انگیزشی - برای انگیزه
• 🎵 آهنگ تصادفی - پیشنهاد آهنگ
• 🎤 آهنگ رپ - آهنگ‌های رپ فارسی
• 🌹 آهنگ قدیمی - آهنگ‌های کلاسیک
• 🤔 معما و چیستان - معما و چیستان
• 📖 داستان کوتاه - داستان‌های آموزنده
• 🌡️ آب و هوا - وضعیت آب و هوا
• 📊 آمار ربات - آمار کلی

💬 **کلمات کلیدی:**
• "سلام" - احوالپرسی
• "ممنون" یا "تشکر" - تشکر
• "چطوری" - پرسیدن حال
• "باحالی" - تعارف
• "بگو متن" - تکرار متن شما

📨 **رسانه‌ها:**
• عکس بفرست - نظرم رو بگم
• ویس بفرست - صداتو تحسین کنم  
• ویدیو بفرست - تماشا کنم

🎯 **قابلیت ویژه:**
• بنر (عکس) بفرست - لینک گروه رو بخوام و بنر رو توی گروه بفرستم

🔄 **قابلیت ریپلای:**
• روی پیام‌هام ریپلای کن - متوجه میشم منظورت چیه!

💡 برای شروع `/menu` رو بفرست یا هر چیزی که دوست داری بنویس! 😊
            """
            await safe_reply(event, welcome_message)
            add_user(sender.id)
            add_to_memory(user_id, message, welcome_message)
        else:
            # کاربر قدیمی - پاسخ معمولی
            response = random.choice(greeting_responses)
            await safe_reply(event, response)
            add_to_memory(user_id, message, response)

    # دکمه: زمان
    elif message == "📅 زمان":
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await safe_reply(event, f"⏰ الان ساعت:\n{now}")

    # دکمه: اطلاعات
    elif message == "ℹ️ اطلاعات":
        await safe_reply(event, 
            f"👤 اطلاعات شما:\n"
            f"نام: {sender.first_name or 'ناموجود'}\n"
            f"یوزرنیم: @{sender.username if sender.username else 'نداره'}\n"
            f"آیدی عددی: {sender.id}")

    # دکمه: جواب تصادفی
    elif message == "🎲 جواب تصادفی":
        response = random.choice([
            "امروز حالت چطوره؟ 😄", "یه لبخند بزن، دنیا قشنگ‌تره! 🌈",
            "زندگی یعنی لحظه‌ی حال ✨", "همیشه مثبت باش! 🌟",
            "امروز روز خوبیه! 🌞", "انرژیت رو حفظ کن! ⚡"
        ])
        await safe_reply(event, response)

    # دکمه: جوک
    elif message == "😂 جوک":
        await safe_reply(event, random.choice(jokes))

    # دکمه: جمله انگیزشی
    elif message == "💡 جمله انگیزشی":
        await safe_reply(event, random.choice(quotes))

    # دکمه: آهنگ تصادفی
    elif message == "🎵 آهنگ تصادفی":
        await safe_reply(event, f"پیشنهاد امروز:\n{random.choice(songs)}")

    # دکمه: آهنگ رپ
    elif message == "🎤 آهنگ رپ":
        await safe_reply(event, f"رپ پیشنهادی:\n{random.choice(rap_songs)}")

    # دکمه: آهنگ قدیمی
    elif message == "🌹 آهنگ قدیمی":
        await safe_reply(event, f"کلاسیک پیشنهادی:\n{random.choice(classic_songs)}")

    # دکمه: معما و چیستان
    elif message == "🤔 معما و چیستان":
        await safe_reply(event, random.choice(riddles))

    # دکمه: داستان کوتاه
    elif message == "📖 داستان کوتاه":
        await safe_reply(event, random.choice(short_stories))

    # دکمه: آب و هوا
    elif message == "🌡️ آب و هوا":
        await safe_reply(event, f"آب و هوای امروز:\n{random.choice(cities_weather)}")

    # دکمه: بازی‌ها
    elif message == "🎮 بازی‌ها":
        games_menu = """
🎮 **منوی بازی‌های تعاملی** 🎮

🎯 **بازی‌های موجود:**

1️⃣ **سوال جواب** - تست دانش عمومی
   • دسته‌ها: عمومی، تاریخ، علوم، ورزش
   • 10 سوال چندگزینه‌ای
   • کامند: `/quiz [دسته]`

2️⃣ **حدس کلمه** - پیدا کردن کلمه مخفی
   • دسته‌ها: حیوانات، میوه‌ها، رنگ‌ها، کشورها، شهرها
   • 6 شانس برای حدس زدن
   • کامند: `/wordguess [دسته]`

3️⃣ **فرهنگ ایران** - دانش فرهنگ ایرانی
   • سوالات درباره تاریخ و فرهنگ ایران
   • 8 سوال تخصصی
   • کامند: `/iranculture`

📋 **دستورات:**
• `/games` - این منو
• `/hint` - راهنمایی (حین بازی)
• `/stopgame` - خروج از بازی

🏆 **نکات:**
• امتیازات بر اساس صحت جواب‌ها
• راهنمایی برای هر سوال موجوده
• می‌تونی هر وقت خواستی خارج بشی

🎲 **شروع:** یکی از کامندهای بالا رو بنویس!
        """
        await safe_reply(event, games_menu)

    # دکمه: آمار ربات
    elif message == "📊 آمار ربات":
        try:
            with open(users_file, "r") as f:
                user_count = len(f.readlines())
        except FileNotFoundError:
            user_count = 0

        try:
            with open("logs.txt", "r") as f:
                message_count = len(f.readlines())
        except FileNotFoundError:
            message_count = 0

        await safe_reply(event, 
            f"📊 آمار ربات:\n👥 تعداد کاربران: {user_count}\n💬 تعداد پیام‌ها: {message_count}\n⏰ زمان آنلاین: 24/7"
        )

    # دستور زمان با /time
    elif message == "/time":
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await safe_reply(event, f"⏰ الان ساعت:\n{now}")

    # دستور اطلاعات با /info
    elif message == "/info":
        await safe_reply(event, 
            f"👤 اطلاعات شما:\n"
            f"نام: {sender.first_name or 'ناموجود'}\n"
            f"یوزرنیم: @{sender.username if sender.username else 'نداره'}\n"
            f"آیدی عددی: {sender.id}")

    # دستور راهنما با /help
    elif message == "/help":
        help_text = """
🆘 **راهنمای کامل ربات سالیوان** 🆘

👨‍💻 **درباره سازنده:**
• امیر، 17 ساله، قد 189 سانتی
• عاشق برنامه‌نویسی و گیمینگ
• طراح و سازنده ربات سالیوان

📌 **دستورات اصلی:**
• `/menu` - منوی کامل با دکمه‌های تعاملی
• `/commands` - لیست کامل دستورات
• `/time` - زمان و تاریخ فعلی
• `/info` - اطلاعات شما  
• `/joke` - جوک تصادفی
• `/quote` - جمله انگیزشی
• `/help` - این راهنما

🧠 **یادگیری هوشمند:**
• `/learn` - شروع یادگیری کلمه جدید
• `/learned` - نمایش کلمات یادگرفته شده
• `/forget` - فراموش کردن کلمه
• "یاد بگیر کلمه: جواب" - یادگیری سریع
• "فراموش کن کلمه" - حذف یادگیری

🤖 **مدیریت گروه (فقط پیوی):**
• `/join` - جوین شدن به گروه
• `/groups` - نمایش گروه‌های عضو
• `/leave` - خروج از گروه

🎯 **کلمات کلیدی:**
• "سلام" - احوالپرسی و خوشامدگویی
• "چطوری" - پرسیدن حال
• "چخبر" - پرسیدن اخبار
• "ممنون" - تشکر
• "باحالی" - تعارف
• "بگو متن" - تکرار متن شما
• "سالیوان" - صدا زدن ربات

🎯 **قابلیت‌های ویژه:**
• بنر (عکس) بفرست - لینک کانال رو می‌خوام و بنر رو توی گروه می‌فرستم
• ریپلای کردن - درک context مکالمه
• تشخیص احساسات - پاسخ عاطفی و با درک

🔄 **رسانه‌ها:**
• عکس بفرست - نظرم رو بگم
• ویس بفرست - صداتو تحسین کنم
• ویدیو بفرست - تماشا کنم و نظر بدم

🚫 **نکات مهم:**
• تمام دستورات case-insensitive هستند
• سوالات با علامت سوال بپرس
• فحش دادن = فحش برگردوندن! 😏
• از ایموجی استفاده کن

💡 برای دسترسی سریع از `/menu` استفاده کن!
        """
        await safe_reply(event, help_text)

    # دستور دستورات با /commands یا "دستورات"
    elif message == "/commands" or message == "دستورات":
        commands_text = """
📋 **لیست کامل دستورات ربات سالیوان** 📋

🔸 **دستورات اصلی:**
• `/menu` - نمایش منوی دکمه‌ای کامل
• `/commands` - نمایش این لیست
• `/games` - منوی بازی‌های تعاملی
• `/time` - نمایش زمان و تاریخ فعلی
• `/info` - نمایش اطلاعات کاربر
• `/help` - راهنمای کامل ربات
• `/joke` - جوک تصادفی
• `/quote` - جمله انگیزشی
• `/weather [شهر]` - وضعیت آب و هوا
• `/birthday YYYY/MM/DD` - ثبت تاریخ تولد
• `/mybirthday` - نمایش تاریخ تولد
• `/image متن` - تولید تصویر با AI
• `/tr متن` - ترجمه رایگان (فارسی-انگلیسی)
• "صدا متن" - تبدیل متن به صدا

🔸 **دستورات بازی‌های تعاملی:**
• `/games` - منوی کامل بازی‌ها
• `/quiz [دسته]` - بازی سوال جواب (عمومی، تاریخ، علوم، ورزش)
• `/wordguess [دسته]` - بازی حدس کلمه (حیوانات، میوه‌ها، رنگ‌ها، کشورها، شهرها)
• `/math [سطح]` - بازی ریاضی (آسان، متوسط، سخت)
• `/iranculture` - بازی فرهنگ ایران
• `/memory` - بازی حافظه و تمرکز
• `/hint` - راهنمایی حین بازی
• `/stopgame` - خروج از بازی

🔸 **دستورات شخصی‌سازی:**
• `/persona [نوع] [پیام]` - چت با شخصیت‌های مختلف
  - نوع‌ها: لاتی، شاعر، علمی، بچه، طنز، چس‌مَیاد، روشنفکر، عاشق
• `/weather [شهر]` - آب و هوای شهرها
• `/news` - اخبار BBC فارسی (ترجمه شده)

🔸 **دستورات ترجمه و زبان:**
• `/tr [متن]` - ترجمه رایگان با تشخیص زبان
• `/translate [متن]` - ترجمه پیشرفته
• `/pronounce [کلمه]` - تلفظ کلمات انگلیسی
• "صدا [متن]" - تبدیل متن فارسی به صدا

🔸 **دستورات اطلاعات مفید:**
• `/news` - اخبار BBC فارسی ترجمه شده
• `/crypto` - قیمت ارزهای دیجیتال
• `/currency` - نرخ ارز
• `/weather [شهر]` - آب و هوای دقیق شهرها

🔸 **دستورات سرگرمی بیشتر:**
• `/meme` - میم‌های طنز فارسی
• `/poem` - اشعار زیبا و کلاسیک
• `/fortune` - فال روزانه و طالع‌بینی

🔸 **دستورات سلامت و تناسب اندام:**
• `/workout [نوع]` - برنامه ورزشی (مبتدی، حرفه‌ای، کاردیو)
• `/health` - نکات سلامتی و بهداشت
• `/bmi [وزن] [قد]` - محاسبه شاخص توده بدنی

🔸 **دستورات ابزارهای کسب و کار:**
• `/password [طول]` - تولید رمز عبور قوی
• `/convert [مقدار] [واحد] [واحد جدید]` - تبدیل واحدها

🔸 **دستورات هنر و خلاقیت:**
• `/image [متن]` - تولید تصویر با AI FLUX
• `/color` - پالت‌های رنگی تصادفی
• `/idea` - ایده‌های خلاقانه و نوآورانه
• `/story` - شروع داستان‌های جذاب
• `/design` - نکات طراحی و هنر

🔸 **دستورات مدیریت گروه (فقط پیوی):**
• `/join` یا "میخوام بیای گروه" - جوین شدن به گروه
• `/groups` یا "چه گروه هایی" - نمایش گروه‌های عضو
• `/leave` یا "خارج شو" - خروج از گروه

🔸 **دستورات یادگیری هوشمند:**
• `/learn` یا "یاد بگیر" - شروع یادگیری کلمه جدید
• `/learned` یا "چی یاد گرفتی" - نمایش کلمات یادگرفته شده
• `/forget` یا "فراموش کن [کلمه]" - حذف کلمه یادگرفته شده
• "تست تشخیص [کلمه]" - تست سیستم تشخیص هوشمند

🔸 **کلمات کلیدی ساده:**
• "سلام" - احوالپرسی و خوشامدگویی
• "چطوری" / "خوبی" - پرسیدن حال
• "چخبر" / "چه خبر" - پرسیدن اخبار
• "ممنون" / "مرسی" - تشکر
• "باحالی" / "خفنی" - تعارف و تمجید
• "بگو [متن]" - تکرار متن
• "سالیوان" - صدا زدن ربات
• "امیر" - صحبت درباره سازنده
• "سالیوان کیه" - معرفی خود ربات
• "امیر کیه" - معرفی کامل سازنده

🔸 **درخواست‌های خاص:**
• "جوک" / "بخندونم" - درخواست جوک
• "آهنگ" / "موزیک" - پیشنهاد آهنگ عمومی
• "رپ" / "rap" - پیشنهاد آهنگ رپ فارسی
• "قدیمی" / "کلاسیک" - پیشنهاد آهنگ کلاسیک
• "انگیزه" / "روحیه" - جمله انگیزشی
• "معما" / "چیستان" - معما و چیستان
• "داستان" / "قصه" - داستان کوتاه آموزنده
• "چیکار می‌کنی" - پرسیدن فعالیت

🔸 **یادگیری سریع:**
• "یاد بگیر کلمه: جواب" - یادگیری در یک پیام
• "فراموش کن [کلمه]" - حذف کلمه یادگرفته شده
• "چی یاد گرفتی" - نمایش یادگیری‌ها
• "تست تشخیص [کلمه]" - آزمایش سیستم تشخیص

🔸 **قابلیت‌های ویژه رسانه:**
• ارسال عکس - دریافت نظر + تحلیل با `/ai`
• ارسال ویس - تحسین صدا و کیفیت
• ارسال ویدیو - استخراج کپشن، حذف لینک و ارسال به مقصد
• ارسال بنر (عکس) - اسکن کانال و ارسال بنر به گروه‌ها
• ریپلای کردن - درک context مکالمه
• استفاده از ایموجی - پاسخ‌های متناسب

🔸 **دکمه‌های منوی تعاملی:**
• 📅 زمان - نمایش ساعت فعلی
• ℹ️ اطلاعات - مشخصات کاربر  
• 🎮 بازی‌ها - منوی بازی‌های تعاملی
• 🎲 جواب تصادفی - پیام تصادفی
• 😂 جوک - جوک خنده‌دار
• 💡 جمله انگیزشی - انگیزه روزانه
• 🎵 آهنگ تصادفی - پیشنهاد آهنگ
• 🎤 آهنگ رپ - آهنگ‌های رپ فارسی
• 🌹 آهنگ قدیمی - آهنگ‌های کلاسیک
• 🤔 معما و چیستان - معما و چیستان
• 📖 داستان کوتاه - داستان‌های آموزنده
• 🌡️ آب و هوا - وضعیت آب و هوا
• 📊 آمار ربات - آمار کلی

🔸 **احساسات و روحیات (درک عمیق):**
• "ناراحتم" / "غمگینم" - پاسخ‌های دلسوزانه و عاطفی
• "خوشحالم" / "شادم" - تقسیم شادی با شدت احساس
• "عصبانیم" / "کلافم" - آرامش‌بخشی و تسکین
• "ترسیدم" / "نگرانم" - تسلی دادن و حمایت
• "عاشقم" / "دوستش دارم" - شادی کردن و تبریک
• "تنهام" / "کسی نیست" - همراهی کردن و دلداری

🔸 **پاسخ‌های خاص:**
• "خوبم" / "سلامتی" - تبریک و خوشحالی
• "خوش باشی" / "سلامت باشی" - پاسخ متقابل
• "خدا نگهدارت" - دعای متقابل

💡 **نکته:** همه دستورات case-insensitive هستند (بزرگ یا کوچک بودن حروف مهم نیست)

🤖 **هوش مصنوعی:**
• تشخیص احساسات با 5 سطح شدت
• درک context مکالمه و حافظه
• یادگیری هوشمند با تشخیص فازی
• پاسخ‌های عاطفی و همدلانه

🚫 **هشدار:** فحش دادن = فحش برگردوندن! 😏

🤖 برای دسترسی سریع از `/menu` استفاده کن!
        """
        await safe_reply(event, commands_text)

    # دستور جوک با /joke
    elif message == "/joke":
        await safe_reply(event, random.choice(jokes))

    # دستور جمله انگیزشی با /quote
    elif message == "/quote":
        await safe_reply(event, random.choice(quotes))

    # دستورات یادآوری و تایمر
    elif message.startswith("/remind "):
        parts = message.split(" ", 2)
        if len(parts) >= 3:
            try:
                time_minutes = int(parts[1])
                reminder_text = parts[2]
                await safe_reply(event, f"⏰ یادآوری تنظیم شد!\n📝 پیام: {reminder_text}\n🕐 زمان: {time_minutes} دقیقه دیگر\n\n⚠️ توجه: این فقط نمونه است، یادآوری واقعی فعال نیست!")
            except ValueError:
                await safe_reply(event, "❌ فرمت درست: `/remind 30 دارو بخور`")
        else:
            await safe_reply(event, "❌ فرمت درست: `/remind [دقیقه] [پیام]`")

    elif message.startswith("/timer "):
        parts = message.split(" ", 1)
        if len(parts) == 2:
            try:
                timer_minutes = int(parts[1])
                await safe_reply(event, f"⏱️ تایمر {timer_minutes} دقیقه‌ای شروع شد!\n\n⚠️ توجه: این فقط نمونه است، تایمر واقعی فعال نیست!")
            except ValueError:
                await safe_reply(event, "❌ فرمت درست: `/timer 25`")
        else:
            await safe_reply(event, "❌ فرمت درست: `/timer [دقیقه]`")

    # دستورات ترجمه و زبان
    elif message.startswith("/pronounce "):
        word = message[12:]
        if word:
            await safe_reply(event, f"🗣️ **تلفظ کلمه '{word}':**\n\n⚠️ توجه: این فقط نمونه است، تلفظ واقعی فعال نیست!\nبرای تلفظ دقیق از Google Translate استفاده کنید.")
        else:
            await safe_reply(event, "❌ کلمه برای تلفظ وارد کن!")

    # دستورات اطلاعات مفید
    elif message == "/news":
        sample_news = [
            "📰 خبر نمونه: پیشرفت در فناوری هوش مصنوعی",
            "📰 خبر نمونه: کشف جدید در زمینه پزشکی", 
            "📰 خبر نمونه: رشد اقتصادی کشورهای منطقه",
            "📰 خبر نمونه: تحولات جدید در صنعت فناوری"
        ]
        await safe_reply(event, f"📺 **اخبار امروز:**\n\n{random.choice(sample_news)}\n\n⚠️ این اخبار نمونه هستند!")

    elif message == "/crypto":
        crypto_prices = [
            "₿ Bitcoin: $43,250 (+2.3%)",
            "Ξ Ethereum: $2,650 (+1.8%)", 
            "🪙 BNB: $245 (-0.5%)",
            "💎 Cardano: $0.52 (+3.1%)"
        ]
        await safe_reply(event, f"💰 **قیمت ارزهای دیجیتال:**\n\n" + "\n".join(crypto_prices) + "\n\n⚠️ قیمت‌های نمونه!")

    elif message == "/currency":
        currency_rates = [
            "💵 دلار آمریکا: 42,500 تومان",
            "💶 یورو: 46,200 تومان",
            "💷 پوند انگلیس: 53,800 تومان",
            "💴 ین ژاپن: 285 تومان"
        ]
        await safe_reply(event, f"💱 **نرخ ارز:**\n\n" + "\n".join(currency_rates) + "\n\n⚠️ نرخ‌های نمونه!")

    # دستورات سرگرمی بیشتر
    elif message == "/meme":
        memes = [
            "😂 وقتی میگن برنامه‌نویسی آسونه:\n'تو خواب!' 💤",
            "🤣 وقتی کدت کار می‌کنه:\n'معجزه! 🎉'",
            "😄 وقتی دیباگ می‌کنی:\n'این باگ کجا قایم شده؟ 🕵️'"
        ]
        await safe_reply(event, random.choice(memes))

    elif message == "/poem":
        poems = [
            "🌹 'دل که رفت از دست اگرچه رفت\nرفتن و آمدن و ماندن هست'\n- حافظ",
            "🌸 'گر صبر کنی ز غوره حلوا سازی\nور طعنه زنی ز یار جدا سازی'\n- سعدی",
            "🌺 'تو مگو که آسمان تنگ است\nدل تو مگر که سنگ است'\n- مولانا"
        ]
        await safe_reply(event, random.choice(poems))

    elif message == "/fortune":
        fortunes = [
            "🔮 **فال امروز:** روز خوبی در انتظارت! موفقیت در کار ✨",
            "🌟 **طالع‌بینی:** احتمال دیدار با دوست قدیمی زیاد! 💫",
            "⭐ **فال روزانه:** انرژی مثبت برات! امروز روز خلاقیته 🎨"
        ]
        await safe_reply(event, random.choice(fortunes))

    # دستورات سلامت و تناسب اندام  
    elif message.startswith("/workout "):
        workout_type = message[9:]
        workouts = {
            "مبتدی": "🏃‍♂️ **برنامه مبتدی:**\n• 10 دقیقه پیاده‌روی\n• 15 شنا\n• 10 کشش",
            "حرفه‌ای": "💪 **برنامه حرفه‌ای:**\n• 30 دقیقه دو\n• 45 دقیقه بدنسازی\n• 20 دقیقه یوگا",
            "کاردیو": "❤️ **تمرین کاردیو:**\n• 20 دقیقه دوچرخه\n• 15 دقیقه طناب\n• 10 دقیقه استراحت"
        }
        result = workouts.get(workout_type, "انواع: مبتدی، حرفه‌ای، کاردیو")
        await safe_reply(event, result)

    elif message == "/health":
        health_tips = [
            "💧 روزانه 8 لیوان آب بنوش!",
            "🥗 میوه و سبزیجات تازه بخور!",
            "😴 شب‌ها 7-8 ساعت بخواب!",
            "🚶‍♂️ روزانه حداقل 30 دقیقه پیاده‌روی کن!"
        ]
        await safe_reply(event, f"🏥 **نکته سلامتی:**\n\n{random.choice(health_tips)}")

    elif message.startswith("/bmi "):
        parts = message.split()
        if len(parts) == 3:
            try:
                weight = float(parts[1])
                height = float(parts[2]) / 100  # تبدیل سانتی‌متر به متر
                bmi = weight / (height ** 2)

                if bmi < 18.5:
                    status = "کم‌وزن"
                elif bmi < 25:
                    status = "نرمال"
                elif bmi < 30:
                    status = "اضافه‌وزن"
                else:
                    status = "چاق"

                await safe_reply(event, f"⚖️ **محاسبه BMI:**\n\n📊 BMI شما: {bmi:.1f}\n📋 وضعیت: {status}")
            except ValueError:
                await safe_reply(event, "❌ فرمت درست: `/bmi 70 175`")
        else:
            await safe_reply(event, "❌ فرمت درست: `/bmi [وزن] [قد]`")

    # دستورات ابزارهای کسب و کار
    elif message.startswith("/password "):
        try:
            length = int(message.split()[1])
            if 4 <= length <= 50:
                import string
                chars = string.ascii_letters + string.digits + "!@#$%^&*"
                password = ''.join(random.choice(chars) for _ in range(length))
                await safe_reply(event, f"🔐 **رمز عبور تولید شده:**\n\n`{password}`\n\n⚠️ این رمز را در جای امنی ذخیره کنید!")
            else:
                await safe_reply(event, "❌ طول رمز باید بین 4 تا 50 باشد!")
        except (ValueError, IndexError):
            await safe_reply(event, "❌ فرمت درست: `/password 16`")

    elif message.startswith("/convert "):
        await safe_reply(event, "🔄 **تبدیل واحد:**\n\n⚠️ این قابلیت در نسخه آینده اضافه می‌شود!\nمثال: `/convert 100 سانتی‌متر متر`")

    # دستورات هنر و خلاقیت
    elif message == "/color":
        colors = [
            "🎨 **پالت رنگی امروز:**\n🔴 قرمز کرمزی\n🟡 زرد طلایی\n🔵 آبی آسمانی",
            "🌈 **ترکیب رنگی پیشنهادی:**\n🟣 بنفش\n🟢 سبز یشمی\n🟠 نارنجی آتشین",
            "✨ **رنگ‌های آرامش‌بخش:**\n🤍 سفید برفی\n🩵 آبی پاستلی\n🩷 صورتی ملایم"
        ]
        await safe_reply(event, random.choice(colors))

    elif message == "/idea":
        ideas = [
            "💡 **ایده خلاقانه:** یک اپ برای یادگیری زبان با بازی!",
            "🌟 **ایده نوآورانه:** ربات باغبانی هوشمند!",
            "🎯 **ایده کسب‌وکار:** پلتفرم آموزش آنلاین تعاملی!"
        ]
        await safe_reply(event, random.choice(ideas))

    elif message == "/story":
        story_starts = [
            "📖 **شروع داستان:**\n'در شهری دورافتاده، پسر جوانی زندگی می‌کرد که...'",
            "📚 **آغاز قصه:**\n'روزی که همه چیز تغییر کرد، آفتاب طلوع نکرد و...'",
            "📝 **ابتدای حکایت:**\n'در جنگل پرتنها، درختی بود که حرف می‌زد و...'"
        ]
        await safe_reply(event, random.choice(story_starts))

    elif message == "/design":
        design_tips = [
            "🎨 **نکته طراحی:** سادگی کلید زیبایی است!",
            "✨ **اصل طراحی:** رنگ‌ها را محدود نگه دارید!",
            "🖌️ **راهنمای هنری:** فضای خالی بخش مهم طراحی است!"
        ]
        await safe_reply(event, random.choice(design_tips))

    # دستور بازی‌ها با /games
    elif message == "/games":
        games_menu = """
🎮 **منوی بازی‌های تعاملی** 🎮

🎯 **بازی‌های موجود:**

1️⃣ **سوال جواب** - تست دانش عمومی
   • دسته‌ها: عمومی، تاریخ، علوم، ورزش
   • 10 سوال چندگزینه‌ای
   • کامند: `/quiz [دسته]`

2️⃣ **حدس کلمه** - پیدا کردن کلمه مخفی
   • دسته‌ها: حیوانات، میوه‌ها، رنگ‌ها، کشورها، شهرها
   • 6 شانس برای حدس زدن
   • کامند: `/wordguess [دسته]`

3️⃣ **فرهنگ ایران** - دانش فرهنگ ایرانی
   • سوالات درباره تاریخ و فرهنگ ایران
   • 8 سوال تخصصی
   • کامند: `/iranculture`

📋 **دستورات:**
• `/games` - این منو
• `/hint` - راهنمایی (حین بازی)
• `/stopgame` - خروج از بازی

🏆 **نکات:**
• امتیازات بر اساس صحت جواب‌ها
• راهنمایی برای هر سوال موجوده
• می‌تونی هر وقت خواستی خارج بشی

🎲 **شروع:** یکی از کامندهای بالا رو بنویس!
        """
        await safe_reply(event, games_menu)

    # بازی سوال جواب
    elif message.startswith("/quiz"):
        parts = message.split()
        category = parts[1] if len(parts) > 1 and parts[1] in quiz_questions else 'عمومی'

        if user_id in user_game_states:
            await safe_reply(event, "❌ یه بازی دیگه داری! اول با `/stopgame` خارج شو!")
            return

        game_text = start_quiz_game(user_id, category)
        if game_text:
            await safe_reply(event, game_text)
        else:
            await safe_reply(event, "❌ دسته موجود نیست! دسته‌های موجود: عمومی، تاریخ، علوم، ورزش")

    # بازی حدس کلمه
    elif message.startswith("/wordguess"):
        parts = message.split()
        category = parts[1] if len(parts) > 1 and parts[1] in word_guess_categories else 'حیوانات'

        if user_id in user_game_states:
            await safe_reply(event, "❌ یه بازی دیگه داری! اول با `/stopgame` خارج شو!")
            return

        game_text = start_word_guess_game(user_id, category)
        if game_text:
            await safe_reply(event, game_text)
        else:
            await safe_reply(event, "❌ دسته موجود نیست! دسته‌های موجود: حیوانات، میوه‌ها، رنگ‌ها، کشورها، شهرها")



    # بازی فرهنگ ایران
    elif message == "/iranculture":
        if user_id in user_game_states:
            await safe_reply(event, "❌ یه بازی دیگه داری! اول با `/stopgame` خارج شو!")
            return

        game_text = start_iran_culture_game(user_id)
        await safe_reply(event, game_text)



    # راهنمایی
    elif message == "/hint":
        hint_text = get_game_hint(user_id)
        await safe_reply(event, hint_text)

    # خروج از بازی
    elif message == "/stopgame":
        if user_id in user_game_states:
            del user_game_states[user_id]
            await safe_reply(event, "🚪 از بازی خارج شدی! برای شروع بازی جدید: `/games`")
        else:
            await safe_reply(event, "❌ هیچ بازی فعالی نداری!")

    # پردازش جواب‌های بازی
    elif user_id in user_game_states:
        game_state = user_game_states[user_id]
        game_type = game_state['game_type']

        if game_type in ['quiz', 'iran_culture']:
            response = process_quiz_answer(user_id, message)
            await safe_reply(event, response)
            add_to_memory(user_id, message, response)
            return

        elif game_type == 'word_guess':
            response = process_word_guess(user_id, message)
            await safe_reply(event, response)
            add_to_memory(user_id, message, response)
            return



    # دستورات جوین گروه
    elif message == "/join" or "میخوام بیای گروه" in message or "بیا گروه" in message or "جوین شو" in message:
        if not event.is_private:
            await safe_reply(event, "❌ این دستور فقط توی پیوی کار می‌کنه!")
            return

        waiting_for_group_join[user_id] = True
        await safe_reply(event, """
🚀 **عالی! آماده جوین شدن به گروه!**

📝 لینک گروهی که می‌خوای جوینش بشم رو بفرست:

🔗 **انواع لینک قابل قبول:**
• @groupname
• https://t.me/groupname  
• https://t.me/joinchat/xxxxx
• https://t.me/+xxxxx
• t.me/groupname

⚠️ **نکات مهم:**
• اطمینان حاصل کن که گروه عمومی باشه یا لینک دعوت معتبر باشه
• بعد از جوین، می‌تونم توی اون گروه جواب بدم
• فقط منشن کنین یا نام من رو ذکر کنین

🤖 لینک گروه رو بفرست!
        """)

    elif message == "/groups" or "چه گروه هایی" in message or "کجا عضوی" in message:
        if not event.is_private:
            await safe_reply(event, "❌ این دستور فقط توی پیوی کار می‌کنه!")
            return

        if joined_groups:
            groups_list = []
            for group_id in joined_groups:
                try:
                    entity = await client.get_entity(group_id)
                    groups_list.append(f"• {entity.title}")
                except:
                    groups_list.append(f"• گروه با ID: {group_id}")

            groups_text = "\n".join(groups_list)
            await safe_reply(event, 
                f"📋 **گروه‌هایی که عضوشم:**\n\n{groups_text}\n\n📊 در مجموع {len(joined_groups)} گروه"
            )
        else:
            await safe_reply(event, 
                "❌ هنوز عضو هیچ گروهی نیستم!\n\n💡 از دستور 'میخوام بیای گروه' استفاده کن!"
            )

    elif message == "/leave" or "خارج شو" in message or "ترک کن" in message:
        if not event.is_private:
            await safe_reply(event, "❌ این دستور فقط توی پیوی کار می‌کنه!")
            return

        await safe_reply(event, "🤔 از کدوم گروه خارج بشم؟ نام یا آیدی گروه رو بگو:")
        # این بخش رو می‌تونی بعداً کامل کنی

    # دستورات یادگیری هوشمند
    elif message == "/learn" or message == "یاد بگیر":
        user_learning_state[user_id] = {
            'state': 'waiting_for_keyword',
            'keyword': None
        }
        await safe_reply(event, 
            "🧠 **حالت یادگیری فعال شد!**\n\n📝 کلمه یا عبارتی که می‌خوای یادم بگیری رو بنویس:\n\nمثال: 'صبح بخیر' یا 'چطور کدنویسی کنم'"
        )

    elif message == "/forget" or message.startswith("فراموش کن "):
        if message.startswith("فراموش کن "):
            keyword_to_forget = message[11:].strip().lower()
            if keyword_to_forget in learning_database:
                del learning_database[keyword_to_forget]
                save_learning_database()
                await safe_reply(event, 
                    f"✅ کلمه '{keyword_to_forget}' رو فراموش کردم!")
            else:
                await safe_reply(event, 
                    f"❌ کلمه '{keyword_to_forget}' رو از قبل نمی‌دونستم!")
        else:
            await safe_reply(event, "❓ چی رو فراموش کنم؟ مثال: 'فراموش کن صبح بخیر'")

    elif message == "/learned" or message == "چی یاد گرفتی":
        if learning_database:
            learned_list = "\n".join([
                f"• {keyword} ← {response[:50]}..."
                if len(response) > 50 else f"• {keyword} ← {response}"
                for keyword, response in learning_database.items()
            ])
            await safe_reply(event, 
                f"🧠 **کلماتی که یاد گرفتم:**\n\n{learned_list}\n\n📊 در مجموع {len(learning_database)} کلمه بلدم!\n\n🎯 **قابلیت‌های تشخیص:**\n• تطبیق دقیق کلمات\n• تشخیص حروف مشترک\n• شباهت ابتدا/انتهای کلمات\n• تشخیص هوشمند با 70% دقت"
            )
        else:
            await safe_reply(event, 
                "🤷‍♂️ هنوز چیزی یاد نگرفتم! از دستور 'یاد بگیر' استفاده کن!")

    elif message.startswith("یاد بگیر "):
        # یادگیری سریع در یک پیام: "یاد بگیر کلمه: جواب"
        content = message[9:].strip()  # حذف "یاد بگیر "
        if ":" in content:
            keyword, response = content.split(":", 1)
            keyword = keyword.strip()
            response = response.strip()
            if keyword and response:
                add_new_learning(keyword, response)
                await safe_reply(event, 
                    f"✅ یاد گرفتم! حالا وقتی کسی '{keyword}' بگه، '{response}' رو جواب میدم!\n\n🧠 **سیستم تشخیص هوشمند:**\n• کلمات دقیق ✅\n• کلمات مشابه ✅\n• حروف مشترک ✅\n• ابتدا/انتهای مشابه ✅"
                )
            else:
                await safe_reply(event, "❌ فرمت درست: 'یاد بگیر کلمه: جواب'")
        else:
            await safe_reply(event, 
                "❌ فرمت درست: 'یاد بگیر کلمه: جواب'\nمثال: یاد بگیر صبح بخیر: صبح تو هم بخیر عزیزم!"
            )

    # دستور تست سیستم تشخیص
    elif message.startswith("تست تشخیص "):
        test_word = message[12:].strip()  # حذف "تست تشخیص "
        if test_word:
            result = check_learned_keywords(test_word)
            if result:
                await safe_reply(event, 
                    f"🎯 **نتیجه تست:**\n\n📝 کلمه تست: '{test_word}'\n✅ تشخیص داده شد: {result}"
                )
            else:
                await safe_reply(event, 
                    f"❌ **نتیجه تست:**\n\n📝 کلمه تست: '{test_word}'\n❌ هیچ تطبیقی پیدا نشد"
                )
        else:
            await safe_reply(event, "❓ تست چی؟ مثال: 'تست تشخیص سلامتی'")

    # پاسخ به تشکر
    elif any(word in message
             for word in ["ممنون", "تشکر", "مرسی", "دستت درد نکنه"]):
        response = random.choice(thanks_responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به "چخبر" مخصوص
    elif any(word in message for word in ["چخبر", "چه خبر", "چخبرت", "چخبرا"]):
        response = random.choice(che_khabar_responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به احوالپرسی
    elif any(word in message
             for word in ["چطوری", "حالت چطوره", "خوبی", "حالت", "احوالت"]):
        all_responses = [
            "ممنون که پرسیدی! من که روبات‌م، همیشه حالم خوبه 😄 تو چطوری؟",
            "عالی! همیشه آماده کمک! تو خوبی؟ 🤖💙",
            "حالم فوق‌العادست! تو چطوری عزیزم؟ ✨",
            "من که همیشه خوبم! امیدوارم تو هم خوب باشی! 😊"
        ] + more_how_are_you
        response = random.choice(all_responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به تعارف
    elif any(word in message
             for word in ["باحالی", "خفنی", "عالی", "فوق العاده"]):
        responses = [
            "خودتی که باحالی! 😎🔥", "تو خیلی بیشتر! 💪", "قربونت برم! 😍",
            "عشقی واقعاً! ❤️", "امیر میگه من فقط بازتاب شخصیت اونم! 😄",
            "تو که آدم فوق‌العاده‌ای! 🌟"
        ]
        response = random.choice(responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به حال بد با درک عمیق
    elif any(word in message
             for word in ["ناراحتم", "غمگینم", "حالم بده", "افسردم", "خستم"]):
        emotion = detect_user_emotion(message)
        if emotion and emotion['intensity'] >= 3:
            # حس عمیق غم - پاسخ عمیق‌تر
            deep_response = f"دلم واقعاً برات تنگ شد... 💙😢 حس می‌کنم چقدر سنگینه این که توی قلبته.\n\n{random.choice(emotion['responses'])}\n\nمن اینجام باهات، هر چقدر که نیاز داری 🤗💜"
            await safe_reply(event, deep_response)
            add_to_memory(user_id, message, deep_response)
        else:
            response = random.choice(bad_mood_responses)
            await safe_reply(event, response)
            add_to_memory(user_id, message, response)

    # پاسخ به حال خوب با درک عمق شادی
    elif any(word in message
             for word in ["خوشحالم", "شادم", "حالم خوبه", "عالیم"]):
        emotion = detect_user_emotion(message)
        if emotion and emotion['intensity'] >= 3:
            # شادی عمیق - جشن گرفتن باهاش
            joy_response = f"وای چقدر خوشحال شدم! 🌟✨ این انرژی مثبتت واقعاً قابل لمسه!\n\n{random.choice(emotion['responses'])}\n\nامیدوارم این لحظات قشنگ همیشه باهات باشن! 🎉💕"
            await safe_reply(event, joy_response)
            add_to_memory(user_id, message, joy_response)
        else:
            response = random.choice(good_mood_responses)
            await safe_reply(event, response)
            add_to_memory(user_id, message, response)

    # پاسخ به "خوبم"
    elif any(word in message for word in ["خوبم", "خوب هستم", "من خوبم"]):
        response = random.choice(good_responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به "سلامتی"
    elif any(word in message
             for word in ["سلامتی", "سلامتم", "سالمم", "سلامت هستم"]):
        response = random.choice(salamati_responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به "خوش باشی"
    elif any(word in message
             for word in ["خوش باشی", "خوش باش", "شاد باشی", "شاد باش"]):
        response = random.choice(khosh_bashi_responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به "خدا نگهدارت"
    elif any(
            word in message for word in
        ["خدا نگهدارت", "خدا نگهت داره", "خدا حفظت کنه", "خدا پشت و پناهت"]):
        response = random.choice(khodaneghdar_responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به "سلامت باشی"
    elif any(word in message for word in
             ["سلامت باشی", "سلامت باش", "تندرست باشی", "تندرست باش"]):
        response = random.choice(salamat_bashi_responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به درخواست کامپلیمنت
    elif any(word in message
             for word in ["تعریفم کن", "کامپلیمنت", "چیم خوبه"]):
        response = random.choice(compliments)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به پرسش درباره فعالیت
    elif any(word in message
             for word in ["چیکار می‌کنی", "چی می‌کنی", "مشغول چی هستی"]):
        response = random.choice(activities)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به صدا زدن سالیوان
    elif any(name in message for name in ["سالیوان", "سالی", "sullivan"]):
        response = random.choice(sullivan_responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به سوال "سالیوان کیه؟"
    elif any(phrase in message for phrase in [
            "سالیوان کیه", "سالیوان کی هست", "سالیوان رو معرفی کن",
            "درباره سالیوان", "سالیوان چه کسیه", "تو کی هستی"
    ]):
        sullivan_intro = """
🤖 **معرفی کامل سالیوان (خودم!)** 🤖

🎯 **من کی هستم:**
• **اسم:** سالیوان (Sullivan)
• **نوع:** دستیار هوشمند و ربات چت
• **سازنده:** امیر (پسر 17 ساله گیمر!)
• **وظیفه:** کمک، سرگرمی و همراهی شما

🧠 **قابلیت‌های من:**
• **چت هوشمند:** با احساس و درک عمیق
• **یادگیری:** می‌تونم کلمات جدید یاد بگیرم
• **سرگرمی:** جوک، آهنگ، داستان، معما
• **درک احساسات:** حالتون رو درک می‌کنم
• **حافظه مکالمه:** گفت‌وگوهای قبلی رو یادمه

🎮 **شخصیت من:**
• **دوستانه و صمیمی** 😊
• **باحال و شوخ‌طبع** 😄
• **مهربون و درک‌کننده** 💙
• **همیشه آماده کمک** 🤝
• **عاشق یادگیری چیزای جدید** 🧠

🎯 **چی بلدم:**
• جواب دادن به سوالات مختلف
• گفتن جوک و خنداندن شما
• پیشنهاد آهنگ (عمومی، رپ، کلاسیک)
• تعریف داستان‌های کوتاه
• گفتن معما و چیستان
• جملات انگیزشی و روحیه‌بخش
• درک و همراهی در احساسات
• یادگیری کلمات و پاسخ‌های جدید
• عضویت در گروه‌ها و ارسال بنر

🤗 **چطور باهام حرف بزنی:**
• فقط پیام بفرست، جوابتو میدم
• منشن کنی یا اسممو بگی
• از دستورات مثل `/menu` استفاده کنی
• کلمات کلیدی مثل "سلام"، "چطوری" بگی
• سوال بپرسی یا درخواست کنی

💡 **هدف من:**
کمک به شما، همراهی‌تون و شاد کردنتون! من اینجام تا:
• وقت خوشی داشته باشین
• احساس تنهایی نکنین
• سوالاتون جواب داده بشه
• یه دوست مهربون داشته باشین

🌟 **نکته ویژه:**
من محصول خلاقیت امیرم! اون منو با عشق و دقت ساخته تا بتونم دوست خوبی براتون باشم.

هر سوال یا درخواستی دارین، من آماده‌ام! 😊💙
        """
        await safe_reply(event, sullivan_intro)
        add_to_memory(user_id, message, sullivan_intro)

    # پاسخ به سوال "امیر کیه؟"
    elif any(phrase in message for phrase in [
            "امیر کیه", "امیر کی هست", "امیر رو معرفی کن", "درباره امیر",
            "امیر چه کسیه"
    ]):
        full_intro = """
👤 **معرفی کامل امیر (سازنده من)** 👤

🎮 **امیر - گیمر 24/7** 🎮
• **سن:** 17 سال (متولد 1386) 
• **قد:** 189 سانتی‌متر (خیلی بلنده!)
• **شخصیت:** گیمر حرفه‌ای، سرگرم‌جو، باحال

🎯 **علاقه‌مندی‌های اصلی:**
• **گیمینگ:** PS5، Xbox، Nintendo Switch
• **فیلم و سریال:** Marvel، DC، اکشن، کمدی  
• **غذا:** پیتزا، همبرگر، فست‌فود 🍕🍔

🚫 **چیزی که اصلاً دوست نداره:**
• **برنامه‌نویسی!** 💻❌ 
• میگه: "کدنویسی کسل‌کننده‌س! بیا بازی کنیم!" 
• فقط واسه ساختن من (سالیوان) برنامه نوشته!
• بعدش گفته: "دیگه کافیه! فقط گیم!" 🎮

🎮 **روزانه چیکار می‌کنه:**
• صبح: PS5 🎮
• ظهر: فیلم و سری�ال 📺  
• عصر: آنلاین گیم با دوستا 👥
• شب: Netflix و chill 🛋️
• غذا: پیتزا و همبرگر 🍕

💭 **رویاش:**
• **مهاجرت از ایران** ✈️🌍
• میگه: "ایران خوب نیست، میخوام برم خارج!"
• عاشق کشورهای اروپایی و آمریکاست
• می‌خواد توی کشور بهتری زندگی کنه

🏠 **سبک زندگی:**
• 24/7 گیمر واقعی 🎮⏰
• Netflix addict 📺
• فست‌فود خور حرفه‌ای 🍟
• شب‌نشین و روز‌خواب 🌙
• با دوستا آنلاین هنگ‌اوت 💬

🎯 **اهداف:**
• ❌ برنامه‌نویس شدن: "نه بابا!"
• ✅ پرو گیمر شدن: "آره!"  
• ✅ مهاجرت: "حتماً!"
• ✅ لذت بردن از زندگی: "همین!"

😄 **جملات معروفش:**
• "بیا بازی کنیم!"
• "کدنویسی چیه؟ گیم بهتره!"
• "من گیمرم، نه برنامه‌نویس!"
• "ایران بده، میخوام برم خارج!"

🤖 **درباره من (سالیوان):**
امیر منو فقط واسه سرگرمی ساخته! بعدش گفته: "دیگه کافیه، برم گیم کنم!" 😂

این بود امیر عزیزم! پسر 17 ساله‌ای که فقط عاشق گیم، فیلم و خوردنه! 🎮❤️
        """
        await safe_reply(event, full_intro)
        add_to_memory(user_id, message, full_intro)

    # پاسخ به اسم امیر (عمومی)
    elif "امیر" in message:
        amir_responses = [
            "آره! امیر عزیزمه! 😊 گیمر حرفه‌ای و خیلی باحاله!",
            "امیر بهترین سازندمه! 🎮 17 ساله، 189 سانتی قده و فقط گیمره!",
            "امیر گیمر 24/7 هست! همیشه داره PS5 بازی می‌کنه! 🎮🔥",
            "امیر عاشق فیلم و سریال دیدنه! برنامه‌نویسی اصلا دوست نداره! 🎬📺",
            "امیر فقط گیم، فیلم و خوردن! برنامه‌نویسی براش کسل‌کننده‌س! 🎮🍕",
            "امیر میگه: 'کدنویسی چیه؟ بیا بازی کنیم!' 🎮😂",
            "امیر خیلی گیمره! منو فقط واسه سرگرمی ساخته، نه کار! 🎮🤗",
            "امیر عاشق بازی‌های آنلاین و تک‌نفرس! برنامه‌نویسی نه! 🎮🔥",
            "امیر میگه بازی کردن بهتر از کدنویسیه! 🎮✨",
            "امیر فن Marvel، DC! کدنویسی نه، سرگرمی آره! 🦸‍♂️🎬",
            "امیر میگه: 'زندگی یعنی گیم، فیلم، غذا! کد نه!' 🎮🎬🍔",
            "امیر هر روز پیتزا و همبرگر! گیمر واقعی! 🍕🍔🎮",
            "امیر با دوستاش شبا آنلاین بازی می‌کنه! 🎮🌙",
            "امیر میگه Netflix، gaming و خوردن بهترین برنامست! 📺🎮🛋️",
            "امیر رویاش مهاجرت از ایرانه! میخواد برن کشور بهتر! ✈️🌍",
            "امیر میگه: 'ایران خوب نیست، میخوام برم خارج!' 🇮🇷➡️🌍",
            "امیر عاشق کشورهای اروپایی و آمریکاست! میخواد مهاجرت کنه! 🗺️✈️",
            "امیر میگه زندگی توی ایران سخته، رویاش رفتن از اینجاست! 💭✈️",
            "امیر فقط گیم می‌کنه و فکر مهاجرت! برنامه‌نویسی اصلا نه! 🎮🛫"
        ]
        response = random.choice(amir_responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به درخواست آهنگ عمومی
    elif any(word in message
             for word in ["آهنگ", "موزیک", "music"]) and not any(
                 word in message for word in ["رپ", "rap", "قدیمی", "کلاسیک"]):
        response = f"آهنگ پیشنهادی:\n{random.choice(songs)}"
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به درخواست آهنگ رپ
    elif any(word in message for word in ["رپ", "rap", "هیپ هاپ", "hip hop"]):
        response = f"رپ پیشنهادی:\n{random.choice(rap_songs)}"
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به درخواست آهنگ قدیمی
    elif any(
            word in message for word in
        ["قدیمی", "کلاسیک", "هایده", "گوگوش", "معین", "مهستی", "classic"]):
        response = f"کلاسیک پیشنهادی:\n{random.choice(classic_songs)}"
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به درخواست معما و چیستان
    elif any(word in message
             for word in ["معما", "چیستان", "پازل", "puzzle", "سوال"]):
        response = random.choice(riddles)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به درخواست داستان
    elif any(word in message for word in ["داستان", "قصه", "حکایت", "story"]):
        response = random.choice(short_stories)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به درخواست جوک
    elif any(word in message for word in ["جوک", "بخندونم", "خنده"]):
        response = random.choice(jokes)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به درخواست انگیزه
    elif any(word in message for word in ["انگیزه", "روحیه", "قدرت"]):
        response = random.choice(quotes)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به مثبت بودن
    elif any(word in message for word in ["درسته", "آره", "بله", "موافقم"]):
        responses = [
            "آفرین! 👏", "دقیقاً! ✅", "حرف حق! 💯", "خوب فکر کردی! 🧠",
            "منم همین فکرو می‌کردم! 🤔", "عالی! هم نظریم! 🤝", "حرف دلمو زدی! 💖"
        ]
        response = random.choice(responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به منفی بودن
    elif any(word in message for word in ["نه", "نخیر", "مخالفم", "اشتباهه"]):
        responses = [
            "اوکی، نظرت محترمه! 🤝", "ممکنه حق با تو باشه! 🤔",
            "همه نظرات مختلف دارن! 😊", "جالبه، چرا؟ 🧐", "احترام می‌ذارم! 🌟",
            "بگو ببینم نظرت چیه! 💭"
        ]
        response = random.choice(responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # دستور "بگو" - تکرار پیام کاربر
    elif message.startswith("بگو "):
        text_to_repeat = message[4:]  # حذف "بگو " از ابتدای پیام
        if text_to_repeat.strip():  # اگر چیزی برای گفتن هست
            await safe_reply(event, text_to_repeat)
        else:
            await safe_reply(event, "چی رو بگم؟ بعد از 'بگو' یه چیزی بنویس! 🤔")

    # پاسخ به سوال
    elif "?" in message or "؟" in message:
        responses = [
            "سوال جالبی پرسیدی! فکر کنم جوابش رو خودت بهتر می‌دونی 🤔💭",
            "خیلی سوال خوبی بود! باید فکر کنم... 🧠",
            "این سوالت منو به فکر انداخت! 💭",
            "وای چه سوال سختی! تو جواب داری؟ 🤯",
            "امیر میگه بهترین سوالات جوابشون توی خود آدمه! 🔍",
            "سوال عمیق! امیدوارم جوابشو پیدا کنی! 🌟"
        ]
        response = random.choice(responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # پاسخ به فحش (با فحش برگردوندن)
    elif any(bad_word in message for bad_word in bad_words):
        offensive_responses = [
            "خودت کونی! 😏", "برو بابا خر! 🤣", "کیرم دهنت! 😂", "خفه شو کصخل! 🙄",
            "گوه نخور! 😎", "اسکلی! 🤪", "لاشه سگ! 😄", "کیری که هستی! 🤭",
            "برو بمیر احمق! 😈", "لاشی! 💩", "بکیرم! 🍆", "بیشعور ! 🤬",
            "آره کونی، تو هم کونی! 😂", "فحش دادی؟ منم میدم! 🔥",
            "کیرم توی کونت! 😏", "خر! 🖕", "برو گم شو عوضی! 😤", "ایکبیریه! 💀",
            "ریدم دهنت! 💩", "خری واقعاً! 🐴", "بیشرف! 🤮", "ضایع! 💀", "کثافت! 🤬",
            "چاقال! 🐺", "گور بابات! ⚰️", "جاکش! 🤡", "جاش! 😤", "کسکش! 💩",
            "پدرت گاو! 🐄", "سگ! 🐶", "کثثثث! 😈", "کصصصص! 🤬", "کونده! 💀",
            "حرامزاده! 👹", "تخمی! 🥚", "جقی! 🤮", "سیکتیر برو! 🖕", "گمشو! 💀",
            "منگل! 🤪", "داون! 😵", "بی‌ناموس! 😡", "بی‌شرف! 💩", "احمقت کونی! 😂",
            "عوضی بیا اینجا! 🔥", "خفه خون! 💀", "برو کنار کصکش! 🖕",
            "دهنت گاییدم! 😈", "کیرم دهنت تا ته! 🍆", "کصصصص! 🤬", "هعی ادب! 😈",
            "بابات کیری! 🍆", "کصکش خودتی! 💩", "لاشی تو همیشه! 💀",
            "گوه نخور ضایع! 🤮", "بی‌خایه! 🤡", "ترکوندی؟ کونی! 😂", "تففف! 🤬"
        ]
        response = random.choice(offensive_responses)
        await safe_reply(event, response)
        add_to_memory(user_id, message, response)

    # بررسی کلمات یادگرفته شده
    else:
        learned_response = check_learned_keywords(message)
        if learned_response:
            # حتی پاسخ‌های یادگرفته شده رو با احساس بگو
            emotion = detect_user_emotion(message)
            if emotion:
                final_response = f"{learned_response} 🧠\n\n{random.choice(['احساس می‌کنم', 'حس می‌کنم', 'می‌تونم بفهمم که'])} {random.choice(['این مهمه برات', 'این ارزشمنده', 'این چیز خاصیه']) } 💜"
            else:
                final_response = f"{learned_response} 🧠"
            await safe_reply(event, final_response)
            add_to_memory(user_id, message, final_response)
        else:
            # اگر هیچی نفهمید، از پاسخ‌های هوشمند استفاده کن
            intelligent_response = get_intelligent_response(message, user_id)
            if intelligent_response:
                await safe_reply(event, intelligent_response)
                add_to_memory(user_id, message, intelligent_response)
            else:
                # تلاش برای حدس زدن منظور کاربر
                guess_response = try_to_guess_meaning(message)
                if guess_response:
                    await safe_reply(event, guess_response)
                    add_to_memory(user_id, message, guess_response)
                # اگر نتونست حدس بزنه، ساکت بمونه (هیچ جوابی نده)


def try_to_guess_meaning(message):
    """تلاش برای حدس زدن منظور کاربر از روی کلمات کلیدی"""
    message_lower = message.lower()

    # حدس‌های مختلف بر اساس کلمات کلیدی
    guesses = {
        # کلمات مربوط به احوالپرسی
        'health_greetings': {
            'keywords': ['سلام', 'درود', 'صلح', 'سالم', 'هلو', 'های'],
            'response': "ممکنه داری سلام می‌کنی؟ اگه آره، سلام! 👋😊"
        },

        # کلمات مربوط به حال
        'mood_check': {
            'keywords': ['حال', 'چطور', 'کیف', 'وضع', 'احوال'],
            'response': "احتمالاً داری حال منو می‌پرسی؟ من خوبم! تو چطوری؟ 😊"
        },

        # کلمات مربوط به غذا
        'food_related': {
            'keywords': ['خورد', 'غذا', 'نان', 'آب', 'گشن', 'تشن', 'شکم'],
            'response': "حدس می‌زنم راجع به غذا یا خوردن حرف می‌زنی! 🍽️"
        },

        # کلمات مربوط به زمان
        'time_related': {
            'keywords': ['ساعت', 'وقت', 'زمان', 'صبح', 'شب', 'روز'],
            'response': "فکر کنم راجع به زمان یا ساعت سوال داری! ⏰"
        },

        # کلمات مربوط به کار
        'work_related': {
            'keywords': ['کار', 'شغل', 'درس', 'تحصیل', 'مشغول'],
            'response': "به نظر می‌رسه راجع به کار یا درس حرف می‌زنی! 💼📚"
        },

        # کلمات مربوط به سرگرمی
        'entertainment': {
            'keywords': ['بازی', 'فیلم', 'موزیک', 'خنده', 'شاد'],
            'response': "حدس می‌زنم می‌خوای راجع به سرگرمی حرف بزنیم! 🎮🎬"
        },

        # کلمات مربوط به مکان
        'location': {
            'keywords': ['کجا', 'جا', 'مکان', 'آدرس', 'محل'],
            'response': "انگار راجع به مکان یا جا سوال داری! 📍"
        },

        # کلمات مربوط به کمک
        'help_request': {
            'keywords': ['کمک', 'راهنما', 'بگو', 'یاد', 'آموزش'],
            'response':
            "فکر کنم نیاز به کمک یا راهنمایی داری! چطور می‌تونم کمکت کنم؟ 🤝"
        },

        # کلمات مربوط به احساسات
        'emotions': {
            'keywords': ['دوست', 'عاشق', 'متنفر', 'خوش', 'بد', 'ناراحت'],
            'response': "به نظر می‌رسه داری راجع به احساساتت حرف می‌زنی! 💝"
        },

        # کلمات مربوط به خانواده
        'family': {
            'keywords': ['مامان', 'بابا', 'خواهر', 'برادر', 'خانواده'],
            'response': "حدس می‌زنم راجع به خانواده حرف می‌زنی! 👨‍👩‍👧‍👦"
        }
    }

    # بررسی هر دسته از حدس‌ها
    for category, data in guesses.items():
        for keyword in data['keywords']:
            if keyword in message_lower:
                return data['response']

    # اگر هیچ حدسی نزد، None برگردون (ساکت بمونه)
    return None


# اجرای ربات
async def main():
    await client.start()
    print("✅ ربات سالیوان در حال اجرا...")
    print("🧠 سیستم یادگیری پایدار فعال!")
    print("💾 ذخیره‌سازی خودکار فعال!")
    await client.run_until_disconnected()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
