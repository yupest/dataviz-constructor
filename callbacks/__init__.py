from .data_callbacks import register_data_callbacks
from .essay_callbacks import register_essay_callbacks
from .dashboard_callbacks import register_dashboard_callbacks
from .tabs_callbacks import register_tabs_callbacks
from .visualization_callbacks import register_visualization_callbacks

def register_all_callbacks(app):
    register_tabs_callbacks(app)
    register_data_callbacks(app)
    register_visualization_callbacks(app)
    register_essay_callbacks(app)
    register_dashboard_callbacks(app)