import json
import urllib.request
user_list = ['elmiram' , 'maryszmary' , 'lizaku' , 'nevmenandr' , 'ancatmara' , 'roctbb' , 'akutuzov' , 'agricolamz' , 'lehkost' , 'kylepjohnson' , 'mikekestemont' , 'demidovakatya' , 'shwars' , 'JelteF' , 'timgraham' , 'arogozhnikov' , 'jasny' , 'bcongdon' , 'whyisjake' , 'gvanrossum' ]
print(user_list)

def get_data(user_list, token):
    user_data = {}
    for user in user_list:
        url = 'https://api.github.com/users/%s/repos?access_token=%s' % (user, token)
        response = urllib.request.urlopen(url)
        text = response.read().decode('utf-8')
        data = json.loads(text)
        user_data[user] = data
    return user_data
          
def pick_user():
    while True:
        user_chosen = input('введите имя пользователя: ')
        if user_chosen not in user_list:
            print('этого пользователя нет в списке!')
            continue
        else:
            return user_chosen
        
def name_and_description(username, all_data):
    chosen_user_data = all_data[username]
    for i in chosen_user_data:
        print('название репозитория:',i["name"],'\n','описание: ', i["description"])

def languages(username, all_data):
    chosen_user_data = all_data[username]
    dict_lang = {}
    for i in chosen_user_data:
        now_l = i["language"]
        if now_l in dict_lang:
            dict_lang[now_l]+=1
        else:
            dict_lang[now_l] = 1
    for lang in dict_lang.keys():
        print(lang, dict_lang[lang])

def main():
    token = input("введите токен: ")
    username = pick_user()
    print('ждите')
    all_data = get_data ( user_list, token)
    name_and_description(username, all_data)
    languages(username, all_data)

main()
    
