import src.space_manager as sm
import pandas as pd

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
        value = {name: value}

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
    # update fn
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
    Get all experiments with their properties and return as a pandas DataFrame.
    '''
    experiments = []

    # Retrieve all experiment nodes under the given project
    project_id = get_node_id(project, "project") if project else edges["project"]
    view = manager.filter_nodes_by_type(node_type="experiment")

    for node_id in view:
        print(node_id)
        print(manager.get_edge_source(node_id))
        if manager.get_edge_source(node_id)[0] == project_id:
            properties = manager.get_node_properties(node_id)
            experiments.append(properties)

    return pd.DataFrame(experiments)


def list_runs(experiment_name=None):
    """Lists all runs for the specified experiment and returns a DataFrame."""

    # Get all nodes of type "experiment" to check available experiment names
    view = manager.filter_nodes_by_type(node_type="experiment")

    # Get the experiment node's ID by name
    print(f"Searching for experiment: {experiment_name}")  # Debugging line
    experiment_ids = manager.get_id_by_name(experiment_name, view=view, predecessor=None)

    print(f"Experiment IDs found: {experiment_ids}")  # Debugging line

    if not experiment_ids:
        print(f"Experiment '{experiment_name}' not found.")
        return pd.DataFrame()  # Return an empty DataFrame if no experiment found

    experiment_id = experiment_ids[0]

    # Get all nodes of type "run"
    run_view = manager.filter_nodes_by_type(node_type="run")
    runs = []

    for node_id in run_view:
        # Get predecessors (sources of edges) for the current run node
        predecessors = manager.get_edge_source(node_id)

        # Debugging line to check predecessors
        print(f"Checking run node {node_id}, predecessors: {predecessors}")

        # Check if the experiment is the predecessor of the current run
        if predecessors and predecessors[0] == experiment_id:
            # Collect the properties of the run node
            properties = manager.get_node_properties(node_id)

            # Flatten nested structures like 'tags'
            if "tags" in properties and isinstance(properties["tags"], list):
                properties["tags"] = ", ".join(properties["tags"])

            # Add the run data to the list of runs
            runs.append(properties)

    # Debugging line to check the runs collected
    print(f"Runs found: {runs}")

    # Ensure `runs` list is non-empty and contains dictionaries
    if not runs:
        print("No runs found for the experiment.")
        return pd.DataFrame()

    # Return the collected runs as a pandas DataFrame
    df = pd.DataFrame(runs)

    # Return DataFrame
    return df


def get_run(experiment_name=None, log_type=None):
    """Retrieve all child nodes (hyperparameters, metrics, artifacts) for a particular run and return as a DataFrame.

    Args:
        experiment_name (str): The name of the experiment to filter runs.
        log_type (str): Type of logs to filter (e.g., "hyperparameter", "metric", "artifact").
                        If None, fetch all types.

        run => {
            hyperparamter : {
                name: value,
                name: value,
                name: value
            },
            metric : {
                name:value
            },
            artifact: {
                name: value
            }

    }
    """
    # Get the experiment node ID using get_node_id
    experiment_id = get_node_id(experiment_name, type="experiment") if experiment_name else edges["experiment"]

    # Retrieve all runs linked to this experiment
    view = manager.filter_nodes_by_type(node_type="run")
    runs = []

    for node_id in view:
        # Check if the run belongs to the given experiment
        if manager.get_edge_source(node_id)[0] == experiment_id:
            properties = manager.get_node_properties(node_id)
            run_data = {
                "run_id": node_id,
                "hyperparameters": [],
                "metrics": [],
                "artifacts": []
            }

            # Expand run_properties dictionary into individual columns
            for key, value in properties.items():
                run_data[key] = value

            # Retrieve child nodes (hyperparameters, metrics, artifacts) for this run
            if log_type is None or log_type == "hyperparameter":
                hyperparameters = get_hyperparameters(run_id=node_id)
                run_data["hyperparameters"] = hyperparameters
            if log_type is None or log_type == "metric":
                metrics = get_log_metrics(run_id=node_id)
                run_data["metrics"] = metrics
            if log_type is None or log_type == "artifact":
                artifacts = get_log_artifacts(run_id=node_id)
                run_data["artifacts"] = artifacts

            runs.append(run_data)

    # Convert the runs list into a DataFrame
    runs_df = pd.DataFrame(runs)
    return runs_df


def get_log_artifacts(run_id):
    """Retrieve all logged artifacts for the specified run."""
    view = manager.filter_nodes_by_type(node_type="artifact")
    artifacts = []
    for node_id in view:
        if manager.get_edge_source(node_id)[0] == run_id:
            properties = manager.get_node_properties(node_id)
            artifacts.append(properties)
    return artifacts


def get_metrics(run_id):
    """Retrieve all logged metrics for the specified run."""
    view = manager.filter_nodes_by_type(node_type="metric")
    metrics = []
    for node_id in view:
        if manager.get_edge_source(node_id)[0] == run_id:
            properties = manager.get_node_properties(node_id)
            metrics.append(properties)
    return metrics


def get_hyperparameters(run_name, as_dataframe = False):
    """Retrieve all logged hyperparameters for the specified run."""
    run_id = get_node_id(run_name, type="run")
    successor_nodes = manager.get_successor(run_id)
    hyperparameters = []
    for node_id in successor_nodes:
        properties = manager.get_node_properties(node_id)
        if properties["type"] == "hyperparameter":
            hyperparameters.append(properties)

    if as_dataframe:
        return pd.DataFrame(hyperparameters)
    else:
        return hyperparameters


def get_best_run(experiment_name=None, metric_name="abc", objective="minimize"):
    """
    Get the best run(s) with their properties based on a specific metric.
    Returns the result as a pandas DataFrame.

    Parameters:
        experiment_name (str): The name of the experiment. If None, considers all experiments.
        metric_name (str): The metric to base the evaluation on.
        objective (str): Either 'minimize' or 'maximize' to define the goal for the metric.

    Returns:
        pd.DataFrame: A DataFrame containing details of the best run(s).
    """

    best_runs = []

    # Fetch the experiments
    # replace this with get_node_id -> get experiment id by name REPLACE:TODO
    experiment_view = manager.filter_nodes_by_type(node_type="experiment")
    experiments = (
        [experiment_name]
        if experiment_name
        else [manager.get_node_properties(e).get("name") for e in experiment_view]
    )


    for exp_name in experiments:
        # Get experiment ID
        experiment_ids = manager.get_id_by_name(exp_name, view=experiment_view)
        if not experiment_ids:
            print(f"Experiment '{exp_name}' not found. Skipping.")
            continue

        experiment_id = experiment_ids[0]


        # REPLACE:TODO -> successor of experiment
        # Get all runs for the experiment
        run_view = manager.filter_nodes_by_type(node_type="run")
        run_ids = manager.get_id_by_name(None, view=run_view, predecessor=experiment_id)

        if not run_ids:
            print(f"No runs found for experiment '{exp_name}'. Skipping.")
            continue

        # Track the best run for the current experiment
        best_run_id = None
        best_metric_value = float("inf") if objective == "minimize" else float("-inf")

        for run_id in run_ids:
            # Fetch metrics for the run
            metric_view = manager.filter_nodes_by_type(node_type="metric")
            metrics = [
                (node_id, manager.get_node_properties(node_id))
                for node_id in metric_view
                if run_id in manager.get_edge_source(node_id)
            ]

            # Extract the value of the specified metric
            for node_id, metric in metrics:

                #get_metrics : REPLACE:TODO - use get metrics to get required metric value
                if metric.get("name") == metric_name:
                    metric_value = float(metric.get("value", float("nan")))
                    if (
                            (objective == "minimize" and metric_value < best_metric_value)
                            or (objective == "maximize" and metric_value > best_metric_value)
                    ):
                        best_metric_value = metric_value
                        best_run_id = run_id
                    break  # Since metrics are unique per run

        #REPLACE : TODO - return run details which results in best metric - call get run function from above based on run name
        # Add the best run details for the current experiment
        if best_run_id is not None:
            run_properties = manager.get_node_properties(best_run_id)
            run_properties["experiment_name"] = exp_name
            run_properties["best_metric"] = best_metric_value
            best_runs.append(run_properties)

    # Return the results as a DataFrame
    if not best_runs:
        print("No suitable runs found.")
        return pd.DataFrame()

    return pd.DataFrame(best_runs)



