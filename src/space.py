from networkx.algorithms.shortest_paths.unweighted import predecessor

import src.space_manager as sm

manager = sm.SpaceManager()
curr_node_id = None
manager.create_graph()

edges = {}

def set_project(**kwargs):
    global edges

    name = kwargs.get("name", None)
    description = kwargs.get("description", "")
    created_by = kwargs.get("created_by", "")
    tags = kwargs.get("tags", [])

    if not name:
        raise ValueError("Please provide a name for the project")
    if manager.check_name_exists(name=name, type="project"):
        raise ValueError("The name is already allocated, use a different name")

    curr_node_id = manager.create_node(
        name=name,
        created_by=created_by,
        description=description,
        tags=tags,
        type="project",
    )
    edges["project"] = curr_node_id
    print(f"Project {name} - (ID: {curr_node_id}) created successfully")


def set_experiment(**kwargs):
    global edges

    name = kwargs.get("name", None)
    description = kwargs.get("description", "")
    created_by = kwargs.get("created_by", "")
    tags = kwargs.get("tags", [])

    if not name:
        raise ValueError("Please provide a name for the project")

    if manager.check_name_exists(name=name, predecessor=edges["project"], type="experiment"):
        raise ValueError("The name is already allocated, use a different name")

    curr_node_id = manager.create_node(
        name=name,
        created_by=created_by,
        description=description,
        tags=tags,
        type="experiment",
    )

    manager.create_edge(edges["project"], curr_node_id)
    edges["experiment"] = curr_node_id
    print(f"Experiment {name} - (ID: {curr_node_id}) created successfully")


def start_run(**kwargs):
    global edges

    name = kwargs.get("name", None)
    description = kwargs.get("description", "")
    created_by = kwargs.get("created_by", "")
    tags = kwargs.get("tags", [])

    if not name:
        raise ValueError("Please provide a name for the project")

    if manager.check_name_exists(name=name, predecessor=edges["experiment"], type="run"):
        raise ValueError("The name is already allocated, use a different name")

    curr_node_id = manager.create_node(
        name=name,
        created_by=created_by,
        description=description,
        tags=tags,
        type="run",
    )

    manager.create_edge(edges["experiment"], curr_node_id)
    if "run" in edges.keys():
        edges["run"].append(curr_node_id)
    else:
        edges["run"] = [curr_node_id]
    print(f"Run {name} - (ID: {curr_node_id}) created successfully")


def stop_run(name=None):
    if not name:
        if "end_time" in manager.get_node_properties(edges["run"][-1]).keys():
            raise Exception("run already stopped")
        manager.update_node_property(
            edges["run"][-1],
            property_name="end_time",
            property_value=manager.get_time(),
            add_new=True,
        )
    else:
        view = manager.filter_nodes_by_type(node_type="run")
        node_id = manager.get_id_by_name(name, view, predecessor=edges["experiment"])
        if not node_id:
            raise ValueError(f"The run : {name} not found")
        else:
            if "end_time" in manager.get_node_properties(node_id[0]).keys():
                raise Exception("run already stopped")
            manager.update_node_property(
                node_id[0],
                property_name="end_time",
                property_value=manager.get_time(),
                add_new=True,
            )
        print(f"run {name} stopped (ID: {node_id[0]})")


def log_hyperparameters(**kwargs):


    name = kwargs.get("name", None)
    run_name = kwargs.get("run_name", None)
    description = kwargs.get("description", "")
    created_by = kwargs.get("created_by", edges["run"][-1])
    tags = kwargs.get("tags", [])
    value = kwargs.get("value")

    if not name and not isinstance(value, dict):
        raise ValueError("Please provide a name")
    if not value:
        raise ValueError("Please provide a value")

    if not isinstance(value, dict):
        value = {name: value}

    view = manager.filter_nodes_by_type(node_type="hyperparameter")
    run_id = []
    if run_name:
        run_id = manager.get_id_by_name(run_name, view, predecessor=edges["experiment"])
        if not run_id:
            raise ValueError("Run - {run_name} not found")

    for name, val in value.items():
        if run_id:
            node_id = manager.get_id_by_name(name, view, predecessor=run_id[0])
        else:
            node_id = manager.get_id_by_name(name, view, predecessor=edges["run"][-1])

        if not node_id:
            node_id = manager.create_node(
                name=name,
                created_by=created_by,
                description=description,
                tags=tags,
                value=val,
                type="hyperparameter",
            )

            manager.create_edge(edges["run"][-1], node_id)
            print(f"'hyperparameter : {name}' logged (ID: {node_id})")
        else:
            property = manager.get_node_properties(node_id[0])["value"]
            if not isinstance(property, list):
                property = [property]
            property.append(value)
            manager.update_node_property(
                node_id[0],
                property_name=name,
                property_value=val,
            )
            print(f"hyperparameter : {name} updated (ID: {node_id[0]})")



def log_metrics(**kwargs):

    # if same name update value
    name = kwargs.get("name", None)
    run_name = kwargs.get("run_name", None)
    description = kwargs.get("description", "")
    created_by = kwargs.get("created_by", edges["run"])
    tags = kwargs.get("tags", [])
    value = kwargs.get("value")

    if not name and not isinstance(value, dict):
        raise ValueError("Please provide a name")
    if not value:
        raise ValueError("Please provide a value")


    view = manager.filter_nodes_by_type(node_type="metric")
    run_id = []
    if run_name:
        run_id = manager.get_id_by_name(run_name, view, predecessor=edges["experiment"])
        if not run_id:
            raise ValueError("Run - {run_name} not found")

    if not isinstance(value, dict):
        value = {name:value}

    for name, val in value.items():
        if run_id:
            node_id = manager.get_id_by_name(name, view, predecessor=run_id[0])
        else:
            node_id = manager.get_id_by_name(name, view, predecessor=edges["run"][-1])


        if not node_id:
            node_id = manager.create_node(
                name=name,
                created_by=created_by,
                description=description,
                tags=tags,
                value=val,
                type="metric",
            )

            manager.create_edge(edges["run"][-1], node_id)
            print(f"'metric : {name}' logged (ID: {node_id})")

        else:
            property = manager.get_node_properties(node_id)["value"]
            if not isinstance(property, list):
                property = [property]
            property.append(val)
            manager.update_node_property(
                node_id[0],
                property_name=name,
                property_value=property,
            )
            print(f"'metric : {name}' updated (ID: {node_id[0]})")


def log_artifacts(**kwargs):

    #update fn
    name = kwargs.get("name", None)
    run_name = kwargs.get("run_name", None)
    description = kwargs.get("description", "")
    created_by = kwargs.get("created_by", edges["run"])
    tags = kwargs.get("tags", [])
    artifact_type = kwargs.get("artifact_type")
    path = kwargs.get("path")
    value = kwargs.get("value")


    if not name:
        raise ValueError("Please provide a name")
    if not artifact_type:
        raise ValueError("Please provide a artifact_type (plot, model, )")
    if not path:
        raise ValueError("Please provide a path")


    if artifact_type not in ["plot", "model", "data"]:
        raise ValueError("Incorrect value for artifact type")

    view = manager.filter_nodes_by_type(node_type="artifact")
    if run_name:
        run_id = manager.get_id_by_name(run_name, view, predecessor=edges["experiment"])
        if not run_id:
            raise ValueError("Run - {run_name} not found")
        else:
            node_id = manager.get_id_by_name(name, view, predecessor=run_id[0])

    else:
        node_id = manager.get_id_by_name(name, view, predecessor=edges["run"][-1])

    if not node_id:
        node_id = manager.create_node(
            name=name,
            created_by=created_by,
            description=description,
            tags=tags,
            value=value,
            type=artifact_type,
        )

        manager.create_edge(edges["run"][-1], node_id)
        print(f"'artifact : {name}' logged (ID: {node_id})")

    else:
        property = manager.get_node_properties(node_id)["value"]
        if not isinstance(property, list):
            property = [property]
        property.append(value)
        manager.update_node_property(
            node_id[0],
            property_name=name,
            property_value=value,
        )
        print(f"artifact : {name} - updated (ID: {node_id[0]})")

def get_node_id(name, type):
    if name and type:
        view = manager.filter_nodes_by_type(node_type=type)
        try:
            if type == "project":
                predecessor = None
            elif type == "experiment":
                predecessor = edges["project"]
            elif type == "run":
                predecessor = edges["experiment"]
            else:
                predecessor = edges["run"][-1]
        except:
            raise ValueError(f"{type} not available")
        node_id = manager.get_id_by_name(name, view, predecessor=predecessor)
        if not node_id:
            raise ValueError(f"{name} : {type} not found")
        else:
            node_id = node_id[0]
    else:
        node_id = curr_node_id

    return node_id

def add_tags(tags, name=None, type=None):
    node_id = get_node_id(name, type) if name and type else curr_node_id

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


def remove_tags(value, name=None, type=None):
    node_id = get_node_id(name, type) if name and type else curr_node_id
    properties = manager.get_node_properties(node_id)
    try:
        properties["tags"].remove(value)
        manager.update_node_property(
            node_id,
            property_name="tags",
            property_value=properties["tags"],
        )
    except Exception as e:
        print(e)

def update_description(description, name, type):
    node_id = get_node_id(name, type) if name and type else curr_node_id
    manager.update_node_property(
        node_id, property_name="description", property_value=description
    )

def update_name(curr_name, latest_name, type):
    node_id = get_node_id(curr_name, type) if curr_name and type else curr_node_id
    manager.update_node_property(
        node_id, property_name="name", property_value=latest_name
    )

def delete(name, type):
    node_id = get_node_id(name, type) if name and type else curr_node_id
    manager.remove(node_id)

def get(id=None):
    return manager.get_node_properties(id)

def list_experiments(project=None):
    '''
    get all experiments with its properties and return it as pandas data frame
    clue: use node properties
    '''

    #TODO: @akshay

def list_runs(experiment=None):
    '''
    get all runs with its properties and return it as pandas data frame
    reference: https://towardsdatascience.com/mlflow-a-primer-6dfe6be48353 (table image)
    clue: retreive all runs and merge it with its child nodes aka - hyperparametr, metric, artifact
           of particular experiment
    '''
    #TODO: @akshay

def get_run(run='<name of run>', experiment='<name of exp>', filter="metric and/or hyperparam and/or artifact"):
    '''
        get all child nodes with its properties and return it as pandas data frame
        reference: https://towardsdatascience.com/mlflow-a-primer-6dfe6be48353 (table image)
        clue: retreive a particular runs  child nodes aka - hyperparametr, metric, artifact
               of particular experiment
               add a filter to only return a specific log like metrics or hyperparamter and/or etc
        '''
    # TODO: @akshay
    
def get_best_run(experiment=None, metric_name="abc", objective="minimize/maximize"):
    '''
        get best runs with its properties and return it as pandas data frame
        reference: https://towardsdatascience.com/mlflow-a-primer-6dfe6be48353 (table image)
        clue: retrive best runs based on one metric for an experiment or all experiments based
         on whether experiment is given
        '''
    # TODO: @akshay





