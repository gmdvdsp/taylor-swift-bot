class Member_data():
    
    def __init__(self):
        self._cooldown = None

    @property
    def cooldown(self):
        return self._cooldown

    @cooldown.setter
    def cooldown(self, value):
        self._cooldown = value