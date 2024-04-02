import logging
import time
import telebot
from time import sleep
import schedule
from threading import Thread
from telegram import *
from telegram.ext import *
from telegram.ext import filters
import random
from tabulate import tabulate
import pickle
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

telbot = telebot.TeleBot('INSERT TOKEN')
chatid = INSERT CHAT ID

n = 0
exclude_powerups = []
exclude_challenges = []
exclude_takenflags = []
exclude_claimedflags = []
exclude_challengelocations = []
counter = 0
anmeldungen = {}
savedchallengesandpowerups = {}
powerupsclaimed = {}
flagscarried = {}
flagcounttake = 0
flagcountclaim = 0
blueflags = 0
redflags = 0

challengeslist = {
    1: {'Name': 'Touch of Water', 'Description': 'Berühre ein Gewässer. Teich, See, Fluss, Bach, etc. Leitungswasser zählt nicht dazu.'},
    2: {'Name': 'The Bridge', 'Description': 'Überquere eine Brücke. Die Brücke muss so groß genug sein, dass du theoretisch auch unter ihr durchgehen könntest.'},
    3: {'Name': 'Be Proud', 'Description': 'Finde eine Deutschlandflagge.'},
    4: {'Name': 'Get drunk', 'Description': 'Erreiche das offiziell Fahrverbot (0,5‰). Nutze den Rechner dazu: https://www.smart-rechner.de/promille/rechner.php'},
    5: {'Name': 'Treasure Hunt', 'Description': 'Finde einen Geocache.'},
    6: {'Name': 'Berlin Meal', 'Description': 'Gönn dir ne Currywurst (oder vegetarische Alternative an einem Ort, wo ebenfalls Currywurst verkauft wird).'},
    7: {'Name': 'Good Boy', 'Description': 'Streichle einen Hund'},
    8: {'Name': 'Find a Dinosaur', 'Description': 'Finde einen Dinosaurier (Muss nicht lebendig sein).'}
}

powerupslist = {
    1: {'Name': 'Tram', 'Description': 'Ein Spieler kann für 15 Minten mit der Tram fahren.'},
    2: {'Name': 'Regio', 'Description': 'Ein Spieler darf einmalig den Regio nutzen.'},
    3: {'Name': 'Hide', 'Description': 'Ein Spieler darf sein GPS auch mit Flagge für 15 Minuten ausschalten'},
    4: {'Name': 'Team Freeze', 'Description': 'Freeze des gesamten gegnerischen Teams für 10 Minuten'},
    5: {'Name': 'Blocked Station', 'Description': 'Das gegnerisches Team darf einen Bahnhof für 20 Minuten nicht benutzen oder durchfahren'},
    6: {'Name': 'No Phone', 'Description': 'Das gegnerisches Team darf 15 Minten nicht das Handy nicht benutzen. Außer die Kamera zum taggen und den Telegram-Bot für Aktionen. Allerdings keinerlei Kommunikation, Google Maps, DB-App oder andere Apps.'},
    7: {'Name': 'I see you', 'Description': 'Das gegnerisches Team muss 10 Minuten ihren Standort teilen, auch wenn sie aktuell keine Flagge besitzen.'},
    8: {'Name': 'UNO Reverse', 'Description': 'Wenn du gefangen wirst, dann muss einmalig dein Fänger in den Freeze oder zum Hauptbahnhof, du aber nicht.'}
}

flaglocations = {
    1: {'Location': 'Wittenau', 'Market': 'Edeka', 'Item': 'Apfel'},
    2: {'Location': 'Reinickendorf', 'Market': 'Lidl', 'Item': 'Banane'},
    3: {'Location': 'Gesundbrunnen', 'Market': 'Aldi', 'Item': 'Rittersport'},
    4: {'Location': 'Pankow', 'Market': 'Lidl', 'Item': 'Smarties'},
    5: {'Location': 'Prenzlau', 'Market': 'REWE', 'Item': 'Eier'},
    6: {'Location': 'Marzahn', 'Market': 'Lidl', 'Item': 'Prinzenrolle'},
    7: {'Location': 'Kaulsdorf', 'Market': 'Netto', 'Item': 'Oreo'},
    8: {'Location': 'Neukölln', 'Market': 'Lidl', 'Item': 'Gewürzgurken'},
    9: {'Location': 'Kreuzberg', 'Market': 'REWE', 'Item': 'Haribo'},
    10: {'Location': 'Schöneberg', 'Market': 'REWE', 'Item': 'Pringels'},
    11: {'Location': 'Steglitz', 'Market': 'Aldi', 'Item': 'PickUp'},
    12: {'Location': 'Zehlendorf', 'Market': 'EDEKA', 'Item': 'Kinderschokolade'},
    13: {'Location': 'Ruhleben', 'Market': 'Aldi', 'Item': 'Ü-Ei'},
    14: {'Location': 'Charlottenburg', 'Market': 'Netto', 'Item': 'NicNacs'},
    15: {'Location': 'Spandau', 'Market': 'EDEKA', 'Item': 'Skittles'}
}

challengelocations = {
    1: {'Name': 'Baumschulenweg'},
    2: {'Name': 'Jungfernheide'},
    3: {'Name': 'Wannsee'},
    4: {'Name': 'Pankow'},
    5: {'Name': 'Mahlsdorf'},
    6: {'Name': 'Tempelhof'},
    7: {'Name': 'Wilmersdorf'},
    8: {'Name': 'Ostkreuz'}
}


def savestate():

    if os.path.exists("backup5.pkl"):
        os.remove("backup5.pkl")
    if os.path.exists("backup4.pkl"):
        os.rename("backup4.pkl", "backup5.pkl")  
    if os.path.exists("backup3.pkl"):
        os.rename("backup3.pkl", "backup4.pkl")  
    if os.path.exists("backup2.pkl"):
        os.rename("backup2.pkl", "backup3.pkl")  
    if os.path.exists("backup1.pkl"):
        os.rename("backup1.pkl", "backup2.pkl")  
    if os.path.exists("backup0.pkl"):
        os.rename("backup0.pkl", "backup1.pkl")  

    with open('backup0.pkl', 'wb') as f:
        pickle.dump((exclude_powerups, exclude_challenges, exclude_takenflags, exclude_claimedflags, exclude_challengelocations, counter, anmeldungen, savedchallengesandpowerups, powerupsclaimed, flagcountclaim, flagscarried, flagcounttake, blueflags, redflags, n), f)

def loadstate(name):
    global exclude_powerups
    global exclude_challenges
    global exclude_takenflags
    global exclude_claimedflags
    global exclude_challengelocations
    global counter
    global anmeldungen
    global savedchallengesandpowerups
    global powerupsclaimed
    global flagcountclaim
    global flagscarried
    global flagcounttake
    global blueflags
    global redflags
    global n

    with open(name, 'rb') as f:
        exclude_powerups, exclude_challenges, exclude_takenflags, exclude_claimedflags, exclude_challengelocations, counter, anmeldungen, savedchallengesandpowerups, powerupsclaimed, flagcountclaim, flagscarried, flagcounttake, blueflags, redflags, n = pickle.load(f)
    if name == "backup0.pkl":
        telbot.send_message(chatid, text=f"Backup geladen.")
    else:
        telbot.send_message(chatid, text=f"Letzte Aktion rückgängig gemacht.")
    
    flagtakerest = 15-flagcounttake
    flagclaimrest= 15-flagcountclaim

    anmeldungen_data = [(f"{anmeldung.get('Name','')} - Team {anmeldung.get('Team','')}") for anmeldung in anmeldungen.values()]
    anmeldungen_table = "\n".join(anmeldungen_data)

    flags_data = [(f"{flaglocations[flags.get('flag_id','')]['Item']} : {anmeldungen[flags.get('user_id','')]['Name']} (Team {anmeldungen[flags.get('user_id','')]['Team']})") for flags in flagscarried.values()]
    flags_table = "\n".join(flags_data)

    powerupsclaimed_data = [(f"{powerupslist.get(powerup_id, {}).get('Name', 'Unknown')} - {powerup_info.get('Team','')}") for powerup_id, powerup_info in powerupsclaimed.items()]
    powerupsclaimed_table = "\n".join(powerupsclaimed_data)

    telbot.send_message(chatid, text=f"Spieler:\n{anmeldungen_table}\nAktueller Punkestand:\nRot: {redflags} - Blau: {blueflags}\nEs sind noch {flagclaimrest} Flaggen im Spiel.\nEs sind noch {flagtakerest} Flaggen an ihren Positionen.\nAktuelle Flaggen im Spiel:\n{flags_table}\nPowerUps:\n{powerupsclaimed_table}")

def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)

def lunchin5min():
    telbot.send_message(chatid, text=f"Die Mittagspause beginnt in 5 Minuten.")
    return schedule.CancelJob
def lunchstart():
    telbot.send_message(chatid, text=f"30 Minuten Mittagspause startet jetzt. Es dürfen keine Flaggen aufgenommen oder Challenges durchgeführt werden. Kehrt zum Ende der Pause an euren momentanen Standort zurück.")
    return schedule.CancelJob
def lunch5min():
    telbot.send_message(chatid, text=f"Die Mittagspause endet in 5 Minuten")
    return schedule.CancelJob
def lunchend():
    telbot.send_message(chatid, text=f"Die Pause ist vorbei. Weiter geht's!")
    return schedule.CancelJob

def freeze1minwarning(name):
    telbot.send_message(chatid, text=f"Noch 1 Minute. Mach dich bereit {str(next(iter(name)))}.")
    return schedule.CancelJob
def freeze5secwarning(name):
    telbot.send_message(chatid, text=f"{str(next(iter(name)))} ist wieder unterwegs in:")
    telbot.send_message(chatid, text=f"--- 5 ---")
    return schedule.CancelJob
def freeze4secwarning(name):
    telbot.send_message(chatid, text=f"--- 4 ---")
    return schedule.CancelJob
def freeze3secwarning(name):
    telbot.send_message(chatid, text=f"--- 3 ---")
    return schedule.CancelJob
def freeze2secwarning(name):
    telbot.send_message(chatid, text=f"--- 2 ---")
    return schedule.CancelJob
def freeze1secwarning(name):
    telbot.send_message(chatid, text=f"--- 1 ---")
    return schedule.CancelJob
def freezeend(name):
    telbot.send_message(chatid, text=f"Du bist frei! GOGOGOGO!")
    return schedule.CancelJob

def tramtenminwarning(name):
    telbot.send_message(chatid, text=f"{str(next(iter(name)))} darf noch 10min mit der Tram fahren.")
    return schedule.CancelJob
def tramend(name):
    telbot.send_message(chatid, text=f"Das war's. Die Tram ist nun wieder gesperrt.")
    return schedule.CancelJob

def hidegpsend(name):
    telbot.send_message(chatid, text=f"{str(next(iter(name)))} muss sein GPS jetzt wieder einschalten.")
    return schedule.CancelJob

def teamfreezeend(team):
    telbot.send_message(chatid, text=f"Der Freeze ist vorbei. Team {str(next(iter(team)))} darf sich wieder bewegen.")
    return schedule.CancelJob

def stationblockend(team):
    telbot.send_message(chatid, text=f"Die Blockade ist vorbei. Team {str(next(iter(team)))} darf sich wieder bewegen.")
    return schedule.CancelJob

def nophoneend(team):
    telbot.send_message(chatid, text=f"Die Sperre ist vorbei. Team {str(next(iter(team)))} darf das Handy wieder in vollem Umfang benutzen.")
    return schedule.CancelJob

def showgpsend(team):
    telbot.send_message(chatid, text=f"Die Zeit ist um. Die Spieler von Team {str(next(iter(team)))} können ihren GPS-Standort wieder ausschalten, sofern sie aktuell keine Flagge tragen.")
    return schedule.CancelJob

def blockoddend(team):
    telbot.send_message(chatid, text=f"Die Einschränkung ist vorbei. Team {str(next(iter(team)))} darf wieder in alle Bahnen einsteigen.")
    return schedule.CancelJob



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    persistent_keyboard = [['Anmeldung']]
    
    await context.bot.send_message(chat_id=user_id, text="Willkommen!", reply_markup=ReplyKeyboardMarkup(persistent_keyboard))   
   
async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=chatid, text="Herzlich Willkommen bei \n \n- CAPTURE THE FLAG BERLIN -")
    await context.bot.send_message(chat_id=chatid, text="Regeln: \n\
    - Es gibt 15 Flaggen und das erste Team, welches 8 Flaggen zum Hauptbahnhof bringt, gewinnt.\n\
    - Erlaubte Transportmittel sind S-Bahn, U-Bahn und die eigenen Füße.\n\
    - Verbotenes bleibt verboten (nicht bei Rot über Ampeln, nicht über die Gleise, kein Ladendiebstahl, kein Aufhalten der S-Bahn-Türen, etc)\n\
    - Alle Aktionen (Erhalten einer Flagge, absolvieren einer Challenge, Fangen eines Gegners, ...) müssen mit einem Beweisvideoclip im Gruppenchat dokumentiert werden.")  
    await context.bot.send_message(chat_id=chatid, text="Flaggen: \n\
    - Eine Flagge gilt als aufgenommen sobald dafür bezahlt wurde.\n\
    - Flaggen können nicht abgelegt werden, sondern nur von einem gegnerischen Spieler abgenommen oder von einem Teampartner übernommen werden.\n\
    - So lange man im Besitz einer Flagge ist muss der GPS-Standort mit dem gegnerischen Team geteilt werden.\n\
    - Flaggen sind erobert, sobald sie sich innerhalb des Hauptbahnhof-Gebäudes befinden.")  
    await context.bot.send_message(chat_id=chatid, text="Fangen: \n\
    - Spieler, welche im Besitz mindestens einer Flagge sind, können nur durch physischen Kontakt gefangen werden. In diesem Fall müssen sie alle ihre Flaggen an den Fänger abgeben und sind für 10 Minuten eingefroren. (Sie müssen am Ende der Zeitspanne am gleichen Ort sein wie zu Beginn)\n\
    - Spieler, welche im Besitz mindestens einer Flagge sind, können keinen anderen Spieler fangen.\n\
    - Spieler, welche im Besitz keiner Flagge sind, können andere Spieler ohne Flaggen über ein eindeutig identifizierbares Bild/Video mit ihrem Handy fangen. Sobald man das geschafft hat, muss man den Gefangenen mit einem 'Hab dich!' dahingehend informieren und das Beweismaterial im Anschluss in die Gruppe posten.\n\
    - Der 'gefangene' Spieler muss daraufhin auf dem schnellsten Weg zurück zum Hauptbahnhof und von dort wieder neu starten. Er darf auf dem Weg dorthin keine anderen Spieler fangen, Flaggen aufnehmen oder Challenges machen. Bis der Hauptbahnhof erreicht wird, muss er für das gegnerische Team seinen GPS-Standort teilen.\n\
    - Es muss versucht werden zu fangen, sobald sich die Möglichkeit ergibt. Wenn ich also sehe, dass ein Spieler des gegnerischen Teams mit mir in der Bahn ist, dann muss ich ihn so früh wie möglich fangen und darf nicht warten, bis wir den Zielbahnhof erreichen.\n\
    - Fangen innerhalb des Hauptbahnhofes ist nicht möglich.")  
    await context.bot.send_message(chat_id=chatid, text="Challenges/PowerUps: \n\
    - Challenges müssen beendet werden, bevor man erneut mit einer Bahn/Tram fährt. \n\
    - Challenges können erneut gestartet oder auch von beiden Teams gleichzeitig durchgeführt werden. Derjenige, der sie als erstes erfolgreich beendet erhält das PowerUp.\n\
    - PowerUps werden für das Team gewonnen und können von jedem Spieler des Teams eingesetzt werden.")

    time.sleep(3)

    table_data = [(f"Flagge {flag_id} - {flag_name['Location']} - {flag_name['Market']} - {flag_name['Item']}") for flag_id, flag_name in flaglocations.items()]
    table = "\n".join(table_data)
    await context.bot.send_message(chat_id=chatid, text=f"Liste Flaggen: \n{table}")

    time.sleep(2)
    
    table_data = [(f"Challenge {challenge_id} - {challenge_name['Name']} - {challenge_name['Description']}") for challenge_id, challenge_name in challengeslist.items()]
    table = "\n".join(table_data)
    await context.bot.send_message(chat_id=chatid, text=f"Liste Challenges: \n{table}") 

    time.sleep(2)
    
    table_data = [(f"Challenge {powerup_id} - {powerup_name['Name']} - {powerup_name['Description']}") for powerup_id, powerup_name in powerupslist.items()]
    table = "\n".join(table_data)
    await context.bot.send_message(chat_id=chatid, text=f"Liste PowerUps: \n{table}") 

    #schedule.every().day.at("12:55").do(lunchin5min)
    #schedule.every().day.at("13:00").do(lunchstart)
    #schedule.every().day.at("13:25").do(lunch5min)
    #schedule.every().day.at("13:30").do(lunchend)


async def timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    schedule.every(1).minutes.do(timerend)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Timer \n startet.")

async def loadbackup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_name = "backup0.pkl"
    loadstate(file_name)

async def undo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text
    number = int(command.split("/undo")[1])
    file_name = f"backup{number}.pkl"
    loadstate(file_name)

async def resetall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global exclude_powerups
    global exclude_challenges
    global exclude_takenflags
    global exclude_claimedflags
    global exclude_challengelocations
    global counter
    global anmeldungen
    global savedchallengesandpowerups
    global powerupsclaimed
    global flagcountclaim
    global flagscarried
    global flagcounttake
    global blueflags
    global redflags
    global name
    global n

    n = 0
    exclude_powerups = []
    exclude_challenges = []
    exclude_takenflags = []
    exclude_claimedflags = []
    exclude_challengelocations = []
    counter = 0
    savedchallengesandpowerups = {}
    powerupsclaimed = {}
    flagscarried = {}
    flagcounttake = 0
    flagcountclaim = 0
    blueflags = 0
    redflags = 0

    persistent_keyboard = [['Anmeldung']]

    for anmeldungen_id, anmeldungen_name in anmeldungen.items():
        await context.bot.send_message(chat_id=anmeldungen_id, text="Reset successful.", reply_markup=ReplyKeyboardMarkup(persistent_keyboard))  

    anmeldungen = {}

async def register(update: Update, context: CallbackContext) -> None:
    global anmeldungen   
    user = update.message.from_user
    user_id = update.message.from_user.id
    name = update.message.from_user.first_name
    
    # Überprüfe, ob der Benutzer bereits angemeldet ist und einen Namen hat
    if user_id in anmeldungen and anmeldungen[user_id]['Name'] is not None:
        name = anmeldungen[user_id]['Name']
        await context.bot.send_message(chat_id=user_id, text=f"Hallo {name}! Du bist bereits angemeldet.")
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Team Rot", callback_data='Rot')],
            [InlineKeyboardButton("Team Blau", callback_data='Blau')]
        ])
        await context.bot.send_message(chat_id=user_id, text=f"Hallo {name}! Wähle dein Team:", reply_markup=keyboard)

async def receive_team(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    team = query.data
    user = query.from_user
    name = query.from_user.first_name

    if user_id not in anmeldungen:
        anmeldungen[user_id] = {'Name': f"{name}", 'Team': team, 'User': user}
        table_data = [(f"{anmeldung.get('Name','')} - Team {anmeldung.get('Team','')}") for anmeldung in anmeldungen.values()]
        table = "\n".join(table_data)
        persistent_keyboard = [['Flags', 'Power-Ups', 'Tagged']]
        await context.bot.send_message(chat_id=user_id, text=f"Vielen Dank! Du bist im Team {team}.", reply_markup=ReplyKeyboardMarkup(persistent_keyboard))
        await context.bot.send_message(chat_id=chatid, text=f"Willkommen {anmeldungen[user_id]['Name']} im Team {team}.\nAnmeldungen bisher:\n{table}")
    else:
        name = anmeldungen[user_id]['Name']
        await context.bot.send_message(chat_id=user_id, text=f"Hallo {name}! Du bist bereits angemeldet.")

async def flags(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Flagge aufgenommen", callback_data='takeflag')],
        [InlineKeyboardButton("Flagge übergeben", callback_data='giveflag')],
        [InlineKeyboardButton("Flagge erobert", callback_data='claimflag')]
    ])

    await context.bot.send_message(chat_id=user_id, text=f"Was möchtest du tun?", reply_markup=keyboard)

async def takeflag(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    flag_buttons = []

    for flag_id, flag_name in flaglocations.items():
        if flag_id not in exclude_takenflags:  # Überprüfe, ob die Flagge bereits weg ist
            # Füge einen Inline-Button für die locations hinzu
            button_text = f"Flagge {flag_id} - {flag_name['Item']}"
            callback_data = f"takeflagresult_{flag_id}"  # Du kannst dies nach Bedarf anpassen
            button = InlineKeyboardButton(button_text, callback_data=callback_data)
            flag_buttons.append([button])
    keyboard = InlineKeyboardMarkup(flag_buttons)
    if flag_buttons:
        await context.bot.send_message(chat_id=user_id, text=f"Welche Flagge hast du aufgenommen?", reply_markup=keyboard)
    else:
        await context.bot.send_message(chat_id=user_id, text=f"Keine Flaggen mehr übrig.", reply_markup=keyboard)    
    

async def takeflagresult(update: Update, context: CallbackContext) -> None:
    global flagcounttake
    global exclude_takenflags
    query = update.callback_query
    user_id = query.from_user.id
    flag = query.data

    callback_data_parts = query.data.split('_')
    if len(callback_data_parts) == 2 and callback_data_parts[0] == 'takeflagresult':
        flag_id = int(callback_data_parts[1])
        flagcounttake = flagcounttake +1
        flagcount = 15-flagcounttake
        exclude_takenflags.append(flag_id)      
        flagscarried[flag_id] = {'flag_id': flag_id, 'user_id': user_id}
        table_data = [(f"{flaglocations[flags.get('flag_id','')]['Item']} : {anmeldungen[flags.get('user_id','')]['Name']} (Team {anmeldungen[flags.get('user_id','')]['Team']})") for flags in flagscarried.values()]
        table = "\n".join(table_data)
        savestate()
        await context.bot.send_message(chat_id=user_id, text=f"Du hast Flagge {flag_id} aufgenommen.")
        await context.bot.send_message(chat_id=chatid, text=f"Flagge {flag_id} wurde von {anmeldungen[user_id]['Name']} (Team {anmeldungen[user_id]['Team']}) aufgenommen.")
        await context.bot.send_message(chat_id=chatid, text=f"Es sind noch {flagcount} Flaggen an ihren Positionen.")
        await context.bot.send_message(chat_id=chatid, text=f"Aktuelle Flaggen im Spiel:\n{table}")



async def claimflag(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id    
    flag_buttons = []

    """
    for flag_id, flag_name in flaglocations.items():
        if flag_id not in exclude_claimedflags:  # Überprüfe, ob die Flagge bereits weg ist
            if flag_id in exclude_takenflags:
                # Füge einen Inline-Button für die locations hinzu
                button_text = f"Flagge {flag_id} - {flag_name['Item']}"
                callback_data = f"claimflagresult_{flag_id}"  # Du kannst dies nach Bedarf anpassen
                button = InlineKeyboardButton(button_text, callback_data=callback_data)
                flag_buttons.append([button])
    keyboard = InlineKeyboardMarkup(flag_buttons)    
    """
    count = 0
    for flag_id, flag_info in flagscarried.items():
        if user_id == flag_info['user_id']:
            count = count + 1

    keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Ja", callback_data='claimflagresult')],
            [InlineKeyboardButton("Nein", callback_data='notatcentral')]
        ])

    if count > 0:
        await context.bot.send_message(chat_id=user_id, text=f"Bist du am Hauptbahnhof?", reply_markup=keyboard)
    else:
        await context.bot.send_message(chat_id=user_id, text=f"Du hast keine Flaggen.")

async def notatcentral(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await context.bot.send_message(chat_id=user_id, text=f"Dann mal los! Hop Hop.")

async def claimflagresult(update: Update, context: CallbackContext) -> None:
    global flagcountclaim
    global blueflags
    global redflags
    global exclude_claimedflags
    global flagscarried
    query = update.callback_query
    user_id = query.from_user.id
    flag = query.data
    flags_to_delete = []

    for flag_id, flag_info in flagscarried.items():
        if user_id == flag_info['user_id']:
            flagcountclaim = flagcountclaim +1
            flagcount = 15-flagcountclaim
            exclude_claimedflags.append(flag_id)
            flags_to_delete.append(flag_id)
            await context.bot.send_message(chat_id=user_id, text=f"Du hast Flagge {flag_id} erobert.")
            await context.bot.send_message(chat_id=chatid, text=f"Flagge {flag_id} wurde von {anmeldungen[user_id]['Name']} (Team {anmeldungen[user_id]['Team']}) erobert.")
            if "Blau" in anmeldungen[user_id]['Team']:
                blueflags = blueflags + 1
            if "Rot" in anmeldungen[user_id]['Team']:
                redflags = redflags + 1  

    for flag_id in flags_to_delete:
        del flagscarried[flag_id]

    savestate()

    await context.bot.send_message(chat_id=chatid, text=f"Es sind noch {flagcount} Flaggen im Spiel.")
    await context.bot.send_message(chat_id=chatid, text=f"Aktueller Punkestand:\nRot: {redflags} - Blau: {blueflags}")

async def giveflag(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    your_team = anmeldungen[user_id]['Team']
    member_buttons = []

    count = 0
    for flag_id, flag_info in flagscarried.items():
        if user_id == flag_info['user_id']:
            count = count + 1

    if count > 0:
        for player_id, player_info in anmeldungen.items():
            if player_id != user_id and player_info['Team'] == your_team:
                # Füge einen Inline-Button für den Gegner hinzu
                button_text = f"{player_info['Name']}"
                callback_data = f"giveflagresult_{player_id}"  # Du kannst dies nach Bedarf anpassen
                button = InlineKeyboardButton(button_text, callback_data=callback_data)
                member_buttons.append([button])

        keyboard = InlineKeyboardMarkup(member_buttons)
        await context.bot.send_message(chat_id=user_id, text=f"An wen möchtest du deine Flagge(n) übergeben?", reply_markup=keyboard)
    else:
        await context.bot.send_message(chat_id=user_id, text=f"Du hast keine Flaggen zum übergeben.")


async def giveflagresult(update: Update, context: CallbackContext) -> None:
    global flagcounttake
    global exclude_takenflags
    query = update.callback_query
    user_id = query.from_user.id
    flag = query.data

    callback_data_parts = query.data.split('_')
    if len(callback_data_parts) == 2 and callback_data_parts[0] == 'giveflagresult':
        give_to_player_id = int(callback_data_parts[1])

        count = 0
        for flag_id, flag_info in flagscarried.items():
            if user_id == flag_info['user_id']:
                flagscarried[flag_id]['user_id'] = give_to_player_id
                count = count + 1

        table_data = [(f"{flaglocations[flags.get('flag_id','')]['Item']} : {anmeldungen[flags.get('user_id','')]['Name']} (Team {anmeldungen[flags.get('user_id','')]['Team']})") for flags in flagscarried.values()]
        table = "\n".join(table_data)

        savestate()

        await context.bot.send_message(chat_id=user_id, text=f"Du hast deine Flaggen an {anmeldungen[give_to_player_id]['Name']} weitergegeben.", reply_markup=keyboard)
        await context.bot.send_message(chat_id=chatid, text=f"Flaggenübergabe: {anmeldungen[user_id]['Name']} --> {anmeldungen[give_to_player_id]['Name']}")    
        await context.bot.send_message(chat_id=chatid, text=f"Aktuelle Flaggen im Spiel:\n{table}")

async def tagged(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    opponent_buttons = []
    your_team = anmeldungen[user_id]['Team']

    if anmeldungen[user_id]['Team'] == "Rot":
        enemyteam = "Blau"           
    if anmeldungen[user_id]['Team'] == "Blau":
        enemyteam = "Rot"

    for player_id, player_info in anmeldungen.items():
        if player_id != user_id and player_info['Team'] != your_team:
            # Füge einen Inline-Button für den Gegner hinzu
            button_text = f"{player_info['Name']}"
            if 8 in powerupsclaimed and enemyteam == powerupsclaimed[8]['Team']:
                callback_data = f"askforreverse_{player_id}_{user_id}"  # Du kannst dies nach Bedarf anpassen
            else:
                callback_data = f"taggedresult_normal_{player_id}"
            button = InlineKeyboardButton(button_text, callback_data=callback_data)
            opponent_buttons.append([button])

    keyboard = InlineKeyboardMarkup(opponent_buttons)
    await context.bot.send_message(chat_id=user_id, text=f"Wen hast du erwischt?", reply_markup=keyboard)

async def askforreverse(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    callback_data_parts = query.data.split('_')

    if len(callback_data_parts) == 3 and callback_data_parts[0] == 'askforreverse':
        tagged_player_id = int(callback_data_parts[1])
        tagger_player_id = int(callback_data_parts[2])

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Ja", callback_data=f'taggedresult_reverse_{tagger_player_id}')],
            [InlineKeyboardButton("Nein", callback_data=f'taggedresult_normal_{tagged_player_id}')]
        ])

        await context.bot.send_message(chat_id=tagged_player_id, text=f"Möchtest du das PowerUp {powerupslist[8]['Name']} einsetzen?", reply_markup=keyboard)
        await context.bot.send_message(chat_id=tagger_player_id, text=f"{anmeldungen[tagged_player_id]['Name']} überlegt, das PowerUp {powerupslist[8]['Name']} einsetzen.")

async def taggedresult(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    callback_data_parts = query.data.split('_')

    if len(callback_data_parts) == 3 and callback_data_parts[0] == 'taggedresult':
        reverse = callback_data_parts[1]
        tagged_player_id = int(callback_data_parts[2])

        if reverse == 'reverse':
            powerupsclaimed[8] = {'Team': 'Used'}

        count = 0
        for flag_id, flag_info in flagscarried.items():
            if tagged_player_id == flag_info['user_id']:
                flagscarried[flag_id]['user_id'] = user_id
                count = count + 1

        if count > 0:
            tagged_player_name = anmeldungen.get(tagged_player_id, {}).get('Name', 'Unbekannt')
            table_data = [(f"{flaglocations[flags.get('flag_id','')]['Item']} : {anmeldungen[flags.get('user_id','')]['Name']} (Team {anmeldungen[flags.get('user_id','')]['Team']})") for flags in flagscarried.values()]
            table = "\n".join(table_data)
            await context.bot.send_message(chat_id=user_id, text=f"Du hast {tagged_player_name} erwischt.")
            await context.bot.send_message(chat_id=chatid, text=f"{tagged_player_name} wurde erwischt. Der 10-Minuten-Freeze beginnt JETZT")
            await context.bot.send_message(chat_id=chatid, text=f"Die Flagge(n) wurden übergeben. Flaggen im Spiel:\n{table}")
            
            schedule.every(540).seconds.do(freeze1minwarning, name={tagged_player_name})
            schedule.every(595).seconds.do(freeze5secwarning, name={tagged_player_name})
            schedule.every(596).seconds.do(freeze4secwarning, name={tagged_player_name})
            schedule.every(597).seconds.do(freeze3secwarning, name={tagged_player_name})
            schedule.every(598).seconds.do(freeze2secwarning, name={tagged_player_name})
            schedule.every(599).seconds.do(freeze1secwarning, name={tagged_player_name})
            schedule.every(600).seconds.do(freezeend, name={tagged_player_name})

        if count == 0:

            keyboard = [['Zurück am Hauptbahnhof']]

            tagged_player_name = anmeldungen.get(tagged_player_id, {}).get('Name', 'Unbekannt')
            await context.bot.send_message(chat_id=user_id, text=f"Du hast {tagged_player_name} erwischt.")
            await context.bot.send_message(chat_id=chatid, text=f"{tagged_player_name} wurde erwischt. Rückkehr zum Hauptbahnhof erforderlich.")       
            await context.bot.send_message(chat_id=tagged_player_id, text=f"Du wurdest erwischt und musst zum Hauptbahnhof zurückkehren.", reply_markup=ReplyKeyboardMarkup(keyboard))       
    else:
        await context.bot.send_message(chat_id=user_id, text=f"Ungültige Auswahl.")

async def returnmainstation(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if update.message:
        user_id = update.message.from_user.id
    
    if query:
        callback_data_parts = query.data.split('_')
        user_id = query.from_user.id

    if query and len(callback_data_parts) == 2 and callback_data_parts[0] == 'returnmainstation':
        status = callback_data_parts[1]
        if status == 'pending':
            await context.bot.send_message(chat_id=user_id, text=f"Na dann beeil dich!")
        if status == 'done':
            persistent_keyboard = [['Flags', 'Power-Ups', 'Tagged']]
            await context.bot.send_message(chat_id=user_id, text=f"Sehr gut! Du darfst nun wieder aktiv mitspielen.", reply_markup=ReplyKeyboardMarkup(persistent_keyboard))

    else:

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Ja", callback_data=f'returnmainstation_done')],
            [InlineKeyboardButton("Nein", callback_data=f'returnmainstation_pending')]
        ])

        await context.bot.send_message(chat_id=user_id, text=f"Bist du zum Hauptbahnhof zurückgekehrt?", reply_markup=keyboard)

async def powerups(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Challenge starten", callback_data='locationselection_challenge')],
        [InlineKeyboardButton("Power-Up erhalten", callback_data='locationselection_powerup')],
        [InlineKeyboardButton("Power-Up einsetzen", callback_data='selectpowerup')]
    ])

    await context.bot.send_message(chat_id=user_id, text=f"Was möchtest du tun?", reply_markup=keyboard)

async def locationselection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    location_buttons = []
    callback_data_parts = query.data.split('_')

    if len(callback_data_parts) == 2 and callback_data_parts[0] == 'locationselection' and callback_data_parts[1] == 'challenge':           
        for location_id, location_name in challengelocations.items():
            if location_id not in exclude_challengelocations:  # Überprüfe, ob die Flagge bereits weg ist# Füge einen Inline-Button  hinzu
                button_text = f"{location_name['Name']}"
                callback_data = f"startchallenge_{location_id}"  # Du kannst dies nach Bedarf anpassen
                button = InlineKeyboardButton(button_text, callback_data=callback_data)
                location_buttons.append([button])
        keyboard = InlineKeyboardMarkup(location_buttons)
        if location_buttons:
            await context.bot.send_message(chat_id=user_id, text=f"Wo bist du gerade?", reply_markup=keyboard)
        else:
            await context.bot.send_message(chat_id=user_id, text=f"Alle Challenges abgeschlossen.", reply_markup=keyboard)
    elif len(callback_data_parts) == 2 and callback_data_parts[0] == 'locationselection' and callback_data_parts[1] == 'powerup':
        for location_id, location_name in challengelocations.items():
            if location_id in savedchallengesandpowerups and location_id not in exclude_challengelocations: 
                button_text = f"{challengeslist[int(savedchallengesandpowerups[location_id]['Challenge'])]['Name']}"
                callback_data = f"getpowerup_{location_id}"  # Du kannst dies nach Bedarf anpassen
                button = InlineKeyboardButton(button_text, callback_data=callback_data)
                location_buttons.append([button])
        keyboard = InlineKeyboardMarkup(location_buttons)
        if location_buttons:
            await context.bot.send_message(chat_id=user_id, text=f"Welche Challenge hast du erfolgreich abgeschlossen?", reply_markup=keyboard)
        else:
            await context.bot.send_message(chat_id=user_id, text=f"Es wurde aktuell keine Challenge gestartet.", reply_markup=keyboard)
    else:
        await context.bot.send_message(chat_id=user_id, text=f"Ungültige Auswahl.")  

async def startchallenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global exclude_powerups
    global exclude_challenges
    global counter
    global savedchallengesandpowerups
    query = update.callback_query
    user_id = query.from_user.id
    
    callback_data_parts = query.data.split('_')
    location_id = int(callback_data_parts[1])

    if location_id not in savedchallengesandpowerups:
        while counter < 8:
            challenge = random.randint(1, 8)  # Generiere eine Zufallszahl zwischen 1 und 8
            if challenge not in exclude_challenges:  # Überprüfe, ob die Zahl weder 6 noch 3 ist
                exclude_challenges.append(challenge)  # Füge die neue Zufallszahl dem Array hinzu
                break  # Beende die Schleife, wenn die Bedingung erfüllt ist
        while counter < 8:
            powerup = random.randint(1, 8)  # Generiere eine Zufallszahl zwischen 1 und 8
            if powerup not in exclude_powerups:  # Überprüfe, ob die Zahl weder 6 noch 3 ist
                exclude_powerups.append(powerup)  # Füge die neue Zufallszahl dem Array hinzu
                break  # Beende die Schleife, wenn die Bedingung erfüllt ist
        counter += 1   
        if counter > 8:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Keine Challenge mehr übrig.")
        else:     
            savedchallengesandpowerups[location_id] = {'PowerUp': f"{powerup}", 'Challenge': f"{challenge}"}                
    else:  
        challenge = int(savedchallengesandpowerups[location_id]['Challenge'])
        powerup = int(savedchallengesandpowerups[location_id]['PowerUp'])

    savestate()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Schaffe die Challenge:\n=== {challengeslist[challenge]['Name']} ===\n{challengeslist[challenge]['Description']}\num folgendes PowerUp zu erhalten:\n=== {powerupslist[powerup]['Name']} ===\n{powerupslist[powerup]['Description']}")
    await context.bot.send_message(chat_id=chatid, text=f"{anmeldungen[user_id]['Name']} hat die Challenge '{challengeslist[challenge]['Name']}' in {challengelocations[location_id]['Name']} gestartet um das PowerUp '{powerupslist[powerup]['Name']}' zu erhalten.")     

async def getpowerup(update: Update, context: CallbackContext) -> None:
    global exclude_challengelocations
    global powerupsclaimed
    query = update.callback_query
    user_id = query.from_user.id
    callback_data_parts = query.data.split('_')
    if len(callback_data_parts) == 2 and callback_data_parts[0] == 'getpowerup':
        location_id = int(callback_data_parts[1])
        powerup = savedchallengesandpowerups[location_id]['PowerUp']
        powerup = int(powerup)
        powerupsclaimed[powerup] = {'Team': anmeldungen[user_id]['Team']}
        exclude_challengelocations.append(location_id)

    savestate()

    await context.bot.send_message(chat_id=user_id, text=f"Glückwunsch. Dein Team hat das PowerUp '{powerupslist[powerup]['Name']}' erhalten.")  
    await context.bot.send_message(chat_id=chatid, text=f"Team {powerupsclaimed[powerup]['Team']} hat das Powerup '{powerupslist[powerup]['Name']}' bekommen.")

async def selectpowerup(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    powerup_buttons = []
    for powerup_id, powerup_name in powerupslist.items():
        if powerup_id in powerupsclaimed:
            if powerupsclaimed[powerup_id]['Team'] == anmeldungen[user_id]['Team']: 
                if powerup_id != 8:
                    button_text = f"{powerup_name['Name']}"
                    callback_data = f"usepowerup_{powerup_id}"  # Du kannst dies nach Bedarf anpassen
                    button = InlineKeyboardButton(button_text, callback_data=callback_data)
                    powerup_buttons.append([button])
    keyboard = InlineKeyboardMarkup(powerup_buttons)   
    if powerup_buttons:
        await context.bot.send_message(chat_id=user_id, text=f"Welches PowerUp möchtest du einsetzen?", reply_markup=keyboard)
    else:
        await context.bot.send_message(chat_id=user_id, text=f"Dein Team hat aktuell keine PowerUps.", reply_markup=keyboard)  

async def usepowerup(update: Update, context: CallbackContext) -> None:
    global exclude_challengelocations
    global powerupsclaimed
    query = update.callback_query
    user_id = query.from_user.id
    callback_data_parts = query.data.split('_')
    powerup = int(callback_data_parts[1])
    powerupsclaimed[powerup] = {'Team': 'Used'}

           
    if anmeldungen[user_id]['Team'] == "Rot":
        enemyteam = "Blau"           
    if anmeldungen[user_id]['Team'] == "Blau":
        enemyteam = "Rot"

    savestate()

    await context.bot.send_message(chat_id=chatid, text=f"Das PowerUp '{powerupslist[powerup]['Name']}' wurde von Team {anmeldungen[user_id]['Team']} eingesetzt.") 
    if powerup == 1:
        await context.bot.send_message(chat_id=user_id, text=f"Du hast das PowerUp '{powerupslist[powerup]['Name']}' eingesetzt und darfst jetzt 15 Minuten die Tram benutzen.") 
        await context.bot.send_message(chat_id=chatid, text=f"{anmeldungen[user_id]['Name']} darf jetzt 15 Minuten die Tram benutzen.")
        schedule.every(15).minutes.do(tramend, name={anmeldungen[user_id]['Name']})
        schedule.every(14).minutes.do(tramtenminwarning, name={anmeldungen[user_id]['Name']}) 
    if powerup == 2:
        await context.bot.send_message(chat_id=user_id, text=f"Du hast das PowerUp '{powerupslist[powerup]['Name']}' eingesetzt und darfst jetzt einmalig mit einem Regio fahren.") 
        await context.bot.send_message(chat_id=chatid, text=f"{anmeldungen[user_id]['Name']} darf jetzt einmalig mit einem Regio fahren.")
    if powerup == 3:
        await context.bot.send_message(chat_id=user_id, text=f"Du hast das PowerUp '{powerupslist[powerup]['Name']}' eingesetzt und darfst dein GPS jetzt 15 Minuten ausschalten.") 
        await context.bot.send_message(chat_id=chatid, text=f"{anmeldungen[user_id]['Name']} darf sein GPS jetzt 15 Minuten ausschalten.")
        schedule.every(15).minutes.do(hidegpsend, name={anmeldungen[user_id]['Name']})
    if powerup == 4:
        await context.bot.send_message(chat_id=chatid, text=f"Du hast das PowerUp '{powerupslist[powerup]['Name']}' eingesetzt und das Team {enemyteam} ist nun für 10 Minuten gefreezt.")
        await context.bot.send_message(chat_id=chatid, text=f"Team {enemyteam} ist 10 Minuten gefreezt! Niemand darf sich bewegen. Alle die sich aktuell in einer Bahn befinden müssen diese am nächsten Bahnhof verlassen und dort warten.")
        schedule.every(10).minutes.do(teamfreezeend, team={enemyteam})
    if powerup == 5:
        await context.bot.send_message(chat_id=user_id, text=f"Du hast das PowerUp '{powerupslist[powerup]['Name']}' eingesetzt.\nBitte schreibe die Station, die du für das gegnerische Team blockieren möchtest, in den Gruppenchat.") 
        await context.bot.send_message(chat_id=chatid, text=f"Folgene Station für das Team {enemyteam} ist nun für 20 Minuten blockiert:")
        schedule.every(20).minutes.do(stationblockend, team={enemyteam})
    if powerup == 6:
        await context.bot.send_message(chat_id=user_id, text=f"Du hast das PowerUp '{powerupslist[powerup]['Name']}' eingesetzt.\nDas Handy für's gegnerische Team ist nun gesperrt.") 
        await context.bot.send_message(chat_id=chatid, text=f"Für 15 Minuten darf Team {enemyteam} das Handy, außer die Kamera zum taggen und den Telegram-Bot für Aktionen, nicht benutzen.")
        schedule.every(15).minutes.do(nophoneend, team={enemyteam})
    if powerup == 7:
        await context.bot.send_message(chat_id=user_id, text=f"Du hast das PowerUp '{powerupslist[powerup]['Name']}' eingesetzt.\nDas gegnerische Team muss nun ihren GPS-Standort für 10 Minuten teilen.") 
        await context.bot.send_message(chat_id=chatid, text=f"Team {enemyteam} muss nun 10 Minuten ihren GPS-Standort hier teilen.")
        schedule.every(10).seconds.do(showgpsend, team={enemyteam})    
    if powerup == 8:
        await context.bot.send_message(chat_id=user_id, text=f"Das solltest du nicht lesen können.") 
   

if __name__ == '__main__':
    application = ApplicationBuilder().token('INSERT TOKEN HERE').build()


    
    Thread(target=schedule_checker).start() 

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('timer', timer))
    application.add_handler(CommandHandler('startgame', startgame))
    application.add_handler(CommandHandler('loadbackup', loadbackup))
    application.add_handler(MessageHandler(filters.Regex(r'^/undo\d+$'), undo))
    application.add_handler(CommandHandler('resetall', resetall))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CallbackQueryHandler(receive_team, pattern='^(Rot|Blau)$'))
    application.add_handler(MessageHandler(filters.Regex(r'^Anmeldung$'), register))
    application.add_handler(MessageHandler(filters.Regex(r'^Power-Ups$'), powerups))
    application.add_handler(MessageHandler(filters.Regex(r'^Flags$'), flags))
    application.add_handler(MessageHandler(filters.Regex(r'^Tagged$'), tagged))
    application.add_handler(MessageHandler(filters.Regex(r'^Zurück am Hauptbahnhof$'), returnmainstation))
    application.add_handler(CallbackQueryHandler(takeflag, pattern='^takeflag$'))
    application.add_handler(CallbackQueryHandler(claimflag, pattern='^claimflag$'))
    application.add_handler(CallbackQueryHandler(giveflag, pattern='^giveflag$'))
    application.add_handler(CallbackQueryHandler(takeflagresult, pattern=r'^takeflagresult_\d+$'))
    application.add_handler(CallbackQueryHandler(giveflagresult, pattern=r'^giveflagresult_\d+$'))
    application.add_handler(CallbackQueryHandler(claimflagresult, pattern='^claimflagresult$'))
    application.add_handler(CallbackQueryHandler(notatcentral, pattern='^notatcentral$'))
    application.add_handler(CallbackQueryHandler(returnmainstation, pattern=r'^returnmainstation_(pending|done)$'))
    application.add_handler(CallbackQueryHandler(taggedresult, pattern=r'^taggedresult_(normal|reverse)_\d+$'))
    application.add_handler(CallbackQueryHandler(askforreverse, pattern=r'^askforreverse_\d+_\d+$'))
    application.add_handler(CallbackQueryHandler(locationselection, pattern=r'^locationselection_(challenge|powerup)'))
    application.add_handler(CallbackQueryHandler(startchallenge, pattern=r'^startchallenge_\d+$'))
    application.add_handler(CallbackQueryHandler(getpowerup, pattern=r'^getpowerup_\d+$'))
    application.add_handler(CallbackQueryHandler(selectpowerup, pattern=r'^selectpowerup$'))
    application.add_handler(CallbackQueryHandler(usepowerup, pattern=r'^usepowerup_\d+$'))


    
    application.run_polling()
