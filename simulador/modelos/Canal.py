#./simulador/modelos/Canal.py

from queue import Queue
from modelos.Sinal import Sinal
import numpy as np

class Canal:
    buffer: Queue
    desvio_ruido: float
    media_ruido: float

    def put(self, sinal: Sinal):
        for i in range(0, len(sinal.amostras), sinal.amostras_p_bit):
            niveis = sinal.amostras[i:(i+sinal.amostras_p_bit)]
            ruido = self.rng.normal(loc=self.media_ruido, 
                                scale=self.desvio_ruido, 
                                size = len(niveis))

            sinal_ruidoso = ruido + niveis
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


