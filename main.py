# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from collections import defaultdict
import os
import time

# --- Конфигурация ---
# Важно: Перед запуском установите переменные окружения BOT_TOKEN и ADMIN_CHAT_ID.
try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    ADMIN_CHAT_ID = os.environ['ADMIN_CHAT_ID']
except KeyError:
    raise ValueError("Переменные окружения BOT_TOKEN и ADMIN_CHAT_ID должны быть установлены!")

bot = telebot.TeleBot(BOT_TOKEN)

# --- Хранилища данных и состояний ---
user_answers = defaultdict(dict)
user_state = defaultdict(dict) # Для хранения истории вопросов для кнопки "Назад"

# --- Структура опросника ---
# Определяем порядок вопросов для навигации
QUESTIONS_ORDER = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12', 'q13', 'q14']

QUESTIONS_DATA = {
    'q1': {
        'text': 'Вы проводили неформальные интервью с клиентами (не продавая, а изучая их проблемы) за последние 3 месяца?',
        'key': 'interviews',
        'answers': {
            'q1_opt1': "Да, регулярно (>5)",
            'q1_opt2': "Да, несколько раз",
            'q1_opt3': "Нет, не проводил"
        }
    },
    'q2': {
        'text': 'Какая ключевая причина, по которой клиенты выбирают именно вас, а не ваших конкурентов?',
        'key': 'reason_to_choose',
        'answers': {
            'q2_opt1': "Уникальное решение",
            'q2_opt2': "Цена/качество",
            'q2_opt3': "Сервис/отношения",
            'q2_opt4': "Сложно сказать"
        }
    },
    'q3': {
        'text': 'Насколько предсказуем ваш процесс продаж? Можете ли вы с уверенностью сказать, сколько денег будет в кассе в следующем месяце?',
        'key': 'sales_predictability',
        'answers': {
            'q3_opt1': "Да, прогноз точный",
            'q3_opt2': "Прогноз неточный",
            'q3_opt3': "Непредсказуемо"
        }
    },
    'q4': {
        'text': 'Какой этап в вашей воронке продаж является самым узким местом?',
        'key': 'bottleneck',
        'answers': {
            'q4_opt1': "Привлечение лидов",
            'q4_opt2': "Квалификация",
            'q4_opt3': "Переговоры/закрытие",
            'q4_opt4': "Повторные продажи",
            'q4_opt5': "Нет воронки"
        }
    },
    'q5': {
        'text': 'Какая часть процесса продаж требует вашего обязательного личного участия?',
        'key': 'personal_involvement',
        'answers': {
            'q5_opt1': "Только стратегические",
            'q5_opt2': "Большинство сделок",
            'q5_opt3': "Почти все"
        }
    },
    'q6': {
        'text': 'Как бы вы оценили ситуацию с чистой прибылью за последние полгода?',
        'key': 'profit_situation',
        'answers': {
            'q6_opt1': "Прибыль растет",
            'q6_opt2': "Прибыль \"плавает\"",
            'q6_opt3': "Ноль/убыток/непредсказуемо"
        }
    },
    'q7': {
        'text': 'Вы ведете анализ прибыльности в разрезе продуктов или клиентских сегментов?',
        'key': 'profit_analysis',
        'answers': {
            'q7_opt1': "Да, по данным",
            'q7_opt2': "Да, интуитивно",
            'q7_opt3': "Нет, общий итог"
        }
    },
    'q8': {
        'text': 'Представьте, что завтра вам нужно увеличить оборот в два раза. Готова ли к этому ваша операционная и финансовая модель?',
        'key': 'scaling_readiness',
        'answers': {
            'q8_opt1': "Да, готова",
            'q8_opt2': "Нет, будет хаос"
        }
    },
    'q9': {
        'text': 'Может ли ваша команда самостоятельно принимать решения и достигать результатов без вашего ежедневного микроменеджмента?',
        'key': 'team_autonomy',
        'answers': {
            'q9_opt1': "Да, автономна",
            'q9_opt2': "Требует контроля",
            'q9_opt3': "Все на мне"
        }
    },
    'q10': {
        'text': 'Как часто в компании меняются краткосрочные приоритеты (задачи на неделю/месяц)?',
        'key': 'priority_change',
        'answers': {
            'q10_opt1': "Редко, по плану",
            'q10_opt2': "Периодически",
            'q10_opt3': "Постоянно, \"пожары\""
        }
    },
    'q11': {
        'text': 'Сколько времени у вас займет проверка новой гипотезы?',
        'key': 'hypothesis_speed',
        'answers': {
            'q11_opt1': "До недели",
            'q11_opt2': "2-4 недели",
            'q11_opt3': "Больше месяца",
            'q11_opt4': "Мы так не работаем"
        }
    },
    'q12': {
        'text': 'Как ваша компания реагирует на неожиданные изменения на рынке?',
        'key': 'market_reaction',
        'answers': {
            'q12_opt1': "Быстро адаптируемся",
            'q12_opt2': "Реагируем, но с хаосом",
            'q12_opt3': "Стараемся игнорировать",
            'q12_opt4': "Адаптация долгая"
        }
    },
    'q13': {
        'text': 'Какая стратегическая цель для вас сейчас в приоритете?',
        'key': 'strategy_goal',
        'answers': {
            'q13_opt1': "Системный бизнес",
            'q13_opt2': "Личный доход",
            'q13_opt3': "Лучший продукт",
            'q13_opt4': "Стабильность"
        }
    },
    'q14': {
        'text': 'Что вас, как собственника, беспокоит больше всего в текущей ситуации?',
        'key': 'frustration',
        'answers': {
            'q14_opt1': "Ощущение \"плато\"",
            'q14_opt2': "Выгорание",
            'q14_opt3': "Прибыль/управляемость",
            'q14_opt4': "Нет фокуса",
            'q14_opt5': "Ничего не беспокоит"
        }
    }
}
# Тексты вердиктов... (полные тексты из ТЗ)
VERDICT_DATA = {
    'verdikt1': {"name": "Стабильность (трекинг не требуется)", "text": "..."},
    'verdikt2': {"name": "Стратегическое масштабирование", "text": "..."},
    'verdikt3': {"name": "Поиск точки кратного роста", "text": "..."},
    'verdikt4': {"name": "Масштабирование через систему", "text": "..."},
    'verdikt5': {"name": "Системный сбой: фокус на восстановлении управляемости", "text": "..."}
}
# Заполним тексты вердиктов из ТЗ
VERDICT_DATA['verdikt1']['text'] = '🎯 Диагностический вывод: Ваша бизнес-система работает стабильно и соответствует вашим текущим целям. Вы находитесь в точке контроля и предсказуемости.\n\nОбоснование: Трекинг — это инструмент для компаний, которые либо находятся в кризисе, либо стремятся к кратному росту, что всегда сопряжено с выходом из зоны комфорта. Судя по вашим ответам, ваш текущий запрос — это стабильность, а не интенсивный рост. В такой ситуации внешнее вмешательство может принести больше вреда, чем пользы.\n\nРекомендация: Продолжайте делать то, что у вас отлично получается. Сохраните этот контакт (@natalia_koch). Если в будущем вы решите, что готовы к новому рывку, или почувствуете, что рынок меняется быстрее, чем вы, — это будет сигналом к тому, что пора провести повторную диагностику.'
VERDICT_DATA['verdikt2']['text'] = '🎯 Диагностический вывод: У вас выстроена эффективная операционная платформа. Бизнес работает системно и прибыльно. Это позволяет перейти от задач операционного управления к задачам стратегического масштабирования.\n\nГипотеза о проблеме: Ваша текущая бизнес-модель, идеально оптимизированная под существующий рынок, исчерпала свой потенциал для кратного роста. Это приводит к стагнации выручки на текущем плато (ущерб в виде упущенной выгоды) и концентрирует все риски в одной рыночной нише. Дальнейший рост требует не улучшения существующих процессов, а запуска системного поиска и проверки новых источников дохода.\n\nКак трекинг может быть полезен: В роли спарринг-партнера по стратегии. Трекер поможет систематизировать работу с неопределенностью: тестировать новые рынки, каналы, продукты, не разрушая при этом работающую систему. Мы вместе проверим гипотезу о вашем ограничении и сфокусируемся на его преодолении.\n\nПредложение: Предлагаю провести стратегическую сессию (1.5 часа), чтобы сформулировать и оценить гипотезы для перехода на следующий уровень роста.'
VERDICT_DATA['verdikt3']['text'] = '🎯 Диагностический вывод: Вы много работаете, но бизнес не растет кратно. Это указывает на то, что ваши усилия и ресурсы тратятся не на то ограничение, которое действительно сдерживает рост системы.\n\nГипотеза о проблеме: В вашей бизнес-системе существует неочевидный системный барьер. Возможно, вы оптимизируете то, что и так работает неплохо, в то время как настоящее "узкое место" остается без внимания.\n\nКак поможет трекер: Как системный диагност. Наша задача — найти то самое ограничение, работа над которым даст максимальный результат. Вы сфокусируете все усилия команды на расшивании этого ограничения. Это позволит превратить хаотичные действия в целенаправленное движение к росту.\n\nПредложение: На диагностической сессии (1.5 часа) мы проведем детальный анализ и выявим то самое "узкое место", которое сдерживает ваш рост, и сформулируем первые гипотезы по его устранению.'
VERDICT_DATA['verdikt4']['text'] = '🎯 Диагностический вывод: Рост вашей компании ограничен скоростью одного человека — вас. Бизнес-процессы, особенно продажи, существуют в виде вашего личного опыта, а не как воспроизводимая система.\n\nГипотеза о проблеме: Ваша глубокая вовлеченность в операционные процессы продаж не оставляет ресурсов на создание масштабируемой технологии. Каждый час, потраченный на "ручное" закрытие сделки, — это час, не вложенный в разработку системы, которая позволила бы команде делать это без вас. Это приводит к стагнации (рост ограничен вашим временем) и создает ключевую уязвимость для бизнеса.\n\nДаже если часть вашей команды работает автономно над проектами, ключевые функции бизнеса (продажи, финансы, стратегия) все еще могут быть замкнуты на вас. Это создает риск: команда может делать \'не то\', а вы — выгорать, пытаясь все контролировать.\n\nКак поможет трекер: Как методолог. Мы сфокусируемся на том, чтобы каждый ваш шаг превращался не только в деньги, но и в элемент будущей системы. Это позволит вам постепенно выходить из операционки, не теряя в качестве, и направить свое время на стратегию.\n\nПредложение: Первый шаг — диагностическая сессия (1.5 часа). На ней мы определим основное ограничение, мешающее вам расти. Далее вы будете последовательно "расшивать" узкие места в вашей системе, в том числе передавая все больше функций команде и контролируя результат.'
VERDICT_DATA['verdikt5']['text'] = '🎯 Диагностический вывод: Ваша бизнес-система работает в реактивном режиме. Усилия расфокусированы, а решения принимаются по принципу "тушения пожаров", что не приводит к стабильному росту чистой прибыли.\n\nГипотеза о проблеме: Процесс принятия решений в компании оторван от его влияния на чистую прибыль. Команда фокусируется на выполнении задач и "тушении пожаров", а не на действиях, которые напрямую увеличивают доход или снижают издержки. Это приводит к постоянной утечке ресурсов и не позволяет бизнесу выйти из состояния хаоса.\n\nКак поможет трекер (фокус на управляемости): Наша первая задача — остановить хаос и вернуть вам контроль через внедрение еженедельного управленческого цикла. Мы найдем одну ключевую метрику, которая напрямую связана с прибыльностью, и сделаем её "компасом" для всех краткосрочных решений. Каждую неделю мы будем ставить цели по этой метрике, проверять гипотезы по её улучшению и анализировать результаты. Это позволит быстро перейти от реактивного управления к проактивному.\n\nПредложение: Предлагаю провести диагностическую сессию (1.5 часа). На ней мы определим те самые ключевые ограничения, которые мешают стабилизировать управление бизнесом. Вы сможете построить системную работу, возвращая в бизнес стабильность и предсказуемость и как финальный результат - достижение своих целей.'

# --- Основные функции ---

def escape_markdown_v2(text: str) -> str:
    """Экранирует символы для MarkdownV2."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def notify_admin(user_id, data, verdict_name):
    """Отправляет уведомление администратору."""
    try:
        user_info = bot.get_chat(user_id)
        username = escape_markdown_v2(user_info.username or "N/A")
        first_name = escape_markdown_v2(user_info.first_name or "")
        message_text = (f"🔔 *Новая заявка на диагностику\\!* \n\n"
                        f"👤 *Пользователь:* @{username} \\({first_name}\\)\n"
                        f"🆔 *User ID:* `{user_id}`\n\n"
                        f"🤖 *Диагноз бота:* {escape_markdown_v2(verdict_name)}\n\n"
                        f"*--- Досье диагностики ---*\n")
        
        report_data = {
            "Клиенты": [
                ("Интервью", data.get('interviews')),
                ("Причина выбора", data.get('reason_to_choose')),
            ],
            "Продажи": [
                ("Предсказуемость", data.get('sales_predictability')),
                ("Узкое место", data.get('bottleneck')),
                ("Личное участие", data.get('personal_involvement')),
            ],
            "Финансы": [
                 ("Прибыль", data.get('profit_situation')),
                 ("Анализ прибыльности", data.get('profit_analysis')),
                 ("Готовность к росту x2", data.get('scaling_readiness')),
            ],
            "Управление": [
                ("Автономность команды", data.get('team_autonomy')),
                ("Смена приоритетов", data.get('priority_change')),
            ],
            "Гибкость": [
                 ("Скорость гипотез", data.get('hypothesis_speed')),
                 ("Реакция на изменения", data.get('market_reaction')),
            ],
            "Стратегия": [
                 ("Приоритет", data.get('strategy_goal')),
                 ("Беспокойство", data.get('frustration')),
            ]
        }

        for block_name, items in report_data.items():
            message_text += f"\n*{escape_markdown_v2(block_name)}:*\n"
            for item_name, item_value in items:
                value_str = escape_markdown_v2(str(item_value) or "Не отвечено")
                message_text += f"• {escape_markdown_v2(item_name)}: _{value_str}_\n"

        bot.send_message(ADMIN_CHAT_ID, message_text, parse_mode="MarkdownV2")
    except Exception as e:
        print(f"Ошибка при отправке админу: {e}")
        bot.send_message(ADMIN_CHAT_ID, f"Не удалось сформировать отчет по анкете от пользователя {user_id}.")

def send_verdict(chat_id, verdict_key):
    """Отправляет финальный вердикт пользователю."""
    data = VERDICT_DATA[verdict_key]
    text = data['text']
    markup = InlineKeyboardMarkup()
    buttons = {
        'verdikt1': ("Спасибо, было полезно", "feedback_thanks"),
        'verdikt2': ("Обсудить стратегию", "https://t.me/natalia_koch"),
        'verdikt3': ("Найти \"узкое место\"", "https://t.me/natalia_koch"),
        'verdikt4': ("Составить план делегирования", "https://t.me/natalia_koch"),
        'verdikt5': ("Разработать антикризисный план", "https://t.me/natalia_koch")
    }
    btn_text, btn_data = buttons.get(verdict_key)
    
    if verdict_key == 'verdikt1':
        markup.add(InlineKeyboardButton(btn_text, callback_data=btn_data))
        bot.send_message(chat_id, text, reply_markup=markup)
        notify_admin(chat_id, user_answers.get(chat_id, {}), data['name'])
    else:
        markup.add(InlineKeyboardButton(btn_text, url=btn_data))
        bot.send_message(chat_id, text, reply_markup=markup)
        # Уведомление админу отправляется в analyze_results, чтобы отправить его до того, как пользователь перейдет по ссылке
    
def ask_question(chat_id, q_index, is_editing=False):
    """Отправляет вопрос пользователю."""
    question_code = QUESTIONS_ORDER[q_index]
    q_data = QUESTIONS_DATA[question_code]
    
    markup = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(text, callback_data=cb_data) for cb_data, text in q_data['answers'].items()]
    markup.add(*buttons)
    
    if q_index > 0:
        markup.add(InlineKeyboardButton("⬅️ Назад", callback_data=f"back_{q_index}"))

    if is_editing:
        bot.edit_message_text(q_data['text'], chat_id, message_id=user_state[chat_id]['last_message_id'], reply_markup=markup)
    else:
        sent_message = bot.send_message(chat_id, q_data['text'], reply_markup=markup)
        user_state[chat_id]['last_message_id'] = sent_message.message_id
    
    user_state[chat_id]['current_q_index'] = q_index

def analyze_results(user_id):
    """Анализирует ответы и определяет вердикт."""
    data = user_answers.get(user_id)
    if not data or len(data) < len(QUESTIONS_DATA):
        bot.send_message(user_id, "Произошла ошибка, не все ответы сохранены. Начните заново: /start")
        return

    # 1. Приоритетная проверка на "Трекинг не нужен"
    if data.get('frustration') == "Ничего не беспокоит" and \
       data.get('profit_situation') == "Прибыль растет" and \
       data.get('team_autonomy') == "Да, автономна":
        verdict_key = 'verdikt1'
        send_verdict(user_id, verdict_key)
        return

    # 2. Начисление баллов для остальных вердиктов
    scores = defaultdict(int)

    # Системный сбой
    if data.get('profit_situation') == "Ноль/убыток/непредсказуемо": scores['verdikt5'] += 2
    if data.get('priority_change') == "Постоянно, \"пожары\"": scores['verdikt5'] += 2
    if data.get('market_reaction') in ["Адаптация долгая", "Изменения выбивают"]: scores['verdikt5'] += 1
    if data.get('frustration') == "Прибыль/управляемость": scores['verdikt5'] += 3
    if data.get('scaling_readiness') == "Нет, будет хаос": scores['verdikt5'] += 1

    # Зависимость от собственника
    if data.get('personal_involvement') in ["Большинство сделок", "Почти все"]: scores['verdikt4'] += 2
    if data.get('team_autonomy') == "Все на мне": scores['verdikt4'] += 2
    if data.get('frustration') == "Выгорание": scores['verdikt4'] += 3

    # Поиск точки роста / Плато
    if data.get('sales_predictability') == "Непредсказуемо": scores['verdikt3'] += 1
    if data.get('profit_situation') == "Прибыль \"плавает\"": scores['verdikt3'] += 1
    if data.get('interviews') == "Нет, не проводил": scores['verdikt3'] += 1
    if data.get('hypothesis_speed') in ["Больше месяца", "Мы так не работаем"]: scores['verdikt3'] += 2
    if data.get('frustration') in ["Ощущение \"плато\"", "Нет фокуса"]: scores['verdikt3'] += 3

    # Стратегическое масштабирование
    if data.get('strategy_goal') != "Стабильность": scores['verdikt2'] += 1
    if data.get('scaling_readiness') == "Да, готова": scores['verdikt2'] += 2
    if data.get('team_autonomy') == "Да, автономна": scores['verdikt2'] += 1
    
    # 3. Выбор победителя по баллам и приоритету
    # Убираем verdikt1, так как он уже проверен
    if 'verdikt1' in scores: del scores['verdikt1']

    if not scores: # Если никаких проблем не найдено, но запрос на рост есть
        verdict_key = 'verdikt2'
    else:
        max_score = max(scores.values())
        winners = [key for key, score in scores.items() if score == max_score]
        
        priority = ['verdikt5', 'verdikt4', 'verdikt3', 'verdikt2']
        for p in priority:
            if p in winners:
                verdict_key = p
                break
        else: # На случай, если что-то пошло не так
            verdict_key = 'verdikt3'
            
    verdict_info = VERDICT_DATA[verdict_key]
    notify_admin(user_id, data, verdict_info['name'])
    send_verdict(user_id, verdict_key)

# --- Обработчики ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_answers[user_id] = {}
    user_state[user_id] = {'history': []}
    
    welcome_text = (
        "Добрый день. Я — бот для диагностики бизнеса. Моя цель — помочь вам за 10 минут выявить ключевые зоны роста и системные ограничения и понять, нужен ли вам сейчас бизнес-трекинг."
        "\nДиалог построен на основе методологии трекинга. Давайте начнем?")
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Начать диагностику", callback_data="start_quiz"))
    bot.send_message(user_id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == "start_quiz":
        bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=None)
        user_state[user_id]['history'] = []
        ask_question(user_id, 0)
        return

    if call.data.startswith('back_'):
        prev_q_index = int(call.data.split('_')[1]) - 1
        if prev_q_index >= 0:
            ask_question(user_id, prev_q_index, is_editing=True)
        return

    if call.data == "feedback_thanks":
        bot.answer_callback_query(call.id, "Спасибо!")
        bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=None)
        return
        
    # Обработка ответов на вопросы
    if call.data.startswith('q'):
        bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=None)
        
        question_code = call.data.split('_')[0]
        q_data = QUESTIONS_DATA[question_code]
        answer_text = q_data['answers'][call.data]
        user_answers[user_id][q_data['key']] = answer_text

        current_q_index = QUESTIONS_ORDER.index(question_code)
        
        progress_messages = {
            2: 'Спасибо. Пройдено 20%. Переходим к продажам.',
            5: 'Принято. Мы на экваторе. Теперь о финансовом здоровье.',
            8: 'Отлично. Пройдено 60%. Теперь об управлении и команде.',
            10: 'Принято. Пройдено 80%. Теперь очень важный блок о скорости и гибкости.',
            12: 'Финальный рывок! Остался последний блок — о вас и будущем.'
        }
        if current_q_index + 1 in progress_messages:
             bot.send_message(user_id, progress_messages[current_q_index + 1])
        
        next_q_index = current_q_index + 1
        if next_q_index < len(QUESTIONS_ORDER):
            ask_question(user_id, next_q_index)
        else:
            bot.send_message(user_id, 'Спасибо, это был последний вопрос. Готовлю для вас персональный вывод...')
            analyze_results(user_id)

if __name__ == '__main__':
    while True:
        try:
            print("Бот запущен...")
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Критическая ошибка в цикле polling: {e}")
            time.sleep(15)
