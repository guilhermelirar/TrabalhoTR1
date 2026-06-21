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

def bits_para_hexa(lista_de_bits):
    # Agrupa a lista de 8 em 8 bits
    bytes_list = [lista_de_bits[i:i+8] 
                  for i in range(0,len(lista_de_bits), 8)]
    
    hexa_str = []
    for b in bytes_list:
        # numero inteiro
        bin_str = "".join(map(str, b)) # string binária
        num = int(bin_str, 2)          # inteiro do binário

        if len(b) == 8:
            # hexa decimal
            hexa_str.append(f"{num:02X}h")
        
        else:
            hexa_str.append(f"{num:07b}b")

    return " ".join(hexa_str)


# === 1/3 Protocolos de enquadramento === #

def enquadrar_contagem(bitstream: list[int], 
                                  num_bytes: int = 4):
    
    bitstream_out = []
    n_bits_quadro = num_bytes * 8
    bitstream_len = len(bitstream)

    report = []
    for i in range(0, bitstream_len, n_bits_quadro):
        final = min(bitstream_len, n_bits_quadro + i)  
        quadro_util = bitstream[i:final]
        
        # 1 byte de contagem de caracteres
        bitstream_out.extend(int_to_bitstream(len(quadro_util), 1))
        bitstream_out.extend(quadro_util)
        
        report.append(f"[{len(quadro_util)//8}]" 
                      f" {bits_para_hexa(quadro_util)}")
        
    print(bitstream_out)
    return bitstream_out, report

def enquadrar_bytes_flag(bitstream: list[int], num_bytes: int = 4):
    FLAG = str_to_bitstream("B")
    ESC = str_to_bitstream("\\")

    report = { "FLAG": bits_para_hexa(FLAG), 
              "ESC": bits_para_hexa(ESC), 
              "BITS": []}
    bitstream_out = []
    n_bits_quadro = num_bytes * 8
    bitstream_len = len(bitstream)
   
    def inserir_escape(quadro_util: list[int]):
        # verifica ocorrência de FLAG ou ESC
        for i in range(0, len(quadro_util), 8):
            byte = quadro_util[i:i+8] 

            # Inserindo ESC quando necessário
            if byte == FLAG or byte == ESC:
                bitstream_out.extend(ESC)
                report["BITS"].append("[ESC]")
            
            bitstream_out.extend(byte) # Inserindo conteúdo original
        report["BITS"].append(bits_para_hexa(quadro_util))

    for i in range(0, bitstream_len, n_bits_quadro):
        final = min(bitstream_len, n_bits_quadro + i)
        quadro_util = bitstream[i:final]

        bitstream_out.extend(FLAG)  # coloca FLAG no inicio
        report["BITS"].append("[FLAG]")

        inserir_escape(quadro_util)

        bitstream_out.extend(FLAG)
        report["BITS"].append("[FLAG]")

    print(report)
    return bitstream_out, report
