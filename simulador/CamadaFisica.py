def modularNRZ_Polar(bitstream: list[int], volt_high: float = 5.0, 
                     volt_low: float = -5.0, 
                     amostras_p_bit: int = 100) -> list[float]:
    valores = [volt_high if b else volt_low for b in bitstream]
    amostras = []

    for v in valores:
        amostras.extend([v]*amostras_p_bit)

    return amostras
