from typing import Dict

import tornado.web
import json
import uuid

from src.data import Model, JSONModel


class Memory:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def get_instance():
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

    def add_document(self, text) -> uuid.UUID:
        model = JSONModel.create(text)
        uid = uuid.uuid4()
        self.documents[uid] = model
        return uid


# noinspection PyAbstractClass
class ApiHandler(tornado.web.RequestHandler):
    def post(self):
        print(self.request.body)
        try:
            request = json.loads(self.request.body)
        except json.decoder.JSONDecodeError:
            self.set_status(400)
            self.finish("Bad JSON.")
            return

        if 'cmd' not in request:
            self.set_status(400)
            self.finish('Nothing to do.')

        if request['cmd'] == 'load':
            file = request['file']
            mem = Memory.get_instance()
            uid = mem.add_document(file)
            self.finish(json.dumps({'uid': uid}))
