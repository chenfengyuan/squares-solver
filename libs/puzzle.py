#!/usr/bin/env python
# coding=utf-8

import json
import collections
import random
import time
__author__ = 'chenfengyuan'


class Piece:
    def __init__(self, type_=0, dir_=0, color=""):
        self.type = type_
        self.dir = dir_
        self.color = color

    def is_empty(self):
        return self.type == 0

    def is_dest(self):
        return self.type == 1

    def is_moveable(self):
        return self.type == 2

    def is_arrow(self):
        return self.type == 3

    def get_delta(self):
        assert self.is_moveable(), "%s is not moveable" % self
        delta_x = 0
        delta_y = 0
        if self.dir == 0:
            delta_x = -1
        elif self.dir == 1:
            delta_y = 1
        elif self.dir == 2:
            delta_x = 1
        elif self.dir == 3:
            delta_y = -1
        return delta_x, delta_y

    def copy(self):
        p = Piece()
        p.type = self.type
        p.dir = self.dir
        p.color = self.color
        return p

    def __repr__(self):
        return "Piece(type_=%s,dir_=%s,color=%s)" % (self.type, self.dir, self.color)


class Puzzle:
    """
WIDTH       y ---->
HEIGHT    x 0 1 2
          \ 1
          \ 2
          \
          v
    """
    WIDTH = 10
    HEIGHT = 10
    SIZE = WIDTH * HEIGHT

    def __init__(self, data=None):
        self.back_board = []
        """:type : list[Piece]"""
        self.front_board = []
        """:type : list[Piece]"""
        self.moveable_pos = {}
        """:type : dict[str, int]"""
        self.dst_pos = {}
        """:type : dict[str, int]"""
        p = Piece()
        for i in range(self.SIZE):
            self.back_board.append(p)
            self.front_board.append(p)

        if data:
            self.min_x = self.HEIGHT
            self.max_x = 0
            self.min_y = self.WIDTH
            self.max_y = 0
            data = json.loads(data)
            assert len(data) == self.SIZE
            for i in range(self.SIZE):
                p = Piece()
                p.type = data[i].get("type", 0)
                p.dir = data[i].get("dir", 0)
                p.color = data[i].get("color", "")
                if p.is_moveable():
                    if p.color in self.moveable_pos:
                        raise RuntimeError("duplicate color " + p.color)
                    self.moveable_pos[p.color] = i
                    self.front_board[i] = p
                else:
                    self.back_board[i] = p
                    if p.is_dest():
                        self.dst_pos[p.color] = i
                if not p.is_empty():
                    x, y = self.get_x_y(i)
                    self.min_x = min(self.min_x, x)
                    self.max_x = max(self.max_x, x)
                    self.min_y = min(self.min_y, y)
                    self.max_y = max(self.max_y, y)

    @classmethod
    def get_x_y(cls, pos):
        x = pos // cls.WIDTH
        y = pos % cls.WIDTH
        assert cls.on_board(x, y)
        return x, y

    @classmethod
    def get_pos(cls, x, y):
        assert cls.on_board(x, y)
        return x * cls.WIDTH + y

    @classmethod
    def on_board(cls, x, y):
        if not (0 <= x < cls.HEIGHT):
            return False
        if not (0 <= y < cls.WIDTH):
            return False
        return True

    def can_move(self, color):
        pos = self.moveable_pos[color]
        p = self.front_board[pos]
        x, y = self.get_x_y(pos)
        delta_x, delta_y = p.get_delta()
        for i in range(min(self.WIDTH, self.HEIGHT)):
            x += delta_x
            y += delta_y
            if not self.on_board(x, y):
                break
            new_pos = self.get_pos(x, y)
            if not self.front_board[new_pos].is_moveable():
                return True

    def move(self, color):
        pos = self.moveable_pos[color]
        p = self.front_board[pos]
        self.front_board[pos] = Piece()
        x, y = self.get_x_y(pos)
        delta_x, delta_y = p.get_delta()
        while True:
            x += delta_x
            y += delta_y
            assert self.on_board(x, y)
            dst_pos = self.get_pos(x, y)
            dst_piece = self.front_board[dst_pos]

            self.moveable_pos[p.color] = dst_pos
            self.front_board[dst_pos] = p
            if self.back_board[dst_pos].is_arrow():
                p.dir = self.back_board[dst_pos].dir
            if dst_piece.is_moveable():
                p = dst_piece
            elif dst_piece.is_empty():
                break
            else:
                raise RuntimeError("%s should not on the front board" % dst_piece)

    def is_finish(self):
        for k, v in self.moveable_pos.items():
            assert k in self.dst_pos
            if self.dst_pos[k] != v:
                return False
        return True

    def get_score(self):
        rv = 0
        for k, v in self.moveable_pos.items():
            assert k in self.dst_pos
            if self.dst_pos[k] == v:
                rv += 1
        return rv

    def copy(self):
        p = Puzzle()
        p.back_board = self.back_board
        for i, x in enumerate(self.front_board):
            assert isinstance(x, Piece)
            p.front_board[i] = x.copy()
        p.moveable_pos = self.moveable_pos.copy()
        p.dst_pos = self.dst_pos.copy()
        return p

    def get_moveable_unique_str(self):
        tmp = []
        for color in sorted(self.moveable_pos):
            tmp += [color]
            tmp += [str(self.moveable_pos[color])]
            tmp += [str(self.front_board[self.moveable_pos[color]].dir)]
        return ','.join(tmp)


class PuzzleSolver:
    def __init__(self, data=None):
        self.id = 0
        self.trace_tree = {}
        self.queue = collections.deque()
        self.unique = set()

        if data:
            p = Puzzle(data)
            d = {"parent_id": None,
                 "id": self.get_id_with_inc(),
                 "data": p,
                 "color": None,
                 "depth": 0}
            self.queue.append(d)
            self.trace_tree[d["id"]] = d

    def trace(self, id_):
        rv = []
        while True:
            d = self.trace_tree[id_]
            if not d["color"]:
                break
            rv.append(d["color"])
            id_ = d["parent_id"]
        rv.reverse()
        return rv

    def solve(self):
        total = 0
        last_time = time.time()
        while self.queue:
            d = self.queue.popleft()
            if time.time() - last_time > 1:
                last_time = time.time()
                print(total)
            puzzle = d["data"]
            assert isinstance(puzzle, Puzzle)
            if d["depth"] == 5:
                if puzzle.get_score() == 0:
                    continue
            else:
                if d["depth"] // 8 > puzzle.get_score():
                    continue
            colors = list(puzzle.moveable_pos)
            random.shuffle(colors)
            for color in colors:
                if puzzle.can_move(color):
                    new_puzzle = puzzle.copy()
                    new_puzzle.move(color)
                    if not new_puzzle.can_move(color):
                        continue
                    total += 1

                    tmp = new_puzzle.get_moveable_unique_str()
                    if tmp in self.unique:
                        continue
                    else:
                        self.unique.add(tmp)

                    if new_puzzle.is_finish():
                        colors = self.trace(d["id"])
                        colors.append(color)
                        return colors
                    else:
                        new_id = self.get_id_with_inc()
                        tmp = {
                            "parent_id": d["id"],
                            "id": new_id,
                            "data": new_puzzle,
                            "color": color,
                            "depth": d["depth"] + 1
                        }
                        self.queue.append(tmp)
                        self.trace_tree[tmp["id"]] = tmp

    def get_id_with_inc(self):
        self.id += 1
        return self.id
