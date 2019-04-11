import json
from uuid import UUID

import tornado.web
from jinja2 import Environment, FileSystemLoader

from src.api import Memory
from src.data import JSONModel

env = Environment(loader=FileSystemLoader('templates'))


# noinspection PyAbstractClass
class EditHandler(tornado.web.RequestHandler):
    def get(self):
        template = env.get_template("edit.html")

        uid = self.get_argument('uid', None)
        if uid == 'empty':
            result = template.render()
            self.finish(result)
            return
        elif uid:
            mem = Memory.get_instance()
            try:
                model = mem.documents[UUID(uid)]
            except KeyError:
                self.set_status(404)
                self.finish("404: Model not found.")
                return
        else:
            with open("doc/default.json", "r") as f:
                model = JSONModel.create(f)()

        vertices = [{'name': vertex} for vertex in model.vertices]
        groups = [{'id': category_id, 'name': category[0], 'levels': category[1]}
                  for category_id, category in model.control_categories.items()]
        levels = [{'gid': level.id, 'level': str(level.level), 'name': level.level_name, 'cost': level.cost,
                   'ind_cost': level.ind_cost, 'flow': level.flow}
                  for category in model.control_subcategories.values() for level in category]
        edges = [{'source': edge.source, 'target': edge.target, 'default_flow': edge.default_flow,
                  'name': edge.vulnerability.name, 'controls': edge.vulnerability.controls_repr()}
                 for edge in model.edges]
        dictionary = {
            'vertices': json.dumps(vertices),
            'groups': json.dumps(groups),
            'levels': json.dumps(levels),
            'edges': json.dumps(edges)
        }

        result = template.render(**dictionary)
        self.finish(result)
