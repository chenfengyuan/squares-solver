#!/usr/bin/env python
# coding=utf-8
__author__ = 'chenfengyuan'

import tornado.web
import tornado.ioloop
import tornado.httputil
import tornado.log
import tornado.queues
import logging
import json


from libs import puzzle


PUZZLE_QUEUES = tornado.queues.Queue


class PuzzleHandler(tornado.web.RequestHandler):
    def post(self):
        req = self.request
        assert isinstance(req, tornado.web.httputil.HTTPServerRequest)
        tornado.log.app_log.debug(req.body)
        s = puzzle.PuzzleSolver(req.body.decode('utf-8'))
        colors = s.solve()
        self.write(json.dumps(colors))


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
    ioloop.start()

if __name__ == '__main__':
    main()
