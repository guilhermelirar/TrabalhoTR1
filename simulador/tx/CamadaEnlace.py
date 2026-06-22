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
            hexa_str.append(f"{num}d")

    return " ".join(hexa_str)


# === 1/3 Protocolos de enquadramento === #

def enquadrar_contagem(bitstream: list[int], 
                                  num_bytes: int = 4):
    
    bitstream_out = []
    n_bits_quadro = num_bytes * 8
    bitstream_len = len(bitstream)

    report_l = ["Quadros de até 4 bytes"]
    for i in range(0, bitstream_len, n_bits_quadro):
        final = min(bitstream_len, n_bits_quadro + i)  
        quadro_util = bitstream[i:final]
        
        bitstream_out.extend(int_to_bitstream(len(quadro_util), 1))
        bitstream_out.extend(quadro_util)
        
        report_l.append(f"[{len(quadro_util)//8}]" 
                      f" {bits_para_hexa(quadro_util)}")
        
    report = "\n".join(report_l)
    return bitstream_out, report

def enquadrar_bytes_flag(bitstream: list[int], num_bytes: int = 4):
    FLAG = str_to_bitstream("B")
    ESC = str_to_bitstream("\\")

    report_l = [f"FLAG: {bits_para_hexa(FLAG)}, ESC: {bits_para_hexa(ESC)}"]
    bitstream_out = []
    n_bits_quadro = num_bytes * 8
    bitstream_len = len(bitstream)
   
    def inserir_escape(quadro_util: list[int]):
        # verifica ocorrência de FLAG ou ESC
        quadro_str = ["[FLAG]"]
        for i in range(0, len(quadro_util), 8):
            byte = quadro_util[i:i+8] 

            # Inserindo ESC quando necessário
            if byte == FLAG or byte == ESC:
                bitstream_out.extend(ESC)
                quadro_str.append("[ESC]")
            
            bitstream_out.extend(byte) # Inserindo conteúdo original

        quadro_str.append(bits_para_hexa(quadro_util))
        quadro_str.append("[FLAG]")
        quadro_str = " ".join(quadro_str)
        report_l.append(quadro_str)

    for i in range(0, bitstream_len, n_bits_quadro):
        final = min(bitstream_len, n_bits_quadro + i)
        quadro_util = bitstream[i:final]

        bitstream_out.extend(FLAG)  # coloca FLAG no inicio
        inserir_escape(quadro_util)
        bitstream_out.extend(FLAG)

    report = "\n".join(report_l)
    return bitstream_out, report

def enquadrar_bits_flag(bits: list[int], num_bytes: int = 4):
    FLAG = [0, 1, 1, 1, 1, 1, 1, 0]
    
    bitstream_out = []
    n_bits_quadro = num_bytes * 8
    bitstream_len = len(bits)
    report_l = [f"FLAG: {bits_para_hexa(FLAG)}"]

    for i in range(0, bitstream_len, n_bits_quadro):
        final = min(bitstream_len, n_bits_quadro + i)
        quadro_util = bits[i:final]

        bitstream_out.extend(FLAG)
        
        # acrescentar 0 após sequência de 5 1s
        quadro_com_stuffing = []
        contador_1 = 0
        
        for bit in quadro_util:
            quadro_com_stuffing.append(bit)
           
            if bit == 1:
                contador_1 += 1
                if contador_1 == 5:
                    quadro_com_stuffing.append(0)
                    contador_1 = 0 
            else:
                contador_1 = 0 

        bitstream_out.extend(quadro_com_stuffing)

        bitstream_out.extend(FLAG)
       
        print("REPORT L", report_l)
        report_l.append(f"[FLAG] {bits_para_hexa(quadro_com_stuffing)} [FLAG]")

    report = "\n".join(report_l)
    return bitstream_out, report

def aplicar_paridade(bits):
    STEP = 8 
    bits_o = []

    report_l = ["Aplicação de paridade: "]
    report_str_count = 0
    report_str = ""
    for i in range(0, len(bits), STEP):
        janela = bits[i:(min(len(bits), i + STEP))]
        n_1s = sum(bit for bit in janela if bit == 1)
        
        p = n_1s % 2 # bit de paridade

        if report_str_count == 4:
            report_l.append(report_str)
            report_str = f"{bits_para_hexa(janela)} ({p}) "
            report_str_count = 1
        else:
            report_str_count += 1
            report_str += f"{bits_para_hexa(janela)} ({p}) "

        janela.append(p) # se resto 0, adiciona 0 (par), cc, 1
        bits_o.extend(janela)

    report_l.append(report_str)
    report = "\n".join(report_l) 

    return bits_o, report


def aplicar_checksum(bits):
    STEP = 8 # soma 8 em 8
    bits_o = bits.copy() # para manter original 

    report_l = ["Aplicação de Checksum: "]
    report_str_count = 0
    report_str = ""
    
    soma_total = 0
    
    # calcular soma dos valores de byte dado por cada bloco
    for i in range(0, len(bits), STEP):
        janela = bits[i:(min(len(bits), i + STEP))]
        
        valor_byte = int("".join(map(str, janela)), 2)
        soma_total += valor_byte

        if report_str_count == 4:
            report_l.append(report_str)
            report_str = f"{bits_para_hexa(janela)} "
            report_str_count = 1
        else:
            report_str_count += 1
            report_str += f"{bits_para_hexa(janela)} "

    # lista de bits 8 menos significativos do complemento da soma
    checksum_val = (~(soma_total % 256)) & 0xFF
    checksum_bits = [int(b) for b in f"{checksum_val:08b}"]
    
    # relatório
    report_str += f"[CS: {bits_para_hexa(checksum_bits)}]"
    report_l.append(report_str)
    report = "\n".join(report_l) 

    bits_o.extend(checksum_bits)

    return bits_o, report
