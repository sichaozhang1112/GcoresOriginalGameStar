import requests
import pickle
import datetime
import os
import argparse
import matplotlib.pyplot as plt
from typing import List


class GameInfo:
    def __init__(self, id: int) -> None:
        self.id = id
        if not self._request():
            return
        self.star: int = self.request["data"]["attributes"]["subscriptions-count"]
        self.title: str = self.request["data"]["attributes"]["title"]

    def _request(self) -> bool:
        try:
            url: str = (
                "https://www.gcores.com/gapi/v1/games/"
                + str(self.id)
                + "?include=tags%2Cuser%2Cgame-stores%2Cinvolvements.entity.user&meta[tags]=%2C"
            )
            self.request = requests.get(url).json()
            return True

        except Exception as e:
            print(e)
            print("Fail to request!")
            return False


class GameInfos:
    def __init__(
        self, date: str, game_infos: List[GameInfo], max_num: int = 10
    ) -> None:
        self.max_num = max_num
        self.date = date
        self.infos = game_infos

    def find(self, id: int) -> int:
        for info in self.infos:
            if info.id == id:
                return info.star
        return -1

    def serialize(self) -> str:
        result: str = ""
        for info in self.infos[: self.max_num]:
            result += info.title + "🌟" + str(info.star) + "\n\n"
        return result

    def print(self) -> None:
        print("today date: ", self.date)
        print("booom game total num: ", len(self.infos))
        for info in self.infos[: self.max_num]:
            print(info.title, "🌟", info.star)


def get_today_infos() -> GameInfos:
    today = datetime.date.today()
    # get game infos
    game_ids: set = get_game_ids()
    game_infos: List[GameInfo] = [info for info in [GameInfo(id) for id in game_ids]]
    # sort by star
    game_infos.sort(key=lambda x: x.star, reverse=True)
    today_infos: GameInfos = GameInfos(today.strftime("%Y-%m-%d"), game_infos)
    return today_infos


def load_infos() -> List[GameInfos]:
    if not os.path.exists("infos.pkl"):
        return []
    with open("infos.pkl", "rb") as f:
        game_infos = pickle.load(f)
    return game_infos


def save_infos(infos: List[GameInfos]) -> None:
    with open("infos.pkl", "wb") as f:
        pickle.dump(infos, f)


def get_game_ids() -> set:
    game_ids: set = set()
    try:
        page_limit: int = 100
        max_offset: int = 10
        for i in range(max_offset):
            url: str = (
                "https://www.gcores.com/gapi/v1/games?page[limit]="
                + str(page_limit)
                + "&page[offset]="
                + str(i * page_limit)
                + "&sort=-content-updated-at&include=tags&filter[is-original]=1&filter[revised]=1&meta[tags]=%2C&meta[games]=%2C"
            )
            request_info = requests.get(url).json()
            if request_info["data"] == []:
                break
            for game in request_info["data"]:
                if "BOOOM作品" not in game["attributes"]["development-status"]:
                    continue
                if game["attributes"]["is-booom"] is not True:
                    continue
                game_ids.add(game["id"])
    except Exception as e:
        print(e)
        print("Fail to request!")
    return game_ids


def write_readme(infos: List[GameInfos]) -> None:
    info: GameInfos = len(infos) > 0 and infos[-1] or get_today_infos()
    with open("README.md", "w") as readme:
        readme.write(
            "# GcoresOriginalGameStar\n\n"
            + "## requirements\n"
            + "```\n"
            + "pip3 install -r requirements.txt\n"
            + "```\n\n"
            + "## how to use\n"
            + "```\n"
            + "python3 get_star.py --update\n"
            + "```\n\n"
            + "## BOOOM lab stars, update on "
            + info.date
            + " \n"
        )
        readme.write("<div align='center'>\n")
        readme.write(
            "<img src=./stars.png alt='BOOOM lab stars' style='width:1000px;height:auto;'>\n"
        )
        readme.write("</div>\n\n")
        readme.write(info.serialize())


def draw(infos: List[GameInfos]) -> None:
    if len(infos) == 0:
        infos = [get_today_infos()]
    x = [info.date for info in infos]
    colors = ["red", "orange", "green", "blue", "purple"]
    plt.figure(figsize=(20, 12))
    for i in range(len(infos[-1].infos)):
        info = infos[-1].infos[i]
        y = []
        for j in range(len(infos)):
            star: int = infos[-j - 1].find(info.id)
            if star == -1:
                star = y[0]
            y.insert(0, star)
        plt.plot(
            x,
            y,
            "-x",
            color=colors[i % len(colors)],
        )
    plt.xlabel("date", fontsize=12, fontweight="bold")
    plt.ylabel("stars", fontsize=12, fontweight="bold")
    plt.title("BOOOM lab game stars", fontsize=16, fontweight="bold")
    plt.grid()
    plt.savefig("stars.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true", help="update today infos")
    parser.add_argument("--clear", action="store_true", help="clear cached infos")

    if parser.parse_args().clear:
        if os.path.exists("README.md"):
            os.remove("README.md")
        if os.path.exists("stars.png"):
            os.remove("stars.png")
        if os.path.exists("infos.pkl"):
            os.remove("infos.pkl")

    infos: List[GameInfos] = load_infos()
    if parser.parse_args().update:
        today_infos: GameInfos = get_today_infos()
        today_infos.print()
        if len(infos) > 0 and infos[-1].date == today_infos.date:
            infos[-1] = today_infos
        else:
            infos.append(today_infos)

    max_date_num: int = 7
    if len(infos) > max_date_num:
        infos = infos[-max_date_num:]
    save_infos(infos)
    draw(infos)
    write_readme(infos)
