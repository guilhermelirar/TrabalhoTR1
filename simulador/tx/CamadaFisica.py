import numpy as np
from math import sqrt

def modularNRZ_Polar(bitstream: list[int], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> np.ndarray:
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

    return np.repeat(valores, amostras_p_bit) 

def modularManchester(bitstream: list[int], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> np.ndarray:
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

    return np.repeat(valores, amostras_p_bit//2)
       

def modularBipolar(bitstream: list[int], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> np.ndarray:
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

    return np.repeat(niveis, amostras_p_bit)
       
def modularASK(bitstream: list[int], volt_high: float = 5.0, 
               amostras_p_bit: int = 100, ciclos_p_bit: int = 4) -> np.ndarray:
    """
    Retorna objeto de Sinal com modulação por amplitude, em que 
    o sinal corresponde à uma senoide de amplitude volt_high enquanto 
    o valor lógico é 1, e 0 V caso contrário.

    Args:
        bitstream: lista de inteiros que representam os bits do sinal 
        volt_high: máximo de energia do sinal
        amostras_p_bit: quantidade de amostras para representar um único bit
        ciclos_p_bit: número de ciclos da onda por bit

    Returns:
        Sinal: objeto sinal com as amostras moduladas para ASK
    """

    niveis = []
    # base de 0 a 2pi quantidade de ciclos
    t_bit = np.linspace(0, 2 * np.pi * ciclos_p_bit, amostras_p_bit, 
                        endpoint=False)

    for b in bitstream:
        # senoide de A = volt_high em caso de 1 lógico, 0 cc
        if b == 1:
            niveis.extend(volt_high * np.sin(t_bit))
        else:
            niveis.extend(np.zeros(amostras_p_bit))
    
    return np.array(niveis)   

def modularPSK(bitstream: list[int], volt_high: float = 5.0, 
                amostras_p_simbolo: int = 100, ciclos_p_bit: int = 4,
               bits_por_simbolo: int = 1) -> np.ndarray: 
    """
    Retorna objeto de Sinal com modulação por Phase Shift Keying, 
    em que  o sinal corresponde à uma senoide com símbolo codificado
    por mudança de fase.

    Args:
        bitstream: lista de inteiros que representam os bits do sinal 
        volt_high: máximo de energia do sinal
        amostras_p_bit: quantidade de amostras para representar um único bit
        ciclos_p_bit: ciclos da senoide durante representação de 1 bit

    Returns:
        Sinal: objeto sinal com as amostras moduladas para PSK. 

    """
   
    tabela_psk = {
            (1,): (1.0, 0.),
            (0,): (-1.0, 0.),
            (0, 0): (-1., -1.),
            (0, 1): (1., -1.),
            (1, 0): (-1., 1.),
            (1, 1): (1., 1.),
            }

    niveis = []
    # base de 0 a 2pi quantidade de ciclos
    t_simbolo = np.linspace(0, 2 * np.pi * ciclos_p_bit, 
                            amostras_p_simbolo, 
                            endpoint=False)
    
    for i in range(0, len(bitstream), bits_por_simbolo):
        # informação que será convertida em 1 símbolo
        bits = bitstream[i:(i+bits_por_simbolo)]
        bits = tuple(bits)

        coordenadas = tabela_psk[bits]

        # cos
        canal_i = volt_high*np.cos(t_simbolo) * coordenadas[0]
        canal_q = -volt_high*np.sin(t_simbolo) * coordenadas[1]

        niveis.extend(canal_i + canal_q)
        
    return np.array(niveis)

def modular16QAM(bitstream: list[int], volt_high: float = 5.0, 
                amostras_p_simbolo: int = 100, ciclos_p_bit: int = 4): 
    """
    Retorna objeto de Sinal com modulação por 16-QAM, 
    em que  o sinal corresponde à uma senoide com símbolo codificado
    por mudança de fase e amplitude, transportando 4 bits por símbolo.

    Args:
        bitstream: lista de inteiros que representam os bits do sinal 
        volt_high: máximo de energia do sinal
        amostras_p_simbolo: quantidade de amostras para representar simbolo
        ciclos_p_bit: ciclos da senoide durante representação de 1 bit

    Returns:
        Sinal: objeto sinal com as amostras moduladas para 16QAM. 

    """

    def get_qam_coordinates(nibble):
        sign_i = 1 if nibble[0] == 1 else -1
        sign_q = 1 if nibble[1] == 1 else -1 
        amp_i = (1/sqrt(2)) if nibble[2] == 1 else (1/(3*sqrt(2)))
        amp_q = (1/sqrt(2))  if nibble[3] == 1 else (1/(3*sqrt(2)))
        return (sign_i * amp_i, sign_q * amp_q)

    niveis = []
    bits_por_simbolo = 4
    # base de 0 a 2pi quantidade de ciclos
    t_simbolo = np.linspace(0, 2 * np.pi * ciclos_p_bit, 
                            amostras_p_simbolo, 
                        endpoint=False)
   
    for i in range(0, len(bitstream), bits_por_simbolo):
        # informação que será convertida em 1 símbolo
        bits = bitstream[i:(i+bits_por_simbolo)]
        bits = tuple(bits)

        coordenadas = get_qam_coordinates(bits)

        # cos
        canal_i = volt_high*np.cos(t_simbolo) * coordenadas[0]
        canal_q = -volt_high*np.sin(t_simbolo) * coordenadas[1]

        niveis.extend(canal_i + canal_q)
        
    return np.array(niveis)


def modularFSK(bitstream: list[int], volt_high: float = 5.0, 
               amostras_p_bit: int = 100,
               ciclos_f0 = 4, ciclos_f1 = 8) -> np.ndarray:
    """
    Retorna objeto de Sinal com modulação por frequência 

    Args:
        bitstream: lista de inteiros que representam os bits do sinal 
        volt_high: máximo de energia do sinal 
        amostras_p_bit: quantidade de amostras para representar um único bit
        freq1: frequência do símbolo 0
        freq2: frequência do símbolo 1

    Returns:
        Sinal: objeto sinal com as amostras moduladas para FSK
    """

    niveis = []
    # base de 0 a 2pi quantidade de ciclos
    t_bit_1 = np.linspace(0, 2 * np.pi * ciclos_f1, amostras_p_bit, 
                        endpoint=False)
    t_bit_0 = np.linspace(0, 2 * np.pi * ciclos_f0, amostras_p_bit, 
                        endpoint=False)
    for b in bitstream:
        # senoide de A = volt_high em caso de 1 lógico, 0 cc
        if b == 1:
            niveis.extend(volt_high * np.sin(t_bit_1))
        else:
            niveis.extend(volt_high * np.sin(t_bit_0))

    return np.array(niveis)

