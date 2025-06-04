from dash import Dash, html

from cost_volume_visualization import visualize
from OptionChanger import OptionChanger

from jaxtyping import install_import_hook

with install_import_hook(
    ("src",),
    ("beartype", "beartype"),
):
    from src.config import load_typed_root_config
    from src.dataset.data_module import DataModule
    from src.global_cfg import set_cfg

app = Dash()

# Requires Dash 2.17.0 or later
app.layout = [html.Div(children='Hello World')]


if __name__ == '__main__':
    app.run(debug=True)