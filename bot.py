import logging
import os
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

# States for ConversationHandler
SELECTING_PRODUCT, SELECTING_OPTION, WAITING_FOR_PAYMENT_PROOF = range(3)

# Product and Prices
PRODUCTS = {
    'capcut_pro': {
        'name_mm': 'CapCut Pro',
        'options': {
            'capcut_share': {'name_mm': '1 Device (Share)', 'price_mm': '10,000 MMK'},
            'capcut_1_private': {'name_mm': '1 Device Private Acc', 'price_mm': '17,000 MMK', 'note_mm': '✅ ရောင်းသူမှ Gmail ပေးပါမည်။'},
            'capcut_2_private': {'name_mm': '2 Device (Phone+PC) Private Acc', 'price_mm': '25,000 MMK', 'note_mm': '✅ ရောင်းသူမှ Gmail ပေးပါမည်။'},
        }
    },
    'tiktok_services': {
        'name_mm': 'TikTok Services',
        'options': {
            'tiktok_like': {'name_mm': 'Like 1K', 'price_mm': '6,000 MMK'},
            'tiktok_view': {'name_mm': 'View 1K', 'price_mm': '2,000 MMK'},
            'tiktok_save': {'name_mm': 'Save 1K', 'price_mm': '1,000 MMK'},
            'tiktok_follower': {'name_mm': 'Follower 1K (လူအစစ်)', 'price_mm': '23,000 MMK'},
            'tiktok_share': {'name_mm': 'Share 1K', 'price_mm': '700 MMK'},
        }
    },
    'alight_motion': {
        'name_mm': 'Alight Motion Premium',
        'options': {
            'alight_1year': {'name_mm': '1 Year', 'price_mm': '15,000 MMK'},
        }
    },
    'canva_pro': {
        'name_mm': 'Canva Pro Lifetime',
        'options': {
            'canva_1year': {'name_mm': '1 Year', 'price_mm': '15,000 MMK'},
        }
    },
    'gemini_ai': {
        'name_mm': 'Gemini AI',
        'options': {
            'gemini_1year': {'name_mm': '1 Year', 'price_mm': '40,000 MMK'},
        }
    },
    'tiktok_boosting': {
        'name_mm': 'TikTok Boosting Service',
        'options': {
            'boost_3': {'name_mm': '3$ Package', 'price_mm': '22,000 MMK'},
            'boost_4': {'name_mm': '4$ Package', 'price_mm': '29,500 MMK'},
            'boost_5': {'name_mm': '5$ Package', 'price_mm': '36,500 MMK'},
            'boost_6': {'name_mm': '6$ Package', 'price_mm': '44,000 MMK'},
            'boost_7': {'name_mm': '7$ Package', 'price_mm': '51,500 MMK'},
            'boost_8': {'name_mm': '8$ Package', 'price_mm': '59,000 MMK'},
            'boost_9': {'name_mm': '9$ Package', 'price_mm': '66,000 MMK'},
            'boost_10': {'name_mm': '10$ Package', 'price_mm': '73,000 MMK'},
        }
    },
    'telegram_premium': {
        'name_mm': 'Telegram Premium',
        'options': {
            'tg_3months': {'name_mm': '3 Months', 'price_mm': '60,000 MMK', 'note_mm': '✅ Gift Link ဖြင့်ပေးပါတယ်။ Visa Card ဖြင့် ဝယ်ပေးတာဖြစ်ပါတယ်။ Account 100% အာမခံပါတယ်။'},
            'tg_6months': {'name_mm': '6 Months', 'price_mm': '89,000 MMK', 'note_mm': '✅ Gift Link ဖြင့်ပေးပါတယ်။ Visa Card ဖြင့် ဝယ်ပေးတာဖြစ်ပါတယ်။ Account 100% အာမခံပါတယ်။'},
            'tg_1year': {'name_mm': '1 Year', 'price_mm': '147,000 MMK', 'note_mm': '✅ Gift Link ဖြင့်ပေးပါတယ်။ Visa Card ဖြင့် ဝယ်ပေးတာဖြစ်ပါတယ်။ Account 100% အာမခံပါတယ်။'},
        }
    },
    'tiktok_coin': {
        'name_mm': 'TikTok Coin Service',
        'options': {
            'coin_300': {'name_mm': '300 Coins', 'price_mm': '17,200 MMK', 'note_mm': '✅ Account 100% တာဝန်ယူပေးပါတယ်။ Coin ဝယ်ပြီးတာနဲ့ Logout ပြန်ထွက်ပြီး SS ပြန်ပို့ပေးပါမယ်။ (15 မိနစ်အတွင်း)'},
            'coin_500': {'name_mm': '500 Coins', 'price_mm': '28,600 MMK', 'note_mm': '✅ Account 100% တာဝန်ယူပေးပါတယ်။ Coin ဝယ်ပြီးတာနဲ့ Logout ပြန်ထွက်ပြီး SS ပြန်ပို့ပေးပါမယ်။ (15 မိနစ်အတွင်း)'},
            'coin_1000': {'name_mm': '1,000 Coins', 'price_mm': '54,800 MMK', 'note_mm': '✅ Account 100% တာဝန်ယူပေးပါတယ်။ Coin ဝယ်ပြီးတာနဲ့ Logout ပြန်ထွက်ပြီး SS ပြန်ပို့ပေးပါမယ်။ (15 မိနစ်အတွင်း)'},
            'coin_5000': {'name_mm': '5,000 Coins', 'price_mm': '266,000 MMK', 'note_mm': '✅ Account 100% တာဝန်ယူပေးပါတယ်။ Coin ဝယ်ပြီးတာနဲ့ Logout ပြန်ထွက်ပြီး SS ပြန်ပို့ပေးပါမယ်။ (15 မိနစ်အတွင်း)'},
            'coin_10000': {'name_mm': '10,000 Coins', 'price_mm': '522,500 MMK', 'note_mm': '✅ Account 100% တာဝန်ယူပေးပါတယ်။ Coin ဝယ်ပြီးတာနဲ့ Logout ပြန်ထွက်ပြီး SS ပြန်ပို့ပေးပါမယ်။ (15 မိနစ်အတွင်း)'},
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
                "ငွေလွှဲမှု မှန်ကန်ကြောင်း သေချာပါက @Thihaadmin သို့ တိုက်ရိုက်ဆက်သွယ်ပါ။"
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
