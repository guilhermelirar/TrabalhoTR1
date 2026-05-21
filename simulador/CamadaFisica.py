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
    Retorna objeto de Sinal com forma de onda Manchester, onde 
    as transições 1 -> 0 representam 1 lógico, e 0 -> 1, 0 lógico,
    resultado da aplicação de um clock embutido ao sinal

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
       

def modularBipolar(bitstream: list[int], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> Sinal:
    """
    Retorna objeto de Sinal com forma de onda Bipolar, onde 0 V 
    representa o 0 lógico, e os valores volt_high, e volt_low
    representam o 1 lógico de forma alternada

    Args:
        bitstream: lista de inteiros que representam os bits do sinal 
        volt_high: máximo de energia do sinal (1 lógico de índice par) 
        volt_low: mínimo de energia do sinal (1 lógico de índice ímpar)
        amostras_p_bit: quantidade de amostras para representar um único bit

    Returns:
        Sinal: objeto sinal com as amostras moduladas para Bipolar
    """

    niveis = []

    # para cada bit, se for 1, usar volt_low ou volt_high alternadamente, 
    # e 0.0 casoc ontrário
    usar_high = True
    for b in bitstream:
        if b == 1:
            niveis.append(volt_high if usar_high else volt_low)
            usar_high = not usar_high
        else:
            niveis.append(0.0)

    return Sinal(
        np.repeat(niveis, amostras_p_bit),
        amostras_p_bit
    )
       
def modularASK(bitstream: list[int], volt_high: float = 5.0, 
                     amostras_p_bit: int = 100) -> Sinal:
    """
    Retorna objeto de Sinal com modulação por amplitude, em que 
    o sinal corresponde à uma senoide de amplitude volt_high enquanto 
    o valor lógico é 1, e 0 V caso contrário.

    Args:
        bitstream: lista de inteiros que representam os bits do sinal 
        volt_high: máximo de energia do sinal (1 lógico de índice par) 
        amostras_p_bit: quantidade de amostras para representar um único bit

    Returns:
        Sinal: objeto sinal com as amostras moduladas para Bipolar
    """

    niveis = []

    for b in bitstream:
        # senoide de A = volt_high em caso de 1 lógico, 0 cc
        if b == 1:
            niveis.extend(volt_high * np.sin(np.arange(amostras_p_bit)))
        else:
            niveis.extend(np.zeros(amostras_p_bit))

    return Sinal(
        np.array(niveis),
        amostras_p_bit
    )
       

