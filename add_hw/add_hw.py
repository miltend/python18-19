from pymorphy2 import MorphAnalyzer
from flask import Flask
from flask import render_template, request
import re
import random
morph = MorphAnalyzer()
app = Flask(__name__)


def many_words():
    with open("1grams-3.txt", "r", encoding="utf-8") as f:
        text = f.read()
    text = text.lower()
    words = set(re.findall('[а-я]+', text))
    instr = []
    wordforms = {}
    for word in words:
        razbor = morph.parse(word)[0]
        instr.append(razbor[:2])
    wordforms.update(instr)
    return wordforms


def parsed_many_words():
    print('Это может занять несколько минут (2)')
    wordforms = many_words()
    return wordforms


parsed_words = parsed_many_words()


def response(user_input):
    words = re.findall('[а-яА-Я]+', user_input)
    instr = []
    wordforms = {}
    for word in words:    # парсит введенные пользователем слова
        razbor = morph.parse(word)[0]
        instr.append(razbor[:2])
    wordforms.update(instr)    # и собирает словарь,
    # где ключ - словоформа, а значение - граммемы
    sentence = []
    for element in wordforms:
        words = []
        for word, gram in parsed_words.items():
            if gram == wordforms[element]:
                words.append(word)
        rand_word = random.choice(words)
        sentence.append(rand_word)
    new_sentence = " ".join(sentence).capitalize() + "."
    return new_sentence


@app.route('/')
def index():
    new_sentence = ""
    if request.args:
        user_input = request.args.get('sentence')
        new_sentence = response(user_input)
    return render_template('lollipop.html', sentence=new_sentence)


if __name__ == '__main__':
    app.run(debug=False)
