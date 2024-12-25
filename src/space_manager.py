import os
import uuid
import json

from numpy.f2py.auxfuncs import isint1

import src.schema as schema
from datetime import datetime


class SpaceManager:
    def __init__(self, path="./"):
        self.path = path
        self.cache = {}


    def create_datastore(self, data):
        try:
            # Convert data to JSON string
            json_data = json.dumps(data)

            # Create directories if they don't exist
            os.makedirs(os.path.dirname(self.path), exist_ok=True)

            # Write data to the file
            with open(self.path, 'w') as f:
                f.write(json_data)

            print(f"Data saved successfully to {self.path}")

        except json.JSONEncoder.encode:
            raise ValueError("Error: Data cannot be encoded to JSON.")
        except OSError as e:
            raise OSError(f"Error saving data to {self.path}: {e}")

    @staticmethod
    def get_time():
        now = datetime.now()
        current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        return current_time_str

    def update_schema(self, schema_type, **kwargs):

        sc = {}

        if schema_type == 'project':
            sc = schema.PROJECT_SCHEMA

        for key, values in kwargs.items():
            sc.update({key:values})

        return sc


    def create_project(self, name, created_by, description, path):

        sc = self.update_schema(schema_type='project',
                                id=str(uuid.uuid4()),
                                name=name,
                                description=description,
                                created_by=created_by,
                                created_at=SpaceManager.get_time(),
                                last_updated = SpaceManager.get_time()
                                )

        self.cache = {'project':sc}
        return self.cache['project']['id']
        #self.create_datastore(project_schema)

    def update_tags(self, ctx, tags=None):
        status = False
        if self.cache and tags:
            if isinstance(tags, list):
                self.cache[ctx]['tags'].extend(tags)
            else:
                self.cache[ctx]['tags'].append(tags)
            self.cache[ctx]['last_updated'] = SpaceManager.get_time()
            status = True
        print(json.dumps(self.cache, indent=4))
        return status






