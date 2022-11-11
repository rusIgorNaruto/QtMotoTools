import datetime


class Moto:
    def __init__(self, name, db_id=-1):
        self.id = db_id
        self.moto_nazvanie = name
        self.histories = []

    def add_history(self, hitory):
        self.histories.append(hitory)


class Work:
    def __init__(self, date=datetime.datetime.now(), work='', mhc=0., cost=0):
        self.name = work
        self.date = date
        self.mhc = mhc
        self.cost = cost

    def __str__(self):
        return ':'.join([self.name, self.date, self.mhc, self.cost])

    def load(self, s):
        ':'.split(s)
