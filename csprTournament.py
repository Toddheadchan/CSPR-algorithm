import json
import glicko2
from utils import *

class Tournament:

	def __init__(self, tournamentId):
		self.tournamentId = tournamentId
		# 获取tournament信息
		self.tournamentInfo = getTournamentDetailInfo(tournamentId)
		self.tournamentName = self.tournamentInfo["tournamentName"]
		self.playerList = self.tournamentInfo["players"]
		self.setList = self.tournamentInfo["sets"]
		self.totalPlayer = self.countTotalPlayer()
		self.totalPlayer = self.tournamentInfo["totalPlayer"]

	def preparePlayer(self, playerList):
		self.participantDic = {}
		for player in playerList:
			if player["id"] in self.playerDictionary == False:
				self.playerDictionary[player["id"]] = glicko2.player()
			self.participantDic[player["participantId"]] = player["id"]

	def countTotalPlayer(self):
		playerSet = set()
		for setInfo in self.setList:
			if setInfo["DQ"] == True: continue
			playerSet.add(setInfo["winner_id"])
			playerSet.add(setInfo["loser_id"])
		return len(playerSet)

	def getTournamentName(self):
		return self.tournamentName

	def getTournamentId(self):
		return self.tournamentId

	def getSortedPlayer(self):
		return sorted(self.playerList, key=lambda player: player["standing"])

	def getTotalPlayer(self):
		return self.totalPlayer

	def getSetList(self):
		return self.setList

	def test(self):
		print (self.tournamentList[0])