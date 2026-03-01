# Пример банка
#
# - Ресурсы: Ресурс
# - События: состояние
#
# Сценарий:
#  Счетчик со случайным временем обслуживания и клиентами, которые отказываются от обслуживания

import random

import simpy

RANDOM_SEED = 42
NEW_CUSTOMERS = 20 # Общее количество клиентов
INTERVAL_CUSTOMERS = 10.0  # Генерирует новых клиентов примерно каждые x секунд
MIN_PATIENCE = 1  # Min терпение клиента
MAX_PATIENCE = 3  # Max терпение клиента


def source(env, number, interval, counter):
    # Источник генерирует клиентов случайным образом
    for i in range(number):
        c = customer(env, f'Customer{i:02d}', counter, time_in_bank=12.0)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)


def customer(env, name, counter, time_in_bank):
    # Клиент приходит, его обслуживают и он уходит
    arrive = env.now
    print(f'{arrive:7.4f} {name}: Here I am')

    with counter.request() as req:
        patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
        results = yield req | env.timeout(patience)

        wait = env.now - arrive

        if req in results:
            # Клиент подошел к стойке
            print(f'{env.now:7.4f} {name}: Waited {wait:6.3f}')

            tib = random.expovariate(1.0 / time_in_bank)
            yield env.timeout(tib)
            print(f'{env.now:7.4f} {name}: Finished')

        else:
            # Клиент ушел
            print(f'{env.now:7.4f} {name}: RENEGED after {wait:6.3f}')


# Настройка и запуск моделирования
print('Bank renege')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Запуск процесса
counter = simpy.Resource(env, capacity=1)
env.process(source(env, NEW_CUSTOMERS, INTERVAL_CUSTOMERS, counter))
env.run()