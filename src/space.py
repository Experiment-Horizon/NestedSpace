import src.space_manager as sm

manager = sm.SpaceManager()
CONTEXT = None

def set_project(**kwargs):
    global CONTEXT

    if 1:
        name = kwargs['name']
        description = kwargs.get('description', '')
        created_by = kwargs.get('created_by', '')
        path = kwargs.get('path', None)
        proj_id = manager.create_project(name=name,
                                    created_by=created_by,
                                    description=description,
                                    path = path)
        CONTEXT = "project"
        print(f"Project ID {proj_id} created successfully")

    #except Exception as e:
    #    return Exception(f'Error in creating the project {e}')


def set_tags(tags=None):
    if tags:
        status = manager.update_tags(CONTEXT, tags)
        print("tags added successfully")




