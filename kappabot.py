import configparser
import discord
import os, random, shutil
import asyncio
from kappabot_utils import trackCommand, makedicepic, getsafeboorupic

CONFIG_PATH = "config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

DISCORD_TOKEN = config["DEFAULT"]["DISCORD_TOKEN"]
HUNIEPOP_PATH = config["DEFAULT"]["HUNIEPOP_PATH"]
OHOHO_PATH = config["DEFAULT"]["OHOHO_PATH"]
DICE_PATH = config["DEFAULT"]["DICE_PATH"]
COINS_PATH = config["DEFAULT"]["COINS_PATH"]
GAMES_PATH = config["DEFAULT"]["GAMES_PATH"]

HELP_MESSAGE = "!help - This help message.\n" + \
	"!info - In case you were wondering what CMUken is about.\n" + \
	"!huniepop - Who is Best Huniepop?\n" + \
	"!diceroll or !dice [optional: dice to roll, up to 5, default is 3] - Clickity-clack.\n" + \
	"!coinflip or !coin - 50/50 paulo's vision.\n" + \
	"!yuri - Posts a random pic of 2 anime girls who are really into each other\n" + \
	"!yaoi - Posts a random pic of 2 anime guys who are really into each other\n" + \
	"!whatgame - Picks a game for you to play/practice\n" + \
	"!baited - Baiiiiitttteeeeeed.\n" + \
	"!gotem - #GOTEM\n" + \
	"!ohoho - Show them the divide in class.\n"
INFO_MESSAGE = "CMUken is part of the Pittsburgh fighting game community. More info on the Facebook group: https://www.facebook.com/groups/CMUken/"

client = discord.Client()

OHOHO_PICS = [f for f in os.listdir(OHOHO_PATH) if os.path.isfile(os.path.join(OHOHO_PATH, f))]

game_list = []
with open(GAMES_PATH) as f:
	for line in f:
		game_list.append(line.strip())

HUNIEPOP_CHOI = "choiral.jpg"
HUNIEPOP_DICT = {
	"aiko.jpg": "Aiko: Guess you're hot for teacher.",
	"audrey.jpg": "Audrey: Because tsundere is so 2000s, mega bitch is the future.",
	"beli.jpg": "Beli: You know what they say about flexible girls.",
	"celeste.jpg": "Celeste: Knows something about tentacles.",
	"choi.jpg": "Choi: C H O I B O Y S",
	"jessie.jpg": "Jessie: Sometimes it's all about experience.",
	"kyanna.jpg": "Kyanna: She can bench you.",
	"kyu.jpg": "Kyu: Get you a girl who collects underwear.",
	"lola.jpg": "Lola: Ask her to wear the uniform.",
	"momo.jpg": "Momo: Careful of falling into the cat girl trap.",
	"naoto.jpg": "Naoto: The 2000 IQ Killjoy Detective. Who will eat and who will be eaten?",
	"nikki.jpg": "Nikki: Money match her.",
	"ryu.jpg": "Ryu: The answer to true love lies in the heart of battle.",
	"sol.jpg": "Sol: Because we know you're all about the bad guy.",
	"tiffany.jpg": "Tiffany: She's cheer captain while you're on the bleachers.",
	"venus.jpg": "Venus: The final challenge.",
	"yuri.jpg": "Yuri: !yuri",
}

kappa_emoji = None
toxic_emoji = None
goodguy_emoji = None

def getKappa(message, kappa_emoji):
	if kappa_emoji == None:
		kappa_emoji = getEmoji(message,  'kappa')
	return kappa_emoji

def getToxic(message, toxic_emoji):
	if toxic_emoji == None:
		toxic_emoji = getEmoji(message, 'toxic')
	return toxic_emoji

def getGoodguy(message, goodguy_emoji):
	if goodguy_emoji == None:
		goodguy_emoji = getEmoji(message, 'goodguy')
	return goodguy_emoji

def getEmoji(message, name):
	emojis = message.guild.emojis
	for e in emojis:
		if e.name == name:
			return str(e)
	return ""

async def get_safebooru(message, tag, pic_path):
	trackCommand(message)
	tags = tag
	if ' ' in message.content:
		tags = tags + ' ' + message.content[message.content.find(' '):].strip()
	posturl = getsafeboorupic(tags, pic_path)
	if posturl == None:
		kappa = getKappa(message, kappa_emoji)
		await message.channel.send("Sorry, no images found " + kappa)
	else:
		with open(pic_path, 'rb') as pic:
			await message.channel.send("<" + posturl + ">", file=discord.File(pic))

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')\

@client.event
async def on_message(message):

	# Don't let bot trigger on own messages
	if message.author.id == client.user.id:
		return

	# Main commands
	if message.content.startswith('!help'):
		await message.channel.send(HELP_MESSAGE)
	elif message.content.startswith('!info'):
		await message.channel.send(INFO_MESSAGE)
	elif message.content.startswith('!zekamashi'):
		with open('zekamashi.jpg', 'rb') as pic:
			await message.channel.send("None", file=discord.File(pic))
	elif message.content.startswith('!huniepop'):
		trackCommand(message)
		await message.channel.send("Who is the Huniepop waifu for " + message.author.mention + "?")
		path = random.choice(list(HUNIEPOP_DICT.keys()))
		with open(os.path.join(HUNIEPOP_PATH, path), 'rb') as pic:
			if path == "choi.jpg":
				if random.random() < 0.50:
					pic = open(os.path.join(HUNIEPOP_PATH, HUNIEPOP_CHOI), 'rb')
			await message.channel.send(HUNIEPOP_DICT[path], file=discord.File(pic))
			pic.close()
	elif message.content.startswith('!ohoho'):
		picpath = os.path.join(OHOHO_PATH, random.choice(OHOHO_PICS))
		with open(picpath, 'rb') as pic:
			await message.channel.send("_Ohoho~_", file=discord.File(pic))
	elif message.content.startswith('!yuri'):
		await get_safebooru(message, "yuri", "yuripic.jpg")
	elif message.content.startswith('!yaoi'):
		await get_safebooru(message, "yaoi", "yaoipic.jpg")
	elif message.content.startswith('!diceroll') or message.content.startswith('!dice'):
		numdice = 3
		try:
			if ' ' in message.content:
				numdice = int(message.content[message.content.find(' '):].strip())
		except ValueError:
			numdice = 3
		if numdice > 5:
			await message.channel.send("I only got 5 dice to roll.")
			numdice = 5
		elif numdice < 1:
			numdice = 1
		values = []
		for i in range(numdice):
			values.append(random.randint(1,6))
		total = makedicepic(DICE_PATH, values)
		dice = random.randint(1,6)
		with open('dicepic.png', 'rb') as pic:
			await message.channel.send("Total: " + str(total), file=discord.File(pic))
	elif message.content.startswith('!coinflip') or message.content.startswith('!coin'):
		if random.random() < 0.50:
			with open(os.path.join(COINS_PATH, 'heads.png'), 'rb') as pic:
				await message.channel.send("Heads.", file=discord.File(pic))
		else:
			with open(os.path.join(COINS_PATH, 'tails.png'), 'rb') as pic:
				await message.channel.send("Tails.", file=discord.File(pic))
	elif message.content.startswith('!whatgame'):
		game = random.choice(game_list)
		if ':kappa:' in game:
			kappa = getKappa(message, kappa_emoji)
			game = game.replace(':kappa:', kappa)
		await message.channel.send(game)
	elif message.content.startswith('!baited'):
		with open('baited.gif', 'rb') as pic:
			await message.channel.send("Baiiiiitttteeeeeed.", file=discord.File(pic))
	elif message.content.startswith('!gotem'):
		trackCommand(message)
		with open('gotem.gif', 'rb') as pic:
			await message.channel.send("Got em.", file=discord.File(pic))
try:
	client.run(DISCORD_TOKEN)
except Exception:
	os.execv(sys.executable, ['python'] + sys.argv)
except Error:
	os.execv(sys.executable, ['python'] + sys.argv)
