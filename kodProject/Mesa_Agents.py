
import random

from mesa import Agent


# MESA (ОСНОВНАЯ СТРУКТУРА)
class ClientAgent(Agent):
    def __init__(self, model, bridge, client_type):
        super().__init__(model)
        self.bridge = bridge
        self.client_type = client_type

        # Устойчивость к жаре (терпение)
        self.base_patience = 30 if client_type == "HEAT_RESISTANT" else 10
        self.status = "ENTERING"

    def step(self):
        # 1. ИДЕМ К КАССАМ (до столбца x=1)
        if self.status == "ENTERING":
            x, y = self.pos
            # Проверяем, есть ли кто-то слева от нас
            cell_to_left = (x - 1, y)
            if x > 1 and self.model.grid.is_cell_empty(cell_to_left):
                self.model.grid.move_agent(self, cell_to_left)
            elif x <= 1:
                self.status = "WAITING"

                # РАСЧЕТ ТЕРПЕНИЯ С УЧЕТОМ ЖАРЫ
                # Если 25 градусов — терпение базовое. Если 50 — в 2 раза меньше.
                current_temp = self.model.temperature
                dynamic_patience = self.base_patience / (current_temp / 25)

                # Передаем вычисленное терпение в SimPy
                self.bridge.start_service(self, duration=2, patience=dynamic_patience)

        # 2. ОБСЛУЖИВАНИЕ (Встаем в столбец 0, меняем цвет на Оранжевый)
        elif self.status == "BEING_SERVED":
            x, y = self.pos
            if x != 0:
                self.model.grid.move_agent(self, (0, y))

        # 3. УХОД (После обслуживания или если кончилось терпение)
        elif self.status in ["SERVED", "LEFT"]:
            x, y = self.pos
            if x < self.model.grid.width - 1:
                self.model.grid.move_agent(self, (x + 1, y))
            else:
                # ВАЖНО: Только убираем с сетки, чтобы он исчез для отрисовки
                if self.pos is not None:
                    self.model.grid.remove_agent(self)
                # Помечаем его для удаления самой моделью
                self.status = "DELETED"
