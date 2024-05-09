from typing import List
import pickle
import os
from utils import GameInfos, GameInfo


def load_infos(type: str) -> List[GameInfos]:
    info_file: str = "./infos/" + type + "_infos.pkl"
    # print(f"try to load {info_file}")
    if not os.path.exists(info_file):
        return []
    with open(info_file, "rb") as f:
        load_infos = pickle.load(f)
    return load_infos


def save_infos(infos: List[GameInfos], type: str) -> None:
    info_file: str = "./infos/" + type + "_infos.pkl"
    with open(info_file, "wb") as f:
        pickle.dump(infos, f)


if __name__ == "__main__":
    infos = load_infos("23dice")
    for info in infos:
        print(info.date)
