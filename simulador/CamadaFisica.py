import numpy as np

def modularNRZ_Polar(bitstream: list[int], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> np.ndarray:

    bits = np.array(bitstream)
    valores = np.where(bits > 0, volt_high, volt_low)
    amostras = np.repeat(valores, amostras_p_bit)

    return amostras
