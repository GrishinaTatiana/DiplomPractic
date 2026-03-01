
import random
import pysd
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from SimPy_kod import BankModule
from Integration import BankBridge
from Mesa_Agents import ClientAgent


class BankModel(Model):
    def __init__(self, width=20, height=10, n_tellers=2, spawn_rate=0.25):
        # 1. Инициализация базового класса Mesa (создает self.steps, self.agents и др.)
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False)
        self.bank = BankModule(n_tellers)
        self.bridge = BankBridge(self.bank)
        self.spawn_rate = spawn_rate  # Вероятность появления (0.25 = 25%)

        # Загружаем SD модель
        self.sd_model = pysd.read_vensim("bank_temp.mdl")

        # Начальное состояние SD модели
        self.temperature = 25  # Начальная температура в градусах

        # 4. Настройка сбора данных для графиков
        self.datacollector = DataCollector(
            model_reporters={
                "Очередь": lambda m: len(m.bank.tellers.queue),
                "Ушли": lambda m: len([a for a in m.agents if a.status == "LEFT"])
            }
        )

    def step(self):
        # 1. Считаем текущее количество людей в банке
        current_people = len(self.agents)

        # 2. Передаем это значение в SD модель как входной параметр (External)
        # И запускаем расчет на 1 шаг времени (step)
        # Метод run позволяет получить значение переменной на текущем шаге
        res = self.sd_model.run(
            params={'people_count': current_people},
            return_columns=['room_temperature'],
            initial_condition='current'  # Продолжаем с того места, где остановились
        )
        new_temp = res['room_temperature'].iloc[-1]

        # ПРОВЕРКА В КОНСОЛИ:
        print(f"Людей: {current_people} | Старая T: {self.temperature:.2f} | Новая T: {new_temp:.2f}")

        # 3. Обновляем температуру в Mesa из результатов SD
        self.temperature = new_temp


        # ВЕРОЯТНОСТЬ ПОЯВЛЕНИЯ (например, 20% шанс каждый ход)
        if random.random() < self.spawn_rate:
            ctype = random.choice(["HEAT_RESISTANT", "HEAT_SENSITIVE"])
            new_client = ClientAgent(self, self.bridge, ctype)
            self.grid.place_agent(new_client, (19, random.randint(0, 9)))

        # Двигаем всех, кто уже в банке
        self.agents.shuffle().do("step")

        # БЕЗОПАСНАЯ ОЧИСТКА: удаляем тех, кто помечен как DELETED
        # Делаем это после хода, чтобы список агентов был стабилен во время отрисовки
        for agent in list(self.agents):
            if agent.status == "DELETED":
                agent.remove()

        # Синхронизация SimPy
        self.bridge.sync(self.steps)
        self.datacollector.collect(self)