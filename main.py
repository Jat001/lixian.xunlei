#/usr/bin/env python
# -*- encoding: utf8 -*-
# author: binux<17175297.hk@gmail.com>

import os
import tornado
import logging
from time import time
from tornado import web
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.options import define, options
from tornado.httpserver import HTTPServer

path = os.path.join(os.path.dirname(__file__), "%s")

define("f", default=path % "config.conf", help="config file path")
define("debug", default=False, help="debug mode")
define("port", default=8080, help="the port tornado listen to")
define("bind_ip", default="127.0.0.1", help="the bind ip")
define("username", default="", help="xunlei vip login name")
define("password", default="", help="xunlei vip password")
define("ga_account", default="", help="account of google analytics")
define("baidu_account", default="", help="account of baidu tongji")
define("site_name", default=u"轻松下", help="site name used in description")
define("site_subtitle", default=u"Easily download it", help="site subtitle used in description")
define("cookie_secret", default="7bLv5TdHG6oQXlt1ORsnrfmbuBQcxGgU",
        help="key for HMAC")
define("re_login_interval", default=60*60*24*7,
        help="the interval of force re-login to xunlei")
define("check_interval", default=60*60,
        help="the interval of checking login status")
define("cache_enabled", default=True,
        help="enable mem cache")
define("cross_userscript", default="https://userscripts.org/scripts/show/161456",
        help="the web url of cross cookie userscirpt")
define("cross_cookie_version", default="0.35",
        help="cross cookie user script version")
define("cross_userscript_local", default="/static/cross-cookie.user.js",
        help="the local path of cross cookie userscirpt")
define("cross_cookie_url", default="http://vip.xunlei.com/gen/yuanxun/gennew/newyx.html",
        help="the url to insert to")
define("cookie_str", default="gdriveid=%s; path=/; domain=.vip.xunlei.com",
        help="the cookie insert to cross path")
define("finished_task_check_interval", default=60*60,
        help="the interval of getting the task list")
define("downloading_task_check_interval", default=5*60,
        help="the interval of getting the downloading task list")
define("task_list_limit", default=500,
        help="the max limit of get task list each time")
define("always_update_lixian_url", default=False,
        help="always update lixian url")
define("database_echo", default=False,
        help="sqlalchemy database engine echo switch")
define("database_engine", default="sqlite://%s" % (path % "task_files.db"),
        help="the database connect string for sqlalchemy")
define("using_xss", default=False,
        help="use xss or cross-cookie")
define("using_xsrf", default=False,
        help="using xsrf to prevent cross-site request forgery")
define("reg_key", default=None,
        help="if setted new user is not allowed except login with '/login?key=<reg_key>'.")
define("enable_share", default=True, help="enable share task")
define("root_user_mode", default=False, help="everyone is root")
define("google_client_id", default="", help="google oauth2 client id")
define("google_client_secret", default="", help="google oauth2 client secret")

class Application(web.Application):
    def __init__(self):
        from handlers import handlers, ui_modules
        from libs.util import ui_methods
        from libs.db_task_manager import DBTaskManager
        from libs.user_manager import UserManager
        from libs.vip_pool import VIPool
        settings = dict(
            debug=options.debug,
            template_path=path % "templates",
            static_path=path % "static",
            cookie_secret=options.cookie_secret,
            login_url="/login",
            autoreload=True,
            compiled_template_cache=False,
            gzip=True,
            serve_traceback=False,
            ui_modules=ui_modules,
            ui_methods=ui_methods
        )
        super(Application, self).__init__(handlers, **settings)

        self.user_manager = UserManager()
        self.task_manager = DBTaskManager(
                    username = options.username,
                    password = options.password
                )
        self.vip_pool = VIPool()
        if not self.task_manager.islogin:
            raise Exception, "xunlei login error"
        self.task_manager.async_update()
        PeriodicCallback(self.task_manager.async_update,
                options.downloading_task_check_interval * 1000).start()
        PeriodicCallback(self.user_manager.reset_all_add_task_limit, 86400 * 1000).start()

        logging.info("load finished! listening on %s:%s" % (options.bind_ip, options.port))

def main():
    tornado.options.parse_command_line()
    if options.f:
        tornado.options.parse_config_file(options.f)
    tornado.options.parse_command_line()

    http_server = HTTPServer(Application(), xheaders=True)
    http_server.bind(options.port, options.bind_ip)
    http_server.start()

    IOLoop.instance().start()

if __name__ == "__main__":
    main()
