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
            'tg_3months': {'name_mm': '💠 3 Months', 'price_mm': '60,000 MMK', 'note_mm': '✅ Gift Link ဖြင့်ပေးပါတယ်။ Visa Card ဖြင့် ဝယ်ပေးတာဖြစ်ပါတယ်။ Account 100% အာမခံပါတယ်။'},
            'tg_6months': {'name_mm': '🔥 6 Months', 'price_mm': '89,000 MMK', 'note_mm': '✅ Gift Link ဖြင့်ပေးပါတယ်။ Visa Card ဖြင့် ဝယ်ပေးတာဖြစ်ပါတယ်။ Account 100% အာမခံပါတယ်။'},
            'tg_1year': {'name_mm': '👑 1 Year', 'price_mm': '147,000 MMK', 'note_mm': '✅ Gift Link ဖြင့်ပေးပါတယ်။ Visa Card ဖြင့် ဝယ်ပေးတာဖြစ်ပါတယ်။ Account 100% အာမခံပါတယ်။'},
        }
    },
    'tiktok_coin': {
        'name_mm': '💰 TikTok Coin Service',
        'options': {
            'coin_300': {'name_mm': '🪨 300 Coins', 'price_mm': '17,200 MMK', 'note_mm': '✅ Account 100% တာဝန်ယူပေးပါတယ်။ Coin ဝယ်ပြီးတာနဲ့ Logout ပြန်ထွက်ပြီး SS ပြန်ပို့ပေးပါမယ်။ (15 မိနစ်အတွင်း)'},
            'coin_500': {'name_mm': '💴 500 Coins', 'price_mm': '28,600 MMK', 'note_mm': '✅ Account 100% တာဝန်ယူပေးပါတယ်။ Coin ဝယ်ပြီးတာနဲ့ Logout ပြန်ထွက်ပြီး SS ပြန်ပို့ပေးပါမယ်။ (15 မိနစ်အတွင်း)'},
            'coin_1000': {'name_mm': '💵 1,000 Coins', 'price_mm': '54,800 MMK', 'note_mm': '✅ Account 100% တာဝန်ယူပေးပါတယ်။ Coin ဝယ်ပြီးတာနဲ့ Logout ပြန်ထွက်ပြီး SS ပြန်ပို့ပေးပါမယ်။ (15 မိနစ်အတွင်း)'},
            'coin_5000': {'name_mm': '💶 5,000 Coins', 'price_mm': '266,000 MMK', 'note_mm': '✅ Account 100% တာဝန်ယူပေးပါတယ်။ Coin ဝယ်ပြီးတာနဲ့ Logout ပြန်ထွက်ပြီး SS ပြန်ပို့ပေးပါမယ်။ (15 မိနစ်အတွင်း)'},
            'coin_10000': {'name_mm': '💎 10,000 Coins', 'price_mm': '522,500 MMK', 'note_mm': '✅ Account 100% တာဝန်ယူပေးပါတယ်။ Coin ဝယ်ပြီးတာနဲ့ Logout ပြန်ထွက်ပြီး SS ပြန်ပို့ပေးပါမယ်။ (15 မိနစ်အတွင်း)'},
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
# ============================================
DAILY_POSTS = [
    # Day 1
    "🎬 CapCut Pro ဖြင့် သင့်ဗီဒီယိုများကို နောက်တစ်ဆင့်သို့ မြှင့်တင်လိုက်ပါ။ ✨\n\nပရော်ဖက်ရှင်နယ်ဆန်သော ဗီဒီယိုတည်းဖြတ်မှုများအတွက် အကောင်းဆုံးရွေးချယ်မှု! 🎬\n\n📱 Share (10,000 MMK)\n🔒 1 Device Private (17,000 MMK)\n💻 2 Device Private (25,000 MMK)\n\n✅ Private Acc = ရောင်းသူမှ Gmail ပေးပါမည်\n\nအသေးစိတ်သိရှိလိုပါက 👉 @ThihaDigitalBot\nChannel: @ThihaDigitalProductService",

    # Day 2
    "💎 CapCut Pro ရဲ့ Hidden Gem - Green Screen Effect ကို ဘယ်လိုအသုံးချမလဲ? 🤔\n\nဒီ Video Editing Tip လေးနဲ့ သင့်ဗီဒီယိုတွေကို ပိုမိုဆန်းသစ်လိုက်ပါ။ 💡\n\nCapCut Pro ကို အခုပဲ ရယူလိုက်ပါ 👉 @ThihaDigitalBot\n\n#CapCutProTips #VideoEditing",

    # Day 3
    "🙏 Customer Feedback\n\n\"CapCut Pro ကို @ThihaDigitalProductService ကနေ ဝယ်ယူပြီးနောက် ကျွန်တော့်ရဲ့ Video တွေ အရမ်းကောင်းလာတယ်။ ဝန်ဆောင်မှုလည်း မြန်ဆန်တယ်!\"\n\n- ကျေနပ်အားရနေတဲ့ Customer တစ်ဦးရဲ့ Feedback ပါ။\n\nသင်လည်း စမ်းသုံးကြည့်ဖို့ ဖိတ်ခေါ်ပါတယ် 👉 @ThihaDigitalBot\n\n#CustomerReview #ThihaDigital",

    # Day 4
    "🎵 TikTok မှာ နာမည်ကြီးချင်လား? 📈\n\n@ThihaDigitalProductService ရဲ့ TikTok Services တွေက သင့်ကို ကူညီပေးပါလိမ့်မယ်။\n\n❤️ Like 1K (6,000 MMK)\n👁️ View 1K (2,000 MMK)\n💾 Save 1K (1,000 MMK)\n👥 Follower 1K - လူအစစ် (23,000 MMK)\n🔁 Share 1K (700 MMK)\n\nသင့် TikTok Account ကို အခုပဲ မြှင့်တင်လိုက်ပါ 🚀\n👉 @ThihaDigitalBot",

    # Day 5
    "🎉 ဒီတစ်ပတ်အတွက် အထူးအစီအစဉ်!\n\nTikTok Services တွေကို Package အလိုက် ဝယ်ယူပြီး ပိုမိုသက်သာစွာ သင့် TikTok ကို မြှင့်တင်လိုက်ပါ။ 🎁\n\nအသေးစိတ်ကို 👉 @ThihaDigitalBot မှာ မေးမြန်းနိုင်ပါတယ်။\n\n#TikTokPromotion #SpecialOffer",

    # Day 6
    "📈 TikTok Video တွေ Foryou တက်ဖို့ ဘာတွေလုပ်သင့်လဲ? 🤔\n\n✅ Trending Hashtag တွေ အသုံးပြုပါ\n✅ Trending Music တွေ ထည့်ပါ\n✅ Hook ကောင်းကောင်း ထည့်ပါ\n✅ Engagement မြှင့်တင်ပါ\n\nEngagement မြှင့်တင်ဖို့ 👉 @ThihaDigitalBot\n\n#TikTokTips #ForyouPage",

    # Day 7
    "🌟 Alight Motion Premium ဖြင့် သင့်ရဲ့ Creative Ideas တွေကို အသက်သွင်းလိုက်ပါ။ ✨\n\nMotion Graphics နဲ့ Video Editing အတွက် အကောင်းဆုံး App! 🎬\n\n💎 1 Year (15,000 MMK)\n\nအခုပဲ ဝယ်ယူပြီး သင့်ရဲ့ ဖန်တီးမှုတွေကို စတင်လိုက်ပါ 🚀\n👉 @ThihaDigitalBot",

    # Day 8
    "🙏 Customer Feedback\n\n\"Alight Motion Premium ကို @ThihaDigitalProductService ကနေ ဝယ်ယူပြီးနောက် ကျွန်တော့်ရဲ့ Motion Graphics တွေ အရမ်းလန်းလာတယ်။ ဝန်ဆောင်မှုလည်း မြန်ဆန်တယ်!\"\n\n- ကျေနပ်အားရနေတဲ့ Customer တစ်ဦးရဲ့ Feedback ပါ။\n\nသင်လည်း စမ်းသုံးကြည့်ဖို့ ဖိတ်ခေါ်ပါတယ် 👉 @ThihaDigitalBot\n\n#CustomerReview #ThihaDigital",

    # Day 9
    "🎨 Canva Pro Lifetime ဖြင့် ပရော်ဖက်ရှင်နယ် Design တွေကို အလွယ်တကူ ဖန်တီးလိုက်ပါ။ 🖌️\n\nGraphic Design အတွက် အကောင်းဆုံး Tool!\n\n💎 1 Year (15,000 MMK)\n\nတစ်သက်တာ အသုံးပြုခွင့်ကို အခုပဲ ရယူလိုက်ပါ 🚀\n👉 @ThihaDigitalBot",

    # Day 10
    "✨ Canva Pro ရဲ့ Magic Resize Feature ကို သိပြီးပြီလား?\n\nဒီ Feature လေးနဲ့ သင့် Design တွေကို Social Media Platform အစုံအတွက် အလွယ်တကူ ပြောင်းလဲလိုက်ပါ။ 💡\n\nCanva Pro ရယူရန် 👉 @ThihaDigitalBot\n\n#CanvaProTips #GraphicDesign",

    # Day 11
    "🙏 Customer Feedback\n\n\"Canva Pro ကို @ThihaDigitalProductService ကနေ ဝယ်ယူပြီးနောက် ကျွန်တော့်ရဲ့ Design တွေ Professional ဖြစ်လာတယ်။ ဝန်ဆောင်မှုလည်း မြန်ဆန်တယ်!\"\n\n- ကျေနပ်အားရနေတဲ့ Customer တစ်ဦးရဲ့ Feedback ပါ။\n\nသင်လည်း စမ်းသုံးကြည့်ဖို့ ဖိတ်ခေါ်ပါတယ် 👉 @ThihaDigitalBot\n\n#CustomerReview #ThihaDigital",

    # Day 12
    "🤖 Gemini AI ဖြင့် သင့်ရဲ့ နေ့စဉ်လုပ်ငန်းဆောင်တာတွေကို ပိုမိုလွယ်ကူမြန်ဆန်စေလိုက်ပါ။ 💡\n\nAI Assistant အဖြစ် အကောင်းဆုံးရွေးချယ်မှု!\n\n💎 1 Year (40,000 MMK)\n\nအခုပဲ ဝယ်ယူပြီး AI ရဲ့ စွမ်းအားကို ခံစားလိုက်ပါ 🚀\n👉 @ThihaDigitalBot",

    # Day 13
    "📚 Gemini AI ကို အသုံးပြုပြီး Research လုပ်နည်း သိပြီးပြီလား?\n\nအချက်အလက်တွေကို အမြန်ဆုံး ရှာဖွေပြီး သင့်ရဲ့ အချိန်တွေကို ချွေတာလိုက်ပါ။ 💡\n\nGemini AI ရယူရန် 👉 @ThihaDigitalBot\n\n#GeminiAITips #AIAssistant",

    # Day 14
    "🙏 Customer Feedback\n\n\"Gemini AI ကို @ThihaDigitalProductService ကနေ ဝယ်ယူပြီးနောက် ကျွန်တော့်ရဲ့ အလုပ်တွေ အရမ်းမြန်ဆန်လာတယ်။ ဝန်ဆောင်မှုလည်း မြန်ဆန်တယ်!\"\n\n- ကျေနပ်အားရနေတဲ့ Customer တစ်ဦးရဲ့ Feedback ပါ။\n\nသင်လည်း စမ်းသုံးကြည့်ဖို့ ဖိတ်ခေါ်ပါတယ် 👉 @ThihaDigitalBot\n\n#CustomerReview #ThihaDigital",

    # Day 15
    "🚀 TikTok မှာ သင့်ဗီဒီယိုတွေကို ပိုမိုလူသိများအောင် လုပ်ချင်လား?\n\n@ThihaDigitalProductService ရဲ့ TikTok Boosting Services!\n\n🟢 3$ (22,000 MMK)\n🟢 4$ (29,500 MMK)\n🟡 5$ (36,500 MMK)\n🟡 6$ (44,000 MMK)\n🟠 7$ (51,500 MMK)\n🟠 8$ (59,000 MMK)\n🔴 9$ (66,000 MMK)\n🔴 10$ (73,000 MMK)\n\nသင့် TikTok ကို အခုပဲ မြှင့်တင်လိုက်ပါ 📈\n👉 @ThihaDigitalBot",

    # Day 16
    "🎉 ဒီတစ်ပတ်အတွက် အထူးအစီအစဉ်!\n\nTikTok Boosting Services တွေကို Package အလိုက် ဝယ်ယူပြီး ပိုမိုသက်သာစွာ သင့် TikTok ကို မြှင့်တင်လိုက်ပါ။ 🎁\n\nအသေးစိတ်ကို 👉 @ThihaDigitalBot မှာ မေးမြန်းနိုင်ပါတယ်။\n\n#TikTokBoostingPromotion #SpecialOffer",

    # Day 17
    "💰 TikTok Coin တွေကို အသက်သာဆုံး ဈေးနှုန်းနဲ့ ဝယ်ယူလိုက်ပါ။\n\nသင့်အကြိုက်ဆုံး Creator တွေကို Support လုပ်ဖို့ အကောင်းဆုံးအခွင့်အရေး! 💖\n\n🪨 300 Coins (17,200 MMK)\n💴 500 Coins (28,600 MMK)\n💵 1,000 Coins (54,800 MMK)\n💶 5,000 Coins (266,000 MMK)\n💎 10,000 Coins (522,500 MMK)\n\n✅ Account 100% တာဝန်ယူပေးပါတယ်\n\nအခုပဲ ဝယ်ယူလိုက်ပါ 🚀\n👉 @ThihaDigitalBot",

    # Day 18
    "🙏 Customer Feedback\n\n\"TikTok Coin တွေကို @ThihaDigitalProductService ကနေ ဝယ်ယူပြီးနောက် ကျွန်တော့်အကြိုက်ဆုံး Creator တွေကို Support လုပ်နိုင်ခဲ့တယ်။ ဈေးနှုန်းလည်း သက်သာတယ်!\"\n\n- ကျေနပ်အားရနေတဲ့ Customer တစ်ဦးရဲ့ Feedback ပါ။\n\nသင်လည်း စမ်းသုံးကြည့်ဖို့ ဖိတ်ခေါ်ပါတယ် 👉 @ThihaDigitalBot\n\n#CustomerReview #ThihaDigital",

    # Day 19
    "🤔 Digital Product တွေ ဝယ်ယူရာမှာ မေးလေ့ရှိတဲ့ မေးခွန်းများ (FAQ)\n\n❓ ဘယ်လိုဝယ်ယူရမလဲ?\n➡️ @ThihaDigitalBot မှာ /start နှိပ်ပြီး ရွေးချယ်ပါ\n\n❓ ငွေပေးချေမှု ဘယ်လိုလုပ်ရမလဲ?\n➡️ KBZPay / UAB Pay ဖြင့် လွှဲပြီး SS ပို့ပါ\n\n❓ ဝယ်ယူပြီးရင် ဘယ်လောက်ကြာရင် ရမလဲ?\n➡️ ၁၅ မိနစ်အတွင်း ရပါတယ်\n\nအသေးစိတ် 👉 @ThihaDigitalBot\n\n#FAQ #DigitalProducts",

    # Day 20
    "🎬✨ CapCut Pro နဲ့ Alight Motion Premium ဘယ်ဟာက သင့်အတွက် ပိုကောင်းလဲ?\n\n🎬 CapCut Pro:\n- လွယ်ကူမြန်ဆန်တဲ့ Video Editing အတွက်\n- TikTok/Reels အတွက် အကောင်းဆုံး\n\n🌟 Alight Motion Premium:\n- Motion Graphics နဲ့ Advanced Effects အတွက်\n- Professional Animation အတွက်\n\nသင့်လိုအပ်ချက်နဲ့ ကိုက်ညီတာကို ရွေးချယ်လိုက်ပါ 🚀\n👉 @ThihaDigitalBot\n\n#CapCutPro #AlightMotionPremium",

    # Day 21
    "🙏 Customer Feedback\n\n\"@ThihaDigitalProductService ရဲ့ ဝန်ဆောင်မှုက အရမ်းကောင်းတယ်။ မြန်ဆန်ပြီး ယုံကြည်စိတ်ချရတယ်။\"\n\n- ကျေနပ်အားရနေတဲ့ Customer တစ်ဦးရဲ့ Feedback ပါ။\n\nသင်လည်း စမ်းသုံးကြည့်ဖို့ ဖိတ်ခေါ်ပါတယ် 👉 @ThihaDigitalBot\n\n#CustomerReview #ThihaDigital",

    # Day 22
    "🎉 အထူး Bundle Deal!\n\nCapCut Pro နဲ့ Canva Pro Lifetime ကို အတူတူဝယ်ယူပြီး ပိုမိုသက်သာစွာ ရယူလိုက်ပါ။ 🎁\n\n🎬 CapCut Pro + 🎨 Canva Pro = Special Price!\n\nအသေးစိတ်ကို 👉 @ThihaDigitalBot မှာ မေးမြန်းနိုင်ပါတယ်။\n\n#BundleDeal #SpecialOffer",

    # Day 23
    "💰 Digital Product တွေနဲ့ Online မှာ ငွေရှာနည်း ၅ မျိုး!\n\n1️⃣ Freelancing လုပ်ငန်းများ\n2️⃣ Online Course များ ဖန်တီးခြင်း\n3️⃣ E-book များ ရေးသားခြင်း\n4️⃣ Social Media Content ဖန်တီးခြင်း\n5️⃣ Digital Marketing ဝန်ဆောင်မှုများ\n\nသင့်ရဲ့ စွမ်းရည်တွေကို အသုံးချပြီး အခုပဲ စတင်လိုက်ပါ 💡\n\nTools တွေ ရယူရန် 👉 @ThihaDigitalBot\n\n#MakeMoneyOnline #DigitalProducts",

    # Day 24
    "✨ @ThihaDigitalProductService ရဲ့ ရည်ရွယ်ချက်က သင့်ရဲ့ Digital Lifestyle ကို ပိုမိုလွယ်ကူစေဖို့ပါ။\n\nကျွန်တော်တို့ရဲ့ ဝန်ဆောင်မှုတွေနဲ့အတူ သင့်ရဲ့ အောင်မြင်မှုခရီးကို လျှောက်လှမ်းလိုက်ပါ။ 💖\n\n🛡️ 100% အာမခံ\n⚡ မြန်ဆန်သော ဝန်ဆောင်မှု\n💰 သက်သာသော ဈေးနှုန်း\n\n👉 @ThihaDigitalBot\n\n#OurStory #ThihaDigital",

    # Day 25
    "🤔 သင်အသုံးပြုနေတဲ့ Digital Product တွေထဲမှာ ဘယ်ဟာက သင့်အတွက် အသုံးအဝင်ဆုံးလဲ?\n\n🎬 CapCut Pro\n🎵 TikTok Services\n🌟 Alight Motion\n🎨 Canva Pro\n🤖 Gemini AI\n⭐ Telegram Premium\n\nComment မှာ ဖြေပေးခဲ့ပါဦး 👇\n\n#Poll #DigitalLife",

    # Day 26
    "🎬 CapCut Pro ရဲ့ Keyframe Animation Feature ကို အသုံးပြုပြီး သင့်ဗီဒီယိုတွေကို ပိုမိုဆန်းသစ်လိုက်ပါ။\n\nKeyframe Animation ဆိုတာ Object တွေကို smooth movement ပေးတဲ့ technique ပါ။ 💡\n\nCapCut Pro ရယူရန် 👉 @ThihaDigitalBot\n\n#CapCutPro #DeepDive",

    # Day 27
    "🙏 Customer Feedback\n\n\"@ThihaDigitalProductService ရဲ့ TikTok Services တွေက ကျွန်တော့်ရဲ့ Follower တွေကို အများကြီး တိုးစေခဲ့တယ်။ အရမ်းကျေးဇူးတင်ပါတယ်!\"\n\n- ကျေနပ်အားရနေတဲ့ Customer တစ်ဦးရဲ့ Feedback ပါ။\n\nသင်လည်း စမ်းသုံးကြည့်ဖို့ ဖိတ်ခေါ်ပါတယ် 👉 @ThihaDigitalBot\n\n#CustomerReview #ThihaDigital",

    # Day 28
    "⚡ Flash Sale! ဒီနေ့တစ်ရက်တည်းသာ!\n\nGemini AI 1 Year ကို အထူးလျှော့စျေးနဲ့ ရယူလိုက်ပါ။ 🎁\n\n🤖 Gemini AI - 1 Year\n💰 ပုံမှန်ဈေး: 40,000 MMK\n🔥 ယနေ့အထူးဈေး: @ThihaDigitalBot မှာ မေးမြန်းပါ\n\nအခုပဲ ဝယ်ယူလိုက်ပါ 👉 @ThihaDigitalBot\n\n#FlashSale #GeminiAI",

    # Day 29
    "🔒 Digital Product တွေ အသုံးပြုရာမှာ လုံခြုံရေးအတွက် သိထားသင့်တဲ့ အချက်များ!\n\n1️⃣ ခိုင်မာတဲ့ Password တွေ အသုံးပြုပါ\n2️⃣ Two-Factor Authentication (2FA) ကို ဖွင့်ထားပါ\n3️⃣ မသင်္ကာဖွယ် Link တွေကို မနှိပ်ပါနဲ့\n4️⃣ Official Source ကနေသာ ဝယ်ယူပါ\n\nသင့်ရဲ့ Digital Data တွေကို ကာကွယ်ပါ 💡\n\nယုံကြည်ရသော Source 👉 @ThihaDigitalBot\n\n#Cybersecurity #DigitalSafety",

    # Day 30
    "🙏 လွန်ခဲ့တဲ့ တစ်လတာကာလအတွင်း @ThihaDigitalProductService ကို အားပေးခဲ့ကြတဲ့ Customer တစ်ဦးစီတိုင်းကို ကျေးဇူးတင်ပါတယ်။\n\nလာမယ့်လတွေမှာလည်း ပိုမိုကောင်းမွန်တဲ့ ဝန်ဆောင်မှုတွေနဲ့ ထုတ်ကုန်အသစ်တွေကို ယူဆောင်လာဖို့ စီစဉ်ထားပါတယ်။ 🚀\n\n🛡️ 100% အာမခံ\n⚡ မြန်ဆန်သော ဝန်ဆောင်မှု\n💰 သက်သာသော ဈေးနှုန်း\n\nစောင့်မျှော်ပေးပါဦး! 💖\n👉 @ThihaDigitalBot\n\n#ThankYou #FuturePlans",
]


# ============================================
# SCHEDULED POST FUNCTION
# ============================================
async def daily_channel_post(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a daily post to the channel at 7:00 PM Myanmar time."""
    # Get current day index (cycles through 30 days)
    if 'post_day_index' not in context.bot_data:
        context.bot_data['post_day_index'] = 0

    day_index = context.bot_data['post_day_index']

    # Get today's post content
    post_content = DAILY_POSTS[day_index % len(DAILY_POSTS)]

    try:
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=post_content
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

    await update.message.reply_text(
        "🎉 မင်္ဂလာပါ! Thiha Digital Product Service မှ ကြိုဆိုပါတယ်။\n\n"
        "💎 အောက်ပါ ဝန်ဆောင်မှုများမှ သင်ဝယ်ယူလိုသော ဝန်ဆောင်မှုကို ရွေးချယ်ပါ။\n\n"
        "🛡️ 100% အာမခံ | ✅ ယုံကြည်စိတ်ချရ",
        reply_markup=reply_markup
    )
    return SELECTING_PRODUCT


async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows options for the selected product."""
    query = update.callback_query
    await query.answer()

    product_key = query.data.replace('product_', '')
    context.user_data['selected_product'] = product_key
    product_data = PRODUCTS[product_key]

    keyboard = []
    for option_key, option_data in product_data['options'].items():
        button_text = f"{option_data['name_mm']} - {option_data['price_mm']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"option_{option_key}")])

    keyboard.append([InlineKeyboardButton("⬅️ နောက်သို့", callback_data="back_to_products")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"🛒 {product_data['name_mm']}\n\n"
        "ကျေးဇူးပြု၍ သင်လိုချင်သော option ကို ရွေးချယ်ပါ။",
        reply_markup=reply_markup
    )
    return SELECTING_OPTION


async def select_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows payment info and asks for screenshot."""
    query = update.callback_query
    await query.answer()

    option_key = query.data.replace('option_', '')
    context.user_data['selected_option'] = option_key
    product_key = context.user_data['selected_product']

    product_name, option_name, price, note = get_product_details(product_key, option_key)

    order_summary = (
        f"📋 သင်ရွေးချယ်ထားသော ဝန်ဆောင်မှု:\n\n"
        f"🔹 {product_name}\n"
        f"🔹 {option_name}\n"
        f"🔹 စျေးနှုန်း: {price}\n"
    )
    if note:
        order_summary += f"\n📌 မှတ်ချက်: {note}\n"

    order_summary += f"\n{'='*30}\n\n{PAYMENT_INFO_MM}"

    await query.edit_message_text(order_summary)
    return WAITING_FOR_PAYMENT_PROOF


async def back_to_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns to the product list."""
    query = update.callback_query
    await query.answer()

    keyboard = []
    for product_key, product_data in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(product_data['name_mm'], callback_data=f"product_{product_key}")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "💎 အောက်ပါ ဝန်ဆောင်မှုများမှ သင်ဝယ်ယူလိုသော ဝန်ဆောင်မှုကို ရွေးချယ်ပါ။",
        reply_markup=reply_markup
    )
    return SELECTING_PRODUCT


async def receive_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives payment screenshot and forwards to owner."""
    user = update.effective_user
    photo_file_id = update.message.photo[-1].file_id

    product_key = context.user_data.get('selected_product')
    option_key = context.user_data.get('selected_option')

    if not product_key or not option_key:
        await update.message.reply_text(
            "⚠️ ကျေးဇူးပြု၍ ဝန်ဆောင်မှုကို အရင်ရွေးချယ်ပါ။\n/start ကိုနှိပ်ပြီး ပြန်စနိုင်ပါတယ်။"
        )
        return ConversationHandler.END

    product_name, option_name, price, _ = get_product_details(product_key, option_key)

    username = user.username if user.username else "N/A"
    order_details = (
        f"🆕 အော်ဒါအသစ်!\n\n"
        f"👤 Customer: {user.full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📱 Username: @{username}\n\n"
        f"🛒 ဝန်ဆောင်မှု: {product_name}\n"
        f"📦 Option: {option_name}\n"
        f"💰 စျေးနှုန်း: {price}\n"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{user.id}_{product_key}_{option_key}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}_{product_key}_{option_key}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Store pending order
    if 'pending_orders' not in context.bot_data:
        context.bot_data['pending_orders'] = {}
    context.bot_data['pending_orders'][user.id] = {
        'product_key': product_key,
        'option_key': option_key,
        'user_info': {'id': user.id, 'full_name': user.full_name, 'username': username},
        'photo_file_id': photo_file_id
    }

    # Forward screenshot to owner with order details and confirm/reject buttons
    await context.bot.send_photo(
        chat_id=OWNER_TELEGRAM_ID,
        photo=photo_file_id,
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
