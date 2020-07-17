import discord
import config
import io
import requests
from bs4 import BeautifulSoup
from github import Github


def get_profile(user):
    document = config.USERS.find_one({'user_id': user.id})
    if document is None:
        document = {'user_id': user.id, 'premium': False, 'is_student': True, 'google_classroom': None, 'note': None,
                    'classes': [], 'teacher_notifications': True, 'student_notifications': True, 'username_cache': user.name, 'discriminator_cache': user.discriminator, 'avatar_cache': str(user.avatar_url)}
        config.USERS.insert_one(document)
        return document, True
    if document['username_cache'] != user.name or document['discriminator_cache'] != user.discriminator:
        config.USERS.update_one({'user_id': user.id}, {'$set': {'username_cache': user.name, 'discriminator_cache': user.discriminator}})
    return document, False


def get_user_classes(user_id):
    return config.CLASSES.find({'members': user_id})


def get_teaching_classes(user_id):
    return config.CLASSES.find({'owner': user_id})


def emoji(emoji):
    emoji_dict = {"leave": "<:leave:732461354065330266>", "time": "<:time:732461354014998619>",
                  "pin": "<:pin:732461353830449173>", "info": "<:info:732116410553073674>",
                  "bug": "<:bug:732105781025046578>", "gift": "<:gift:732105778055610428>",
                  "enter": "<:enter:732105777577459723>", "auth": "<:auth:732103030110945332>",
                  "on_b": "<:on_b:732103029930590229>", "off": "<:off:732103029892841564>",
                  "check_verify_b": "<:check_verify_b:732103029800697886>", "check": "<:check:732103029733720134>",
                  "announce": "<:announce:732103029725200425>", "cross": "<:cross:732103029712617482>",
                  "on": "<:on:732103029624537109>", "dev": "<:dev:732103029620211783>",
                  "people": "<:people:732103029565947934>", "news": "<:news:732103029565685770>",
                  "poo": "<:poo:732103029553364992>", "card": "<:card:732103029523873823>",
                  "plus": "<:plus:732103029435924491>", "inv": "<:inv:732103029213364295>",
                  "check_verify": "<:check_verify:732103029121089638>", "checkb": "<:checkb:732103029020557323>",
                  "online": "<:online:732103028873756683>", "crown": "<:crown:732103028781613117>",
                  "minus": "<:minus:732103028726824982>", "dbl": "<a:dbl:732105777703288883>",
                  "loading": "<a:loading:732103030799073291>", "bell": "<a:bell:732103030488432720>",
                  "error": "<:error:732714132461191330>", "settings": "<:settings:732811659118379008>",
                  "git": "<:git:733077008312959029>", "cloud": "<:cloud:733180288141754398>"}
    try:
        theEmoji = emoji_dict[emoji.lower()]
    except:
        theEmoji = emoji_dict['error']
    return (theEmoji)


def get_new_version():
    url = requests.get("https://github.com/LuisVervaet/DiscordClassroom/blob/master/Main.py")
    soup = BeautifulSoup(url.content, "html.parser")
    text = soup.find('td', {'id': "LC12"})
    text = text.find('span', {'class': "pl-s"}).text
    text = text.replace('"', "")
    return text


def get_new_version_text():
    g = Github()
    branch = g.get_repo('LuisVervaet/DiscordClassroom').get_branch("master")
    return branch.commit.commit.message
