import simpy
import random
import solara
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.visualization import SolaraViz, make_space_component, make_plot_component


# SimPy - логика процессов
class LogisticsModule:
    def __init__(self):
        self.env = simpy.Environment()
        self.loading_bay = simpy.Resource(self.env, capacity=2) # только 2 грузовика могут загружаться одновременно

    def loading_process(self, agent_id, duration):
        with self.loading_bay.request() as req:
            yield req
            yield self.env.timeout(duration)


#  Bridge - интерфейстный слой
class IntegrationBridge:
    def __init__(self, logistics):
        self.logistics = logistics
        self.active_tasks = {}

    def start_loading(self, agent_id, duration):
        event = self.logistics.env.process(self.logistics.loading_process(agent_id, duration))
        self.active_tasks[agent_id] = event

    def is_finished(self, agent_id):
        event = self.active_tasks.get(agent_id)
        return event.processed if event else True

    def sync(self, until_time):
        if self.logistics.env.now < until_time:
            self.logistics.env.run(until=until_time)


# Mesa - агенты
class TruckAgent(Agent):
    def __init__(self, model, bridge):
        super().__init__(model)  # unique_id создается автоматически
        self.bridge = bridge
        self.status = "MOVING"

    def step(self):
        if self.status == "MOVING":
            x, y = self.pos
            if x > 0:
                self.model.grid.move_agent(self, (x - 1, y))
            else:
                # Начало процесса в SimPy
                self.bridge.start_loading(self.unique_id, duration=random.uniform(2, 5))
                self.status = "WAITING"

        elif self.status in ["WAITING", "LOADING"]:
            if self.bridge.is_finished(self.unique_id):
                self.status = "DONE"
                # Возвращаем агента в начало для зацикливания примера
                self.model.grid.move_agent(self, (self.model.grid.width - 1, random.randint(0, 9)))
                self.status = "MOVING"
            else:
                # Проверка - агент в очереди или уже на погрузке
                res = self.bridge.logistics.loading_bay
                is_loading = any(p.proc == self.bridge.active_tasks[self.unique_id] for p in res.users)
                self.status = "LOADING" if is_loading else "WAITING"

# Mesa - модель
class WarehouseModel(Model):
    def __init__(self, n_trucks=15, width=10, height=10):
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False)

        # подключение SimPy через Bridge
        self.logistics = LogisticsModule()
        self.bridge = IntegrationBridge(self.logistics)

        # настройка сбора данных для графиков
        self.datacollector = DataCollector(
            model_reporters={
                "Queue": lambda m: len(m.logistics.loading_bay.queue)
            }
        )

        # создание и размещение агентов
        for _ in range(n_trucks):
            truck = TruckAgent(self, self.bridge)
            # грузовики у правого края (x = width-1)
            start_pos = (width - 1, random.randint(0, height - 1))
            self.grid.place_agent(truck, start_pos)

    def step(self):
        # Основной цикл модели:
        # Mesa (Агенты) -> SimPy (Процессы) -> DataCollector (Статистика)

        # активация всех агентов в случайном порядке
        # вызываем метод step() у каждого агента
        self.agents.shuffle().do("step")

        # продвигаем время в SimPy до текущего шага Mesa
        self.bridge.sync(self.steps)

        # собираем данные для визуализации (длина очереди)
        self.datacollector.collect(self)


# визуализация
def agent_portrayal(agent):
    colors = {"MOVING": "blue", "WAITING": "yellow", "LOADING": "red", "DONE": "green"}
    return {"color": colors.get(agent.status, "gray"), "marker": "o", "size": 30}


# создание экземпляра модели
model_instance = WarehouseModel(n_trucks=8)

# Solara - настройка интерфейса
page = SolaraViz(
    model_instance,
    components=[
        make_space_component(agent_portrayal),
        make_plot_component({"Queue": "red"})
    ],
    name="Mesa + SimPy Hybrid System"
)
