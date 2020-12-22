from wand.image import Image
import os, random, urllib, shutil, sqlite3, datetime, sys
import xml.etree.ElementTree as etree
import asyncio

DICE_DICT = {
	1: 'dice1.png',
	2: 'dice2.png',
	3: 'dice3.png',
	4: 'dice4.png',
	5: 'dice5.png',
	6: 'dice6.png',
}

SAFEBOORU_POST_URL = "https://safebooru.org/index.php?page=post&s=view&id="

COMMAND_TABLE_CREATE = "CREATE TABLE [commandusage] ([id] INTEGER NOT NULL PRIMARY KEY, [command] TEXT NOT NULL, [count] INTEGER NOT NULL, [discord_id] TEXT NOT NULL)"
LAST_TABLE_CREATE = "CREATE TABLE [lastused] ([id] INTEGER NOT NULL PRIMARY KEY, [discord_id] TEXT NOT NULL, [lastused] INTEGER NOT NULL)"
TOXIC_TABLE_CREATE = "CREATE TABLE [toxic] ([id] INTEGER NOT NULL PRIMARY KEY, [discord_id] TEXT NOT NULL, [toxic] INTEGER NOT NULL)"
DB_TABLES = [COMMAND_TABLE_CREATE, LAST_TABLE_CREATE, TOXIC_TABLE_CREATE]

def check_or_create_toxic_db(db_path, recreate=False):
	# If wanting to start over, set recreate=True
	if not os.path.exists(db_path) or recreate:
		print("need to create db")
		db_file = open(db_path, "wb")
		db_file.close()
		conn = sqlite3.connect(db_path)
		for statement in DB_TABLES:
			conn.execute(statement)
		conn.commit()
		conn.close()
	return sqlite3.connect(db_path)

def track_command(message, toxicconn, toxicdb):
	commandUsed = None
	command = message.content.split(' ')[0].strip()
	if command == "!bestlovelive":
		command = "!lovelive"
	elif command == "!teachmemisslitchi":
		command = "!blazblue"
	if message.guild != None and message.author != None:
		if message.author != None:
			t = (message.author.id,command)
			toxicdb.execute('SELECT * FROM commandusage WHERE discord_id=? and command=?', t)
			commandUsed = toxicdb.fetchone()
		if commandUsed == None:
			t = (None, command, 1, message.author.id)
			toxicdb.execute('INSERT INTO commandusage VALUES (?, ?, ?, ?)', t)
		else:
			value = int(commandUsed[2]) + 1
			t = (value, message.author.id, command)
			toxicdb.execute('UPDATE commandusage SET count=? where discord_id=? and command=?', t)
		toxicconn.commit()

def makedicepic(dice_path, values):
	total = 0
	with Image(width=len(values)*100, height=100) as img:
		index = 0
		for die in values:
			with Image(filename=os.path.join(dice_path, DICE_DICT[die])) as i:
				img.composite(i, left=index*100, top=0)
			index += 1
			total += die
		img.save(filename=os.path.join(sys.path[0], "dicepic.png"))
	return total

def getsafeboorupic(tag, filename, blur=False):
	"""Returns a random, resized picture from safebooru using the provided tag to the provided file"""
	if not blur and tag == 'yuri':
		# With some probabilty, put up a pic of yuri from kof because you can.
		if random.random() < 0.10:
			shutil.copyfile(os.path.join(sys.path[0], 'yuri.jpg'), os.path.join(sys.path[0], 'yuripic.jpg'))
			return 'http://safebooru.org/index.php?page=post&s=view&id=1782381'
	encoded_tags = urllib.parse.urlencode({
		"tags": tag
	})
	response = urllib.request.urlopen("https://safebooru.org/index.php?page=dapi&s=post&q=index&" + encoded_tags).read()
	root = etree.fromstring(response)
	urls = []
	for child in root:
		urls.append((child.attrib['sample_url'], child.attrib['id']))
	if len(urls) == 0:
		return None
	picurl = random.choice(urls)
	urllib.request.urlretrieve(picurl[0], filename)
	posturl = SAFEBOORU_POST_URL + picurl[1]

	with Image(filename=filename) as img:
		width = img.width
		height = img.height
		if img.height > width:
			width = int(width * (300 / height))
			height = 300
		else:
			height = int(height * (300 / width))
			width = 300
		if blur:
			img.resize(int(width/2), int(height/2), filter='box', blur=4)
		img.resize(width, height)
		img.save(filename=filename)

	return posturl


def check_last_used(message, toxicdb):
	lastused = None
	if ' ' in message.content and message.guild != None and message.author != None:
		if message.author != None:
			t = (message.author.id,)
			toxicdb.execute('SELECT * FROM lastused WHERE discord_id=?', t)
			lastused = toxicdb.fetchone()
	return lastused

def adjust_toxicity(message, lastused, toxicconn, toxicdb, toxic=True):
	result = None
	if ' ' in message.content and message.guild != None and message.author != None:
		now_ts = int(datetime.datetime.now().timestamp())
		target = message.content[message.content.find(' '):].strip()
		server = message.guild
		target_member = None
		self_toxic = False

		for m in server.members:
			if m.display_name.lower().startswith(target.lower()) or m.name.lower().startswith(target.lower()):
				target_member = m
				break
		if message.author != None and target_member != None:
			if message.author.id == target_member.id and not toxic:
				toxic = True
				self_toxic = True
			if lastused == None:
				t = (None, message.author.id, now_ts)
				toxicdb.execute('INSERT INTO lastused VALUES (?, ?, ?)', t)
			else:
				t = (now_ts, message.author.id)
				toxicdb.execute('UPDATE lastused SET lastused=? where discord_id=?', t)
			t = (target_member.id,)
			toxicdb.execute('SELECT * FROM toxic WHERE discord_id=?', t)
			toxicresult = toxicdb.fetchone()
			name = target_member.nick
			if name == None:
				name = target_member.name
			if toxicresult == None:
				value = 1
				if not toxic:
					value = -1
				t = (None, target_member.id, value)
				toxicdb.execute('INSERT INTO toxic VALUES (?, ? , ?)', t)
				result = (name, value, self_toxic)
			else:
				value = toxicresult[2]
				if toxic:
					value += 1
				else:
					value -= 1
				t = (value, target_member.id)
				toxicdb.execute('UPDATE toxic SET toxic=? where discord_id=?', t)
				result = (name, value, self_toxic)

	toxicconn.commit()
	return result

async def get_toxicity(message, toxicdb):
	result = []
	if message.guild != None:
		toxicdb.execute('SELECT * FROM toxic')
		toxicresult = toxicdb.fetchall()
		for t in toxicresult:
			member = await message.guild.fetch_member(t[1])
			value = t[2]
			if member == None:
				continue
			name = member.nick
			if name == None:
				name = member.name
			result.append((name,value))
	return sorted(result, key=lambda x: -x[1])
