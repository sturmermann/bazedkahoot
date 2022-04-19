import requests
import random 
import time
import json
from threading import Thread

class user():
    def __init__(self,id):
        self.id = id
        self.creating = 0

class actualGame():
    def __init__(self, pin, gameFounder, templateId):
        self.PIN = pin
        self.gameFounder = int(gameFounder)
        self.templateId = templateId
        self.actualQuestion = 0
        self.lastTime = 0
        self.players = [{"id":int(gameFounder), "score":-10000000, "nickname":"GameFounder"}]
        #[{"id":668794674, "score":0, "nickname":"Белый Негр"}]
        self.playersWhoAnswered = [gameFounder]
        

def textOrderisation(text):
    textN = ""
    for i in text:
        if i != " ":
            textN+= i
    return textN.lower()

def sendMessage(peerId, randomId, text, attachment="" , keyboard = ""):
    return requests.get(f"https://api.vk.com/method/messages.send?message={text}&attachment={attachment}&keyboard={keyboard}&peer_id={peerId}&access_token={token}&v=5.131&random_id={randomId}")

def uploadPic(peer_id, picName):
    a = requests.get("https://api.vk.com/method/photos.getMessagesUploadServer?peer_id={}&access_token={}&v=5.131".format(peer_id,token)).json()
    b = requests.post(a['response']['upload_url'], files={'photo': open(picName, 'rb')}).json()
    c = requests.get( "https://api.vk.com/method/photos.saveMessagesPhoto?photo={}&server={}&hash={}&access_token={}&v=5.131".format(b['photo'],b['server'],b['hash'], token) ).json()
    d = "photo{}_{}".format(c["response"][0]["owner_id"], c["response"][0]["id"])
    return d

def findingNumbers(text):
    k = ""
    for i in text:
        if i.isdigit():
            k += i
    if k == "":
        return "Nope"
    return int(k)

def generatePin():
    i = int(f"{random.randint(1,9)}{random.randint(0,9)}{random.randint(0,9)}")
    PINs = []
    for x in gameBase:
        PINs.append(x.PIN)
    while i in PINs:
        i = int(f"{random.randint(1,9)}{random.randint(0,9)}{random.randint(0,9)}")
    return i

def sorting(players):
    s = []
    for a in players:
        s.append(a["score"])
    a = s.copy()
    s.sort()
    s.reverse()
    new = []
    for i in s:
        new.append(players[a.index(i)])
        players.pop(a.index(i))
        a.remove(i)
    return new

def generateList(players):
    text = ""
    for i in players: 
        text += "   [id{}|{}] : {} \n".format(i["id"], i["nickname"], i["score"])
    return text


def play(text, update):
    for i in gameBase:
        if i.gameFounder == update["object"]['message']['from_id']:
            sendMessage(update["object"]['message']['peer_id'],update["object"]['message']['random_id'],"i saw you in Химки :(", attachment= uploadPic(update['object']['message']['peer_id'], "br.png"))
            return
    templateId = findingNumbers(text)
    if templateId == "Nope" or templateId >= len(dataBaseQuiz):
        return sendMessage(update["object"]['message']['peer_id'],update["object"]['message']['random_id'],"No Game With Such ID :(", attachment= uploadPic(update['object']['message']['peer_id'], "sorry.png"))
    pin = generatePin()
    sendMessage(update["object"]['message']['peer_id'],update["object"]['message']['random_id'], f"{pin} - PIN of your game", keyboard= json.dumps(keyboardStart))
    gameBase.append(actualGame(pin, update["object"]['message']['from_id'], templateId))

def game(text, update):
    game = 0
    for i in gameBase:
        if i.gameFounder == update["object"]['message']['from_id']:
            game = i
            break
    if game == 0:
        return sendMessage(update["object"]['message']['peer_id'],update["object"]['message']['random_id'],"You haven't created game yet, m8 :)", attachment= uploadPic(update['object']['message']['peer_id'], "sorry.png"))
    sendMessage(update["object"]['message']['peer_id'],update["object"]['message']['random_id'],"Game Started!")
    txt = generateList(game.players)
    for i in game.players:
        sendMessage(int(i["id"]), update["object"]['message']['random_id'], "Hello! It's bazed kahoot. Game started in one second. There is a list of our players. Good luck, m8!")
        sendMessage(int(i["id"]), update["object"]['message']['random_id'], txt)
        sendMessage(int(i["id"]), update["object"]['message']['random_id'],  dataBaseQuiz[game.templateId]["questions"][game.actualQuestion]["text"], keyboard= json.dumps(keyboardPlayer))
    game.lastTime = time.time()
    

def connectTo(text, update):
    if "\"" not in text:
        return sendMessage(update["object"]['message']['peer_id'],update["object"]['message']['random_id'], "No \", m8", attachment= uploadPic(update['object']['message']['peer_id'], "must.png"))
    for i in gameBase:
        for b in i.players:
            if b["id"] == int(update["object"]["message"]["from_id"]):
                return sendMessage(update["object"]['message']['peer_id'],update["object"]['message']['random_id'], "You are already in game! or broken code", attachment= uploadPic(update['object']['message']['peer_id'], "must.png"))
    pin = findingNumbers(text[:text.find("\"")])
    s = update["object"]["message"]["text"][update["object"]["message"]["text"].find("\""):] 
    nickname = s[1:s.find("\"")-1]
    if nickname == "":
        nickname = "IDIOT"
    for i in gameBase:
        if i.PIN == pin:
            i.players.append( {"id":int(update["object"]['message']['from_id']), "score":0, "nickname":nickname} )
            sendMessage(i.gameFounder, update["object"]['message']['random_id'], "[id{}|{}] join to us!".format(update["object"]['message']['from_id'],nickname))
            i.players = sorting(i.players)
            sendMessage(i.gameFounder, update["object"]['message']['random_id'], generateList(i.players), keyboard=json.dumps(keyboardStart))
            sendMessage(update["object"]['message']['peer_id'], update["object"]['message']['random_id'], "Welcum to the game, m8!")
            return
    return sendMessage(update["object"]['message']['peer_id'],update["object"]['message']['random_id'], "Wrong pin may be :) or broken code",  attachment= uploadPic( "must.png"))

dataBaseFile = open("dataBase.json", "r+", encoding='utf-8')
dataBaseQuiz = json.load(dataBaseFile)
gameBase = []
print(dataBaseQuiz)

keyboardStart = {   "one_time":True, "buttons":
        [ 
    [ 
        {  
            "action":
            {  
               "type":"text",
               "label":"START"
            },
            "color":"positive"
        }
    ]
        ] 
    }
keyboardPlayer = {   "one_time":True, "buttons":
        [ [ {"action":{ "type":"text","label":"1"},"color":"positive"}, {"action":{ "type":"text","label":"2"},"color":"negative"}],
        [ {"action":{ "type":"text","label":"3"},"color":"primary"}, {"action":{ "type":"text","label":"4"},"color":"secondary"}]
        ] 
    }

token = ""
timeForAnswer = 20

def myMain():
    response = requests.get('https://api.vk.com/method/groups.getLongPollServer', params={'access_token': token, "v":5.131, "group_id":212435180}).json()["response"]
    keyLongPoll = response["key"]
    ts = response["ts"]
    serverLongPoll = response["server"] 
    commands = {"play":lambda:play(text, update),"connect":lambda:connectTo(text, update), "start":lambda:game(text, update)}
    while (True):
        response = requests.get(f"{serverLongPoll}?act=a_check&key={keyLongPoll}&ts={ts}&wait=25&mode=2&version=5.131").json()
        if response["updates"]: 
            for update in response["updates"]:
                if update["type"] == "message_new":
                    #print(update)
                    text = textOrderisation(update["object"]["message"]["text"]) 
                    deal = 0
                    for i in gameBase:
                        if i.lastTime == 0 or findingNumbers(text) == "Nope":
                            break
                        if int(update["object"]['message']['from_id']) in i.playersWhoAnswered:
                            sendMessage(nt(update["object"]['message']['from_id']), int(time.time() * 100000000), "m8, you have already answered")
                            break
                        for j in i.players:
                            if j["id"] == int(update["object"]['message']['from_id']):
                                if findingNumbers(text) in dataBaseQuiz[i.templateId]["questions"][i.actualQuestion]["answers"]:
                                    j["score"] += int(2000 * ((timeForAnswer - (int(time.time()) - int(i.lastTime)) )/timeForAnswer))
                                i.playersWhoAnswered.append(j["id"])
                                deal = 1
                                break
                        if deal == 1:
                            break   
         
                    for i in commands.keys():
                        if i in text:
                            commands[i]()
                            break
                                    
        ts = response["ts"]

def myBack():
    global gameBase
    while True:
        k = gameBase.copy()
        for i in gameBase:
            if i.lastTime == 0:
                continue
            for b in i.players:
                sendMessage(b["id"], int(time.time() * 100000000), f"TIME: {int(time.time() - i.lastTime)}")
        for i in gameBase:
            if i.lastTime != 0:
                if int(time.time()) - int(i.lastTime) > timeForAnswer or len(i.players) == len(i.playersWhoAnswered):
                    i.playersWhoAnswered = []
                    i.playersWhoAnswered.append(i.gameFounder)
                    i.lastTime = time.time()
                    i.players = sorting(i.players)
                    j = generateList(i.players)
                    i.actualQuestion += 1
                    if i.actualQuestion >= len(dataBaseQuiz[i.templateId]["questions"]):
                        for b in i.players:
                            sendMessage(b["id"], int(time.time() * 100000000), "True answer was {} \n Game ended. So, here the list!: \n {}".format( dataBaseQuiz[i.templateId]["questions"][i.actualQuestion -1]["answers"],j), attachment= uploadPic(b["id"],"sorry.png"))
                        gameBase.remove(i)
                        continue
                    for b in i.players:
                        sendMessage(b["id"], int(time.time() * 100000000), "True answer was {} \n Actual list: \n {}".format( dataBaseQuiz[i.templateId]["questions"][i.actualQuestion -1]["answers"],j))
                        sendMessage(b["id"], int(time.time() * 100000000), dataBaseQuiz[i.templateId]["questions"][i.actualQuestion]["text"], keyboard = json.dumps(keyboardPlayer))
        time.sleep(2)

firstThread = Thread(target=myMain)
secondThread = Thread(target=myBack)

firstThread.start()
secondThread.start()