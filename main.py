import asyncio
import logging as logger
from modules import Constants
import os
import pymysql
from pyrogram import Client, Emoji, Filters, Message
from pyrogram.api.functions.account import UpdateStatus
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
commands = list(["check", "evaluate", "exec", "help", "retrieve", "scheduling", "update"])
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
chatIdList.append("me")
logger.info("Chats initializated\nInitializing the Client ...")
app = Client(session_name=constants.username, api_id=constants.id, api_hash=constants.hash, phone_number=constants.phoneNumber)


@app.on_message(Filters.service)
async def automaticRemovalStatus(_, message: Message):
	await message.delete(revoke=True)


@app.on_message(Filters.command("check", prefixes="/") & Filters.user(constants.creator) & Filters.chat(chatIdList) & stopFilter)
async def checkDatabase(_, _):
	global adminsIdList, connection, chatIdList

	await message.delete(revoke=True)
	with connection.cursor() as cursor:
		cursor.execute("SELECT * FROM `Admins`")
		print("{}".format(cursor.fetchall()))
	print("\n{}\n".format(adminsIdList))
	print("{}\n".format(list(map(lambda n: "\t{} - {}\n".format(n, type(n)), adminsIdList))))
	with connection.cursor() as cursor:
		cursor.execute("SELECT * FROM `Chats`")
		print("{}".format(cursor.fetchall()))
	print("\n{}\n".format(chatIdList))
	print("{}\n".format(list(map(lambda n: "\t{} - {}\n".format(n, type(n)), chatIdList))))
	print("\n\n")
	logger.info("I have checked the admin and the chat list.")


@app.on_message(Filters.command("evaluate", prefixes="/") & Filters.user(constants.creator))
async def evaluation(_, message: Message):
	global messageMaxLength

	message.command.pop(0)
	command = " ".join(message.command)
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


@app.on_message(Filters.command("exec", prefixes="/") & Filters.user(constants.creator))
async def execution(_, message: Message):
	global messageMaxLength

	message.command.pop(0)
	command = " ".join(message.command)
	if command == "clear":
		os.system(command)
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


@app.on_message(Filters.command("help", prefixes="/") & Filters.user(constants.creator) & Filters.chat(chatIdList))
async def help(_, message: Message):
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


@app.on_message(Filters.command("retrieve", prefixes="/") & (Filters.user(constants.creator) | Filters.channel) & stopFilter)
async def retrieveChatId(client: Client, message: Message):
	global adminsIdList, chatIdList, connection, stopFilter

	await stopFilter.commute()
	if message.from_user is not None and message.from_user.id != constants.creator:
		await stopFilter.commute()
		return
	lists = chatIdList
	text = "The chat {} is already present in the list of allowed chat.".format(chat.title)
	if message.chat.type == "private":
		chat = await client.get_users(message.chat.id)
		chat = chat.__dict__
		lists = adminsIdList
		text = "The user {}{} is already present in the list of allowed user.".format("{} ".format(chat["first_name"]) if chat["first_name"] is not None else "", "{} ".format(chat["last_name"]) if chat["last_name"] is not None else "")
	else:
		chat = await client.get_chat(message.chat.id)
		chat = chat.__dict__
	await message.delete(revoke=True)
	if chat["id"] == constants.creator or chat["id"] in lists:
		await stopFilter.commute()
		logger.info(text)
		return
	if message.chat.type == "private":
		adminsIdList.append(chat["id"])
	else:
		chatIdList.append(chat["id"])
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
		if message.chat.type == "private":
			cursor.execute("INSERT INTO `Admins` (`id`, `is_self` ,`is_contact`, `is_mutual_contact`, `is_deleted`, `is_bot`, `is_verified`, `is_restricted`, `is_scam`, `is_support`, `first_name`, `last_name`, `username`, `language_code`, `phone_number`, `role`) VALUES (%(id)s, %(is_self)s, %(is_contact)s, %(is_mutual_contact)s, %(is_deleted)s, %(is_bot)s, %(is_verified)s, %(is_restricted)s, %(is_scam)s, %(is_support)s, %(first_name)s, %(last_name)s, %(username)s, %(language_code)s, %(phone_number)s)", chat)
			text = "I added {}{} to the list of allowed user.".format("{} ".format(chat["first_name"]) if chat["first_name"] is not None else "", "{} ".format(chat["last_name"]) if chat["last_name"] is not None else "")
		else:
			cursor.execute("INSERT INTO `Chats` (`id`, `type`, `is_verified`, `is_restricted`, `is_scam`, `is_support`, `title`, `username`, `first_name`, `last_name`, `invite_link`) VALUES (%(id)s, %(type)s, %(is_verified)s, %(is_restricted)s, %(is_scam)s, %(is_support)s, %(title)s, %(username)s, %(first_name)s, %(last_name)s, %(invite_link)s)", chat)
			text = "I added {} to the list of allowed chat.".format(chat["title"])
		connection.commit()
	await stopFilter.commute()
	logger.info(text)


@app.on_message(Filters.command("scheduling", prefixes="/") & Filters.user(adminsIdList))
def scheduling(client: Client, _):
	global messageMaxLength, scheduler

	logger.info("Setted the Job Queue")
	messageMaxLength = await client.send(GetConfig()).message_length_max
	scheduler.every().day.do(updateDatabase, client=client).run()
	while True:
		scheduler.run_pending()
		time.sleep(minute * 60 * 23)


@app.on_message(Filters.command("update", prefixes="/") & Filters.user(adminsIdList) & stopFilter)
async def updateDatabase(client: Client, message: Message = None):
	global adminsIdList, chatIdList, connection, constants, stopFilter

	await stopFilter.commute()
	if message is not None:
		await message.delete(revoke=True)
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
	chats = list()
	chatIdList.remove("me")
	for i in chatIdList:
		try:
			await chats.append(client.get_chat(i).__dict__)
		except FloodWait as e:
			time.sleep(e.x)
	chatIdList.append("me")
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
	return Filters.create(func, "UnknownFilter", p=re.compile("/{}".format("|/".join(commands)), 0))


@app.on_message(unknownFilter() & Filters.user(adminsIdList) & Filters.chat(chatIdList))
async def unknown(_, message: Message):
	if message.chat.type == "bot":
		return
	await message.edit_text("This command isn\'t supported.")
	logger.info("I managed an unsupported command.")


logger.info("Client initializated\nSetting the markup syntax ...")
app.set_parse_mode("html")
logger.info("Setted the markup syntax\nStarted serving ...")
app.run()
connection.close()
