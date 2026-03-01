

# ИНТЕРФЕЙСНЫЙ СЛОЙ (BRIDGE)
class BankBridge:
    def __init__(self, bank):
        self.bank = bank
        self.active_tasks = {}

    def start_service(self, agent, duration, patience):
        self.bank.env.process(self.bank.service_process(agent, duration, patience))

    def sync(self, until_time):
        if self.bank.env.now < until_time:
            self.bank.env.run(until=until_time)