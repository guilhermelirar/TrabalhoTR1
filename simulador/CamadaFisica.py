import numpy as np

from Modelos import Sinal

def modularNRZ_Polar(bitstream: list[int], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> Sinal:
    """
    Retorna objeto de Sinal com forma de onda NRZ 

    Args:
        bitstream: lista de inteiros que representam os bits do sinal 
        volt_high: máximo de energia do sinal 
        volt_low: mínimo de energia do sinal 
        amostras_p_bit: quantidade de amostras para representar um único bit

    Returns:
        Sinal: objeto sinal com as amostras moduladas para o NRZ
    """

    bits = np.array(bitstream)  # usando numpy

    # traduzindo para volt_high e volt_low
    valores = np.where(bits > 0, volt_high, volt_low)

    return Sinal(
            np.repeat(valores, amostras_p_bit), 
            amostras_p_bit
    )

def modularManchester(bitstream: list[int], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> Sinal:
    """
    Retorna objeto de Sinal com forma de onda Manchester

    Args:
        bitstream: lista de inteiros que representam os bits do sinal 
        volt_high: máximo de energia do sinal 
        volt_low: mínimo de energia do sinal 
        amostras_p_bit: quantidade de amostras para representar um único bit

    Returns:
        Sinal: objeto sinal com as amostras moduladas para o Manchester
    """

    bits = np.array(bitstream)
   
    # produzindo metades (para valores de clock)
    m1 = np.where(bits > 0, volt_high, volt_low)
    m2 = np.where(bits > 0, volt_low, volt_high)

    # unindo metades (transições representam valores)
    valores = np.column_stack((m1, m2)).flatten()

    return Sinal(
        np.repeat(valores, amostras_p_bit//2),
        amostras_p_bit
    )
        
