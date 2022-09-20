import time
import logging
import bisect
import cherrypy

logger = logging.getLogger("earlytool-monitor")


# https://stackoverflow.com/questions/18127415/non-blocking-cherrypy-does-not-receive-anything
# https://stackoverflow.com/questions/7254845/change-cherrypy-port-and-restart-web-server

@cherrypy.expose
class BroadcastWebService(object):
    latest_update = {}

    def __init__(self, queue):
        self.queue = queue
        self.flow_storage = {}
        self.flow_timestamp = {}

    def update_flows(self):
        try:
            while True:
                f = self.queue.pop()
                name = f["name"]
                self.flow_storage[name] = f
                try:
                    del self.flow_timestamp[name]
                except KeyError:
                    pass
                self.flow_timestamp[name] = time.time()
        except IndexError:
            pass

    def fetch_recent_flow(self, timestamp):
        i = bisect.bisect_right(list(self.flow_timestamp.values()), timestamp)
        recent_keys = list(self.flow_timestamp.keys())[i:]
        flows = []
        for k in recent_keys:
            flows.append(self.flow_storage[k])
        return flows

    @cherrypy.tools.json_out()
    def GET(self, last_time):
        # msg = BroadcastWebService.latest_update
        self.update_flows()
        # print(self.flow_storage)
        # print(self.flow_timestamp)
        flows = self.fetch_recent_flow(float(last_time))
        try:
            latest_ts = list(self.flow_timestamp.values())[-1]
        except IndexError:
            # There are no flows in the queue yet
            latest_ts = 0.0
        results = {"flows": flows, "latest_timestamp": latest_ts}
        # print(flows)
        return results


class BroadcastServer:
    def __init__(self, queue, port):
        self.queue = queue
        self.port = port
        self.ip = "0.0.0.0"

    def startServer(self):
        conf = {
            'global': {
                'server.socket_host': self.ip,
                'server.socket_port': self.port,
                # 'tools.log_headers.on': False,
                'log.screen': False,
                # 'request.show_tracebacks': False,
                # 'request.show_mismatched_params': False,

                # 'server.thread_pool' : 8,
                # interval in seconds at which the timeout monitor runs
                # 'engine.timeout_monitor.frequency' : 1
            },
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True,
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [('Content-Type', 'application/json')],
            }
        }
        cherrypy.config.update(conf)
        web_server = BroadcastWebService(self.queue)
        cherrypy.tree.mount(web_server, "/status", config=conf)

        # Disabling Cherrypy log https://stackoverflow.com/a/31707202/6551880
        cherrypy.log.access_log.propagate = False
        cherrypy.log.error_log.propagate = False

        logger.info(f"Broadcast web server is running at port http://localhost:{self.port}")
        cherrypy.engine.signal_handler.subscribe()
        cherrypy.engine.start()

    def stopServer(self):
        cherrypy.engine.stop()
        cherrypy.engine.exit()
