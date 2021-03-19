import json
from uuid import UUID

import tornado.web
from jinja2 import Environment, FileSystemLoader

from src.api import Memory

env = Environment(loader=FileSystemLoader("templates"))


# noinspection PyAbstractClass
class EditHandler(tornado.web.RequestHandler):
    def get(self):
        template = env.get_template("edit.html")

        _id = self.get_argument("id", None)
        print(_id)
        memory = Memory.get_instance()
        if _id == "empty":
            result = template.render()
            self.finish(result)
            return
        elif _id:
            try:
                model = memory.documents[UUID(_id)]
            except KeyError:
                self.set_status(404)
                self.finish("404: Model not found.")
                return
        else:
            model = memory.documents[memory.templates[0]]

        vertices = [
            {"name": vertex_name, "target": vertex_id in model.targets}
            for vertex_id, vertex_name in enumerate(model.vertices)
        ]
        groups = [
            {
                "id": category_id,
                "name": category[0],
                "levels": category[1],
                "no_control_name": category[2],
            }
            for category_id, category in model.control_categories.items()
        ]
        levels = [
            {
                "gid": level.id,
                "level": str(level.level),
                "name": level.level_name,
                "cost": level.cost,
                "ind_cost": level.ind_cost,
                "flow": level.flow,
            }
            for category in model.control_subcategories.values()
            for level in category
        ]
        edges = [
            {
                "source": edge.source,
                "target": edge.target,
                "default_flow": edge.default_flow,
                "name": edge.vulnerability.name,
                "controls": edge.vulnerability.controls_repr(),
                "url": edge.url,
            }
            for edge in model.edges
        ]
        dictionary = {
            "name": model.name or "Model",
            "vertices": json.dumps(vertices),
            "groups": json.dumps(groups),
            "levels": json.dumps(levels),
            "edges": json.dumps(edges),
        }

        result = template.render(**dictionary)
        self.finish(result)
