# database
import pymysql
import datetime

# 获取数据库连接
def getDB():
	#db = pymysql.connect(host='112.74.17.146', port=8036, user='root', password='GZ_smash8', database='cspr_dev')
	db = pymysql.connect(host='112.74.17.146', port=8036, user='root', password='GZ_smash8', database='cspr')
	cursor = db.cursor()

	return db, cursor

def getTournamentTime(tournament):
	return tournament['time']

# 获取需要计算cspr的比赛
def getCSPRTournamentList(season):

	db, cursor = getDB()

	sql = 'select * from tournament where season = %d and cspr_rate = 1' % season
	cursor.execute(sql)
	results = cursor.fetchall()
	db.close()

	tournamentList = []

	for row in results:
		tournamentList.append({
			'tournamentId': row[0],
			'time': row[3]
		})

	tournamentList.sort(key=getTournamentTime)

	return tournamentList

# 获取比赛详细信息
def getTournamentDetailInfo(tournamentId):

	db, cursor = getDB()

	sql = 'select * from participate_tournament where tournament_id = %d' % tournamentId
	cursor.execute(sql)
	results = cursor.fetchall()
	db.close()

	tournamentInfo = {
		"startTime": int(results[0][6].timestamp()),
		"tournamentName": results[0][4],
		"totalPlayer": len(results)
	}

	# 组装参加者数据
	players = []
	for row in results:
		players.append({
			"id": row[1],
			"gamerTag": row[2],
			"standing": row[3]
		})

	# 获取sets数据
	db, cursor = getDB()
	sql = 'select * from player_set where tournament_id = %d' % tournamentId
	cursor.execute(sql)
	results = cursor.fetchall()
	db.close()

	sets = []
	for row in results:
		sets.append({
			"winner_id": row[0],
			"loser_id": row[2],
			'round': row[5],
			'roundText': row[6],
			"DQ": (row[8] == -1)
		})

	tournamentInfo["players"] = players
	tournamentInfo["sets"] = sets

	return tournamentInfo

# 上传CSPR数据
def updateCSPRDB(playerList, season):

	db, cursor = getDB()

	# 删除旧数据
	sql = 'delete from cspr where season = %d' % season
	cursor.execute(sql)
	sql = 'delete from cspr_log where season = %d' % season
	cursor.execute(sql)

	# 组合新数据并添加数据库
	lastRating = 0
	ranking = 0
	showingRanking = 0
	for player in playerList:
		ranking += 1
		if player["rating"] != lastRating:
			showingRanking = ranking
		lastRating = player["rating"]
		print(player["id"], player["name"], player["rating"])
		sql = 'insert into cspr values(%d, %d, %d, %d)' % (player["id"], int(player['rating']), season, showingRanking)
		cursor.execute(sql)
		# 添加log表
		for log in player["log"]:
			sql = 'insert into cspr_log values(null, %d, %d, %d, %d, %d)' % (player["id"], log["tournamentId"], int(log["oldRating"]), int(log["rating"]), season)
			cursor.execute(sql)
	db.commit()