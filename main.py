#!/usr/bin/env python
# coding=utf-8
import logging
import json
from concurrent.futures import ProcessPoolExecutor

import tornado.web
import tornado.ioloop
import tornado.httputil
import tornado.log
import tornado.queues
import tornado.gen
import tornado.concurrent

from libs import puzzle

__author__ = 'chenfengyuan'

PUZZLE_QUEUES = tornado.queues.Queue()
TASKS = {}
COUNTER = 0
EXECUTOR = ProcessPoolExecutor()


class PuzzleHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @tornado.gen.coroutine
    def post(self):
        req = self.request
        assert isinstance(req, tornado.web.httputil.HTTPServerRequest)
        f = tornado.gen.Future()
        yield PUZZLE_QUEUES.put({"data": req.body.decode('utf-8'), "f": f})
        colors = yield f
        self.write(json.dumps(colors))

    @tornado.gen.coroutine
    def get(self):
        global COUNTER
        d = yield PUZZLE_QUEUES.get()
        id_ = COUNTER
        COUNTER += 1
        TASKS[id_] = d["f"]
        self.write(json.dumps({"id": id_, "data": d["data"]}))

    @tornado.gen.coroutine
    def put(self):
        req = self.request
        assert isinstance(req, tornado.web.httputil.HTTPServerRequest)
        id_ = self.get_body_argument("id")
        data = self.get_body_argument("data")
        f = TASKS[int(id_)]
        del TASKS[int(id_)]
        assert isinstance(f, tornado.gen.Future)
        f.set_result(json.loads(data))


def in_app_solver(data, with_depth_limit):
    solver = puzzle.PuzzleSolver(data)
    return EXECUTOR.submit(solver.solve, with_depth_limit)


@tornado.gen.coroutine
def in_app_worker():
    while True:
        d = yield PUZZLE_QUEUES.get()
        ans = yield in_app_solver(d["data"], True)
        if not ans:
            ans = yield in_app_solver(d["data"], False)
        d["f"].set_result(ans)


def main():
    ioloop = tornado.ioloop.IOLoop.current()
    tornado.log.enable_pretty_logging()
    tornado.log.app_log.setLevel(logging.DEBUG)
    app = tornado.web.Application(
        [
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
            (r"/api/puzzle", PuzzleHandler),
        ]
    )
    app.listen(8888)
    ioloop.add_callback(in_app_worker)
    ioloop.add_callback(in_app_worker)
    ioloop.start()


if __name__ == '__main__':
    main()
