import random
import re

hanged_man = ['''
    +---+
    |   |
    O   |
        |
        |
        |
 =========''','''
    +---+
    |   |
    O   |
    |   |
        |
        |
 =========''','''
    +---+
    |   |
    O   |
   /|   |
        |
        |
 =========''','''
    +---+
    |   |
    O   |
   /|\  |
        |
        |
 =========''','''
    +---+
    |   |
    O   |
   /|\  |
   /    |
        |
 =========''','''
    +---+
    |   |
    O   |
   /|\  |
   / \  |
        |
 =========''']

def picking_the_word():     #выбор темы и случайный выбор слова
    while True:
        try:
            topics = {1: "era.txt", 2: "lingua.txt", 3: "tarot.txt"}
            topic_number = int(input("выберите тему: напечатайте\n'1' для темы 'Геологическая эра'\n'2' для темы 'Линвгистические термины'\n'3' для темы 'Таро': \n"))
            with open(topics[topic_number], "r", encoding="utf-8") as f:
                text = f.read()
                words = text.splitlines()
                word = random.choice(words)
                return word
        except KeyError:
            print("введите цифру от 1 до 3!\n")
        except ValueError:
            print("введите цифру от 1 до 3!\n")

def guessing_word():
    word = picking_the_word()
    print('у вас есть 6 попыток,чтобы отгадать слово из ' + str(len(word)) + ' букв.')
    letters = { i : [] for i in set(word)}      #буквы из слова (по 1 вхождению)
    for position, letter in enumerate(word):
        letters[letter].append(position)
    display_letters = ['_'] * len(word)         # "_" по количеству букв в слове
    a = 0
    while '_' in display_letters:
        guess = input("введите букву: ").lower()
        if re.search(r'[а-я]', guess) == None:
            print("введите букву русского алфавита!: ")
        elif guess in display_letters:
            print("вы уже отгадали эту букву!")
        elif guess in letters:
            for i in letters[guess]:
                display_letters[i] = guess
            print(display_letters)
        else:
            if a < 5:
                a += 1
                print(hanged_man[a-1])
                if a == 1:
                    print("такой буквы нет!\nосталось " + str( 6 - a) + "попыток\n")
                elif a<=4 and a>=2:
                    print("такой буквы нет!\nосталось " + str( 6 - a) + "попытки\n")
                else:
                    print("такой буквы нет!\nосталась " + str( 6 - a) + "попытка\n")
            else:
                print("вы проиграли", hanged_man[5],'\n')
                break
    if '_' not in display_letters:
        print("вы выиграли!\n")

def new_game():             #предлагает сыграть еще раз
    while True:
        answer = input("вы хотите сыграть еще раз?:").lower()
        if answer == 'да':
            guessing_word()
        elif answer == 'нет':
            print("ок, спасибо за игру!")
            break
        else:
            print("пожалуйста, введите 'да' или 'нет'")
            continue

guessing_word()
new_game()
