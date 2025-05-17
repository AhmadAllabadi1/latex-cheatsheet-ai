from jinja2 import Environment, FileSystemLoader
import os

def render_latex(content: str, font_size: str = "\\small", columns: int = 2, orientation: str = "portrait") -> str:
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('base.tex')
    return template.render(
        content=content,
        font_size=font_size,
        columns=columns,
        orientation=orientation
    )

