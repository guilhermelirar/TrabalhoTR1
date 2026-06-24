# simulador/rx/CamadaFisica.py

"""
Implementações dos demoduladores (Camada Física)
do lado do receptor
"""

import math

def demodularNRZ_Polar(amostras: list[float], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> list[int]:

    """
    Demodula sinal NRZ polar e retorna bits extraídos
    
    Args:
        amostras: lista de valores de Voltagem
        volt_high: referência de valor máximo
        volt_low: referencia do valor mínimo

    Returns:
        list: bits resultantes da demodulação
    """
    limiar = (volt_high + volt_low)/2

    bitstream = []
    janela = []
    
    for inicio in range(0, len(amostras), amostras_p_bit):
        # bloco de amostras_p_bit
        fim = inicio + amostras_p_bit
        janela = amostras[inicio:fim]
        
        if len(janela) == 0:
            continue
            
        media_janela = sum(janela) / len(janela)
        bitstream.append(1 if media_janela > limiar else 0)

    return bitstream

def demodularManchester(amostras: list[float], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> list[int]:
    """
    Demodula sinal Manchester polar e retorna bits extraídos
    
    Args:
        amostras: lista de valores de Voltagem
        volt_high: referência de valor máximo
        volt_low: referencia do valor mínimo

    Returns:
        list: bits resultantes da demodulação
    """

    # Obtém bits considerando sinal NRZ com metade da taxa de amostragem
    transitions = demodularNRZ_Polar(amostras, volt_high, volt_low, 
                                     amostras_p_bit//2)

    # Dupla de bits (transição) determinam bits finais
    bitstream = []
    for i in range(0, len(transitions) - 1, 2):
        if transitions[i] == 1 and transitions[i+1] == 0:
            bitstream.append(1)
        else:
            bitstream.append(0)

    return bitstream

def demodularBipolar(amostras: list[float], volt_high: float = 5.0, 
                     amostras_p_bit: int = 100) -> list[int]:
    """
    Demodula sinal Bipolar AMI e retorna bits extraídos
    
    Args:
        amostras: lista de valores de Voltagem
        volt_high: referência de valor máximo
        volt_low: referencia do valor mínimo

    Returns:
        list: bits resultantes da demodulação
    """

    # consideram módulo e interpreta como NRZ
    amostras = [abs(i) for i in amostras]
    bitstream = demodularNRZ_Polar(amostras, volt_high, 0.0, amostras_p_bit)

    return bitstream

def demodularASK(amostras: list[float], volt_high: float = 5.0, 
                 amostras_p_bit: int = 100) -> list[int]:
    bitstream = []
    """
    Demodula sinal ASK e retorna bits extraídos. 
    Retifica o sinal e usa NRZ_Polar com referência 
    na média do valor de uma senoide modificada
    
    Args:
        amostras: lista de valores de Voltagem
        volt_high: referência de valor máximo
        volt_low: referencia do valor mínimo

    Returns:
        list: bits resultantes da demodulação
    """

    amostras_retificadas = [abs(x) for x in amostras]
    media_bit1 = 2 * volt_high / math.pi # média de senoide retificada

    bitstream = demodularNRZ_Polar(amostras_retificadas, media_bit1, 
                                   0.0, amostras_p_bit)

    return bitstream

def demodularFSK(amostras: list[float], 
                 volt_high: float = 5.0, amostras_p_bit: int = 100,
                 ciclos_f0 = 4, ciclos_f1 = 8):
    """
    Demodula sinal FSK e retorna bits extraídos
    
    Args:
        amostras: lista de valores de Voltagem
        volt_high: referência de valor máximo
        ciclos_f0: ciclos do símbolo 0
        ciclos_f1: ciclos do símbolo 1

    Returns:
        list: bits resultantes da demodulação
    """

    import numpy as np
    bitstream = []
  
    # construção das portadoras de referência
    t_bit_1 = np.linspace(0, 2 * np.pi * ciclos_f1, amostras_p_bit, 
                        endpoint=False)
    t_bit_0 = np.linspace(0, 2 * np.pi * ciclos_f0, amostras_p_bit, 
                        endpoint=False)
    
    portadora_1 = volt_high * np.sin(t_bit_1) 
    portadora_0 = volt_high * np.sin(t_bit_0) 

    # faz decisão com base em correlação da onda observada 
    # com as portadoras de referência
    for inicio in range(0, len(amostras), amostras_p_bit):

        # bloco de amostras_p_bit
        fim = inicio + amostras_p_bit
        janela = amostras[inicio:fim]
        
        if len(janela) == 0:
            continue

        # correlação da janela com a portadora 
        # (correlação máxima ideal é igual ao quadrado da portadora)
        corr_0 = np.sum(janela * portadora_0)
        corr_1 = np.sum(janela * portadora_1)

        bitstream.append(1 if corr_1 > corr_0 else 0)
    
    return bitstream

def demodularBPSK(amostras: list[float], volt_high = 5.0, 
                  amostras_p_simbolo = 100, ciclos_f = 4):
    """
    Demodula sinal NRZ polar e retorna bits extraídos
    
    Args:
        amostras: lista de valores de Voltagem
        volt_high: referência de valor máximo
        ciclos_f: número de ciclos da senoide

    Returns:
        list: bits resultantes da demodulação
    """   

    import numpy as np 
    bitstream = []

    t = np.linspace(0, 1, amostras_p_simbolo, endpoint=False)

    # portadora referencia para bit 1 no BPSK
    portadora_ref = volt_high * np.cos(2 * np.pi * ciclos_f * t)

    # decide com base na correlação
    for inicio in range(0, len(amostras), amostras_p_simbolo):
        fim = inicio + amostras_p_simbolo
        janela = np.array(amostras[inicio:fim])
        
        if len(janela) < amostras_p_simbolo:
            continue

        correlacao = np.sum(janela * portadora_ref)
  
        if correlacao > 0:
            bitstream.append(1)
        else: # fora de fase, valores negativos multiplicam valores positivos
            bitstream.append(0)
    
    return bitstream


def demodularQPSK(amostras: list[float], volt_high = 5.0, 
                  amostras_p_simbolo = 100, ciclos_f = 4):
    """
    Demodula sinal NRZ polar e retorna bits extraídos
    
    Args:
        amostras: lista de valores de Voltagem
        volt_high: referência de valor máximo
        ciclos_f: número de ciclos da senoide

    Returns:
        list: bits resultantes da demodulação
    """ 
    import numpy as np 
    bitstream = []

    t = np.linspace(0, 1, amostras_p_simbolo, endpoint=False)

    # portadora referencia para bit 1 no BPSK
    canal_I = volt_high * np.cos(2 * np.pi * ciclos_f * t)
    canal_Q = -volt_high * np.sin(2 * np.pi * ciclos_f * t)

    for inicio in range(0, len(amostras), amostras_p_simbolo):
        fim = inicio + amostras_p_simbolo
        janela = np.array(amostras[inicio:fim])
        
        if len(janela) < amostras_p_simbolo:
            continue

        correlacao_I = np.sum(janela * canal_I)
        correlacao_Q = np.sum(janela * canal_Q)

        print(f"Correlação i: {correlacao_I}, q: {correlacao_Q}")
      
        #     bits    C_I, C_Q
        #    (0, 0): (-1., -1.),
        #    (0, 1): (1., -1.),
        #    (1, 0): (-1., 1.),
        #    (1, 1): (1., 1.),
        bitstream.append(1 if correlacao_Q > 0 else 0)
        bitstream.append(1 if correlacao_I > 0 else 0)

    return bitstream


def demodular16QAM(amostras: list[float], volt_high: float = 5.0, 
                   amostras_p_simbolo: int = 100, ciclos_p_bit: int = 4):
    import numpy as np
    from math import sqrt
    
    bitstream = []
    
    # base de tempo usada na modulação
    t_simbolo = np.linspace(0, 2 * np.pi * ciclos_p_bit, 
                            amostras_p_simbolo, 
                            endpoint=False)
    
    # portadoras de referência para cálculo de correlação
    referencia_I = volt_high * np.cos(t_simbolo)
    referencia_Q = -volt_high * np.sin(t_simbolo)
    
    # ganho da correlação (integral de cos^2) para normalizar o sinal
    fator_escala = (volt_high ** 2) * (amostras_p_simbolo / 2)

    # limiar entre duas amplitudes de cada canal
    # ~0,47
    limiar_amplitude = (1 / sqrt(2) + 1 / (3 * sqrt(2))) / 2
    
    for inicio in range(0, len(amostras), amostras_p_simbolo):
        janela = np.array(amostras[inicio:inicio + amostras_p_simbolo])
        
        if len(janela) < amostras_p_simbolo:
            continue
            
        correlacao_I = np.sum(janela * referencia_I)
        correlacao_Q = np.sum(janela * referencia_Q)
        
        coord_i = correlacao_I / fator_escala
        coord_q = correlacao_Q / fator_escala
        
        # 3. Decisão dos bits com base nos limiares
        
        # ---- CANAL I (Bits 0 e 2) ----
        # define sinal
        bit0 = 1 if coord_i > 0 else 0
        # define amplitude
        bit2 = 1 if abs(coord_i) > limiar_amplitude else 0
        
        # ---- CANAL Q (Bits 1 e 3) ----
        bit1 = 1 if coord_q > 0 else 0
        bit3 = 1 if abs(coord_q) > limiar_amplitude else 0
        
        bitstream.extend([bit0, bit1, bit2, bit3])
        
    return bitstream

