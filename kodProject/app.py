from Mesa_Model import BankModel

import matplotlib.pyplot as plt


def run_simulation(steps=500):
    # Инициализация модели
    model = BankModel(width=20, height=10, n_tellers=1, spawn_rate=0.8)

    # Включаем интерактивный режим Matplotlib
    plt.ion()
    fig, ax = plt.subplots(figsize=(12, 6))

    # Флаг для управления циклом
    is_running = True

    # Функция-обработчик закрытия окна
    def on_close(event):
        nonlocal is_running
        is_running = False
        print(f"\nПроцесс остановлен пользователем на шаге {model.steps}.")

    # Привязываем событие закрытия окна к нашей функции
    fig.canvas.mpl_connect('close_event', on_close)

    # Карта цветов для статусов
    colors_map = {
        "ENTERING": "blue",
        "WAITING": "yellow",
        "BEING_SERVED": "orange",
        "SERVED": "green",
        "LEFT": "red"
    }

    print("Симуляция запущена. Закройте окно для остановки.")

    for i in range(steps):
        # ПРОВЕРКА 1: Остановлен ли цикл флагом
        if not is_running:
            break

        # Выполнение одного шага модели
        model.step()

        # ПРОВЕРКА 2: Существует ли еще окно перед отрисовкой
        if not plt.fignum_exists(fig.number):
            break

        try:
            ax.clear()

            # Настройка осей и сетки
            ax.set_xlim(-1, 20)
            ax.set_ylim(-1, 10)
            ax.set_aspect('equal')
            ax.set_title(
                f"Шаг: {model.steps} | В очереди: {len(model.bank.tellers.queue)} | Ушло: {len([a for a in model.agents if a.status == 'LEFT'])} | Температура: {model.temperature:.1f}°C")
            ax.grid(True, linestyle=':', alpha=0.6)

            # Линия касс (для наглядности)
            ax.axvline(x=0.5, color='black', linestyle='--', alpha=0.3)

            # Отрисовка всех активных агентов
            for agent in model.agents:
                if hasattr(agent, "pos") and agent.pos is not None:
                    # 1. ОПРЕДЕЛЯЕМ БАЗОВЫЙ ЦВЕТ ПО ТИПУ (для ENTERING и WAITING)
                    if agent.client_type == "HEAT_RESISTANT":
                        c = "blue"
                    else:
                        c = "purple"

                    # 2. ПЕРЕКРАШИВАЕМ ТОЛЬКО ЕСЛИ СТАТУС ОСОБЫЙ
                    # Если статус в списке ниже, он заменит синий/фиолетовый.
                    # Статус "WAITING" в этот список не включаем, чтобы цвет не менялся.
                    if agent.status == "BEING_SERVED":
                        c = "orange"
                    elif agent.status == "SERVED":
                        c = "green"
                    elif agent.status == "LEFT":
                        c = "red"

                    # 3. ВЫБИРАЕМ ФОРМУ
                    marker = 's' if agent.status == "BEING_SERVED" else 'o'
                    size = 180 if agent.status == "BEING_SERVED" else 100

                    # Отрисовка
                    ax.scatter(agent.pos[0], agent.pos[1],
                               c=c, s=size, marker=marker,
                               edgecolors='black', linewidths=0.5, zorder=3)

            # Обновление графического окна
            fig.canvas.draw()
            fig.canvas.flush_events()

            # Пауза для контроля скорости анимации (в секундах)
            plt.pause(0.1)

        except Exception as e:
            # Если возникла ошибка отрисовки (например, окно закрылось в процессе)
            print(f"Завершение отрисовки.")
            break

    # Корректное завершение работы Matplotlib
    plt.ioff()
    plt.close('all')
    print("Симуляция полностью завершена.")


if __name__ == "__main__":
    run_simulation(500)


