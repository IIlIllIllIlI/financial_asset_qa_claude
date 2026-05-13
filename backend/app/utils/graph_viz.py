"""LangGraph flowchart visualization using system default image viewer."""

import io
import threading
from PIL import Image

from app.utils.logger import setup_logger

logger = setup_logger("utils.graph_viz")


def show_graph_image(compiled_graph) -> None:
    """Render LangGraph Mermaid PNG and open with system default viewer.

    Runs in a daemon thread so it never blocks the server startup.
    """

    def _show():
        try:
            png_bytes = compiled_graph.get_graph().draw_mermaid_png()
            img = Image.open(io.BytesIO(png_bytes))
            img.show()
            logger.info("LangGraph flowchart displayed")
        except Exception as e:
            logger.warning(f"Failed to display graph image: {e}")

    t = threading.Thread(target=_show, daemon=True)
    t.start()
