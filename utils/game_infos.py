import datetime
import time
import requests
from typing import List


def identify_game_type(data: dict) -> str:
    if data["attributes"]["event-name"] == "2024 side effect":
        return "24SideEffect"
    elif data["attributes"]["event-name"] == "2023 Re":
        return "23Re"
    elif data["attributes"]["event-name"] == "2023 Dice":
        return "23Dice"
    elif data["attributes"]["event-name"] == "2021 时间是幻觉":
        return "21TimeIsAnIllusion"
    elif data["attributes"]["event-name"] == "夏日纳凉特别篇｜Giggling":
        return "Giggling"
    elif data["attributes"]["event-name"] == "保时捷特别回合":
        return "24Porsche"
    return "Others"


class GameInfo:

    def __init__(self, id: int) -> None:
        # init info
        self.id = id
        self.star = 0
        self.title = "game"
        self.team_size = 0
        self.type = "Others"

        if not self._request():
            return

        self.star: int = self.request["data"]["attributes"]["subscriptions-count"]
        self.title: str = self.request["data"]["attributes"]["title"]
        self.team_size = 0
        for data in self.request["included"]:
            if data["type"] == "users":
                self.team_size += 1
        self.type: str = identify_game_type(self.request["data"])

    def _request(self) -> bool:
        try:
            url: str = (
                "https://www.gcores.com/gapi/v1/games/"
                + str(self.id)
                + "?include=tags%2Cuser%2Cgame-stores%2Cinvolvements.entity.user&meta[tags]=%2C"
            )
            self.request = requests.get(url).json()
            time.sleep(0.5)
            return True

        except Exception as e:
            print(e)
            print("fail to request game ", self.id, "!")
            time.sleep(1)
            return False


class GameInfos:

    def __init__(
        self, date: str, game_infos: List[GameInfo], max_num: int = 10
    ) -> None:
        self.max_num = max_num
        self.date = date
        self.infos = game_infos
        self.type = game_infos[0].type

    def sort(self) -> None:
        self.infos.sort(key=lambda x: x.star, reverse=True)

    def find(self, id: int) -> int:
        for info in self.infos:
            if info.id == id:
                return info.star
        return -1

    def serialize(self) -> str:
        result: str = ""
        for info in self.infos[: self.max_num]:
            result += (
                "{:<5}".format("🌟" + str(info.star))
                + "{:<5}".format("👥" + str(info.team_size))
                + "{:<20}".format("🎮" + info.title)
                + "\n\n"
            )
        return result

    def print(self) -> None:
        print("today date: ", self.date)
        print("booom ", self.type, " game total num: ", len(self.infos))
        cnt = 1
        for info in self.infos[:]:
            print(
                cnt,
                ".",
                "{:<5}".format("🌟" + str(info.star)),
                "{:<5}".format("👥" + str(info.team_size)),
                "{:<20}".format("🎮" + info.title),
            )
            cnt += 1
