import configparser
import discord
import os, random, shutil, sqlite3, datetime, sys
import asyncio
from kappabot_utils import track_command, makedicepic, getsafeboorupic, check_or_create_toxic_db, check_last_used, adjust_toxicity, get_toxicity

CONFIG_PATH = os.path.join(sys.path[0], "config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

DISCORD_TOKEN = config["DEFAULT"]["DISCORD_TOKEN"]
HUNIEPOP_PATH = os.path.join(sys.path[0], config["DEFAULT"]["HUNIEPOP_PATH"])
TOXIC_DB_PATH = os.path.join(sys.path[0], config["DEFAULT"]["TOXIC_DB_PATH"])
OHOHO_PATH = os.path.join(sys.path[0], config["DEFAULT"]["OHOHO_PATH"])
DICE_PATH = os.path.join(sys.path[0], config["DEFAULT"]["DICE_PATH"])
COINS_PATH = os.path.join(sys.path[0], config["DEFAULT"]["COINS_PATH"])
GAMES_PATH = os.path.join(sys.path[0], config["DEFAULT"]["GAMES_PATH"])
DEAD_PATH = os.path.join(sys.path[0], config["DEFAULT"]["DEAD_PATH"])
TOXIC_TIMEOUT = int(config["DEFAULT"]["TOXIC_TIMEOUT"])

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
toxicconn = check_or_create_toxic_db(TOXIC_DB_PATH)
toxicdb = toxicconn.cursor()


HELP_MESSAGE = "!help - This help message.\n" + \
	"!info - In case you were wondering what CMUken is about.\n" + \
	"!baited - Baiiiiitttteeeeeed.\n" + \
	"!coinflip or !coin - 50/50 paulo's vision.\n" + \
	"!dead or !rip - Destroyed.\n" + \
	"!gotem - #GOTEM\n" + \
	"!diceroll or !dice [optional: dice to roll, up to 5, default is 3] - Clickity-clack.\n" + \
	"!huniepop - Who is Best Huniepop?\n" + \
	"!ohoho - Show them the divide in class.\n" + \
	"!mindgames - Mental guard crush.\n" + \
	"!toxic or !goodguy/gal - Divy up toxic points.\n" + \
	"!triggered - For times when you are triggered.\n" + \
	"!whatgame - Picks a game for you to play/practice\n" + \
	"!yuri - Posts a random pic of 2 anime girls who are really into each other\n" + \
	"!yaoi - Posts a random pic of 2 anime guys who are really into each other\n"

INFO_MESSAGE = "CMUken is part of the Pittsburgh fighting game community. More info on the Facebook group: https://www.facebook.com/groups/CMUken/"

OHOHO_PICS = [f for f in os.listdir(OHOHO_PATH) if os.path.isfile(os.path.join(OHOHO_PATH, f))]
DEAD_PICS = [f for f in os.listdir(DEAD_PATH) if os.path.isfile(os.path.join(DEAD_PATH, f))]

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

async def send_safebooru_message(message, tag, pic_path, track=True):
	local_path = os.path.join(sys.path[0], pic_path)
	if track:
		track_command(message, toxicconn, toxicdb)
	tags = tag
	if ' ' in message.content:
		tags = tags + ' ' + message.content[message.content.find(' '):].strip()
	posturl = getsafeboorupic(tags, local_path)
	if posturl == None:
		kappa = getKappa(message, kappa_emoji)
		await message.channel.send("Sorry, no images found " + kappa)
	else:
		with open(local_path, 'rb') as pic:
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
		track_command(message, toxicconn, toxicdb)
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
		await send_safebooru_message(message, "yuri", "yuripic.jpg")
	elif message.content.startswith('!yaoi'):
		await send_safebooru_message(message, "yaoi", "yaoipic.jpg")
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
		with open(os.path.join(sys.path[0], 'dicepic.png'), 'rb') as pic:
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
		with open(os.path.join(sys.path[0], 'baited.gif'), 'rb') as pic:
			await message.channel.send("Baiiiiitttteeeeeed.", file=discord.File(pic))
	elif message.content.startswith('!gotem'):
		track_command(message, toxicconn, toxicdb)
		with open(os.path.join(sys.path[0], 'gotem.gif'), 'rb') as pic:
			await message.channel.send("Got em.", file=discord.File(pic))
	elif message.content.startswith('ARMS'):
		track_command(message, toxicconn, toxicdb)
		with open(os.path.join(sys.path[0], 'ARMS.jpg'), 'rb') as pic:
			await message.channel.send("Woh-oh-oh-oh-oh-ohhhhhh~", file=discord.File(pic))
	elif message.content.startswith('!mindgames'):
		track_command(message, toxicconn, toxicdb)
		with open(os.path.join(sys.path[0], 'mindgames.gif'), 'rb') as pic:
			await message.channel.send("Mind Games!", file=discord.File(pic))
	elif message.content.startswith('!dead') or message.content.startswith('!rip'):
		track_command(message, toxicconn, toxicdb)
		path = random.choice(DEAD_PICS)
		with open(os.path.join(DEAD_PATH, path), 'rb') as pic:
			await message.channel.send("Destroyed.", file=discord.File(pic))
	elif message.content.startswith('!toxicity') or message.content.startswith('!toxicboard'):
		# NOTE: due to how the message parsing is... this has to be above the !toxic command :kappa:
		toxicity = await get_toxicity(message, toxicdb)
		output = "Toxicity Rankings: "
		for t in toxicity:
			face = getToxic(message, toxic_emoji)
			if t[1] <= 0:
				face = getGoodguy(message, goodguy_emoji)
			output += '\n\t{} {}\t-\t{}'.format(t[0], face, t[1])
		if len(output) > 2000:
			# split output into two, obviously not scalable if the list gets longer
			s = output.split('\n')
			splitIndex = int(len(s)/2 + 1)
			output1 = s[:splitIndex]
			output2 = s[splitIndex:]
			await message.channel.send("\n".join(output1))
			await message.channel.send("\n".join(output2))
		else:
			await message.channel.send(output)
	elif message.content.startswith('!toxic') or message.content.startswith('!goodguy') or message.content.startswith('!goodgirl') or message.content.startswith('!goodgal') or message.content.startswith('!roulette'):
			track_command(message, toxicconn, toxicdb)
			lastused = check_last_used(message, toxicdb)
			if lastused != None:
				now_ts = int(datetime.datetime.now().timestamp())
				time_elapsed = now_ts - lastused[2]
				if time_elapsed < TOXIC_TIMEOUT:
					kappa = getKappa(message, kappa_emoji)
					await message.channel.send('{}, chill out for {} more seconds {}'.format(message.author.mention, TOXIC_TIMEOUT - time_elapsed, kappa))
					return
			result = None
			if message.content.startswith('!toxic'):
				result = adjust_toxicity(message, lastused, toxicconn, toxicdb, 1)
			elif message.content.startswith('!goodguy') or message.content.startswith('!goodgirl') or message.content.startswith('!goodgal'):
				result = adjust_toxicity(message, lastused, toxicconn, toxicdb, -1)
			elif message.content.startswith('!roulette'):
				rval = random.randint(-2, 2)
				# messing with the twins
				if (message.author.id == 118207276086591497 or message.author.id == 177883979385536513) and rval <= -1:
					rval = 0
				result = adjust_toxicity(message, lastused, toxicconn, toxicdb, rval)
				# potential issue here if slowmode is enabled and the bot has to respect it
				await message.channel.send('{} rolled {} {} points!'.format(message.author.mention, abs(rval), 'toxic' if rval >= 0 else 'goodguy'))
			if result != None:
				face = getToxic(message, toxic_emoji)
				if result[1] <= 0:
					face = getGoodguy(message, goodguy_emoji)
				if result[2]:
					# caught em trying to give themselves goodguy points kappa
					kappa = getKappa(message, kappa_emoji)
					await message.channel.send('{} {}\t-\t{} {}'.format(result[0], face, result[1], kappa))
				else:
					await message.channel.send('{} {}\t-\t{}'.format(result[0], face, result[1]))
	elif message.content.startswith('!triggered'):
		track_command(message, toxicconn, toxicdb)
		await message.channel.send("Triggered? Let me help you with that.")
		await message.channel.send( "!yuri")
		await send_safebooru_message(message, "yuri", "yuripic.jpg", track=False)
try:
	client.run(DISCORD_TOKEN)
except Exception:
	os.execv(sys.executable, ['python'] + sys.argv)
except Error:
	os.execv(sys.executable, ['python'] + sys.argv)
