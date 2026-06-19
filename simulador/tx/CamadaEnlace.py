# simulador/tx/CamadaEnlace.py

"""
Implementação dos serviços da camada da camada de 
enlace
"""

def str_to_bitstream(string: str):
    res_str = ''.join(format(ord(char), '08b') for char in string)
    return [int(c) for c in res_str]

def int_to_bitstream(number: int, max_bytes: int) -> list[int]:
    total_bits = max_bytes * 8
    binary_str = format(number, f'0{total_bits}b')
    return [int(bit) for bit in binary_str]

# === 1/3 Protocolos de enquadramento === #

def enquadrar_contagem_caracteres(bitstream: list[int], 
                                  num_bytes: int = 4):
    
    bitstream_out = []
    n_bits_quadro = num_bytes * 8
    bitstream_len = len(bitstream)

    for i in range(0, bitstream_len, n_bits_quadro):
        final = min(bitstream_len, n_bits_quadro + i)  
        quadro_util = bitstream[i:final]
        
        # 1 byte de contagem de caracteres
        bitstream_out.extend(int_to_bitstream(len(quadro_util), 1))
        bitstream_out.extend(quadro_util)

        print(f"Quadro {i} tem {len(quadro_util)}")
        
    print(bitstream_out)
    return bitstream_out
