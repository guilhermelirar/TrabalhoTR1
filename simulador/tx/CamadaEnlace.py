# simulador/tx/CamadaEnlace.py

from Utils import *

"""
Implementação dos serviços da camada da camada de 
enlace
"""
""""
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

def aplicar_crc32(bits):
    bits_o = bits.copy()
    report_l = ["Aplicação de CRC-32: "]
    
    # agrupar em bytes
    STEP = 8
    report_str = ""
    report_str_count = 0
    for i in range(0, len(bits), STEP):
        janela = bits[i:min(len(bits), i + STEP)]
        if report_str_count == 4:
            report_l.append(report_str)
            report_str = f"{bits_para_hexa(janela)} "
            report_str_count = 1
        else:
            report_str_count += 1
            report_str += f"{bits_para_hexa(janela)} "

    # usando inteiros
    crc = 0xFFFFFFFF
    for i in range(0, len(bits), 8):
        janela = bits[i:i+8]
        while len(janela) < 8:
            janela.append(0)
        byte_val = int("".join(map(str, janela)), 2)
        
        crc ^= byte_val
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xEDB88320 
            else:
                crc >>= 1
                
    crc_final = crc ^ 0xFFFFFFFF
    
    crc_bits = [int(b) for b in f"{crc_final:032b}"]
    
    bits_o.extend(crc_bits)
    
    report_str += f"[CRC: {bits_para_hexa(crc_bits)}]"
    report_l.append(report_str)
    report = "\n".join(report_l)
    
    return bits_o, report

def aplicar_hamming(bits):
    bits_o = []
    report_l = ["Aplicação de Hamming (7,4)"]
    report_str = ""
    report_str_count = 0

    # 4 em 4 bytes para inserir 3
    for i in range(0, len(bits), 4):
        janela = bits[i:i+4]
        while len(janela) < 4:
            janela.append(0)
            
        d1, d2, d3, d4 = janela[0], janela[1], janela[2], janela[3]
        
        p1 = d1 ^ d2 ^ d4
        p2 = d1 ^ d3 ^ d4
        p3 = d2 ^ d3 ^ d4
       
        # bloco final
        bloco_7bits = [p1, p2, d1, p3, d2, d3, d4]
        bits_o.extend(bloco_7bits)
        
        if report_str_count == 4:
            report_l.append(report_str)
            report_str = f"{bits_para_hexa(janela)}"\
                    f"->{p1}{p2}{d1}{p3}{d2}{d3}{d4}"
            report_str_count = 1
        else:
            report_str_count += 1
            report_str += f"{bits_para_hexa(janela)} ->"\
                    f"Bloco({p1}{p2}{d1}{p3}{d2}{d3}{d4}) "
            
    report_l.append(report_str)
    report = "\n".join(report_l)
    return bits_o, report
"""""

from Utils import *

def aplicar_hamming(bits: list[int]):
    bits_o = []
    report = ["Aplicando de Hamming (7,4)"]

    # 4 em 4 bytes para inserir 3

    current_byte = []
    converted_byte = []
    for nibble in slice_list(bits, 4):
        current_byte.extend(nibble)
        d1, d2, d3, d4 = nibble[0], nibble[1], nibble[2], nibble[3]
       
        # bits de paridade
        p1 = d1 ^ d2 ^ d4
        p2 = d1 ^ d3 ^ d4
        p3 = d2 ^ d3 ^ d4

        # blcoo final
        bloco_7bits = [p1, p2, d1, p3, d2, d3, d4]
        converted_byte.extend(bloco_7bits)

        if len(current_byte) == 8:
            report.append(
                    f"[{bits_to_str(current_byte)}]->" 
                    f"[{bits_to_str(converted_byte)}]"
                    )
            bits_o.extend(converted_byte)
            current_byte = []
            converted_byte = []

    return bits_o, report

def obter_fn_erro(tipo_deteccao: str, usar_hamming: bool):
    def fn_correcao_idle(dado: list[int]):
        return dado, ["(sem correção de erro)"]
    
    def fn_deteccao_idle(dado: list[int]):
        return dado, ["(sem detecção de erro)"]

    def bit_paridade(dado: list[int]):
        report = ["Aplicando bit de paridade: "]
        soma = sum(dado)
        p = soma % 2
        
        report.append(f"{bits_to_str(dado)}+{p}")
        
        dado.append(p)
        
        return dado, report
    
    detectores = {
            "bit de paridade": bit_paridade,
            }
    
    fn_deteccao = detectores.get(tipo_deteccao.lower(), fn_deteccao_idle)
    fn_correcao = aplicar_hamming if usar_hamming else fn_correcao_idle

    def fn_erro(bytes_d: list[list[int]]):
        report = ["Tratamento de erro: "]
        bits_in = concat(bytes_d)  
        
        bits_correcao, report_correcao = fn_correcao(bits_in)
        report.extend(report_correcao)

        bits_finais, report_deteccao = fn_deteccao(bits_correcao)
        report.extend(report_deteccao)

        return bits_finais, report

    return fn_erro

    
def obter_enquadrador(enquadramento: str, fn_erro):
    def quadro_contagem(bytes_d: list[list[int]]):
        num_bytes = len(bytes_d)
        report = ["[Quadro por contagem]", f"N de bytes: {num_bytes}"]
        header = int_to_byte(num_bytes)
        quadro = header
        conteudo, report_erro = fn_erro(bytes_d)
        report.extend(report_erro)
        quadro.extend(conteudo)
        report.append(f"Quadro final: {bits_to_str(quadro)}")
        return quadro, report

    def quadro_insercao_byte(bytes_d: list[list[int]]):
        FLAG = [0, 1, 1, 1, 1, 1, 1, 0]
        ESC = str_to_bytes("\\")[0]
        report = ["[Inserção de Bytes]", 
                  f"FLAG[{bits_to_str(FLAG)}] ESC[{bits_to_str(ESC)}]"]
        
        quadro = []
        quadro.extend(FLAG)
        
        conteudo, report_erro = fn_erro(bytes_d)
        report.extend(report_erro)
       
        report_quadro_str = "Quadro: [FLAG]"
        
        
        i = 0
        while i < len(conteudo):
            bloco = conteudo[i:i+8]
            if bloco == FLAG or bloco == ESC:
                quadro.extend(ESC)
                report_quadro_str += "[ESC]"
                i += 8
            
                quadro.extend(bloco)
                report_quadro_str += bits_to_str(bloco) 
            
            else: 
                report_quadro_str += bits_to_str([conteudo[i]])
                quadro.append(conteudo[i])
                i += 1

        quadro.extend(FLAG)
        report_quadro_str += "[FLAG]"
        report.append(report_quadro_str)

        return quadro, report

    enquadradores = {
            "contagem de caracteres": quadro_contagem,
            "inserção de bytes": quadro_insercao_byte
            }

    return enquadradores.get(enquadramento.lower(), quadro_contagem)
