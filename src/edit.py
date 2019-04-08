import tornado.web
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))


# noinspection PyAbstractClass
class EditHandler(tornado.web.RequestHandler):
    def get(self):
        template = env.get_template("edit.html")
        result = template.render()
        self.finish(result)
