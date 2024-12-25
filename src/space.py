from IPython.core.completer import context_matcher

import src.space_manager as sm

manager = sm.SpaceManager()
CONTEXT = None

def set_project(**kwargs):
    global CONTEXT

    if 1:
        CONTEXT = "project"
        name = kwargs['name']
        description = kwargs.get('description', '')
        created_by = kwargs.get('created_by', '')
        proj_id = manager.create_node(name=name,
                                    created_by=created_by,
                                    description=description,
                                    context = CONTEXT)
        print(f"Project (ID: {proj_id}) created successfully")

    #except Exception as e:
    #    return Exception(f'Error in creating the project {e}')


def set_tags(tags=None):
    if tags:
        status = manager.update_tags(CONTEXT, tags)
        print("tags added successfully")

def set_experiment(**kwargs):
    global CONTEXT

    CONTEXT = "experiment"
    name = kwargs['name']
    description = kwargs.get('description', '')
    created_by = kwargs.get('created_by', '')
    exp_id = manager.create_node(name=name,
                                     created_by=created_by,
                                     description=description,
                                     context=CONTEXT)
    print(f"Experiment (ID: {exp_id}) created successfully")




