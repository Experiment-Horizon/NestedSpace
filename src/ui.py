import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd

# Sample data for experiments with hyperparameters and metrics
experiments = {
    "Experiment 1": {
        "description": "This is the first experiment.",
        "title": "First Experiment",
        "tags": ["tag1", "tag2"],
        "created_by": "User A",
        "runs": [
            {
                "run_id": 1,
                "status": "completed",
                "hyperparameters": {"learning_rate": 0.01, "batch_size": 32},
                "metrics": {"accuracy": 0.95, "loss": 0.05, "mse": 111},
            },
            {
                "run_id": 2,
                "status": "failed",
                "hyperparameters": {"learning_rate": 0.001, "batch_size": 64},
                "metrics": {"accuracy": 0.80, "loss": 0.2, "mse": 123},
            },
        ]
    },
    "Experiment 2": {
        "description": "This is the second experiment.",
        "title": "Second Experiment",
        "tags": ["tag3", "tag4"],
        "created_by": "User B",
        "runs": [
            {
                "run_id": 3,
                "status": "in progress",
                "hyperparameters": {"learning_rate": 0.1, "batch_size": 128},
                "metrics": {"accuracy": 0.90, "loss": 0.1, "mse": 223},
            },
            {
                "run_id": 4,
                "status": "completed",
                "hyperparameters": {"learning_rate": 0.05, "batch_size": 16},
                "metrics": {"accuracy": 0.98, "loss": 0.02, "mse": 123},
            },
        ]
    }
}

# Create a dropdown for selecting experiments
experiment_selector = widgets.Dropdown(
    options=list(experiments.keys()),
    description='Select Experiment:',
)

# Create labels for displaying information with HTML formatting and increased font size
title_label = widgets.HTML()
description_label = widgets.HTML()
tags_label = widgets.HTML()
created_by_label = widgets.HTML()

# Create output area for table
output_table = widgets.Output()

# Create sorting dropdowns for each column
sort_by_dropdown = widgets.Dropdown(
    options=['Learning Rate', 'Batch Size', 'Accuracy', 'Loss'],
    description='Sort by:',
    disabled=False,
)

sort_order_dropdown = widgets.Dropdown(
    options=['Ascending', 'Descending'],
    description='Order:',
    disabled=False,
)


def sort_table(change):
    selected_experiment = experiment_selector.value
    experiment_data = experiments[selected_experiment]

    # Convert run data into a pandas DataFrame for easy sorting
    runs = experiment_data['runs']
    data = []

    for run in runs:
        row = {
            'Run ID': run['run_id'],
            'Status': run['status'],
            'Learning Rate': run['hyperparameters']['learning_rate'],
            'Batch Size': run['hyperparameters']['batch_size'],
            'Accuracy': run['metrics']['accuracy'],
            'Loss': run['metrics']['loss'],
            'mse': run['metrics']['mse'],
        }
        data.append(row)

    df = pd.DataFrame(data)

    sort_column = sort_by_dropdown.value
    sort_order = sort_order_dropdown.value
    ascending = sort_order == 'Ascending'

    # Map dropdown labels to DataFrame column names
    column_mapping = {
        'Learning Rate': 'Learning Rate',
        'Batch Size': 'Batch Size',
        'Accuracy': 'Accuracy',
        'Loss': 'Loss',
        "MSE": 'mse'
    }

    # Sort the DataFrame based on the selected column and order
    sorted_df = df.sort_values(by=column_mapping[sort_column], ascending=ascending)

    # Display sorted table
    with output_table:
        clear_output()
        display_sorted_table(sorted_df)


## Function to display sorted table
def display_sorted_table(df):
    # Create an HTML table from the pandas DataFrame
    table_html = """
    <h3>Runs Table:</h3>
    <table style='width:100%; border-collapse: collapse;'>
        <tr>
            <th style='border: 1px solid black; padding: 8px; white-space: nowrap;'>Run ID</th>
            <th style='border: 1px solid black; padding: 8px; white-space: nowrap;'>Status</th>
            <th style='border: 1px solid black; padding: 8px; white-space: nowrap;'>Learning Rate</th>
            <th style='border: 1px solid black; padding: 8px; white-space: nowrap;'>Batch Size</th>
            <th style='border: 1px solid black; padding: 8px; white-space: nowrap;'>Accuracy</th>
            <th style='border: 1px solid black; padding: 8px; white-space: nowrap;'>Loss</th>
            <th style='border: 1px solid black; padding: 8px; white-space: nowrap;'>MSE</th>
        </tr>
    """

    # Add rows
    for _, row in df.iterrows():
        table_html += f"""
        <tr>
            <td style='border: 1px solid black; padding: 8px; white-space: nowrap;'>{row['Run ID']}</td>
            <td style='border: 1px solid black; padding: 8px; white-space: nowrap;'>{row['Status']}</td>
            <td style='border: 1px solid black; padding: 8px; white-space: nowrap;'>{row['Learning Rate']}</td>
            <td style='border: 1px solid black; padding: 8px; white-space: nowrap;'>{row['Batch Size']}</td>
            <td style='border: 1px solid black; padding: 8px; white-space: nowrap;'>{row['Accuracy']}</td>
            <td style='border: 1px solid black; padding: 8px; white-space: nowrap;'>{row['Loss']}</td>
            <td style='border: 1px solid black; padding: 8px; white-space: nowrap;'>{row['mse']}</td>
        </tr>
        """

    table_html += "</table>"
    display(HTML(table_html))


# Function to update the display when experiment changes
def on_experiment_change(change):
    selected_experiment = change['new']
    experiment_data = experiments[selected_experiment]

    # Update labels with experiment data using HTML for bold text and increased font size
    title_label.value = f"<span style='font-size: 2em;'><b>Title:</b> {experiment_data['title']}</span>"
    description_label.value = f"<span style='font-size: 2em;'><b>Description:</b> {experiment_data['description']}</span>"
    tags_label.value = f"<span style='font-size: 2em;'><b>Tags:</b> {', '.join(experiment_data['tags'])}</span>"
    created_by_label.value = f"<span style='font-size: 2em;'><b>Created By:</b> {experiment_data['created_by']}</span>"

    with output_table:
        clear_output()

        # Convert run data into a pandas DataFrame for easy sorting
        runs = experiment_data['runs']
        data = []

        for run in runs:
            row = {
                'Run ID': run['run_id'],
                'Status': run['status'],
                'Learning Rate': run['hyperparameters']['learning_rate'],
                'Batch Size': run['hyperparameters']['batch_size'],
                'Accuracy': run['metrics']['accuracy'],
                'Loss': run['metrics']['loss'],
                'mse': run['metrics']['mse'],
            }
            data.append(row)

        df = pd.DataFrame(data)

        # Initial display of the sorted table (sorted by 'Learning Rate' in ascending order by default)
        display_sorted_table(df)


# Link the dropdown to the function
experiment_selector.observe(on_experiment_change, names='value')

# Display the widgets (sorting dropdowns, experiment selector, labels, and table)
display(sort_by_dropdown, sort_order_dropdown)
display(experiment_selector)
display(title_label)
display(description_label)
display(tags_label)
display(created_by_label)
display(output_table)

# Initial display of experiment data (trigger change manually to populate)
on_experiment_change({'new': experiment_selector.value})
