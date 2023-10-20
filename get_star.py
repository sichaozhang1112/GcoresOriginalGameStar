import requests
import pickle
import datetime
import os
import argparse
import time
import matplotlib.pyplot as plt
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
            result += info.title + "🌟" + str(info.star) + "\n\n"
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


def get_today_infos() -> GameInfos:
    today = datetime.date.today()
    # get game infos
    game_ids: set = get_game_ids()
    game_infos: List[GameInfo] = [
        info for info in [GameInfo(id) for id in game_ids]
    ]
    # sort by star
    game_infos.sort(key=lambda x: x.star, reverse=True)
    today_infos: GameInfos = GameInfos(today.strftime("%Y-%m-%d"), game_infos)
    return today_infos


def load_infos(type: str) -> List[GameInfos]:
    info_file: str = "./infos/" + type + "_infos.pkl"
    if not os.path.exists(info_file):
        return []
    with open(info_file, "rb") as f:
        game_infos = pickle.load(f)
    return game_infos


def save_infos(infos: List[GameInfos], type: str) -> None:
    info_file: str = "./infos/" + type + "_infos.pkl"
    with open(info_file, "wb") as f:
        pickle.dump(infos, f)


def get_game_ids() -> set:
    game_ids: set = set()
    try:
        page_limit: int = 100
        max_offset: int = 10
        for i in range(max_offset):
            url: str = (
                "https://www.gcores.com/gapi/v1/games?page[limit]=" +
                str(page_limit) + "&page[offset]=" + str(i * page_limit) +
                "&sort=-content-updated-at&include=tags&filter[is-original]=1&filter[revised]=1&meta[tags]=%2C&meta[games]=%2C"
            )
            request_info = requests.get(url).json()
            if request_info["data"] == []:
                break
            for game in request_info["data"]:
                if "BOOOM作品" not in game["attributes"]["development-status"]:
                    continue
                game_ids.add(game["id"])
            time.sleep(1)
    except Exception as e:
        print(e)
        print("fail to request game ids!")
    return game_ids


def write_readme(booom_list: List) -> None:
    with open("README.md", "w") as readme:
        readme.write("# GcoresOriginalGameStar\n\n" + "## requirements\n" +
                     "```\n" + "pip3 install -r requirements.txt\n" +
                     "```\n\n" + "## how to use\n" + "```\n" +
                     "python3 get_star.py --update\n" + "```\n\n")
        for type in booom_list:
            infos = load_infos(type)
            if len(infos) == 0:
                continue
            info = infos[-1]
            readme.write("## BOOOM " + type + " stars, update on " +
                         info.date + " \n")
            readme.write("<div align='center'>\n")
            readme.write(
                "<img src=./pics/" + type +
                "_stars.png alt='BOOOM stars' style='width:1000px;height:auto;'>\n"
            )
            readme.write("</div>\n\n")
            readme.write(info.serialize())


def draw(infos: List[GameInfos], type: str) -> None:
    x = [info.date for info in infos]
    colors = ["red", "orange", "green", "blue", "purple"]
    plt.figure(figsize=(20, 15))
    plt.xkcd()
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
    plt.title("BOOOM " + type + " game stars", fontsize=16, fontweight="bold")
    plt.xticks(rotation=90)
    plt.grid()
    plt.savefig("./pics/" + type + "_stars.png")


def update(today_infos: GameInfos, type: str) -> None:
    infos: List[GameInfos] = load_infos(type)
    if len(infos) > 0 and infos[-1].date == today_infos.date:
        infos[-1] = today_infos
    else:
        infos.append(today_infos)
    max_date_num: int = 30
    if type == "all":
        max_date_num = 7
    if len(infos) > max_date_num:
        infos = infos[-max_date_num:]
    draw(infos, type)
    save_infos(infos, type)


def select_type_infos(today_infos: GameInfos, type: str) -> GameInfos:
    if type == "all":
        return today_infos
    game_infos: List[GameInfo] = []
    for info in today_infos.infos:
        if info.type == type:
            game_infos.append(info)
    return GameInfos(today_infos.date, game_infos)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update",
                        type=str,
                        default="all",
                        help="update today infos")
    parser.add_argument("--print",
                        type=str,
                        default="",
                        help="print today infos")
    parser.add_argument("--clear",
                        action="store_true",
                        help="clear cached infos")
    parser.add_argument("--debug", type=str, default="", help="debug mode")

    if parser.parse_args().clear:
        if os.path.exists("README.md"):
            os.remove("README.md")
        if os.path.exists("./infos/"):
            os.rmdir("./infos/")
        if os.path.exists("./pics/"):
            os.rmdir("./pics/")

    os.makedirs("./infos/", exist_ok=True)
    os.makedirs("./pics/", exist_ok=True)

    booom_list: List = ["all", "23lab", "23dice"]

    if parser.parse_args().debug != "":
        game_ids: set = get_game_ids()
        for id in game_ids:
            if parser.parse_args().debug == str(id):
                print("find ", id)
    elif parser.parse_args().print != "":
        infos: List[GameInfos] = load_infos(parser.parse_args().print)
        if len(infos) == 0:
            print("no infos!")
            exit(0)
        infos[-1].print()
    elif parser.parse_args().update == "all":
        today_infos: GameInfos = get_today_infos()
        for type in booom_list:
            type_infos: GameInfos = select_type_infos(today_infos, type)
            # type_infos.print()
            update(type_infos, type)
    elif parser.parse_args().update in booom_list:
        today_infos: GameInfos = get_today_infos()
        type = parser.parse_args().update
        type_infos: GameInfos = select_type_infos(today_infos, type)
        # type_infos.print()
        update(type_infos, type)
    write_readme(booom_list)
