import asyncio
import logging as logger
from modules import Constants
import os
import pymysql
from pyrogram import Client, Filters, Message
from pyrogram.api.functions.help import GetConfig
from pyrogram.errors import FloodWait
import re
import schedule
import subprocess
import time

def stopFilterCommute(self):
	self.flag = not self.flag


adminsIdList = list()
chatIdList = list()
commands = list(["add", "ban", "check", "evaluate", "exec", "help", "remove", "report", "scheduling", "start", "unban", "update"])
connection = pymysql.connect(host="localhost", user="myUser", password="myPassword", database=constants.username, port=3306, charset="utf8", cursorclass=pymysql.cursors.DictCursor, autocommit=False)
constants = Constants.Constants()
logger.basicConfig(filename="{}{}.log".format(constants.databasePath, constants.username), datefmt="%d/%m/%Y %H:%M:%S", format="At %(asctime)s was logged the event:\t%(levelname)s - %(message)s", level=logger.INFO)
messageMaxLength = 0
minute = 60
scheduler = schedule.default_scheduler
stopFilter = Filters.create(lambda self, _: self.flag, flag=True, commute=stopFilterCommute)
with connection.cursor() as cursor:
	logger.info("Initializing the Admins ...")
	cursor.execute("SELECT `id` FROM `Admins` WHERE `username`=%(user)s", dict({"user": "myUser"}))
	constants.creator = cursor.fetchone()["id"]
	logger.info("Admins initializated\nSetting the admins list ...")
	cursor.execute("SELECT `id` FROM `Admins`")
	for i in cursor.fetchall():
		adminsIdList.append(i["id"])
	logger.info("Admins setted\nSetting the chats list ...")
	cursor.execute("SELECT `id` FROM `Chats`")
	for i in cursor.fetchall():
		chatIdList.append(i["id"])
logger.info("Chats initializated\nInitializing the Database ...")
with open("{}database.json".format(constants.databasePath), "r") as databaseFile:
	database = json.load(databaseFile)
logger.info("Database initializated\nInitializing the Client ...")
app = Client(session_name=constants.username, api_id=constants.id, api_hash=constants.hash, bot_token=constants.token)


@app.on_message(Filters.command("add", prefixes="/") & (Filters.user(constants.creator) | Filters.channel) & stopFilter)
async def addToTheDatabase(client: Client, message: Message):
	# /add
	global adminsIdList, chatIdList, connection, constants, stopFilter

	await stopFilter.commute()
	# Checking if the message arrive from a channel and, if not, checking if the user that runs the command is allowed
	if message.from_user is not None and message.from_user.id != constants.creator:
		await stopFilter.commute()
		return
	lists = chatIdList
	text = "The chat {} is already present in the list of allowed chat.".format(chat.title)
	# Checking if the data are of a chat or of a user
	if message.reply_to_message is not None:
		chat = await client.get_users(message.reply_to_message.from_user.id)
		chat = chat.__dict__
		lists = adminsIdList
		text = "The user @{} is already an admin.".format(chat["username"])
	else:
		chat = await client.get_chat(message.chat.id)
		chat = chat.__dict__
		# Deleting the message
		await message.delete(revoke=True)
	# Checking if the chat/user is in the list
	if chat["id"] in lists:
		await stopFilter.commute()
		logger.info(text)
		return
	# Adding the chat/user to the database
	lists.append(chat["id"])
	try:
		del chat["_client"]
	except KeyError:
		pass
	try:
		del chat["_"]
	except KeyError:
		pass
	try:
		del chat["photo"]
	except KeyError:
		pass
	try:
		del chat["description"]
	except KeyError:
		pass
	try:
		del chat["pinned_message"]
	except KeyError:
		pass
	try:
		del chat["sticker_set_name"]
	except KeyError:
		pass
	try:
		del chat["can_set_sticker_set"]
	except KeyError:
		pass
	try:
		del chat["members_count"]
	except KeyError:
		pass
	try:
		del chat["restrictions"]
	except KeyError:
		pass
	try:
		del chat["permissions"]
	except KeyError:
		pass
	try:
		del chat["distance"]
	except KeyError:
		pass
	try:
		del chat["status"]
	except KeyError:
		pass
	try:
		del chat["last_online_date"]
	except KeyError:
		pass
	try:
		del chat["next_offline_date"]
	except KeyError:
		pass
	try:
		del chat["dc_id"]
	except KeyError:
		pass
	with connection.cursor() as cursor:
		if constants.creator in lists:
			cursor.execute("INSERT INTO `Admins` (`id`, `is_self` ,`is_contact`, `is_mutual_contact`, `is_deleted`, `is_bot`, `is_verified`, `is_restricted`, `is_scam`, `is_support`, `first_name`, `last_name`, `username`, `language_code`, `phone_number`, `role`) VALUES (%(id)s, %(is_self)s, %(is_contact)s, %(is_mutual_contact)s, %(is_deleted)s, %(is_bot)s, %(is_verified)s, %(is_restricted)s, %(is_scam)s, %(is_support)s, %(first_name)s, %(last_name)s, %(username)s, %(language_code)s, %(phone_number)s)", chat)
			text = "I added {}{} to the list of allowed user.".format("{} ".format(chat["first_name"]) if chat["first_name"] is not None else "", "{} ".format(chat["last_name"]) if chat["last_name"] is not None else "")
		else:
			cursor.execute("INSERT INTO `Chats` (`id`, `type`, `is_verified`, `is_restricted`, `is_scam`, `is_support`, `title`, `username`, `first_name`, `last_name`, `invite_link`) VALUES (%(id)s, %(type)s, %(is_verified)s, %(is_restricted)s, %(is_scam)s, %(is_support)s, %(title)s, %(username)s, %(first_name)s, %(last_name)s, %(invite_link)s)", chat)
			text = "I added {} to the list of allowed chat.".format(chat["title"])
		connection.commit()
	await stopFilter.commute()
	logger.info(text)


@app.on_message(Filters.chat(chatIdList) & Filters.regex("^(\@admin)\s?(.*)$", re.IGNORECASE | re.UNICODE | re.MULTILINE))
def admin(client: Client, message: Message):
	global connection, constants

	# Checking if the message have the correct syntax
	if message.text.startswith("@admin") is False or len(message.matches) != 1:
		return
	message.text = message.text[len("@admin"):]
	if message.text != "" and message.text[0] not in list([" ", "\n", "\t"]):
		return
	# Retrieving the admins
	match = message.matches.pop(0)
	with connection.cursor() as cursor:
		cursor.execute("SELECT `id`, `username` FROM `Admins`")
		admins = cursor.fetchall()
	text = "\n@{} needs your help".format(message.from_user.username)
	# Retrieving the eventual message for the admins
	if match.group(2) != "":
		text += " for {}".format(match.group(2))
	text += "."
	# Tagging the admins
	await message.reply_to_message.reply_text(" ".join(list(map(lambda n: "@{}".format(n["username"]), admins))), quote=True)
	await message.delete(revoke=True)
	for i in admins:
		await client.send_message(i["id"], "@{}{}".format(i["username"], text))
	logger.info("I sent @{}\'s request to the competent admin.".format(message.from_user.username))


@app.on_message(Filters.service & Filters.chat(chatIdList))
async def automaticRemovalStatus(_, message: Message):
	await message.delete(revoke=True)


@app.on_message(Filters.command(list(["ban", "unban"]), prefixes="/") & Filters.user(adminsIdList) & Filters.chat(chatIdList))
async def banHammer(client: Client, message: Message):
	# /ban
	# /unban <username>
	global adminsIdList

	command = message.command.pop(0)
	if command == "unban"
		user = await client.get_users(message.command.pop(0))
		await message.chat.unban_member(user.id)
	elif message.reply_to_message is not None and message.reply_to_message.from_user.id not in adminsIdList:
		user = message.reply_to_message.from_user
		await message.chat.kick_member(user.id)
	await message.reply_text("I have {}ned @{}.".format(command, user.username), quote=True)
	logger.info("I have {}ned @{}.".format(command, user.username))


@app.on_message(Filters.command("check", prefixes="/") & Filters.user(constants.creator) & Filters.private & stopFilter)
async def checkDatabase(_, _):
	# /check
	global adminsIdList, connection, chatIdList, database

	await message.delete(revoke=True)
	with connection.cursor() as cursor:
		cursor.execute("SELECT * FROM `Admins`")
		print("{}\n".format(cursor.fetchall()))
	print("{}\n\n".format(list(map(lambda n: "\t{} - {}\n".format(n, type(n)), adminsIdList))))
	with connection.cursor() as cursor:
		cursor.execute("SELECT * FROM `Chats`")
		print("{}\n".format(cursor.fetchall()))
	print("{}\n\n".format(list(map(lambda n: "\t{} - {}\n".format(n, type(n)), chatIdList))))
	print("{}\n\n".format(database)
	print("\n")
	logger.info("I have checked the admin and the chat list.")


@app.on_message(Filters.command("evaluate", prefixes="/") & Filters.chat(chatIdList) & Filters.user(constants.creator))
async def evaluation(_, message: Message):
	# /evaluate
	global messageMaxLength

	message.command.pop(0)
	# Retrieving the command to evaluate
	command = " ".join(message.command)
	# Evaluating the command
	result = eval(command)
	text = "<b>Espression:</b>\n\t<code>{}</code>\n\n<b>Result:</b>\n\t<code>{}</code>".format(command, result)
	await message.edit_text(text[:messageMaxLength])
	if len(text) >= messageMaxLength:
		for i in range(1, len(text), messageMaxLength):
			try:
				await message.reply_text(text[i:i + messageMaxLength], quote=False)
			except FloodWait as e:
				time.sleep(e.x)
	logger.info("I have evaluated the command <code>{}</code>.".format(command))


@app.on_message(Filters.command("exec", prefixes="/") & Filters.chat(chatIdList) & Filters.user(constants.creator))
async def execution(_, message: Message):
	# /exec
	global messageMaxLength

	message.command.pop(0)
	# Retrieving the command to exec
	command = " ".join(message.command)
	# Checking if the command can execute in the real shell
	if command == "clear":
		os.system(command)
	# Executing the command in a virtual shell
	result = subprocess.check_output(command, shell=True)
	result = result.decode("utf-8")
	result = result.replace("\n", "</code>\n\t<code>")
	text = "<b>Command:</b>\n\t<code>{}</code>\n\n<b>Result:</b>\n\t<code>{}</code>".format(command, result)
	await message.edit_text(text[:messageMaxLength])
	if len(text) >= messageMaxLength:
		for i in range(1, len(text), messageMaxLength):
			try:
				await message.reply_text(text[i:i + messageMaxLength], quote=False)
			except FloodWait as e:
				time.sleep(e.x)
	logger.info("I have executed the command <code>{}</code>.".format(command))


@app.on_message(Filters.command("help", prefixes="/") & Filters.user(constants.creator) & Filters.private)
async def help(_, message: Message):
	# /help
	global commands

	text = "The commands are:\n\t\t<code>/{}</code>".format("<code>\n\t\t/</code>".join(commands))
	await message.edit_text(text[:messageMaxLength])
	if len(text) >= messageMaxLength:
		for i in range(1, len(text), messageMaxLength):
			try:
				await message.reply_text(text[i:i + messageMaxLength], quote=False)
			except FloodWait as e:
				time.sleep(e.x)
	logger.info("I sent the help.")
	await client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("remove", prefixes="/") & (Filters.user(constants.creator) | Filters.channel) & stopFilter)
async def removeFromTheDatabase(client: Client, message: Message):
	# /remove
	global adminsIdList, chatIdList, connection, constants, stopFilter

	await stopFilter.commute()
	# Checking if the message arrive from a channel and, if not, checking if the user that runs the command is allowed
	if message.from_user is not None and message.from_user.id != constants.creator:
		await stopFilter.commute()
		return
	lists = chatIdList
	title = message.chat.title
	text = "The chat {} hasn\'t been removed from the list of allowed chat.".format(title)
	# Checking if the data are of a chat or of a user
	if message.reply_to_message is not None:
		ids = message.reply_to_message.from_user.id
		lists = adminsIdList
		text = "The user @{} hasn\'t been removed from the admins list.".format(message.reply_to_message.from_user.username)
	else:
		ids = message.chat.id
		# Deleting the message
		await message.delete(revoke=True)
	# Checking if the chat/user is in the list
	if ids not in lists:
		await stopFilter.commute()
		logger.info(text)
		return
	# Removing the chat/user from the database
	lists.remove(ids)
	with connection.cursor() as cursor:
		if constants.creator in lists:
			cursor.execute("DELETE FROM `Admins` WHERE `id`=%(id)s", dict({"id": ids}))
			text = "The user @{} has been removed from the admins list.".format(message.reply_to_message.from_user.username)
		else:
			cursor.execute("DELETE FROM `Chats` WHERE `id`=%(id)s", dict({"id": ids}))
			text = "The chat {} has been removed from the list of allowed chat.".format(title)
		connection.commit()
	await stopFilter.commute()
	logger.info(text)


@app.on_message(Filters.command("report", prefixes=list(["/"])) & Filters.user(constants.creator) & Filters.private)
async def report(_, message: Message):
	# /report
	await message.reply_text("/add - Add an admin or a chat to the database\n" +
							"/check - Check the database\n" +
							"/evaluate - Evaluate a command\n" +
							"/exec - Exec a Shell command\n" +
							"/help - Show the help\n" +
							"/report - Send a report on the list of the commands\n" +
							"/scheduling - Start the Job Queue\n" +
							"/start - Start the bot\n" +
							"/update - Update the database")
	logger.info("I send a report.")


@app.on_message(Filters.chat(chatIdList) & Filters.regex("^\+{1, 5}$|^\-{1, 5}$", re.IGNORECASE | re.UNICODE | re.MULTILINE))
def reputation(_, message: Message):
	global database

	for i in database:
		# Searching the chat in the database
		if i["id"] == message.chat.id:
			# Checking if the user is already in the database and changing its reputation
			if message.from_user.id in list(map(lambda n: n["id"], i["reputation"])):
				for j in i["reputation"]:
					# Searching the user in the database
					if j["id"] == message.from_user.id:
						if message.text.startswith("+") is True:
							j["quantity"] += len(message.text)
						else:
							j["quantity"] -= len(message.text)
							if j["quantity"] < 0:
								j["quantity"] = 0
						break
			else:
				i["reputation"].append(dict({"id": message.from_user.id, "quantity": len(message.text) if message.text.startswith("+") is True else 0}))
			break
	# Saving the database
	with open("{}database.json".format(constants.databasePath), "w") as databaseFile:
		databaseFile.write(database)
	logger.info("I changed ({}) the reputation of @{}.".format("+" if message.text.startswith("+") is True else "-", message.from_user.username))


@app.on_message(Filters.command("scheduling", prefixes="/") & Filters.user(adminsIdList) & Filters.private)
def scheduling(client: Client, _):
	# /scheduling
	global messageMaxLength, scheduler

	messageMaxLength = await client.send(GetConfig()).message_length_max
	while True:
		scheduler.run_pending()
		time.sleep(minute * 60 * 23)


@app.on_message(Filters.command("start", prefixes="/") & Filters.user(userIdList) & Filters.private)
async def start(_, message: Message):
	# /start
	await message.reply_text("Welcome @{}.\nThis bot is the PoliTo version of @combot.".format(message.from_user.username))
	logger.info("I started because of @{}.".format(message.from_user.username))


@app.on_message(Filters.command("update", prefixes="/") & Filters.user(adminsIdList) & Filters.private & stopFilter)
async def updateDatabase(client: Client, message: Message = None):
	# /update
	global adminsIdList, chatIdList, connection, constants, stopFilter

	await stopFilter.commute()
	# Checking if the updating was programmed or not
	if message is not None:
		await message.delete(revoke=True)
	# Updating the admin's database
	adminsIdList.remove(constants.creator)
	chats = await client.get_users(adminsIdList)
	adminsIdList.append(constants.creator)
	await chats.append(client.get_me())
	chats = list(map(lambda n: n.__dict__, chats))
	with connection.cursor() as cursor:
		for i in chats:
			try:
				del i["_client"]
			except KeyError:
				pass
			try:
				del i["_"]
			except KeyError:
				pass
			try:
				del i["photo"]
			except KeyError:
				pass
			try:
				del i["restrictions"]
			except KeyError:
				pass
			try:
				del i["status"]
			except KeyError:
				pass
			try:
				del i["last_online_date"]
			except KeyError:
				pass
			try:
				del i["next_offline_date"]
			except KeyError:
				pass
			try:
				del i["dc_id"]
			except KeyError:
				pass
			cursor.execute("UPDATE `Admins` SET `is_self`=%(is_self)s, `is_contact`=%(is_contact)s, `is_mutual_contact`=%(is_mutual_contact)s, `is_deleted`=%(is_deleted)s, `is_bot`=%(is_bot)s, `is_verified`=%(is_verified)s, `is_restricted`=%(is_restricted)s, `is_scam`=%(is_scam)s, `is_support`=%(is_support)s, `first_name`=%(first_name)s, `last_name`=%(last_name)s, `username`=%(username)s, `language_code`=%(language_code)s, `phone_number`=%(phone_number)s WHERE `id`=%(id)s", i)
		connection.commit()
	# Updating the chats' database
	chats = list()
	for i in chatIdList:
		try:
			await chats.append(client.get_chat(i).__dict__)
		except FloodWait as e:
			time.sleep(e.x)
	with connection.cursor() as cursor:
		for i in chats:
			try:
				del i["_client"]
			except KeyError:
				pass
			try:
				del i["_"]
			except KeyError:
				pass
			try:
				del i["photo"]
			except KeyError:
				pass
			try:
				del i["description"]
			except KeyError:
				pass
			try:
				del i["pinned_message"]
			except KeyError:
				pass
			try:
				del i["sticker_set_name"]
			except KeyError:
				pass
			try:
				del i["can_set_sticker_set"]
			except KeyError:
				pass
			try:
				del i["members_count"]
			except KeyError:
				pass
			try:
				del i["restrictions"]
			except KeyError:
				pass
			try:
				del i["permissions"]
			except KeyError:
				pass
			try:
				del i["distance"]
			except KeyError:
				pass
			cursor.execute("UPDATE `Chats` SET `type`=%(type)s, `is_verified`=%(is_verified)s, `is_restricted`=%(is_restricted)s, `is_scam`=%(is_scam)s, `is_support`=%(is_support)s, `title`=%(title)s, `username`=%(username)s, `first_name`=%(first_name)s, `last_name`=%(last_name)s, `invite_link`=%(invite_link)s WHERE `id`=%(id)s", i)
		connection.commit()
	await stopFilter.commute()
	logger.info("I have updated the database.")


def unknownFilter():
	global commands

	def func(flt, message: Message):
		text = message.text or message.caption
		if text:
			message.matches = list(flt.p.finditer(text)) or None
			if bool(message.matches) is False and text.startswith("/") is True and len(text) > 1:
				return True
		return False
	return Filters.create(func, "UnknownFilter", p=re.compile("^/{}".format("|^/".join(commands)), 0))


@app.on_message(unknownFilter() & Filters.user(adminsIdList) & (Filters.chat(chatIdList) | Filters.private))
async def unknown(_, message: Message):
	await message.edit_text("This command isn\'t supported.")
	logger.info("I managed an unsupported command.")


logger.info("Client initializated\nSetting the markup syntax ...")
app.set_parse_mode("html")
logger.info("Setted the markup syntax\Setting the Job Queue ...")
scheduler.every().day.at("00:00").do(updateDatabase, client=app)
logger.info("Setted the Job Queue\nStarted serving ...")
app.run()
connection.close()
