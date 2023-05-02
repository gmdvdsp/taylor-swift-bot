
class Wordle_guess():
    def __init__(self, word):
        self.letters = [None, None, None, None, None]
        self.greens = 0
        self.initialize_data(word)

    def initialize_data(self, word):
        for index in range(len(self.letters)):
            self.letters[index] = [word[index], 'w'] 