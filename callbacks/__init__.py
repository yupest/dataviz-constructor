from .data_callbacks import register_data_callbacks
from .visualization_callbacks import register_visualization_callbacks

def register_all_callbacks(app):
    register_data_callbacks(app)
    register_visualization_callbacks(app)