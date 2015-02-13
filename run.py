#!/usr/bin/env python
# http://blog.yeradis.com/2012/11/standalone-flask-wsgi-running-under.html
from app import app
# app.debug = True
# print 'Twisted on port 5000...'
# from twisted.internet import reactor
# from twisted.web.server import Site
# from twisted.web.wsgi import WSGIResource

# resource = WSGIResource(reactor, reactor.getThreadPool(), app)
# site = Site(resource)

# reactor.listenTCP(5000, site, interface="0.0.0.0")
# reactor.run()

print 'Tornado on port 5000...'
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado import autoreload
from tornado.web import FallbackHandler, Application

## regular non-async tornado settings
# http_server = HTTPServer(WSGIContainer(app))
# http_server.listen(5000)
# ioloop = IOLoop.instance()
# autoreload.start(ioloop)
# ioloop.start()

# tornado async settings
tr = WSGIContainer(app)
application = Application([
    (r".*", FallbackHandler, dict(fallback=tr)),
    ], debug=True)

application.listen(5000)
ioloop = IOLoop.instance()
autoreload.start(ioloop)
ioloop.start()

# app.run(debug=True)
