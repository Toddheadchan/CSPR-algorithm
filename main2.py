import csprTournament
import glicko2
import json
import math
from utils import *

class CSPR:

	a = 0.8
	b = 0.2

	def getPlayer(self, id):
		return self.playerDictionary[id]

	def getBonusLine(self, bonusLine):
		ind = 0
		for i in range(len(self.rankingSpread)):
			if (self.rankingSpread[i] > bonusLine):
				return self.rankingSpread[i - 1]
		return self.rankingSpread[ind - 1]

	def getBonusPlayerCount(self, bonusLine):
		ind = 0
		for i in range(len(self.rankingSpread)):
			if (self.rankingSpread[i] > bonusLine):
				return self.rankingSpread[i - 1]
		return self.rankingSpread[ind] - 1


	def getLevelRanking(self, standing):
		for i in range(len(self.rankingSpread)):
			if (self.rankingSpread[i] == standing):
				return i+1
		return -1

	def preparePlayerInfo(self, playerList):

		tournamentBonus = 0
		totalPlayer = self.tournament.getTotalPlayer()
		bonusRate = math.log(totalPlayer, 8) ** 0.5

		self.rankingSpread = []

		for player in playerList:
			if not (player["id"] in self.playerDictionary):
				self.playerDictionary[player["id"]] = glicko2.Player()
				self.getPlayer(player["id"]).setInfo(player["gamerTag"], player["id"])
			self.getPlayer(player["id"]).resetResult()
			if self.rankingSpread == [] or (self.rankingSpread != [] and player["standing"] != self.rankingSpread[-1]):
				self.rankingSpread.append(player["standing"])

			tournamentBonus += self.playerDictionary[player["id"]].getPlayerWeight()
			# tournamentBonus += 1

		bonusLine = self.getBonusLine(totalPlayer / 4)

		# counting bonus

		avgPlayerCount = math.floor(totalPlayer * 0.6) 

		for player in playerList:
			standing = player["standing"]
			if (standing == -1): 
				continue
			rankingRate = self.a / self.getLevelRanking(standing) + max(0, self.b * (avgPlayerCount - standing) / 2 / avgPlayerCount)
			self.getPlayer(player["id"]).bonusRating(tournamentBonus * bonusRate * rankingRate - self.getPlayer(player["id"]).getPlayerWeight())
			# print (player["gamerTag"], ' BONUS: ', tournamentBonus * bonusRate * rankingRate - self.getPlayer(player["id"]).getPlayerWeight())

	def setsAdapt(self, setInfo):
		winnerId = setInfo["winner_id"]
		loserId = setInfo["loser_id"]
		winner = self.getPlayer(winnerId)
		loser = self.getPlayer(loserId)
		'''
		self.getPlayer(winnerId).newSet(loser.getRating(), loser.getRd(), 1)
		self.getPlayer(loserId).newSet(winner.getRating(), winner.getRd(), 0)
		'''
		self.getPlayer(winnerId).myUpdate2(loser.getRating(), loser.getRd(), 1)
		self.getPlayer(loserId).myUpdate2(winner.getRating(), winner.getRd(), 0)

	def countingSets(self, setList):
		winnerBracket = []
		loserBracket = []
		grandFinal = {}
		grandFinalReset = {}

		for setInfo in setList:
			if setInfo["DQ"] == True:
				continue
			if setInfo['round'] > 0:
				if setInfo['roundText'] == 'Grand Final':
					grandFinal = setInfo
				elif setInfo['roundText'] == 'Grand Final Reset':
					grandFinalReset = setInfo
				else: winnerBracket.append(setInfo)
			if setInfo['round'] < 0:
				loserBracket.append(setInfo)

		winnerBracket = sorted(winnerBracket, key=lambda setInfo: setInfo["round"])
		loserBracket = sorted(loserBracket, key=lambda setInfo: setInfo["round"], reverse=True)

		for setInfo in winnerBracket:
			self.setsAdapt(setInfo)
		for setInfo in loserBracket:
			self.setsAdapt(setInfo)
		if grandFinal != {}:
			self.setsAdapt(grandFinal)
		if grandFinalReset != {}:
			self.setsAdapt(grandFinalReset)
			
	def updatePlayer(self, playerList):
		totalPlayer = self.tournament.getTotalPlayer()
		for player in playerList:
			self.getPlayer(player["id"]).myUpdate(player["standing"], totalPlayer, self.tournament.getTournamentId())

	def runTournament(self, tournamentId):
		self.participant = {}
		self.tournament = csprTournament.Tournament(tournamentId)
		playerList = self.tournament.getSortedPlayer()
		self.preparePlayerInfo(playerList)
		self.countingSets(self.tournament.getSetList())
		# self.updatePlayer(playerList)

	def printCSPR(self):
		playerList = []
		for playerId in self.playerDictionary:
			player = self.playerDictionary[playerId]
			if not player.getIsRanked(): continue
			playerList.append({
				"name": player.getName(),
				"rating": player.getRating(),
				"RD": player.getRd(),
				"id": player.getPlayerId(),
				"log": player.getLog()
			})

		playerList = sorted(playerList, key=lambda player: player["rating"], reverse=True)
		for player in playerList:
			print (player["name"], "       ", player["rating"])
		#updateCSPRDB(playerList, self.season)


	def runCSPR(self):
		for tournament in self.tournamentList:
			self.tournamentId = tournament["tournamentId"]
			self.runTournament(tournament["tournamentId"])
		self.printCSPR()

	def __init__(self, season):
		self.playerDictionary = {}
		self.season = season
		self.tournamentList = getCSPRTournamentList(self.season)

if __name__ == "__main__":
	CSPR0 = CSPR(1)
	CSPR0.runCSPR()