# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

from tornado.web import RequestHandler
from tornado.options import options


class BaseHandler(RequestHandler):
    @property
    def task_manager(self):
        return self.application.task_manager

    @property
    def user_manager(self):
        return self.application.user_manager

    @property
    def vip_pool(self):
        return self.application.vip_pool

    def get_vip(self):
        return self.vip_pool.get_vip(self.get_cookie("xss", None)) or self.task_manager.get_vip()

    def render_string(self, template_name, **kwargs):
        kwargs["options"] = options
        return super(BaseHandler, self).render_string(template_name, **kwargs)

    def get_current_user(self):
        # fix cookie
        if self.request.cookies is None:
            return None
        email = self.get_secure_cookie("email")
        name = self.get_secure_cookie("name")
        if email and name:
            return {
                    "id": self.user_manager.get_id(email),
                    "email": email,
                    "name": name,
                    "group": self.user_manager.get_group(email),
                    "permission": self.user_manager.get_permission(email),
                   }
        elif self.request.remote_ip in ("localhost", "127.0.0.1") or options.root_user_mode:
            return {
                    "id": 0,
                    "email": "bot@localhost",
                    "name": "bot",
                    "group": "admin",
                    "permission": 999,
                    }
        else:
            return None

    def installed_userjs(self):
        if options.using_xss:
            return True
        cookie = self.get_cookie("cross-cookie")
        if cookie == options.cross_cookie_version or cookie == "disabled":
            return True

    def disabled_userjs(self):
        if options.using_xss:
            return False
        return self.get_cookie("cross-cookie") == "disabled"

    def has_permission(self, permission):
        email = self.current_user and self.current_user["email"] or None
        return self.user_manager.check_permission(email, permission)

    def change_protocol(self):
        ssl = self.get_cookie('ssl')
        if ssl:
            new_url = '%s%s' % (self.request.host, self.request.path)
            if self.request.query:
                new_url = '%s?%s' % (new_url, self.request.query)

            if self.request.protocol == 'http' and ssl == 'true':
                return 'https://%s' % new_url

            if self.request.protocol == 'https':
                if ssl == 'true':
                    self.set_header("Strict-Transport-Security", "max-age=31536000")
                elif ssl == 'false':
                    self.set_header("Strict-Transport-Security", "max-age=0")
                    return 'http://%s' % new_url

        return None
