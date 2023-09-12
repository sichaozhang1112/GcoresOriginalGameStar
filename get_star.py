import requests
from typing import List


def get_original_game_ids() -> set:
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
                if game["attributes"]["is-booom"] is not True:
                    continue
                game_ids.add(game["id"])
    except Exception as e:
        print(e)
        print("Fail to request!")
    return game_ids


class GameInfo:

    def __init__(self, id: int) -> None:
        self.id = id
        if not self._request():
            return
        self.star: int = self.request["data"]["attributes"][
            "subscriptions-count"]
        self.title: str = self.request["data"]["attributes"]["title"]

    def _request(self) -> bool:
        try:
            url: str = (
                "https://www.gcores.com/gapi/v1/games/" + str(self.id) +
                "?include=tags%2Cuser%2Cgame-stores%2Cinvolvements.entity.user&meta[tags]=%2C"
            )
            self.request = requests.get(url).json()
            return True

        except Exception as e:
            print(e)
            print("Fail to request!")
            return False


if __name__ == "__main__":
    game_ids: set = get_original_game_ids()
    print("booom game total num: ", len(game_ids))
    game_infos: List[GameInfo] = [
        info for info in [GameInfo(id) for id in game_ids]
    ]
    # sort by star
    game_infos.sort(key=lambda x: x.star, reverse=True)
    for info in game_infos:
        print(info.title + ": " + str(info.star))
