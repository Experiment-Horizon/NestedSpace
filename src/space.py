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


def add_tags(tags):
    properties = manager.get_node_properties(curr_node_id)
    if isinstance(tags, list):
        properties["tags"].extend(tags)
    else:
        properties["tags"].append(tags)

    manager.update_node_property(
        curr_node_id,
        property_name="tags",
        property_value=properties["tags"],
    )


def update_name(name):
    manager.update_node_property(
        curr_node_id, property_name="name", property_value=name
    )


def update_description(description):
    manager.update_node_property(
        curr_node_id, property_name="description", property_value=description
    )


def get(id=None):
    return manager.get_node_properties(id)
