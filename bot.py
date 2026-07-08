import logging
import os
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token and Owner ID
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8264683686:AAEGr8mNpsI4Wm_GLMZYaurjaEomIKAb1u4')
OWNER_TELEGRAM_ID = 5911159063  # Thiha Tun's Telegram ID
CHANNEL_USERNAME = "@ThihaDigitalProductService"

# Myanmar Timezone (UTC+6:30)
MYANMAR_TZ = datetime.timezone(datetime.timedelta(hours=6, minutes=30))

# States for ConversationHandler
SELECTING_PRODUCT, SELECTING_OPTION, WAITING_FOR_PAYMENT_PROOF = range(3)

# Product and Prices
PRODUCTS = {
    'capcut_pro': {
        'name_mm': '🎬 CapCut Pro',
        'options': {
            'capcut_share': {'name_mm': '📱 1 Device (Share)', 'price_mm': '10,000 MMK'},
            'capcut_1_private': {'name_mm': '🔒 1 Device Private Acc', 'price_mm': '17,000 MMK', 'note_mm': '✅ ရောင်းသူမှ Gmail ပေးပါမည်။'},
            'capcut_2_private': {'name_mm': '💻 2 Device (Phone+PC) Private', 'price_mm': '25,000 MMK', 'note_mm': '✅ ရောင်းသူမှ Gmail ပေးပါမည်။'},
        }
    },
    'tiktok_services': {
        'name_mm': '🎵 TikTok Services',
        'options': {
            'tiktok_like': {'name_mm': '❤️ Like 1K', 'price_mm': '6,000 MMK'},
            'tiktok_view': {'name_mm': '👁️ View 1K', 'price_mm': '2,000 MMK'},
            'tiktok_save': {'name_mm': '💾 Save 1K', 'price_mm': '1,000 MMK'},
            'tiktok_follower': {'name_mm': '👥 Follower 1K (လူအစစ်)', 'price_mm': '23,000 MMK'},
            'tiktok_share': {'name_mm': '🔁 Share 1K', 'price_mm': '700 MMK'},
        }
    },
    'alight_motion': {
        'name_mm': '🌟 Alight Motion Premium',
        'options': {
            'alight_1year': {'name_mm': '💎 1 Year', 'price_mm': '15,000 MMK'},
        }
    },
    'canva_pro': {
        'name_mm': '🎨 Canva Pro Lifetime',
        'options': {
            'canva_1year': {'name_mm': '💎 1 Year', 'price_mm': '15,000 MMK'},
        }
    },
    'gemini_ai': {
        'name_mm': '🤖 Gemini AI',
        'options': {
            'gemini_1year': {'name_mm': '💎 1 Year', 'price_mm': '40,000 MMK'},
        }
    },
    'tiktok_boosting': {
        'name_mm': '🚀 TikTok Boosting Service',
        'options': {
            'boost_3': {'name_mm': '🟢 3$ Package', 'price_mm': '22,000 MMK'},
            'boost_4': {'name_mm': '🟢 4$ Package', 'price_mm': '29,500 MMK'},
            'boost_5': {'name_mm': '🟡 5$ Package', 'price_mm': '36,500 MMK'},
            'boost_6': {'name_mm': '🟡 6$ Package', 'price_mm': '44,000 MMK'},
            'boost_7': {'name_mm': '🟠 7$ Package', 'price_mm': '51,500 MMK'},
            'boost_8': {'name_mm': '🟠 8$ Package', 'price_mm': '59,000 MMK'},
            'boost_9': {'name_mm': '🔴 9$ Package', 'price_mm': '66,000 MMK'},
            'boost_10': {'name_mm': '🔴 10$ Package', 'price_mm': '73,000 MMK'},
        }
    },
    'telegram_premium': {
        'name_mm': '⭐ Telegram Premium',
        'options': {
            'tg_3months': {'name_mm': '💎 3 Months', 'price_mm': '60,000 MMK'},
            'tg_6months': {'name_mm': '🔥 6 Months', 'price_mm': '89,000 MMK'},
            'tg_1year': {'name_mm': '👑 1 Year', 'price_mm': '147,000 MMK'},
        }
    },
    'tiktok_coin': {
        'name_mm': '💰 TikTok Coin Service',
        'options': {
            'coin_300': {'name_mm': '🪨 300 Coins', 'price_mm': '17,200 MMK'},
            'coin_500': {'name_mm': '💴 500 Coins', 'price_mm': '28,600 MMK'},
            'coin_1000': {'name_mm': '💵 1,000 Coins', 'price_mm': '54,800 MMK'},
            'coin_5000': {'name_mm': '💶 5,000 Coins', 'price_mm': '266,000 MMK'},
            'coin_10000': {'name_mm': '💎 10,000 Coins', 'price_mm': '522,500 MMK'},
        }
    },
}

# Payment Info
PAYMENT_INFO_MM = (
    "💳 ငွေပေးချေရန်:\n\n"
    "KBZPay: 09943257604 (Thiha Tun)\n"
    "UAB Pay: 09943257604 (Thiha Tun)\n\n"
    "📸 ငွေလွှဲပြီးပါက Screenshot ပို့ပေးပါ။"
)

# ============================================
# DAILY AUTO-POST CONTENT (30 Days)
# Each entry: {'caption': '...', 'image': 'filename or None'}
# image=None means text-only post
# ============================================
DAILY_POSTS = [
    # Day 1 - Telegram Premium မိတ်ဆက်
    {
        'caption': "Telegram ကို အရှိန်အဟုန်အပြည့်နဲ့ Premium ဆန်ဆန် သုံးကြမယ် ✨\n\nTelegram ကို အလုပ်အတွက်ပဲဖြစ်ဖြစ်၊ ဖျော်ဖြေရေးအတွက်ပဲဖြစ်ဖြစ် နေ့တိုင်းသုံးနေရသူလား? ဒါဆိုရင် ပိုမိုမြန်ဆန်တဲ့ Download Speed၊ ပိုကြီးမားတဲ့ File Sharing နဲ့ စိတ်ဝင်စားစရာ Feature ပေါင်းများစွာ ပါဝင်တဲ့ Telegram Premium ကို အသုံးပြုဖို့ တိုက်တွန်းပါရစေ။\n\nThiha Digital Product Service မှာ အသက်သာဆုံးနှုန်းထားတွေနဲ့ စိတ်ချလက်ချ ဝယ်ယူရရှိနိုင်ပါပြီဗျာ။ 🥰\n\n💰 စျေးနှုန်းများ:\n3 Months ── 60,000 MMK\n6 Months ── 89,000 MMK\n1 Year ── 147,000 MMK\n\n🛡️ ဝန်ဆောင်မှုအာမခံချက်:\n✅ Gift Link ဖြင့် တရားဝင် မြှင့်တင်ပေးခြင်း\n✅ Visa Card ဖြင့် ဝယ်ပေးတာဖြစ်ပါတယ်\n✅ Account 100% အာမခံ\n\n📲 အခုပဲ မှာယူရန်: @ThihaTun4055\n@ThihaDigitalProductService",
        'image': 'price_telegram_premium.png'
    },
    # Day 2 - Telegram Premium Features ပညာပေး
    {
        'caption': "💎 Telegram Premium ရဲ့ ထူးခြားတဲ့ Features များ\n\n⚡ 4GB အထိ ဖိုင်ပို့နိုင်ခြင်း\n⚡ Download Speed 2 ဆ မြန်ဆန်ခြင်း\n⚡ Sticker & Emoji Premium Pack များ\n⚡ Chat Folders ပိုမိုများပြားခြင်း\n⚡ Voice-to-Text Transcription\n⚡ No Ads (ကြော်ငြာကင်းစင်)\n\nဒီ Features တွေအားလုံးကို တစ်နှစ်လုံးမှ 147,000 ကျပ်ထဲနဲ့ ရယူနိုင်ပါပြီ။\n\n📲 မှာယူရန်: @ThihaTun4055\n@ThihaDigitalProductService",
        'image': 'price_telegram_premium.png'
    },
    # Day 3 - CapCut Pro (ခဏရပ်ထား - ပစ္စည်းပျက်နေ)
    None,
    # Day 4 - CapCut Pro Tips (ခဏရပ်ထား - ပစ္စည်းပျက်နေ)
    None,
    # Day 5 - TikTok Services မိတ်ဆက်
    {
        'caption': "🎵 TikTok မှာ နာမည်ကြီးချင်လား? 📈\n\n@ThihaDigitalProductService ရဲ့ TikTok Services တွေက သင့်ကို ကူညီပေးပါလိမ့်မယ်။\n\n❤️ Like 1K ── 6,000 MMK\n👁️ View 1K ── 2,000 MMK\n💾 Save 1K ── 1,000 MMK\n👥 Follower 1K (လူအစစ်) ── 23,000 MMK\n🔁 Share 1K ── 700 MMK\n\n✅ မြန်ဆန်သော ဝန်ဆောင်မှု\n✅ လူအစစ် Engagement\n\nသင့် TikTok Account ကို အခုပဲ မြှင့်တင်လိုက်ပါ 🚀\n📲 @ThihaTun4055",
        'image': 'price_tiktok_services.png'
    },
    # Day 6 - TikTok Tips
    {
        'caption': "📈 TikTok Video တွေ Foryou တက်ဖို့ ဘာတွေလုပ်သင့်လဲ? 🤔\n\n✅ Trending Hashtag တွေ အသုံးပြုပါ\n✅ Trending Music တွေ ထည့်ပါ\n✅ Hook ကောင်းကောင်း ထည့်ပါ\n✅ Engagement မြှင့်တင်ပါ\n✅ Post Time ကို ညနေ 6-9 နာရီ ထားပါ\n\nEngagement မြှင့်တင်ဖို့ 👉 @ThihaDigitalBot\n\n#TikTokTips #ForyouPage",
        'image': 'price_tiktok_services.png'
    },
    # Day 7 - TikTok Services Special Offer
    {
        'caption': "🎉 ဒီတစ်ပတ်အတွက် အထူးအစီအစဉ်!\n\nTikTok Services တွေကို Package အလိုက် ဝယ်ယူပြီး ပိုမိုသက်သာစွာ သင့် TikTok ကို မြှင့်တင်လိုက်ပါ။ 🎁\n\nLike + View + Save ── Package ဈေးနဲ့ ရနိုင်ပါတယ်!\n\nအသေးစိတ်ကို 👉 @ThihaDigitalBot မှာ မေးမြန်းနိုင်ပါတယ်။\n\n#TikTokPromotion #SpecialOffer",
        'image': 'price_tiktok_services.png'
    },
    # Day 8 - TikTok Coins Top-Up
    {
        'caption': "TikTok Live မှာ Coin ကြဲမလား? အကောင့်တိုက်ရိုက် အမြန်ဆုံး Top-Up လုပ်မလား? ⚡🪙\n\nTikTok Creator တွေအတွက် မရှိမဖြစ်လိုအပ်တဲ့ TikTok Coins တွေကို အသက်သာဆုံး စျေးနှုန်း၊ အမြန်ဆုံး စနစ်နဲ့ ဖြည့်သွင်းပေးနေပါပြီ။\n\n⚡ Coins စျေးနှုန်းများ:\n🪨 300 Coins ── 17,200 MMK\n💴 500 Coins ── 28,600 MMK\n💵 1,000 Coins ── 54,800 MMK\n💶 5,000 Coins ── 266,000 MMK\n💎 10,000 Coins ── 522,500 MMK\n\n🔒 ဝန်ဆောင်မှု:\n✅ ဝယ်ယူသူ အကောင့်တိုက်ရိုက် Login ဝင်၍ ဝယ်ယူပေးခြင်း\n✅ ၁၀၀% အကောင့် လုံခြုံမှု အာမခံခြင်း\n✅ ကြာမြင့်ချိန် ၁၅ မိနစ်သာ!\n\n📲 ချက်ချင်း အားဖြည့်ရန်: @ThihaTun4055",
        'image': 'price_tiktok_coin.png'
    },
    # Day 9 - TikTok Coin ပညာပေး
    {
        'caption': "💡 TikTok Live လွှင့်ရင် Coin ရှိဖို့ ဘာလို့ လိုတာလဲ?\n\nတခြား Live လွှင့်တဲ့သူတွေကို Coin ပြန်ကြဲပေးခြင်း၊ မိတ်ဆွေဖွဲ့ခြင်းက သင့်အကောင့်ရဲ့ Traffic (လူမြင်နှုန်း) ကို တက်စေပါတယ်။\n\nCoin ကြဲလေ → Live Rank တက်လေ → လူမြင်များလေ → Follower တိုးလေ 🚀\n\nTikTok Coins အားဖြည့်ရန်: @ThihaTun4055\n@ThihaDigitalProductService",
        'image': 'price_tiktok_coin.png'
    },
    # Day 10 - Alight Motion Premium
    {
        'caption': "🌟 Alight Motion Premium ဖြင့် သင့်ရဲ့ Creative Ideas တွေကို အသက်သွင်းလိုက်ပါ ✨\n\nMotion Graphics နဲ့ Video Editing အတွက် အကောင်းဆုံး App! 🎬\n\n💎 1 Year ── 15,000 MMK\n\nPremium Features:\n✅ All Effects Unlocked\n✅ No Watermark\n✅ Premium Fonts & Stickers\n✅ Export Quality အမြင့်ဆုံး\n\nအခုပဲ ဝယ်ယူပြီး သင့်ရဲ့ ဖန်တီးမှုတွေကို စတင်လိုက်ပါ 🚀\n📲 @ThihaTun4055",
        'image': 'price_alight_motion.png'
    },
    # Day 11 - Canva Pro
    {
        'caption': "🎨 Canva Pro Lifetime ဖြင့် ပရော်ဖက်ရှင်နယ် Design တွေကို အလွယ်တကူ ဖန်တီးလိုက်ပါ 🖌️\n\nGraphic Design အတွက် အကောင်းဆုံး Tool!\n\n💎 1 Year ── 15,000 MMK\n\nCanva Pro Features:\n✅ Premium Templates 100M+\n✅ Background Remover\n✅ Magic Resize\n✅ Brand Kit\n✅ 100GB Cloud Storage\n\nတစ်နှစ်လုံးမှ ၁၅,၀၀၀ ကျပ်ထဲ! 🚀\n📲 @ThihaTun4055",
        'image': 'price_canva_pro.png'
    },
    # Day 12 - Canva Pro Tips
    {
        'caption': "✨ Canva Pro ရဲ့ Magic Resize Feature ကို သိပြီးပြီလား?\n\nDesign တစ်ခုကို Facebook, Instagram, TikTok, YouTube Thumbnail အကုန်လုံးအတွက် တစ်ချက်နှိပ်ရုံနဲ့ Size ပြောင်းလို့ရပါတယ်။\n\nDesigner ငှားစရာမလို - Canva Pro နဲ့ ကိုယ်တိုင်လုပ်လိုက်ပါ! 💡\n\nCanva Pro ရယူရန် 👉 @ThihaDigitalBot\n\n#CanvaProTips #GraphicDesign",
        'image': 'price_canva_pro.png'
    },
    # Day 13 - Gemini AI
    {
        'caption': "🤖 Google ရဲ့ အဆင့်မြင့်ဆုံးနည်းပညာ Gemini AI ကို Premium Plan နဲ့ အသုံးပြုကြမယ် 🧠🚀\n\nသင့်ရဲ့ နေ့စဥ်အလုပ်တွေ၊ Content ဖန်တီးမှုတွေကို စက္ကန့်ပိုင်းအတွင်း ဖြေရှင်းပေးမယ့် စမတ်ကျတဲ့ လုပ်ဖော်ကိုင်ဖက်!\n\n✨ Gemini AI Advanced:\n✅ AI Chat & Assistant\n✅ Writing & Content Creation\n✅ Coding & Debugging\n✅ Research & Data Analysis\n\n💰 1 Year ── 40,000 MMK သာ!\n\n📲 အခုပဲ မှာယူရန်: @ThihaTun4055\n@ThihaDigitalProductService",
        'image': 'price_gemini_ai.png'
    },
    # Day 14 - Gemini AI ပညာပေး
    {
        'caption': "💡 Gemini AI ကို ဘယ်လိုသုံးမလဲ?\n\nContent Creator တွေအတွက်:\n\"ကျွန်တော့်ရဲ့ Digital Product ဆိုင်အတွက် ဆွဲဆောင်မှုရှိတဲ့ စာသား ၃ ခု ရေးပေးပါ\" လို့ မြန်မာလို ရိုက်ထည့်လိုက်ရုံနဲ့ အသင့်သုံး Copywriting တွေ ရလာမှာပါ။\n\nတစ်နှစ်လုံးမှ ၄၀,၀၀၀ ကျပ် = တစ်ရက်ကို ၁၀၀ ကျပ်ကျော်ပဲ ကျသင့်မှာပါ 🥰\n\n📲 @ThihaTun4055\n@ThihaDigitalProductService",
        'image': 'price_gemini_ai.png'
    },
    # Day 15 - TikTok Boosting Service
    {
        'caption': "🚀 TikTok မှာ သင့်ဗီဒီယိုတွေကို ပိုမိုလူသိများအောင် Boost လုပ်ချင်လား?\n\n@ThihaDigitalProductService ရဲ့ TikTok Boosting Services!\n\n🟢 3$ ── 22,000 MMK\n🟢 4$ ── 29,500 MMK\n🟡 5$ ── 36,500 MMK\n🟡 6$ ── 44,000 MMK\n🟠 7$ ── 51,500 MMK\n🟠 8$ ── 59,000 MMK\n🔴 9$ ── 66,000 MMK\n🔴 10$ ── 73,000 MMK\n\n✅ Real Engagement\n✅ Target Audience ရွေးချယ်နိုင်\n✅ 24 နာရီအတွင်း Results\n\nသင့် TikTok ကို အခုပဲ မြှင့်တင်လိုက်ပါ 📈\n📲 @ThihaTun4055",
        'image': 'price_tiktok_boosting.png'
    },
    # Day 16 - TikTok Boosting ပညာပေး
    {
        'caption': "📊 TikTok Boosting ဘာကြောင့် လိုအပ်တာလဲ?\n\nသင့် Video ကို ပထမ 1 နာရီအတွင်း Engagement မရရင် Algorithm က ဖျက်ချလိုက်ပါတယ်။\n\nBoosting လုပ်ရင်:\n✅ Video ကို Target Audience ဆီ တိုက်ရိုက်ရောက်\n✅ Engagement Rate မြင့်တက်\n✅ Foryou Page တက်နိုင်ခြေ ပိုများ\n✅ Follower Organic တိုးလာ\n\n3$ ကနေ စတင်ပြီး Boost လုပ်နိုင်ပါပြီ!\n📲 @ThihaTun4055",
        'image': 'price_tiktok_boosting.png'
    },
    # Day 17 - Telegram Premium Reminder
    {
        'caption': "⭐ စိတ်အနှောင့်အယှက်မရှိ အလုပ်လုပ်နိုင်ဖို့ Telegram Premium!\n\nကြော်ငြာတွေ မမြင်ရတော့ဘူး 🚫\nFile Size 4GB အထိ ပို့နိုင် 📁\nDownload Speed 2x မြန် ⚡\nPremium Stickers & Emoji 🎨\n\n💰 စျေးနှုန်းများ:\n3 Months ── 60,000 MMK\n6 Months ── 89,000 MMK\n1 Year ── 147,000 MMK\n\nGift Link + Visa Card + 100% အာမခံ ✅\n\n📲 @ThihaTun4055\n@ThihaDigitalProductService",
        'image': 'price_telegram_premium.png'
    },
    # Day 18 - Customer Testimonial
    {
        'caption': "🙏 Customer Feedback\n\n\"Telegram Premium ကို @ThihaDigitalProductService ကနေ ဝယ်ယူပြီးနောက် Download Speed အရမ်းမြန်လာတယ်။ ကြော်ငြာလည်း မမြင်ရတော့ဘူး။ ဝန်ဆောင်မှုလည်း မြန်ဆန်တယ်!\"\n\n- ကျေနပ်အားရနေတဲ့ Customer တစ်ဦးရဲ့ Feedback ပါ။\n\n✅ Gift Link ဖြင့် 100% Safe\n✅ 15 မိနစ်အတွင်း ရရှိ\n\nသင်လည်း စမ်းသုံးကြည့်ဖို့ ဖိတ်ခေါ်ပါတယ် 👉 @ThihaDigitalBot\n\n#CustomerReview #TelegramPremium",
        'image': 'price_telegram_premium.png'
    },
    # Day 19 - FAQ Post
    {
        'caption': "🤔 Digital Product တွေ ဝယ်ယူရာမှာ မေးလေ့ရှိတဲ့ မေးခွန်းများ (FAQ)\n\n❓ ဘယ်လိုဝယ်ယူရမလဲ?\n➡️ @ThihaDigitalBot မှာ /start နှိပ်ပြီး ရွေးချယ်ပါ\n\n❓ ငွေပေးချေမှု ဘယ်လိုလုပ်ရမလဲ?\n➡️ KBZPay / UAB Pay (09943257604) ဖြင့် လွှဲပြီး SS ပို့ပါ\n\n❓ ဝယ်ယူပြီးရင် ဘယ်လောက်ကြာရင် ရမလဲ?\n➡️ ၁၅ မိနစ်အတွင်း ရပါတယ်\n\n❓ အာမခံ ရှိလား?\n➡️ 100% အာမခံပါတယ်\n\n📲 @ThihaTun4055\n#FAQ #DigitalProducts",
        'image': None
    },
    # Day 20 - CapCut Pro vs Alight Motion (ခဏရပ်ထား - CapCut ပစ္စည်းပျက်နေ)
    None,
    # Day 21 - Customer Testimonial (General)
    {
        'caption': "🙏 Customer Feedback\n\n\"@ThihaDigitalProductService ရဲ့ ဝန်ဆောင်မှုက အရမ်းကောင်းတယ်။ မြန်ဆန်ပြီး ယုံကြည်စိတ်ချရတယ်။ TikTok Coin ဝယ်တာ ၁၅ မိနစ်ပဲ ကြာတယ်!\"\n\n- ကျေနပ်အားရနေတဲ့ Customer တစ်ဦးရဲ့ Feedback ပါ။\n\n🛡️ 100% အာမခံ | ⚡ 15 မိနစ်အတွင်း\n\nသင်လည်း စမ်းသုံးကြည့်ဖို့ ဖိတ်ခေါ်ပါတယ် 👉 @ThihaDigitalBot\n\n#CustomerReview #ThihaDigital",
        'image': None
    },
    # Day 22 - Bundle Deal
    {
        'caption': "🎉 အထူး Bundle Deal!\n\nCapCut Pro + Canva Pro ── Special Package Price!\n\n🎬 CapCut Pro (Video Editing)\n🎨 Canva Pro (Graphic Design)\n\nContent Creator တွေအတွက် မရှိမဖြစ် Tools နှစ်ခုကို Package ဈေးနဲ့ ရယူလိုက်ပါ! 🎁\n\nအသေးစိတ် 👉 @ThihaDigitalBot\n📲 @ThihaTun4055\n\n#BundleDeal #SpecialOffer",
        'image': None
    },
    # Day 23 - TikTok Coin Reminder
    {
        'caption': "💰 TikTok Coin တွေကို အသက်သာဆုံး ဈေးနှုန်းနဲ့ ဝယ်ယူလိုက်ပါ!\n\nသင့်အကြိုက်ဆုံး Creator တွေကို Support လုပ်ဖို့ အကောင်းဆုံးအခွင့်အရေး! 💖\n\n🪨 300 Coins ── 17,200 MMK\n💴 500 Coins ── 28,600 MMK\n💵 1,000 Coins ── 54,800 MMK\n💶 5,000 Coins ── 266,000 MMK\n💎 10,000 Coins ── 522,500 MMK\n\n✅ Account 100% အာမခံ\n✅ 15 မိနစ်အတွင်း ပြီးစီး\n\n📲 @ThihaTun4055",
        'image': 'price_tiktok_coin.png'
    },
    # Day 24 - Canva Pro အမြန်ရောင်းချမှု
    {
        'caption': "👑 တစ်နှစ်လုံးမှ ၁၅,၀၀၀ ကျပ်ထဲနဲ့ Canva Pro အသုံးပြုခွင့်!\n\nပိုက်ဆံအများကြီး အကုန်ခံပြီး Designer ငှားစရာမလိုဘဲ အမိုက်စား ဒီဇိုင်းတွေကို ကိုယ်တိုင် ဖန်တီးလိုက်ပါ။\n\n✅ Official Account\n✅ သုံးနေရင်း ပျက်သွားမှာ ပူစရာမလို\n✅ 24/7 Support\n\n📲 စာရင်းပေးသွင်းရန်: @ThihaTun4055\n@ThihaDigitalProductService",
        'image': 'price_canva_pro.png'
    },
    # Day 25 - TikTok Boosting Reminder
    {
        'caption': "🚀 ရောင်းအားတက်ချင်တဲ့ စျေးသည်များအတွက် အထိရောက်ဆုံး TikTok Boosting!\n\n3$ Package ကနေ စတင်ပြီး သင့်ဗီဒီယိုတွေကို Target Customer တွေဆီ အရောက်တွန်းပို့လိုက်ပါ။\n\n📈 Results:\n• Follower တိုးတက်\n• Likes & Views မြင့်တက်\n• Sales ပိုရ\n\nလုပ်ငန်းပိုမို အောင်မြင်လာပါစေ!\n📲 @ThihaTun4055",
        'image': 'price_tiktok_boosting.png'
    },
    # Day 26 - CapCut Pro Deep Dive (ခဏရပ်ထား - ပစ္စည်းပျက်နေ)
    None,
    # Day 27 - Customer Testimonial (TikTok)
    {
        'caption': "🙏 Customer Feedback\n\n\"@ThihaDigitalProductService ရဲ့ TikTok Services တွေက ကျွန်တော့်ရဲ့ Follower တွေကို အများကြီး တိုးစေခဲ့တယ်။ Boosting လုပ်ပြီး ၂ ရက်အတွင်း Follower 500 တိုးလာတယ်!\"\n\n- ကျေနပ်အားရနေတဲ့ Customer တစ်ဦးရဲ့ Feedback ပါ။\n\nသင်လည်း စမ်းသုံးကြည့်ဖို့ ဖိတ်ခေါ်ပါတယ် 👉 @ThihaDigitalBot\n\n#CustomerReview #TikTokGrowth",
        'image': 'price_tiktok_services.png'
    },
    # Day 28 - Flash Sale Gemini AI
    {
        'caption': "⚡ Flash Sale! ဒီနေ့တစ်ရက်တည်းသာ!\n\n🤖 Gemini AI 1 Year ── 40,000 MMK\n\nGoogle ရဲ့ အဆင့်မြင့်ဆုံး AI ကို တစ်နှစ်လုံး အသုံးပြုခွင့်!\n\n✅ Content Writing\n✅ Research & Analysis\n✅ Coding Help\n✅ Creative Ideas\n\nတစ်ရက်ကို ၁၀၀ ကျပ်ကျော်ပဲ ကျသင့်မှာပါ!\n\n📲 အခုပဲ မှာယူပါ: @ThihaTun4055\n#FlashSale #GeminiAI",
        'image': 'price_gemini_ai.png'
    },
    # Day 29 - Cybersecurity Tips
    {
        'caption': "🔒 Digital Product တွေ အသုံးပြုရာမှာ လုံခြုံရေးအတွက် သိထားသင့်တဲ့ အချက်များ!\n\n1️⃣ ခိုင်မာတဲ့ Password တွေ အသုံးပြုပါ\n2️⃣ Two-Factor Authentication (2FA) ကို ဖွင့်ထားပါ\n3️⃣ မသင်္ကာဖွယ် Link တွေကို မနှိပ်ပါနဲ့\n4️⃣ Official Source ကနေသာ ဝယ်ယူပါ\n\nသင့်ရဲ့ Digital Data တွေကို ကာကွယ်ပါ 💡\n\nယုံကြည်ရသော Source 👉 @ThihaDigitalBot\n\n#Cybersecurity #DigitalSafety",
        'image': None
    },
    # Day 30 - Thank You & Future Plans
    {
        'caption': "🙏 လွန်ခဲ့တဲ့ တစ်လတာကာလအတွင်း @ThihaDigitalProductService ကို အားပေးခဲ့ကြတဲ့ Customer တစ်ဦးစီတိုင်းကို ကျေးဇူးအထူးတင်ပါတယ်ဗျာ။\n\nလူကြီးမင်းတို့ရဲ့ အားပေးမှုက ကျွန်တော်တို့အတွက် အင်အားပါပဲ။ အမြဲတမ်း အကောင်းဆုံး ဖြစ်အောင် ကြိုးစားနေပါဦးမယ်။\n\n🛡️ 100% အာမခံ\n⚡ မြန်ဆန်သော ဝန်ဆောင်မှု\n💰 သက်သာသော ဈေးနှုန်း\n\nနောက်လမှာကော ဘယ်လို Products မျိုးတွေ လိုချင်ကြလဲ? Comment မှာ ပြောခဲ့ကြပါဦး! 💖\n\n📲 @ThihaTun4055\n#ThankYou #FuturePlans",
        'image': None
    },
]


# ============================================
# SCHEDULED POST FUNCTION
# ============================================
async def daily_channel_post(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a daily post to the channel at 7:00 PM Myanmar time with image+caption."""
    # Get current day index (cycles through 30 days)
    if 'post_day_index' not in context.bot_data:
        context.bot_data['post_day_index'] = 0

    day_index = context.bot_data['post_day_index']

    # Get today's post content (skip None entries - disabled products)
    post_data = DAILY_POSTS[day_index % len(DAILY_POSTS)]
    
    # Skip disabled posts (None)
    if post_data is None:
        logger.info(f"Day {day_index + 1} is disabled (CapCut), skipping...")
        context.bot_data['post_day_index'] = (day_index + 1) % len(DAILY_POSTS)
        # Try next day's post
        next_index = context.bot_data['post_day_index']
        post_data = DAILY_POSTS[next_index % len(DAILY_POSTS)]
        if post_data is None:
            # Skip again if next is also None
            context.bot_data['post_day_index'] = (next_index + 1) % len(DAILY_POSTS)
            next_index = context.bot_data['post_day_index']
            post_data = DAILY_POSTS[next_index % len(DAILY_POSTS)]
        day_index = context.bot_data['post_day_index']
    caption = post_data['caption']
    image_file = post_data['image']
    
    # Ensure @ThihaDigitalBot is in every post
    if '@ThihaDigitalBot' not in caption:
        caption += '\n\n🤖 Bot မှာ မှာယူရန်: @ThihaDigitalBot'

    try:
        if image_file:
            # Send photo with caption
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', image_file)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=CHANNEL_USERNAME,
                        photo=photo,
                        caption=caption
                    )
            else:
                # If image not found, send text only
                await context.bot.send_message(
                    chat_id=CHANNEL_USERNAME,
                    text=caption
                )
                logger.warning(f"Image not found: {image_path}, sent text only")
        else:
            # Text-only post
            await context.bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=caption
            )

        logger.info(f"✅ Daily post sent successfully! Day {day_index + 1}")

        # Notify owner
        await context.bot.send_message(
            chat_id=OWNER_TELEGRAM_ID,
            text=f"📢 Channel Auto-Post (Day {day_index + 1}/30) တင်ပြီးပါပြီ ✅"
        )
    except Exception as e:
        logger.error(f"❌ Failed to send daily post: {e}")
        await context.bot.send_message(
            chat_id=OWNER_TELEGRAM_ID,
            text=f"❌ Channel Auto-Post (Day {day_index + 1}) fail ဖြစ်ပါတယ်: {e}"
        )

    # Move to next day
    context.bot_data['post_day_index'] = (day_index + 1) % len(DAILY_POSTS)


def get_product_details(product_key, option_key):
    """Helper function to get product and option details."""
    product = PRODUCTS.get(product_key)
    if product:
        option = product['options'].get(option_key)
        if option:
            return product['name_mm'], option['name_mm'], option['price_mm'], option.get('note_mm', '')
    return None, None, None, None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends a welcome message and lists products."""
    keyboard = []
    for product_key, product_data in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(product_data['name_mm'], callback_data=f"product_{product_key}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "🎉 မဂ်္လာပါ! Thiha Digital Product Service မှ ကြိုဆိုပါတယ်။\n\n"
        "💎 အောက်ပါ ဝန်ဆောင်မှုများမှ သင်ဝယ်ယူလိုသော option ကို ရွေးချယ်ပါ။\n\n"
        "🛡️ 100% အာမခံ | ✅ ယုံကြည်စိတ်ချရ"
    )

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup)

    return SELECTING_PRODUCT


async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows options for the selected product."""
    query = update.callback_query
    await query.answer()

    product_key = query.data.replace('product_', '')
    product = PRODUCTS.get(product_key)

    if not product:
        await query.edit_message_text("⚠️ ထုတ်ကုန်ကို ရှာမတွေ့ပါ။ /start ကိုနှိပ်ပြီး ပြန်စပါ။")
        return ConversationHandler.END

    context.user_data['selected_product'] = product_key

    keyboard = []
    for option_key, option_data in product['options'].items():
        button_text = f"{option_data['name_mm']} - {option_data['price_mm']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"option_{option_key}")])

    keyboard.append([InlineKeyboardButton("◀️ နောက်သို့", callback_data="back_to_products")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"{product['name_mm']}\n\nကျေးဇူးပြု၍ သင်လိုချင်သော option ကို ရွေးချယ်ပါ။"
    await query.edit_message_text(text, reply_markup=reply_markup)

    return SELECTING_OPTION


async def select_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows payment info after selecting an option."""
    query = update.callback_query
    await query.answer()

    option_key = query.data.replace('option_', '')
    product_key = context.user_data.get('selected_product')

    product_name, option_name, price, note = get_product_details(product_key, option_key)

    if not product_name:
        await query.edit_message_text("⚠️ ရွေးချယ်မှု မှားယွင်းနေပါတယ်။ /start ကိုနှိပ်ပြီး ပြန်စပါ။")
        return ConversationHandler.END

    context.user_data['selected_option'] = option_key

    text = (
        f"🛒 သင်ရွေးချယ်ထားသော ဝန်ဆောင်မှု:\n\n"
        f"📦 {product_name}\n"
        f"🔹 {option_name}\n"
        f"💰 {price}\n"
    )

    if note:
        text += f"\n📝 {note}\n"

    text += f"\n{'─'*25}\n\n{PAYMENT_INFO_MM}"

    await query.edit_message_text(text)

    return WAITING_FOR_PAYMENT_PROOF


async def back_to_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Goes back to the product list."""
    return await start(update, context)


async def receive_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives payment screenshot and forwards to owner."""
    user = update.effective_user
    product_key = context.user_data.get('selected_product')
    option_key = context.user_data.get('selected_option')

    product_name, option_name, price, _ = get_product_details(product_key, option_key)

    if not product_name:
        await update.message.reply_text("⚠️ ရွေးချယ်မှု မှားယွင်းနေပါတယ်။ /start ကိုနှိပ်ပြီး ပြန်စပါ။")
        return ConversationHandler.END

    # Store order info
    user_info = {
        'user_id': user.id,
        'username': user.username or 'N/A',
        'full_name': user.full_name or 'N/A',
    }

    if 'pending_orders' not in context.bot_data:
        context.bot_data['pending_orders'] = {}

    context.bot_data['pending_orders'][user.id] = {
        'product_key': product_key,
        'option_key': option_key,
        'user_info': user_info,
    }

    # Forward to owner with confirm/reject buttons
    order_details = (
        f"📋 အော်ဒါအသစ်!\n\n"
        f"👤 Customer: {user.full_name} (@{user.username})\n"
        f"🆔 ID: {user.id}\n\n"
        f"🛒 {product_name}\n"
        f"🔹 {option_name}\n"
        f"💰 {price}\n"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{user.id}_{product_key}_{option_key}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}_{product_key}_{option_key}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Forward the photo to owner
    await context.bot.send_photo(
        chat_id=OWNER_TELEGRAM_ID,
        photo=update.message.photo[-1].file_id,
        caption=order_details,
        reply_markup=reply_markup
    )

    await update.message.reply_text(
        "✅ ငွေပေးချေမှု Screenshot ကို လက်ခံရရှိပါပြီ။\n\n"
        "⏳ Admin မှ စစ်ဆေးပြီး မကြာမီ အကြောင်းပြန်ပါမည်။\n"
        "ကျေးဇူးပြု၍ ခဏစောင့်ပါ။"
    )
    return WAITING_FOR_PAYMENT_PROOF


async def owner_confirm_reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles owner's confirmation or rejection of payment."""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != OWNER_TELEGRAM_ID:
        await query.answer("ခွင့်ပြုချက်မရှိပါ။", show_alert=True)
        return

    data_parts = query.data.split('_')
    action_type = data_parts[0]  # confirm or reject
    user_id = int(data_parts[1])
    product_key = data_parts[2]
    option_key = '_'.join(data_parts[3:])  # option_key might contain underscores

    product_name, option_name, price, _ = get_product_details(product_key, option_key)

    # Remove from pending orders
    if 'pending_orders' in context.bot_data and user_id in context.bot_data['pending_orders']:
        del context.bot_data['pending_orders'][user_id]

    if action_type == 'confirm':
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "✅ သင်၏ငွေပေးချေမှုကို အတည်ပြုပြီးပါပြီ!\n\n"
                f"🛒 {product_name} - {option_name}\n\n"
                "Admin မှ သင်မှာယူထားသော ဝန်ဆောင်မှုကို မကြာမီ ပို့ဆောင်ပေးပါမည်။\n"
                "ကျေးဇူးတင်ပါတယ်! 🙏"
            )
        )
        await query.edit_message_caption(
            caption=f"✅ အတည်ပြုပြီး!\n\nCustomer: {user_id}\n{product_name} - {option_name} ({price})"
        )
    elif action_type == 'reject':
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "❌ သင်၏ငွေပေးချေမှုကို အတည်မပြုနိုင်ပါ။\n\n"
                "ငွေလွှဲမှု မှန်ကန်ကြောင်း သေချာပါက @ThihaTun4055 သို့ တိုက်ရိုက်ဆက်သွယ်ပါ။"
            )
        )
        await query.edit_message_caption(
            caption=f"❌ ပယ်ချပြီး!\n\nCustomer: {user_id}\n{product_name} - {option_name} ({price})"
        )


async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows pending orders to the owner."""
    if update.effective_user.id != OWNER_TELEGRAM_ID:
        await update.message.reply_text("⚠️ ဤ command ကို အသုံးပြုရန် ခွင့်ပြုချက်မရှိပါ။")
        return

    pending_orders = context.bot_data.get('pending_orders', {})
    if not pending_orders:
        await update.message.reply_text("📋 လက်ရှိ ဆိုင်းငံ့ထားသော အော်ဒါများ မရှိပါ။")
        return

    order_list_text = "📋 ဆိုင်းငံ့ထားသော အော်ဒါများ:\n\n"
    for uid, order_data in pending_orders.items():
        product_name, option_name, price, _ = get_product_details(order_data['product_key'], order_data['option_key'])
        user_info = order_data['user_info']
        order_list_text += (
            f"👤 {user_info['full_name']} (@{user_info['username']})\n"
            f"🛒 {product_name} - {option_name} ({price})\n"
            f"{'─'*25}\n"
        )

    await update.message.reply_text(order_list_text)


async def handle_photo_outside_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles photos sent outside of the conversation flow."""
    await update.message.reply_text(
        "⚠️ ဝန်ဆောင်မှုကို အရင်ရွေးချယ်ပြီးမှ Screenshot ပို့ပေးပါ။\n\n"
        "/start ကိုနှိပ်ပြီး ဝန်ဆောင်မှု ရွေးချယ်ပါ။"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "❌ လုပ်ငန်းစဉ်ကို ဖျက်သိမ်းလိုက်ပါပြီ။\n/start ကိုနှိပ်ပြီး ပြန်စနိုင်ပါတယ်။"
    )
    return ConversationHandler.END


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles unknown commands or messages."""
    if update.message:
        await update.message.reply_text(
            "🤔 နားမလည်ပါ။\n/start ကိုနှိပ်ပြီး ဝန်ဆောင်မှု ရွေးချယ်နိုင်ပါတယ်။"
        )


def main() -> None:
    """Run the bot."""
    from telegram.request import HTTPXRequest

    request = HTTPXRequest(
        connect_timeout=20.0,
        read_timeout=40.0,
        write_timeout=40.0,
        pool_timeout=10.0,
    )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )

    # ============================================
    # SCHEDULE DAILY POST AT 7:00 PM MYANMAR TIME
    # ============================================
    job_queue = application.job_queue
    post_time = datetime.time(hour=19, minute=0, second=0, tzinfo=MYANMAR_TZ)
    job_queue.run_daily(daily_channel_post, time=post_time, name="daily_channel_post")
    logger.info(f"📅 Daily channel post scheduled at 7:00 PM Myanmar Time")

    # Conversation Handler for customer flow
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_PRODUCT: [
                CallbackQueryHandler(select_product, pattern='^product_'),
                CallbackQueryHandler(back_to_products, pattern='^back_to_products$'),
            ],
            SELECTING_OPTION: [
                CallbackQueryHandler(select_option, pattern='^option_'),
                CallbackQueryHandler(back_to_products, pattern='^back_to_products$'),
            ],
            WAITING_FOR_PAYMENT_PROOF: [
                MessageHandler(filters.PHOTO, receive_payment_proof),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', start),
        ],
        per_message=False,
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('orders', orders_command))
    application.add_handler(CallbackQueryHandler(owner_confirm_reject, pattern='^(confirm|reject)_'))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo_outside_conv))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    logger.info("Bot started successfully!")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        poll_interval=1.0,
        timeout=30,
    )


if __name__ == '__main__':
    main()
