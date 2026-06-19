# simulador/rx/CamadaFisica.py

"""
Implementações dos demoduladores (Camada Física)
do lado do receptor
"""

import math

from numpy import append

def demodularNRZ_Polar(amostras: list[float], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> list[int]:

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
    
    transitions = demodularNRZ_Polar(amostras, volt_high, volt_low, 
                                     amostras_p_bit//2)

    bitstream = []
    for i in range(0, len(transitions) - 1, 2):
        if transitions[i] == 1 and transitions[i+1] == 0:
            bitstream.append(1)
        else:
            bitstream.append(0)

    return bitstream

def demodularBipolar(amostras: list[float], volt_high: float = 5.0, 
                     amostras_p_bit: int = 100) -> list[int]:
    
    amostras = [abs(i) for i in amostras]
    bitstream = demodularNRZ_Polar(amostras, volt_high, 0.0, amostras_p_bit)

    return bitstream

def demodularASK(amostras: list[float], volt_high: float = 5.0, 
                 amostras_p_bit: int = 100) -> list[int]:
    bitstream = []
    
    amostras_retificadas = [abs(x) for x in amostras]
    media_bit1 = 2 * volt_high / math.pi # média de senoide retificada

    bitstream = demodularNRZ_Polar(amostras_retificadas, media_bit1, 
                                   0.0, amostras_p_bit)

    return bitstream

def demodularFSK(amostras: list[float], 
                 volt_high: float = 5.0, amostras_p_bit: int = 100,
                 ciclos_f0 = 4, ciclos_f1 = 8):
    import numpy as np
    bitstream = []
    
    t_bit_1 = np.linspace(0, 2 * np.pi * ciclos_f1, amostras_p_bit, 
                        endpoint=False)
    t_bit_0 = np.linspace(0, 2 * np.pi * ciclos_f0, amostras_p_bit, 
                        endpoint=False)
    
    portadora_1 = volt_high * np.sin(t_bit_1) 
    portadora_0 = volt_high * np.sin(t_bit_0) 

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
    import numpy as np 
    bitstream = []

    t = np.linspace(0, 1, amostras_p_simbolo, endpoint=False)

    # portadora referencia para bit 1 no BPSK
    portadora_ref = volt_high * np.cos(2 * np.pi * ciclos_f * t)

    for inicio in range(0, len(amostras), amostras_p_simbolo):
        fim = inicio + amostras_p_simbolo
        janela = np.array(amostras[inicio:fim])
        
        if len(janela) < amostras_p_simbolo:
            continue

        correlacao = np.sum(janela * portadora_ref)
  
        if correlacao > 0:
            bitstream.append(1)
        else: # fora de fase
            bitstream.append(0)
    
    return bitstream


def demodularQPSK(amostras: list[float], volt_high = 5.0, 
                  amostras_p_simbolo = 100, ciclos_f = 4):
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
