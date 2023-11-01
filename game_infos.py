import datetime
import time
import requests
from typing import List


class GameInfo:

    def __init__(self, id: int) -> None:
        self.id = id
        if not self._request():
            return

        self.star: int = self.request["data"]["attributes"][
            "subscriptions-count"]
        self.title: str = self.request["data"]["attributes"]["title"]
        self.type: str = "all"
        if self.request["data"]["attributes"]["is-booom"]:
            self.type = "23lab"
        modified_date = datetime.datetime.strptime(
            self.request["data"]["attributes"]["modified-at"][:10], "%Y-%m-%d")
        if modified_date >= datetime.datetime(
                2023, 9, 20) and modified_date <= datetime.datetime(
                    2023, 10, 11):
            self.type = "23dice"
        self.team_size = 0
        for data in self.request["included"]:
            if data["type"] == "users":
                self.team_size += 1
        # print("find ", self.id, "🎮", self.title, "🌟", self.star, "😊",
        #       self.team_size)

    def _request(self) -> bool:
        try:
            url: str = (
                "https://www.gcores.com/gapi/v1/games/" + str(self.id) +
                "?include=tags%2Cuser%2Cgame-stores%2Cinvolvements.entity.user&meta[tags]=%2C"
            )
            self.request = requests.get(url).json()
            time.sleep(1)
            return True

        except Exception as e:
            print(e)
            print("fail to request game ", self.id, "!")
            time.sleep(1)
            return False


class GameInfos:

    def __init__(self,
                 date: str,
                 game_infos: List[GameInfo],
                 max_num: int = 10) -> None:
        self.max_num = max_num
        self.date = date
        self.infos = game_infos
        self.type = game_infos[0].type

    def find(self, id: int) -> int:
        for info in self.infos:
            if info.id == id:
                return info.star
        return -1

    def serialize(self) -> str:
        result: str = ""
        for info in self.infos[:self.max_num]:
            result += "{:<5}".format("🌟" + str(info.star)) + "{:<5}".format("😊" + str(info.team_size)) + "{:<20}".format("🎮" + info.title) + "\n\n"
        return result

    def print(self) -> None:
        print("today date: ", self.date)
        print("booom ", self.type, " game total num: ", len(self.infos))
        for info in self.infos[:]:
            print(
                "{:<5}".format("🌟" + str(info.star)),
                "{:<5}".format("😊" + str(info.team_size)),
                "{:<20}".format("🎮" + info.title),
            )
