import os
import uuid
import json
import src.schema as schema

class SpaceManager:
    def __init__(self, path="./"):
        self.path = path


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

    def update_schema(self, schema_type, **kwargs):

        sc = {}

        if schema_type == 'project':
            sc = schema.PROJECT_SCHEMA

        for key, values in kwargs.items():
            sc.update({key:values})

        return sc


    def create_project(self, name, created_by, description, path):

        description = '' if description is None else description
        sc = self.update_schema(schema_type='project', name=name, description=description,
                                )
        print({'project':sc})
        #self.create_datastore(project_schema)






