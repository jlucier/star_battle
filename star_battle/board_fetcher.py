import json
from pathlib import Path
import random

import requests

BASE_URL = "https://krazydad.com/tablet/starbattle/"
KINDS = {
    8: "8x8",
    10: "10x10",
    14: "14x14",
}
VOLUMES = list(range(1, 5))
BOOKS = list(range(1, 100))
PUZZLES = list(range(1, 24))


def parse_puzzle_data(page_content):
    start_seq = "var pRec = "
    end_seq = "};</script>"

    start = page_content.index(start_seq)
    return json.loads(
        page_content[start + len(start_seq) : page_content.index(end_seq, start) + 1]
    )["puzzle_data"]


def download_puzzle(kind=10, volume=1, book=1, puzzle=1):
    resp = requests.get(
        BASE_URL,
        params={"kind": kind, "volumeNumber": volume, "bookNumber": book, "puzzleNumber": puzzle,},
    )

    if resp.status_code != 200:
        raise Exception(f"Couldn't get puzzle: {resp}")

    return parse_puzzle_data(resp.content.decode())


def get_random_puzzle():
    kind = KINDS[random.choice(list(KINDS.keys()))]
    volume = random.choice(VOLUMES)
    book = random.choice(BOOKS)
    puzzle = random.choice(PUZZLES)

    return download_puzzle(kind=kind, volume=volume, book=book, puzzle=puzzle)


def get_local_puzzle(num=3):
    with open(Path(__file__).parent / "data" / f"puzzle_{num}.json") as f:
        return json.load(f)["puzzle_data"]
