import numpy as np

def modularNRZ_Polar(bitstream: list[int], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> np.ndarray:

    bits = np.array(bitstream)
    valores = np.where(bits > 0, volt_high, volt_low)
    amostras = np.repeat(valores, amostras_p_bit)

    return amostras

def modularManchester(bitstream: list[int], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> np.ndarray:
    
    bits = np.array(bitstream)
    
    m1 = np.where(bits > 0, volt_high, volt_low)
    m2 = np.where(bits > 0, volt_low, volt_high)

    valores = np.column_stack((m1, m2)).flatten()
    amostras = np.repeat(valores, amostras_p_bit//2)

    return amostras
        
