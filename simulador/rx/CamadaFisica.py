# simulador/rx/CamadaFisica.py

"""
Implementações dos demoduladores (Camada Física)
do lado do receptor
"""

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
