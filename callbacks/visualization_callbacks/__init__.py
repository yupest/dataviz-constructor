from .barchart_callbacks import register_barchart_callbacks
from .linechart_callbacks import register_linechart_callbacks
from .wordcloud_callbacks import register_wordcloud_callbacks
from .dotchart_callbacks import register_dotchart_callbacks
from .piechart_callbacks import register_piechart_callbacks
from .table_callbacks import register_table_callbacks
from .text_callbacks import register_text_callbacks

def register_visualization_callbacks(app):
    register_barchart_callbacks(app)
    register_linechart_callbacks(app)
    register_wordcloud_callbacks(app)
    register_dotchart_callbacks(app)
    register_piechart_callbacks(app)
    register_table_callbacks(app)
    register_text_callbacks(app)