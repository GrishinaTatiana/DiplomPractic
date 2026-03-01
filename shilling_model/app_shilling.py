import os

import solara

from mesa.examples.basic.schelling.model import Schelling
from mesa.visualization import (
    Slider,
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
)


def get_happy_agents(model):
    # Отображает текстовое сообщение о количестве счастливых агентов
    return solara.Markdown(f"**Happy agents: {model.happy}**")

def agent_portrayal(agent):
    # 'o' - круг, 's' - квадрат
    # 'blue' и 'orange' - цвета
    color = "tab:blue" if agent.type == 0 else "tab:orange"
    marker = "o" if agent.happy else "X"  # Счастливые - кружки, несчастные - крестики

    return {
        "color": color,
        "marker": marker,
        "size": 50,
    }


path = os.path.dirname(os.path.abspath(__file__))


model_params = {
    "rng": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "density": Slider("Agent density", 0.8, 0.1, 1.0, 0.1),
    "minority_pc": Slider("Fraction minority", 0.2, 0.0, 1.0, 0.05),
    "homophily": Slider("Homophily", 0.4, 0.0, 1.0, 0.125),
    "width": 20,
    "height": 20,
}


model1 = Schelling()
renderer = SpaceRenderer(model1, backend="matplotlib").setup_agents(agent_portrayal)
# используется renderer.render() для визуализации агентов и сетки за один раз
renderer.render()

HappyPlot = make_plot_component({"happy": "tab:green"})

page = SolaraViz(
    model1,
    renderer,
    components=[
        HappyPlot,
        get_happy_agents,
    ],
    model_params=model_params,
)
page

# запуск:
# cd "D:\Пользователи\Tatiana Grishina\Python\ВКР\.venv\shilling_model"
# solara run app_shilling.py
