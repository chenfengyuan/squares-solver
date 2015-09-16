#!/usr/bin/env python
# coding=utf-8
import requests
import json

from libs import puzzle
__author__ = 'chenfengyuan'


def main():
    session = requests.Session()
    while True:
        resp = session.get("http://127.0.0.1:8888/api/puzzle")
        print(resp.content)
        data = json.loads(resp.content.decode('utf-8'))
        solver = puzzle.PuzzleSolver(data["data"])
        data["data"] = json.dumps(solver.solve())
        requests.put("http://127.0.0.1:8888/api/puzzle", data=data)


if __name__ == '__main__':
    main()