import numpy as np 
from dataclasses import dataclass

@dataclass
class Sinal:
    amostras: np.ndarray
    amostras_p_bit: int 
    is_digital: bool = False

    @property
    def tempo(self) -> np.ndarray:
        return np.arange(len(self.amostras))

