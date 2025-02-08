import src.space_manager as sm
import src.ui as ui
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


def list_experiments(project=None, as_dataframe=False):
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

    if as_dataframe:
        return pd.DataFrame(experiments)
    else:
        return experiments


def list_runs(experiment_name=None, as_dataframe=False):
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
        return runs

    if as_dataframe:
        # Return the collected runs as a pandas DataFrame
        df = pd.DataFrame(runs)
        return df
    else:
        return runs



def get_runs(experiment_name=None):
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
    run_ids = manager.get_successor(experiment_id)
    tracked_data = {}

    for run_id in run_ids:
        run_name = manager.get_name_by_id(run_id)
        tracked_data[run_name] = {}
        tracked_data[run_name]["hyperparameters"] = get_hyperparameters(run_name)
        tracked_data[run_name]["metrics"] = get_metrics(run_name)
        tracked_data[run_name]["artifacts"] = get_artifacts(run_name)

    return tracked_data



def get_artifacts(run_name, as_dataframe=False):
    """Retrieve all logged artifacts for the specified run."""
    run_id = get_node_id(run_name, type="run")
    successor_nodes = manager.get_successor(run_id)
    print(successor_nodes)
    artifacts = []
    for node_id in successor_nodes:
        properties = manager.get_node_properties(node_id)
        if properties["type"] in ['plot', 'model', 'data']:
            artifacts.append(properties)

    if as_dataframe:
        return pd.DataFrame(artifacts)
    else:
        return artifacts



def get_metrics(run_name, as_dataframe=False):
    """Retrieve all logged metrics for the specified run."""
    run_id = get_node_id(run_name, type="run")
    successor_nodes = manager.get_successor(run_id)
    metrics = []
    for node_id in successor_nodes:
        properties = manager.get_node_properties(node_id)
        if properties["type"] == "metric":
            metrics.append(properties)

    if as_dataframe:
        return pd.DataFrame(metrics)
    else:
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


def get_best_run(experiment_name=None, metric_name="mae", objective="minimize"):
    """
    Retrieve the best run(s) based on a specific metric from an experiment and return as a DataFrame.

    Args:
        experiment_name (str): The name of the experiment to filter runs.
        metric_name (str): The metric to evaluate for determining the best run.
        objective (str): Either 'minimize' or 'maximize' to define the goal for the metric.

    Returns:
        pd.DataFrame: A DataFrame containing details of the best run(s).
    """
    # Step 1: Get the experiment node ID
    experiment_id = get_node_id(experiment_name, type="experiment")
    if not experiment_id:
        print(f"Error: Experiment '{experiment_name}' not found.")
        return pd.DataFrame()

    # Step 2: Find all runs associated with the experiment
    successor_runs = manager.get_successor(experiment_id)
    if not successor_runs:
        print(f"No runs found for experiment '{experiment_name}'.")
        return pd.DataFrame()

    # Step 3: Track the best run based on the specified metric
    best_run = None
    best_metric_value = float("inf") if objective == "minimize" else float("-inf")

    # Step 4: Iterate through the runs and fetch metrics
    for run_id in successor_runs:
        name = manager.get_name_by_id(run_id)
        metrics = get_metrics(name)
        if not metrics:
            print(f"No metrics found for run '{run_id}', skipping.")
            continue

        metric_value = 0
        for metric in metrics:
            if metric_name in list(metric.values()):
                metric_value = float(metric['value'])
        print(metric_name)

        # Step 5: Update the best run based on the metric and objective
        if (
            (objective == "minimize" and metric_value < best_metric_value) or
            (objective == "maximize" and metric_value > best_metric_value)
        ):
            best_metric_value = metric_value
            best_run = {
                "run_id": run_id,
                "experiment_name": experiment_name,
                "best_metric": best_metric_value,
                **manager.get_node_properties(run_id)  # Merge with run properties
            }

    if not best_run:
        print(f"No suitable runs found for experiment '{experiment_name}' with metric '{metric_name}'.")
        return pd.DataFrame()

    # Convert the best run data into a DataFrame and return
    return pd.DataFrame([best_run])



def extract_named_items(data, item_type):
    """
    Extracts items with "name" and "value" (or similar) from a dictionary.

    Args:
        data: The input dictionary.
        item_type: The key where the list of items is stored (e.g., "hyperparameters", "metrics").

    Returns:
        A dictionary where keys are the "name" values and values are the
        corresponding "value" values. Returns an empty dictionary if the
        specified item_type is not found or if the data is not in the
        expected format.
    """
    extracted_items = {}

    if isinstance(data, dict) and item_type in data:
        items_list = data[item_type]

        if isinstance(items_list, list):  # Check if it's a list
            for item in items_list:
                if isinstance(item, dict) and "name" in item and "value" in item:
                    name = item["name"]
                    value = item["value"]
                    extracted_items[name] = round(value, 2)
                # Handle cases where "name" or "value" might be missing
                elif isinstance(item, dict):
                    print(f"Warning: Item in '{item_type}' is missing 'name' or 'value': {item}")
        else:
            print(f"Warning: '{item_type}' is not a list in the data.")
    else:
        print(f"Warning: Data is not a dictionary or '{item_type}' key not found.")

    return extracted_items



def get_experiment_data():
    """
    Retrieves and structures experiment data, including runs, hyperparameters, and metrics.

    Args:
        space: An object representing the experiment space (e.g., a client or API wrapper).
               This object should provide methods like list_experiments, list_runs, and get_runs.

    Returns:
        A dictionary where keys are experiment names and values are dictionaries containing
        experiment details and a list of runs. Each run includes hyperparameters and metrics.
        Returns an empty dictionary if no experiments are found or if an error occurs.
    """
    try:
        experiment_list = list_experiments()
        experiment_data_dict = {}

        for experiment in experiment_list:
            experiment_name = experiment["name"]
            experiment_data_dict[experiment_name] = experiment
            experiment_data_dict[experiment_name]["runs"] = []

            run_list = list_runs(experiment_name=experiment_name)
            for run in run_list:
                tracked_run_data = get_runs(experiment_name=experiment_name)
                if run["name"] in tracked_run_data: #Check if run name exists in tracked data.
                    run["hyperparameters"] = extract_named_items(tracked_run_data[run["name"]], item_type="hyperparameters")
                    run["metrics"] = extract_named_items(tracked_run_data[run["name"]], item_type="metrics")
                    experiment_data_dict[experiment_name]["runs"].append(run)
                else:
                    print(f"Warning: Run '{run['name']}' not found in tracked data for experiment '{experiment_name}'. Skipping.")


        return experiment_data_dict
    except Exception as e:
        print(f"Error retrieving experiment data: {e}")
        return {}


def show(experiment_name=None):
    experiments_data = get_experiment_data()
    if not experiment_name:
        ui.ExperimentView(experiments_data)
    else:
        runs = {run['name']: {k: v for k, v in run.items() if k != 'name'} for run in experiments_data[experiment_name]["runs"]}
        ui.RunView(runs)
