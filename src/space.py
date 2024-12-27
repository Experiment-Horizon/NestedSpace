from multiprocessing.managers import Value

from tomlkit import value

import src.space_manager as sm

manager = sm.SpaceManager()
prev_node_id = None
curr_node_id = None


def set_project(**kwargs):
    global curr_node_id, prev_node_id

    manager.create_graph()
    name = kwargs["name"]
    description = kwargs.get("description", "")
    created_by = kwargs.get("created_by", "")
    tags = kwargs.get("tags", [])
    prev_node_id = None
    curr_node_id = manager.create_node(
        name=name,
        created_by=created_by,
        description=description,
        tags=tags,
        context="project",
    )
    print(f"Project (ID: {curr_node_id}) created successfully")


def set_experiment(**kwargs):
    global curr_node_id, prev_node_id

    name = kwargs["name"]
    description = kwargs.get("description", "")
    created_by = kwargs.get("created_by", "")
    tags = kwargs.get("tags", [])
    prev_node_id = curr_node_id
    curr_node_id = manager.create_node(
        name=name,
        created_by=created_by,
        description=description,
        tags=tags,
        context="experiment",
    )

    manager.create_edge(prev_node_id, curr_node_id)
    print(f"Experiment (ID: {curr_node_id}) created successfully")


def start_run(**kwargs):
    global curr_node_id, prev_node_id

    name = kwargs["name"]
    description = kwargs.get("description", "")
    created_by = kwargs.get("created_by", "")
    tags = kwargs.get("tags", [])
    prev_node_id = curr_node_id
    curr_node_id = manager.create_node(
        name=name,
        created_by=created_by,
        description=description,
        tags=tags,
        context="run",
    )

    manager.create_edge(prev_node_id, curr_node_id)
    print(f"Run (ID: {curr_node_id}) created successfully")


def stop_run(id=None, **kwargs):
    node_id = id if id else curr_node_id
    manager.update_node_property(
        node_id,
        property_name="end_time",
        property_value=manager.get_time(),
        add_new=True,
    )

def log_hyperparameter(id=None, **kwargs):


    name = kwargs["name"]
    description = kwargs.get("description", "")
    created_by = kwargs.get("created_by", prev_node_id)
    tags = kwargs.get("tags", [])
    value = kwargs.get("value")

    if not name:
        raise ValueError("Please provide a name")
    if not value:
        raise ValueError("Please provide a value")

    if id:
        node_exists = manager.check_node_exists(id)
        manager.update_node_property(
            id,
            property_name=name,
            property_value=value,
        )
        print(f"hyperparameter {name} updated")
        return



    id = manager.create_node(
        name=name,
        created_by=created_by,
        description=description,
        tags=tags,
        value = value,
        context="hyperparameter",
    )

    manager.create_edge(prev_node_id, id)
    print(f"'{name}' logged")


def log_metric(id=None, **kwargs):

    # if same name update value
    name = kwargs["name"]
    description = kwargs.get("description", "")
    created_by = kwargs.get("created_by", prev_node_id)
    tags = kwargs.get("tags", [])
    operation = kwargs.get("operation", "ADD")

    if not name:
        raise ValueError("Please provide a name")
    if not value:
        raise ValueError("Please provide a value")

    if id and operation == "CONCAT":
        property = manager.get_node_properties(id)["value"]
        if not isinstance(property, list):
            property = [property]
        property.append(value)
    else:
        id = manager.create_node(
            name=name,
            created_by=created_by,
            description=description,
            tags=tags,
            value=value,
            context="metric",
        )

        manager.create_edge(prev_node_id, id)
        print(f"'{name}' logged")

def log_artifacts(id=None, **kwargs):

    #update fn
    name = kwargs["name"]
    description = kwargs.get("description", "")
    created_by = kwargs.get("created_by", prev_node_id)
    tags = kwargs.get("tags", [])
    artifact_type = kwargs.get("artifact_type")
    path = kwargs.get("path")


    if not name:
        raise ValueError("Please provide a name")
    if not artifact_type:
        raise ValueError("Please provide a artifact_type (plot, model, )")
    if not path:
        raise ValueError("Please provide a path")


    if artifact_type not in ["plot", "model", "data"]:
        raise ValueError("Incorrect value for artifact type")

    id = manager.create_node(
        name=name,
        created_by=created_by,
        description=description,
        tags=tags,
        value=value,
        context=artifact_type,
    )

    manager.create_edge(prev_node_id, id)
    print(f"'{name}' logged")


def add_tags(tags, id=None):
    node_id = id if id else curr_node_id
    properties = manager.get_node_properties(node_id)
    if isinstance(tags, list):
        properties["tags"].extend(tags)
    else:
        properties["tags"].append(tags)

    manager.update_node_property(
        node_id,
        property_name="tags",
        property_value=properties["tags"],
    )


def remove_tags(value, id=None):
    node_id = id if id else curr_node_id
    properties = manager.get_node_properties(node_id)
    try:
        properties["tags"].remove(value)
        manager.update_node_property(
            node_id,
            property_name="tags",
            property_value=properties["tags"],
        )
    except Exception as e:
        print("no such tag not found")


def update_name(name, id=None):
    node_id = id if id else curr_node_id
    manager.update_node_property(node_id, property_name="name", property_value=name)


def update_description(description, id=None):
    node_id = id if id else curr_node_id
    manager.update_node_property(
        node_id, property_name="description", property_value=description
    )

def get(id=None):
    return manager.get_node_properties(id)


#TODO SET/LOAD/EDIT ALL with name, throw error if name exists
