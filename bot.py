"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started.
Usage:
Parent-child learning bot: The parent can advance his child's knowledge by assigning specific tasks and following the
progress via reports
"""
import logging
import bot_keyboards
import re
import secret_settings
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
from telegram import Update

from func_help import send_gif_wellcome, send_stick_ans, send_gif_end_task, send_gif_start_task
from model import add_parent_to_db, add_child_to_db, child_name_to_parent, is_parent, child_id_to_parent, \
    get_current_task, NUMBER_Q_IN_TASK, get_task_level, get_question, check_answer, set_task_start_to_true, \
    get_current_ques, set_ques_status_to_true, set_current_question, ready_tasks, set_task_status_true, get_report
from telegram.ext import (CallbackContext)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_info_from(key: str):
    name, parent_id = key.split('-')
    return name, parent_id


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    key = context.args
    if key:
        logger.info(f"> Start child chat #{chat_id}")
        name, parent_id = get_info_from(key[0])
        add_child_to_db(name, parent_id, chat_id)
        child_id_to_parent(parent_id, chat_id)
        send_gif_wellcome(update, context, chat_id)
        home_child(update, context, chat_id)
    else:
        logger.info(f"> Start parent chat #{chat_id}")
        add_parent_to_db(update, chat_id)
        context.bot.send_message(chat_id=chat_id, text=f"Welcome! {update.message.from_user['first_name']}")
        add_child(update, context, chat_id)


def home_parent(update: Update, chat_id, context: CallbackContext):
    bot_keyboards.main_parent_keyboard(update, chat_id, context)


def home_child(update: Update, context: CallbackContext, chat_id):
    bot_keyboards.main_child_keyboard(update, chat_id, context)


def add_child(update, context, chat_id):
    context.bot.send_message(chat_id=chat_id, text=f"Enter your child's name:")


def adding_child(update, context, child_name):
    chat_id = update.effective_chat.id
    logger.info(f"> Adding {child_name} to parent #{chat_id}")

    child_name_to_parent(chat_id, child_name)
    context.bot.send_message(chat_id=chat_id, text=f"Send your child this link to join this bot: "
                                                   f"\n https://t.me/teachild_bot?start={child_name}-{str(chat_id)}")
    home_parent(update, chat_id, context)


def assign_task(update: Update, context: CallbackContext):
    bot_keyboards.choose_child_for_task(update, context, update.effective_chat.id)


def start_task_one(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if not ready_tasks(chat_id):
        context.bot.send_message(chat_id=chat_id, text=f"No task set for you yet!")
    else:
        logger.info(f"> child chat #{chat_id} starting task 1")
        set_task_start_to_true(chat_id)
        level = get_task_level(chat_id)
        context.bot.send_message(chat_id=chat_id, text=f"You are solving Math - level {level}.\n Good luck!!!")
        amount_questions = NUMBER_Q_IN_TASK
        ques_pic, status = get_question(chat_id, 1)
        context.bot.send_photo(chat_id=chat_id, photo=open(ques_pic, 'rb'),
                               caption=f"Question #1/{amount_questions}")
        bot_keyboards.continue_task_keyboard(update)


def check_and_set_next_ques(update: Update, context: CallbackContext, answer):
    chat_id = update.effective_chat.id
    current_ques = get_current_ques(chat_id)
    ques_pic, status = get_question(chat_id, current_ques)
    is_correct = check_answer(ques_pic, answer)
    if is_correct:
        set_ques_status_to_true(chat_id, current_ques)
    send_stick_ans(context, chat_id, is_correct)
    set_current_question(chat_id, current_ques + 1)
    bot_keyboards.continue_task_keyboard(update)


def next_task(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    current_ques = get_current_ques(chat_id)
    if current_ques == NUMBER_Q_IN_TASK + 1:
        set_task_status_true(chat_id)
        set_current_question(chat_id, 0)
        send_gif_end_task(context, chat_id)
        bot_keyboards.main_child_keyboard(update, chat_id, context)
    else:
        set_task_start_to_true(chat_id)
        ques_pic, status = get_question(chat_id, current_ques)
        context.bot.send_photo(chat_id=chat_id, photo=open(ques_pic, 'rb'),
                               caption=f"Question #{current_ques}/{NUMBER_Q_IN_TASK}")
        bot_keyboards.continue_task_keyboard(update)


def callback_query_handler_choose_child(update, context):
    context.user_data['choose_child'] = update.callback_query.data
    bot_keyboards.choose_level_task(update, context)


def callback_query_handler_choose_level(update, context):
    chat_id = update.effective_chat.id
    child_level = update.callback_query.data
    bot_keyboards.model.create_task_in_db(chat_id, context.user_data['choose_child'], child_level.replace('x', ''))
    context.bot.send_message(chat_id=chat_id, text="Task sent")
    send_gif_start_task(context, int(context.user_data['choose_child']))


def callback_query_handler_choose_child_for_report(update, context):
    chat_id = update.effective_chat.id

    child_id = update.callback_query.data
    child_id = child_id.replace('r', '')
    get_report(chat_id, context, int(''.join(child_id)))


def respond(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    text = update.message.text
    if text == 'Add child':
        add_child(update, context, chat_id)
    elif text == 'Assign task':
        assign_task(update, context)
    elif text == 'Get report':
        bot_keyboards.choose_child_for_report(update, context, chat_id)
    elif text == 'Start Task':
        start_task_one(update, context)
    elif text == 'Show Tasks':
        pass
    elif text == 'Next':
        next_task(update, context)
    elif is_parent(chat_id):
        adding_child(update, context, text)
    else:
        check_and_set_next_ques(update, context, text)


def help(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id,
                             text=f"Press one of the buttons above to continue.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(secret_settings.BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # log all errors
    dispatcher.add_error_handler(error)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)

    dispatcher.add_handler(
        CallbackQueryHandler(callback_query_handler_choose_child_for_report, pattern=re.compile(r'r\d+')))

    echo_handler = MessageHandler(Filters.text, respond)
    dispatcher.add_handler(echo_handler)

    dispatcher.add_handler(CallbackQueryHandler(callback_query_handler_choose_child, pattern=re.compile(r'\d')))

    dispatcher.add_handler(CallbackQueryHandler(callback_query_handler_choose_level, pattern=re.compile(r'x\d+')))

    logger.info("* Start polling...")
    updater.start_polling()  # Starts polling in a background thread.
    updater.idle()  # Wait until Ctrl+C is pressed
    logger.info("* Bye!")


if __name__ == '__main__':
    main()
