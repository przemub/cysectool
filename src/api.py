import os
from typing import Dict

import tornado.web
import json
import uuid

from src.data import Model, JSONModel, GraphError


class Memory:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def get_instance() -> "Memory":
        """ Static access method. """
        if Memory.__instance is None:
            Memory()
        return Memory.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Memory.__instance is not None:
            raise Exception("This class is a singleton!")

        Memory.__instance = self

        self.documents: Dict[uuid.UUID, Model] = {}

        # Load templates
        self.templates = []
        for file in sorted(os.listdir("doc/templates/")):
            if not file.endswith(".json"):
                continue
            with open(os.path.join("doc/templates/", file), "r") as f:
                _id = self.add_document(f.read())
                self.templates.append(_id)

    def add_document(self, text) -> uuid.UUID:
        while len(self.documents) > 100:
            self.documents.popitem()
        if len(text) > 1024 * 1024:
            raise MemoryError("Too large file.")

        model = JSONModel.create(text)
        _id = uuid.uuid4()
        self.documents[_id] = model()
        return _id


# noinspection PyAbstractClass
class ApiHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            request = json.loads(self.request.body)
        except json.decoder.JSONDecodeError:
            self.set_status(400)
            self.finish("400: Bad JSON.")
            return

        if "cmd" not in request:
            self.set_status(400)
            self.finish("400: Nothing to do.")

        if request["cmd"] == "load":
            file = request["file"]
            mem = Memory.get_instance()
            try:
                _id = mem.add_document(file)
            except MemoryError:
                self.set_status(413)
                self.finish("413: Payload too long.")
            except (JSONModel.JSONError, json.decoder.JSONDecodeError) as jsone:
                self.set_status(400)
                self.finish("400:\n%s" % jsone.args)
            except GraphError as ge:
                self.set_status(422)
                self.finish("422:\n%s" % ge.args)
            else:
                self.finish(json.dumps({"id": str(_id)}))
        elif request["cmd"] == "save":
            if "id" in request:
                mem = Memory.get_instance()
                model = mem.documents[uuid.UUID(request["id"])]
            else:
                with open("doc/templates/0_default.json", "r") as f:
                    model = JSONModel.create(f)()
            self.set_header("Content-Type", "application/json")
            self.set_header(
                "Content-Disposition",
                'attachment; filename="%s.json"' % model.name,
            )
            self.finish(model.save())


class PingHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish("PONG")
