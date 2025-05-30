from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = '7486063873:AAGhebewo6dbB1R030ekIGh6-u2zXXZzpZ4'
ADMIN_CHAT_ID = '6947939129'
API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

user_states = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    message = data.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')

    if not chat_id:
        return 'no chat', 400

    state = user_states.get(chat_id, 'start')

    if text == '/start':
        send_message(chat_id, "أهلاً وسهلاً بك 👋\nشو بتحب تشحن؟", [
            ["ألعاب 🎮", "تطبيقات 💬"]
        ])
        user_states[chat_id] = 'choose_type'

    elif state == 'choose_type':
        if text == "ألعاب 🎮":
            send_message(chat_id, "اختر اللعبة يلي بدك تشحن عليها:", [
                ["ببجي", "فري فاير"],
                ["كلاش اوف كلانس", "لودو"],
                ["جواكر", "موبايل ليجند"]
            ])
            user_states[chat_id] = 'choose_game'

        elif text == "تطبيقات 💬":
            send_message(chat_id, "اختر التطبيق يلي بدك تشحنه:", [
                ["تامي شات", "سول شات"],
                ["ايومي شات", "سوشال"],
                ["بيجو لايف", "ميجو لايف"],
                ["لايت شات", "هيا شات"],
                ["اهلا شات", "زينة شات"]
            ])
            user_states[chat_id] = 'choose_app'

    elif state in ['choose_game', 'choose_app']:
        user_states[chat_id] = {'product': text, 'stage': 'ask_uid'}
        send_message(chat_id, "👍 حلو، هلا بعتلي الـ UID أو اسم الحساب يلي بدك نشحن عليه")

    elif isinstance(state, dict) and state.get('stage') == 'ask_uid':
        user_states[chat_id]['uid'] = text
        user_states[chat_id]['stage'] = 'ask_payment'
        send_message(chat_id, "اختر طريقة الدفع:", [
            ["💸 حوالة (الهرم / الفؤاد)"],
            ["📱 سيرياتيل كاش", "📱 MTN كاش"],
            ["💳 شام كاش"]
        ])

    elif isinstance(state, dict) and state.get('stage') == 'ask_payment':
        product = state['product']
        uid = state['uid']
        payment = text

        summary = f"""🆕 طلب جديد:
المنتج: {product}
الحساب/UID: {uid}
طريقة الدفع: {payment}
من المستخدم: {chat_id}
        """

        send_message(chat_id, "✅ تم استلام الطلب، رح يتم التواصل معك بأقرب وقت 🙌")
        send_message(ADMIN_CHAT_ID, summary)
        user_states.pop(chat_id, None)

    else:
        send_message(chat_id, "اكتب /start لنرجع نبلّش من الأول 🌀")

    return 'ok'

def send_message(chat_id, text, buttons=None):
    payload = {'chat_id': chat_id, 'text': text}
    if buttons:
        keyboard = [[{'text': btn} for btn in row] for row in buttons]
        payload['reply_markup'] = {'keyboard': keyboard, 'resize_keyboard': True}
    requests.post(f'{API_URL}/sendMessage', json=payload)