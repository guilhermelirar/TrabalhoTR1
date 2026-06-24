#./simulador/modelos/Canal.py

from queue import Queue
import numpy as np

class Canal:
    buffer: Queue
    desvio_ruido: float
    media_ruido: float

    def _ruido(self, size):
        return self.rng.normal(loc=self.media_ruido, 
                                scale=self.desvio_ruido, 
                                size = size)

    def put(self, sinal: np.ndarray):
        STEP = 100 # número de amostras 
        for i in range(0, len(sinal), STEP):
            niveis = sinal[i:(i+STEP)]
            sinal_ruidoso = self._ruido(len(niveis)) + niveis
            self.buffer.put(sinal_ruidoso)

    def empty(self):
        return self.buffer.empty()

    def get(self):
        return self.buffer.get()

    def __init__(self):
        self.desvio_ruido = .5
        self.media_ruido = .0
        self.buffer = Queue()

        self.rng = np.random.default_rng(seed=42)
        pass


