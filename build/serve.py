
print('==> Loading web server...')

import os
import re
import socket
import threading
import tornado

import tornado.concurrent
import tornado.httputil
import tornado.httpserver
import tornado.gen
import tornado.ioloop
import tornado.web

WEB_PORT = 80

""" consq_sub -- Consecutively substitute patterns in RegEx. """
def consq_sub(s, *args):
    if len(args) % 2 != 0:
        raise AttributeError('Odd arguments given')
    for i in range(0, len(args), 2):
        s = re.sub(args[i], args[i + 1], s)
    return s

class StaticHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'HEAD']

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, file_path):
        if '?' in file_path:
            file_path = consq_sub(file_path,
                r'\?(.*)$', r'',)
        file_path = '../' + file_path
        if os.path.isdir(file_path):
            file_path += '/index.html'

        # In case it does not exist.
        try:
            future = tornado.concurrent.Future()
            def get_file_data_async():
                f_handle = open(file_path, 'rb')
                file_data = f_handle.read()
                f_handle.close()
                future.set_result(file_data)
            tornado.ioloop.IOLoop.instance().add_callback(get_file_data_async)
            file_data = yield future
        except Exception:
            raise tornado.web.HTTPError(404)

        # File actually exists, sending data
        self.set_status(200, "OK")
        self._headers = tornado.httputil.HTTPHeaders()
        self.add_header('Cache-Control', 'max-age=0')
        self.add_header('Connection', 'close')
        self.add_header('Content-Length', str(len(file_data)))

        # Push result to client in one blob
        self.write(file_data)
        self.flush()
        self.finish()
        return self

    head=get
    pass

def main():
    # Creating web application
    web_app = tornado.web.Application([
            (r'^/(.*)$', StaticHandler),
        ],
        xsrf_cookies=False, # True to prevent CSRF third party attacks
        compress_response=True # True to support GZIP encoding when transferring data
    )
    # Starting server
    web_sockets = tornado.netutil.bind_sockets(80,
        family=socket.AF_INET)
    web_server = tornado.httpserver.HTTPServer(web_app,
        max_body_size=64*1024*1024,
        xheaders=True)
    web_server.add_sockets(web_sockets)
    # Boot I/O thread for asynchronous purposes
    print(' .. Server started on http://localhost:80.')
    tornado.ioloop.IOLoop.instance().start()
    print('==> Caught signal, terminating server.')
    return 0

ret_code = main()
exit(ret_code)
