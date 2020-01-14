import random


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def send_gif_wellcome(update, context, chat_id):
    i = (random.randint(1, 2))
    context.bot.send_animation(chat_id=chat_id,
                               animation=open(r'DB\gif\wellcome\\' + f'{i}.gif', 'rb'),
                               caption=f"Welcome! {update.message.from_user['first_name']}")


def send_stick_ans(context, chat_id, bool):
    if bool:
        #i = (random.randint(1, 12))
        context.bot.send_animation(chat_id=chat_id,
                                   animation=open(r'DB\gif\ans_good\\' + f'{1}.webp', 'rb'), caption="GOOD JOB!")
    else:
        #i = (random.randint(1, 7))
        context.bot.send_animation(chat_id=chat_id,
                                   animation=open(r'DB\gif\ans_bad\\' + f'{1}.webp', 'rb'), caption="WRONG ANSWER!")


def send_gif_end_task(context, chat_id):
    #i = (random.randint(1, 5))
    context.bot.send_animation(chat_id=chat_id,
                               animation=open(r'DB\gif\finish_task_good\\' + f'{1}.gif', 'rb'),
                               caption=f"You completed the task!")


def send_gif_start_task(context, chat_id):
    #i = (random.randint(1, 3))
    context.bot.send_animation(chat_id=chat_id,
                               animation=open(r'DB\gif\start\\' + f'{1}.gif', 'rb'),
                               caption=f"Hi, you have a new assignment 😃")
