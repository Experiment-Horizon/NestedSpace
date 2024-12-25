import src.space_manager as sm

manager = sm.SpaceManager()

def set_project(**kwargs):
    if 1:
        name = kwargs['name']
        description = kwargs.get('description', '')
        created_by = kwargs.get('created_by', '')
        path = kwargs.get('path', None)
        return manager.create_project(name=name,
                                    created_by=created_by,
                                    description=description,
                               path = path)

    #except Exception as e:
    #    return Exception(f'Error in creating the project {e}')


