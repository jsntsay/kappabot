from wand.image import Image
import os, random, urllib, shutil
import xml.etree.ElementTree as etree

DICE_DICT = {
	1: 'dice1.png',
	2: 'dice2.png',
	3: 'dice3.png',
	4: 'dice4.png',
	5: 'dice5.png',
	6: 'dice6.png',
}

SAFEBOORU_POST_URL = "https://safebooru.org/index.php?page=post&s=view&id="

def trackCommand(message):
	return # TODO: remove this
	commandUsed = None
	command = message.content.split(' ')[0].strip()
	if command == "!bestlovelive":
		command = "!lovelive"
	elif command == "!teachmemisslitchi":
		command = "!blazblue"
	if message.server != None and message.author != None:
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
		img.save(filename="dicepic.png")
	return total

def getsafeboorupic(tag, filename, blur=False):
	"""Returns a random, resized picture from safebooru using the provided tag to the provided file"""
	if not blur and tag == 'yuri':
		# With some probabilty, put up a pic of yuri from kof because you can.
		if random.random() < 0.10:
			shutil.copyfile('yuri.jpg', 'yuripic.jpg')
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
