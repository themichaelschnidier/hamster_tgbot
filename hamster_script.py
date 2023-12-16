import telebot
import threading
from telebot import types
import random

bot = telebot.TeleBot('токен бота')
data_dict = {} #для ответов
waiting_dict = {} #для таймеров
el=["-", "-", "-", "-", "-", "-", "-", "-", "-"] # наша сетка. 
position = 0 #позиция хомяка

def GameRules(message): # вывод правила/описание игры
    bot.send_message(message.chat.id, "📄Правила просты:\n\n• В одной из клеток находится хомячок\n\
• В течение 5 секунд вам нужно ввести ТРЕХЗАЧНОЕ простое число, которое СОДЕРЖИТ цифру, соответствующую НОМЕРУ клетки с хомячком. Если вы не успеете - вам будет предложено ввести число еще раз, но хомячок уже убежит в другую клетку\n\
• В случае точного попадания (вы написали число, соответствующее требованиям) хомячок будет пойман\n\
• Игра продолжается до тех пор, пока вы не напишите верное число.")

def rand(): # генерация позиции хомяка, номера клеток 0-8 (+1 в выводе для красоты)
    global position
    position = random.randint(0, 8)
    
def ChangeHamsterPosition(): # смена позиции хомяка
    for i in range(len(el)):
        if i == position:
            el[i] = "🐹"
        else:
            el[i] = "🌿"
                  
def print_map(user_id): # вывод сетки с позицией хомяка. 
    rand()
    ChangeHamsterPosition()
    bot.send_message(user_id, f"❗️Хомячок в {position + 1} клетке, ЛОВИ ГАДА \n\n{el[0]} {el[1]} {el[2]}\
    \n{el[3]} {el[4]} {el[5]}\
    \n{el[6]} {el[7]} {el[8]}")

def Is_prime(num): #простота числа
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def Сontain_number(num): #содержание числом нужной цифры
    global position
    num = str(num)
    digit = str(position + 1)
    if (len(num) == 3) and (digit in num) :
        return True
    return False

def is_number(s):#проверка является ли ввод числовым
    try:
        float(s)
        return True
    except ValueError:
        return False
    
# хендлер и функция для обработки команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, text="Привет, {0.first_name} 👋!\nВыбери нужное действие:".format(message.from_user))
    bot.send_message(message.chat.id, text="/rules - 📄Правила игры\n\n/play - 🚀 Начать игру")

# хендлер и функция для обработки команды /play
@bot.message_handler(commands=['play'])
def start(message):
    user_id = message.from_user.id
    print_map(user_id)
    waiting_dict[user_id] = threading.Timer(5, handle_timeout, args=[user_id])
    waiting_dict[user_id].start()

def handle_timeout(user_id):
    if user_id in waiting_dict:
        bot.send_message(user_id, "Время вышло, хомяк убежал⏰")
        print_map(user_id)
        waiting_dict[user_id] = threading.Timer(5, handle_timeout, args=[user_id])
        waiting_dict[user_id].start()

# хендлер и функция для обработки команды /rules
@bot.message_handler(commands=['rules'])
def rules(message):
    GameRules(message)

@bot.message_handler(func=lambda message: message.from_user.id in waiting_dict)
def process_data(message):
    user_id = message.from_user.id
    data_dict[user_id] = message.text
    if (user_id in waiting_dict) and is_number(data_dict[user_id]) == True:
        if Is_prime(int(data_dict[user_id])) and Сontain_number(int(data_dict[user_id])):
            waiting_dict[user_id].cancel()
            del waiting_dict[user_id] #удаляем таймер
            bot.send_message(user_id, "Вы поймали хомячка🥳")
            bot.send_message(user_id, "Чтобы сыграть еще раз, нажми сюда👉🏻 /play")
            del data_dict[user_id] #удаляем запомненное число
        else:
            waiting_dict[user_id].cancel()
            bot.send_message(user_id, "Вы не поймали хомячка, попробуйте еще раз😭")
            #del data_dict[user_id] #удаляем запомненное число
            print_map(user_id)
            waiting_dict[user_id] = threading.Timer(5, handle_timeout, args=[user_id])
            waiting_dict[user_id].start()
    else:
        bot.send_message(user_id, "Это не число😒\nВведите данные снова - у вас 5 секунд!")
        #del data_dict[user_id] #удаляем запомненное число
        
# Запускаем постоянный опрос бота в Телеграме
bot.polling(none_stop=True, interval=0)