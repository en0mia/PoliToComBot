import subprocess


class Constants:

	def __init__(self):
		self.__appHash = "HASH"
		self.__appId = 0
		self.__botUsername = "PoliToComBot"
		self.__botToken = "TOKEN DEL BOT"
		self.__creator = 0
		pwd = str(subprocess.check_output("pwd", shell=True))
		pwd = pwd.replace("b\'", "")
		pwd = pwd.replace("\\n\'", "")
		if pwd == "/":
			self.__path = "home/USER/Documents/gitHub/{}/".format(self.__botUsername)
		elif pwd == "/home":
			self.__path = "USER/Documents/gitHub/{}/".format(self.__botUsername)
		elif pwd == "/home/USER":
			self.__path = "Documents/gitHub/{}/".format(self.__botUsername)
		elif pwd == "/home/USER/Documents":
			self.__path = "gitHub/{}/".format(self.__botUsername)
		elif pwd == "/home/USER/Documents/gitHub":
			self.__path = "{}/".format(self.__botUsername)
		elif pwd == "/root":
			self.__path = "/home/USER/Documents/gitHub/{}/".format(self.__botUsername)
		elif pwd == "/data/data/com.termux/files/home":
			self.__path = "downloads/{}/".format(self.__botUsername)
		elif pwd == "/data/data/com.termux/files/home/downloads":
			self.__path = "{}/".format(self.__botUsername)
		else:
			self.__path = "./"

	@property
	def creator(self) -> int:
		return self.__creator

	@property.setter
	def creator(self, ID: int):
		self.__creator = ID

	@property.deleter
	def creator(self):
		self.__creator = 0

	@property
	def databasePath(self) -> str:
		return self.__path

	@property
	def hash(self) -> str:
		return self.__appHash

	@property
	def id(self) -> int:
		return self.__appId

	@property
	def token(self) -> str:
		return self.__botToken

	@property
	def username(self) -> str:
		return self.__botUsername
