import requests
import pickle
import datetime
import os
import argparse
import time
import matplotlib.pyplot as plt
from typing import List
from utils import GameInfo, GameInfos, identify_game_type
from utils import load_infos, save_infos


def get_today_infos(type: str="all") -> GameInfos:
    today = datetime.date.today()
    # get game infos
    game_ids: set = get_game_ids(type)
    print(f"today game ids total cnt {len(game_ids)}")
    game_infos: List[GameInfo] = [info for info in [GameInfo(id) for id in game_ids]]
    today_infos: GameInfos = GameInfos(today.strftime("%Y-%m-%d"), game_infos)
    today_infos.sort()
    return today_infos


def get_game_ids(type: str="all") -> set:
    game_ids: set = set()
    try:
        page_limit: int = 100
        max_offset: int = 100
        for i in range(max_offset):
            url: str = (
                "https://www.gcores.com/gapi/v1/games?page[limit]="
                + str(page_limit)
                + "&page[offset]="
                + str(i * page_limit)
                + "&sort=-content-updated-at&include=tags&filter[is-original]=1&filter[revised]=1&meta[tags]=%2C&meta[games]=%2C"
            )
            print(f"try to reuqest from {url}")
            request_info = requests.get(url).json()
            if request_info["data"] == []:
                break
            for game in request_info["data"]:
                # print(f"{game["attributes"]["title"]} is {identify_game_type(game)}")
                if type != "all" and identify_game_type(game) != type:
                    continue
                game_ids.add(game["id"])
            time.sleep(1)
    except Exception as e:
        print(e)
        print("fail to request game ids!")
    return game_ids


def write_readme(booom_list: List) -> None:
    with open("README.md", "w") as readme:
        readme.write(
            "# GcoresOriginalGameStar\n\n"
            + "## requirements\n"
            + "```\n"
            + "pip3 install -r requirements.txt\n"
            + "```\n\n"
            + "## how to use\n"
            + "```\n"
            + "python3 get_star.py --update all\n"
            + "python3 gen_html.py\n"
            + "```\n\n"
        )
        for type in booom_list:
            infos = load_infos(type)
            if len(infos) == 0:
                continue
            info = infos[-1]
            readme.write(
                "## [🔗BOOOM "
                + type
                + " stars, update on "
                + info.date
                + "👈](https://raw.githack.com/sichaozhang1112/GcoresOriginalGameStar/main/html/"
                + type
                + ".html)"
                + " \n"
            )
            # readme.write("<div align='center'>\n")
            # readme.write(
            #     "<img src=./pics/" + type +
            #     "_stars.png alt='BOOOM stars' style='width:1000px;height:auto;'>\n"
            # )
            # readme.write("</div>\n\n")
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
    parser.add_argument("--update", type=str, default="all", help="update today infos")
    parser.add_argument("--print", type=str, default="", help="print today infos")
    parser.add_argument("--clear", action="store_true", help="clear cached infos")
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

    booom_list: List = ["all", "24SideEffect"]

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
        print(f"today infos total cnt {len(today_infos.infos)}")
        for type in booom_list:
            type_infos: GameInfos = select_type_infos(today_infos, type)
            print(f"today {type} infos total cnt {len(type_infos.infos)}")
            # type_infos.print()
            update(type_infos, type)
    elif parser.parse_args().update in booom_list:
        today_infos: GameInfos = get_today_infos(parser.parse_args().update)
        print(f"today infos total cnt {len(today_infos.infos)}")
        type = parser.parse_args().update
        type_infos: GameInfos = select_type_infos(today_infos, type)
        print(f"today {type} infos total cnt {len(type_infos.infos)}")
        # type_infos.print()
        update(type_infos, type)
    write_readme(booom_list)
