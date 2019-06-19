import flask
import random
import re
import string
import gensim
import os
#from nltk.tokenize import sent_tokenize
#from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer
import telebot
from telebot import types

morph = MorphAnalyzer()
#telebot.apihelper.proxy = {'https':os.environ["DATA"]}
tb = telebot.TeleBot(os.environ["TOKEN"], threaded=False)
tb.remove_webhook()
tb.set_webhook(url="https://chekhovapp.herokuapp.com/bot")
app = flask.Flask(__name__)

with open("chehov.txt", encoding="utf-8") as f:
    text = f.read()
sentences = re.split(r'[.!?]', text)
#urllib.request.urlretrieve("http://rusvectores.org/static/models/rusvectores2/ruscorpora_mystem_cbow_300_2_2015.bin.gz",
#                           "ruscorpora_mystem_cbow_300_2_2015.bin.gz")
m = 'ruscorpora_mystem_cbow_300_2_2015.bin.gz'
model = gensim.models.KeyedVectors.load_word2vec_format(m, binary=True)

def marked_word(word): # навешивает часть речи на слово
    list_by_hands = [ 'это', 'то', 'я', 'таки', 'нам', 'обо', 'около', 'эта', 'ха']
    #russian_stopwords = stopwords.words("russian") + list_by_hands
    if word.lower() not in list_by_hands:
        if morph.parse(word)[0].tag.POS == 'NOUN':
            word = morph.parse(word)[0].normal_form + "_S"
        elif (morph.parse(word)[0].tag.POS == 'VERB' or 
              morph.parse(word)[0].tag.POS == 'INFN'):
            word = morph.parse(word)[0].normal_form + "_V"
        elif morph.parse(word)[0].tag.POS == 'ADJF':
            word = morph.parse(word)[0].normal_form + "_A"
    return word

def similar_word(word): # находит похожее слово
    try:
        x = []
        part_of_speech = word[-2:]
        for i in model.most_similar(positive=[word], topn=20):
            if i[0].endswith(part_of_speech) and i[0] != word:
                x.append(i[0])
        pick = random.choice(x)
        return pick
    except IndexError:
        return word

def gramems(word): # возвращает граммемы слова
    p = morph.parse(word)[0]
    list_of_gram = []
    if p.tag.POS:
        list_of_gram.append(p.tag.POS)
    if p.tag.aspect:
        list_of_gram.append(p.tag.aspect)
    if p.tag.case:
        list_of_gram.append(p.tag.case)
    if p.tag.involvement:
        list_of_gram.append(p.tag.involvement)
    if p.tag.mood:
        list_of_gram.append(p.tag.mood)
    if p.tag.number:
        list_of_gram.append(p.tag.number)
    if p.tag.person:
        list_of_gram.append(p.tag.person)
    if p.tag.tense:
        list_of_gram.append(p.tag.tense)
    if p.tag.transitivity:
        list_of_gram.append(p.tag.transitivity)
    if p.tag.voice:
        list_of_gram.append(p.tag.voice)
    #if p.tag.animacy:
    #    list_of_gram.append(p.tag.animacy)
    #if p.tag.gender:
    #    list_of_gram.append(p.tag.gender)
    return list_of_gram   

def needed_word_form(word, gramems): # склоняет слово
    p = morph.parse(word)[0]
    inflected_form = p.inflect(set(gramems)) 
    return inflected_form[0]


def two_sentences(): # возвращает исходное предложение и сгенерированное
    cleaned_sentences = []
    xxx1 = {}
    xxx2 = {}
    for sen in sentences:
        if len(sen) > 20 and len(sen)< 150:
            if sen.startswith('—'):
                continue
            cleaned_sentences.append(sen)
    pick = random.choice(cleaned_sentences)
    words = pick.split()
    i = 0
    for word in words:
        if word.endswith(tuple(string.punctuation)):
            xxx1[i] = marked_word(word.strip(string.punctuation))
        else:
            xxx1[i] = marked_word(word)
        i+=1
    for k, w in xxx1.items():
        try:
            if len(w) >= 2 and w[-2] == '_':
                xxx2[k] = similar_word(w)
            else:
                xxx2[k] = w
        except KeyError:
            xxx2[k] = w
    generated_sentence = []
    z = 0
    for elem in words:
        try:
            if len(xxx2[z]) >= 2 and xxx2[z][-2] == '_':
                generated_sentence.append(needed_word_form(xxx2[z][:-2], gramems(elem)))
            else:
                generated_sentence.append(elem)
        except TypeError:
            generated_sentence.append(elem)
        z+=1
    f = 0
    for element in words:
        if (words[f].endswith(tuple(string.punctuation)) and 
            generated_sentence[f].endswith(tuple(re.findall('[а-яА-Я]+', generated_sentence[f])))):
            generated_sentence[f] = generated_sentence[f] + element[-1]
        f+=1
    generated_sentence[0] = generated_sentence[0].capitalize()
    gen_sent = ' '.join(generated_sentence)
    original_sentence = ' '.join(words)
    two_sent = {'real': original_sentence + '.', 'fake': gen_sent + '.'}
    return two_sent


def add_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Из произведения')
    btn2 = types.KeyboardButton('Сгенерированное')
    btn3 = types.KeyboardButton('Завершить игру')
    markup.add(btn1, btn2, btn3)
    return markup

def delete_keyboard():
    markup = types.ReplyKeyboardRemove(selective=False)
    return markup


@tb.message_handler(commands=['start'])
def send_welcome(message):
    tb.send_message(message.chat.id, ("Давай сыграем в игру!\n"\
                                      "Ты должен угадать, взято предложение из произведения "\
                                      "Чехова или же оно сгенерировано компьютером.\n"\
                                      "Начать игру – /startgame"), reply_markup=delete_keyboard())

@tb.message_handler(commands=['startgame'])
def start_the_game(message):
    global correct_answer
    global incorrect_answer
    correct_answer = 0
    incorrect_answer = 0
    def random_sentence():
        sentence = two_sentences()
        global pick
        pick = random.choice(list(sentence))
        return sentence[pick]
    tb.send_message(message.chat.id, random_sentence(), reply_markup=add_keyboard())
    
@tb.message_handler(func=lambda message: message.text == 'Из произведения')
def get_answer(message):
    global correct_answer
    global incorrect_answer
    if pick == 'real':
        reply = 'Правильно!\n'
        correct_answer +=1
    elif pick == 'fake':
        reply = 'Неправильно :(\n'
        incorrect_answer +=1
    def random_sentence():
        sentence = two_sentences()
        global pick
        pick = random.choice(list(sentence))
        return sentence[pick]
    tb.send_message(message.chat.id, reply + random_sentence(), reply_markup=add_keyboard())
    
    
@tb.message_handler(func=lambda message: message.text == 'Сгенерированное')
def get_answer(message):
    global correct_answer
    global incorrect_answer
    if pick == 'fake':
        reply = 'Правильно!\n'
        correct_answer +=1
    elif pick == 'real':
        reply = 'Неправильно :(\n'
        incorrect_answer +=1
    def random_sentence():
        sentence = two_sentences()
        global pick
        pick = random.choice(list(sentence))
        return sentence[pick]
    tb.send_message(message.chat.id, reply + random_sentence(), reply_markup=add_keyboard())

@tb.message_handler(func=lambda message: message.text == 'Завершить игру')
def get_answer(message):
    global correct_answer
    global incorrect_answer
    text = ('Спасибо за игру!\nПравильных ответов: ' + str(correct_answer) + '\n'
            'Неправильных ответов: ' + str(incorrect_answer) + '\n'
            'Для начала новой игры – /startgame')
    tb.send_message(message.chat.id, text , reply_markup=delete_keyboard())
    
@tb.message_handler(func=lambda m: True)
def something_is_wrong_reply(message):
    tb.send_message(message.chat.id, 'Вы ввели что-то не то.')

@app.route("/", methods=['GET', 'HEAD'])
def index():
    return 'ok'

# страница для нашего бота
@app.route("/bot", methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        tb.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


    
if __name__ == '__main__':
    import os
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
