import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd


class ExperimentView:
    def __init__(self, experiments):
        self.experiments = experiments
        self.df = None
        self.numerical_columns = []

        # Create UI elements
        self.experiment_selector = widgets.Dropdown(options=list(self.experiments.keys()),
                                                    )
        self.experiment_selector_view = widgets.HBox(
            [widgets.HTML(value="<b>Select Experiment:</b>"), self.experiment_selector],
            layout=widgets.Layout(margin='10px 0 15px 0'), )
        self.title_label = widgets.HTML()
        self.description_label = widgets.HTML()
        self.tags_label = widgets.HTML()
        self.created_by_label = widgets.HTML()
        self.output_table = widgets.Output()

        # Initialize display
        self.sort_by_dropdown = widgets.Dropdown(description='Sort by:',
                                                 layout=widgets.Layout(margin='20px 0 5px 0', width="350px"))
        self.sort_order_dropdown = widgets.Dropdown(options=['Ascending', 'Descending'], description='Order:',
                                                    layout=widgets.Layout(margin='20px 0 5px 0', width="200px"))
        self.sort_menu = widgets.Box([self.sort_by_dropdown, self.sort_order_dropdown],
                                     layout=widgets.Layout(display='flex', justify_content='flex-end'))

        # Link events to functions
        self.experiment_selector.observe(self.on_experiment_change, names='value')
        self.sort_by_dropdown.observe(self.sort_table, names='value')
        self.sort_order_dropdown.observe(self.sort_table, names='value')

        # Initial display of experiment data
        self.update_display(self.experiment_selector.value)

        # Display the UI components
        display(self.experiment_selector_view)
        display(self.title_label)
        display(self.description_label)
        display(self.tags_label)
        display(self.created_by_label)
        display(self.sort_menu)
        display(self.output_table)

    def create_dataframe(self, selected_experiment):
        """Convert run data into a pandas DataFrame."""
        runs = self.experiments[selected_experiment]['runs']

        # Extracting data for DataFrame creation
        data = []
        for run in runs:
            run_data = {
                "Run Name": run["name"],
                "Created At": run["created_at"],
                "Last Updated": run["last_updated"],
                "Created By": run["created_by"]
            }

            # Dynamically adding hyperparameters and metrics
            for key, value in run['hyperparameters'].items():
                run_data[f'Hyperparameter: {key}'] = value

            for key, value in run['metrics'].items():
                run_data[f'Metric: {key}'] = value

            data.append(run_data)

        self.df = pd.DataFrame(data)

        # Detecting numerical columns
        self.numerical_columns = self.df.select_dtypes(include=['number']).columns.tolist()

    def display_sorted_table(self, df):
        """Display the sorted DataFrame as an HTML table."""
        table_html = df.to_html(index=False, border=1)
        with self.output_table:
            clear_output()
            display(HTML(table_html))

    def update_display(self, selected_experiment):
        """Update the display based on selected experiment."""
        experiment_data = self.experiments[selected_experiment]

        self.title_label.value = f"<span style='font-size: 1.2em;'><b>Title:</b></span> <span style='font-size: 1em;'>{experiment_data['name']}</span>"
        self.description_label.value = f"<span style='font-size: 1.2em;'><b>Description:</b></span> <span style='font-size: 1em;'>{experiment_data['description']}</span>"
        self.tags_label.value = f"<span style='font-size: 1.2em;'><b>Tags:</b></span> <span style='font-size: 1em;'>{', '.join(experiment_data['tags'])}</span>"
        self.created_by_label.value = f"<span style='font-size: 1.2em;'><b>Created By:</b></span> <span style='font-size: 1em;'>{experiment_data['created_by']}</span>"

        self.create_dataframe(selected_experiment)

        # Update sort options based on new DataFrame
        self.sort_by_dropdown.options = self.numerical_columns

        # Display the initial sorted table
        if len(self.numerical_columns) > 0:
            self.display_sorted_table(self.df)

    def on_experiment_change(self, change):
        """Handle change in experiment selection."""
        self.update_display(change['new'])

    def sort_table(self, change):
        """Sort and display the table based on selected criteria."""
        if not self.df.empty:
            sorted_df = self.df.sort_values(by=self.sort_by_dropdown.value,
                                            ascending=self.sort_order_dropdown.value == 'Ascending')
            self.display_sorted_table(sorted_df)


# Sample data for experiments with hyperparameters and metrics
experiments_data = {
    "Experiment 1": {
        "description": "Lung cancer detection involves using advanced diagnostic techniques and tools to identify the presence of cancerous cells in the lungs at an early stage. This process typically integrates medical imaging technologies like X-rays, CT scans, and PET scans with emerging computational tools, such as artificial intelligence (AI) and machine learning algorithms. These technologies can analyze medical images to identify abnormalities, such as nodules or tumors, that may indicate cancer.",
        "title": "First Experiment",
        "tags": ["tag1", "tag2"],
        "created_by": "User A",
        "runs": [
            {"run_id": "1", "status": "completed",
             "hyperparameters": {"learning_rate": 0.01, "batch_size": 32, "alpha": 0.02, "epoch": 64},
             "metrics": {"accuracy": 0.95, "loss": 0.05}},
            {"run_id": "2", "status": "failed",
             "hyperparameters": {"learning_rate": 0.001, "batch_size": 64, "alpha": 0.03, "epoch": 128},
             "metrics": {"accuracy": 0.80, "loss": 0.2}},
        ]
    },
    "Experiment 2": {
        "description": "This is the second experiment.",
        "title": "Second Experiment",
        "tags": ["tag3", "tag4"],
        "created_by": "User B",
        "runs": [
            {"run_id": "3", "status": "in progress", "hyperparameters": {"learning_rate": 0.1, "batch_size": 128},
             "metrics": {"accuracy": 0.90, "loss": 0.1}},
            {"run_id": "4", "status": "completed", "hyperparameters": {"learning_rate": 0.05, "batch_size": 16},
             "metrics": {"accuracy": 0.98, "loss": 0.02}},
        ]
    }
}

# Create an instance of ExperimentManager with the sample data
#experiment_manager = ExperimentView(experiments_data)

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd

class RunView:
    def __init__(self, runs_data):
        self.runs_data = runs_data
        self.selected_run = None

        # Create UI elements
        self.run_selector = widgets.Dropdown(options=list(self.runs_data.keys()), description='Select Run:')

        self.title_label = widgets.HTML()
        self.description_label = widgets.HTML()
        self.tags_label = widgets.HTML()
        self.hyperparameters_label = widgets.HTML(value="<b>Hyperparameters:</b>")
        self.hyperparameters_table = widgets.Output()
        self.metrics_label = widgets.HTML(value="<b>Metrics:</b>")
        self.metrics_table = widgets.Output()
        self.artifacts_label = widgets.HTML(value="<b>Artifacts:</b>")
        self.artifacts_display = widgets.Output()

        # Link event to function
        self.run_selector.observe(self.on_run_change, names='value')

        # Display the UI components
        display(self.run_selector)
        display(self.title_label)
        display(self.description_label)
        display(self.tags_label)
        display(self.hyperparameters_label)
        display(self.hyperparameters_table)
        display(self.metrics_label)
        display(self.metrics_table)
        display(self.artifacts_label)
        display(self.artifacts_display)

        self.display_all(list(self.runs_data.keys())[0])

    def on_run_change(self, change):
        """Handle change in run selection."""
        selected_run_id = change['new']

        if not selected_run_id:
            return

        display_all(selected_run_id)

    def display_all(self, selected_run_id):
        # Get the selected run data
        run_data = self.runs_data[selected_run_id]

        # Update title and description labels
        self.title_label.value = f"<b>Run Name:</b> {selected_run_id}"
        self.description_label.value = f"<b>Description:</b> {run_data.get('description', 'No description available.')}"

        # Update tags label
        tags = run_data.get('tags', [])
        self.tags_label.value = f"<b>Tags:</b> {', '.join(tags) if tags else 'No tags available'}"

        # Display hyperparameters table
        hyperparameters_df = pd.DataFrame(run_data.get('hyperparameters', {}).items(), columns=['Hyperparameter', 'Value'])

        with self.hyperparameters_table:
            clear_output(wait=True)
            display(HTML(hyperparameters_df.to_html(index=False)))

        # Display metrics table
        metrics_df = pd.DataFrame(run_data.get('metrics', {}).items(), columns=['Metric', 'Value'])

        with self.metrics_table:
            clear_output(wait=True)
            display(HTML(metrics_df.to_html(index=False)))

        # Display artifacts (assuming they are image URLs)
        with self.artifacts_display:
            clear_output(wait=True)
            artifacts = run_data.get('artifacts', [])
            if artifacts:
                for artifact in artifacts:
                    display(HTML(f"<img src='{artifact}' style='width: 200px; height: auto; margin: 5px;'>"))
            else:
                display(HTML("<p>No artifacts available for this run.</p>"))
