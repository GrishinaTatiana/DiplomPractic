import simpy
from Mesa_Agents import ClientAgent


# SIMPY (ЛОГИКА ПРОЦЕССОВ)
class BankModule:
    def __init__(self, n_tellers):
        self.env = simpy.Environment()
        self.tellers  = simpy.Resource(self.env, capacity=n_tellers) # окна кассиров (колво окон - n_tellers)

    def service_process(self, agent, duration, patience):

        # Клиент запрашивает окно
        with self.tellers.request() as req:
            # Механизм терпения: ждем освобождения окна или истечения терпения
            results = yield req | self.env.timeout(patience)

            if req in results:
                agent.status = "BEING_SERVED"  # Переключаем статус для смены цвета
                yield self.env.timeout(duration)  # Обслуживание 2 шага
                agent.status = "SERVED"
            else:
                agent.status = "LEFT"