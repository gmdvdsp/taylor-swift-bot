import datetime as time

class Member_data():
    
    def __init__(self):
        self._cooldown = time.datetime.now()
        self._listens: int = 0

    @property
    def cooldown(self):
        return self._cooldown

    @cooldown.setter
    def cooldown(self, value):
        self._cooldown = value

    @property
    def listens(self):
        return self._listens

    @listens.setter
    def listens(self, value):
        self._listens = value