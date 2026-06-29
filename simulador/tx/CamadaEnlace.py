# simulador/tx/CamadaEnlace.py

from Utils import *

"""
Implementação dos serviços da camada da camada de 
enlace
"""

from Utils import *

def obter_fn_erro(tipo_tratamento: str):
    def fn_deteccao_idle(dado: list[int]):
        """Função padrão sem tratamento de erro"""
        return dado, ["(sem tratamento de erro)"]
    
    def aplicar_checksum(bits: list[int]):
        """Calcula checksum"""
        report = ["Aplicando checksum"]
        soma = sum([bits_to_int(byte) for byte in slice_list(bits, 8)])


        while soma > 255:
            vai_um = soma >> 8   
            soma = (soma & 0xFF) + vai_um 

        checksum_byte = int_to_byte(~soma & 0xFF)
        report.append(f"Checksum({bits_to_str(bits)})="
            f"{bits_to_int(checksum_byte)}")
        
        res = bits.copy()
        res.extend(checksum_byte)
        report.append(f"Res: {bits_to_str(res)}") 

        return res, report

    def aplicar_hamming(bits: list[int]):
        """Função que aplica hamming aos bits"""
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

    def bit_paridade(dado: list[int]):
        """Insere um bit de paridade ao final dos bits"""
        report = ["Aplicando bit de paridade: "]
        soma = sum(dado)
        p = soma % 2
        
        report.append(f"{bits_to_str(dado)}+{p}")
        
        dado.append(p)
        
        return dado, report
    
    def aplicar_crc32(bits: list[int]):
        """Calcula CRC-32 e retorna bits com o CRC no final"""
        bits_o = bits.copy()
        report = ["Aplicação de CRC-32: "]
        
        # agrupar em bytes para o relatório
        report_str = ""
        report_str_count = 0
        for janela in slice_list(bits, 8):
            if report_str_count == 4:
                report.append(report_str)
                report_str = f"{bits_to_str(janela)} "
                report_str_count = 1
            else:
                report_str_count += 1
                report_str += f"{bits_to_str(janela)} "

        # cálculo do CRC-32
        crc = 0xFFFFFFFF
        for janela in slice_list(bits, 8):
            byte_val = bits_to_int(janela) 
            
            crc ^= byte_val
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xEDB88320 
                else:
                    crc >>= 1
                    
        crc_final = crc ^ 0xFFFFFFFF
        
        # preenchimento de 32b 
        crc_bits = [int(b) for b in f"{crc_final:032b}"]
        
        bits_o.extend(crc_bits)
        
        report_str += f"[CRC: {bits_to_str(crc_bits)}]"
        report.append(report_str)
    
        return bits_o, report   

    funcoes_erro = {
            "bit de paridade": bit_paridade,
            "hamming": aplicar_hamming, 
            "checksum": aplicar_checksum,
            "crc-32": aplicar_crc32
            }
    
    return funcoes_erro.get(tipo_tratamento.lower(), fn_deteccao_idle)
    
def obter_enquadrador(enquadramento: str, fn_erro):
    FLAG = [0, 1, 1, 1, 1, 1, 1, 0]
    ESC = str_to_bytes("\\")[0]

    def quadro_contagem(bytes_d: list[list[int]]):
        num_bytes = len(bytes_d)
        report = ["[Quadro por contagem]", f"N de bytes: {num_bytes}"]
        header = int_to_byte(num_bytes)
        quadro = header
        conteudo, report_erro = fn_erro(concat(bytes_d))
        report.extend(report_erro)
        quadro.extend(conteudo)
        report.append(f"Quadro final: {bits_to_str(quadro)}")
        return quadro, report

    def quadro_insercao_byte(bytes_d: list[list[int]]):
        """Retorna uma lista de bits que representa um quadro por 
        insserção de bytes e escape (quando necessário)"""
        report = ["[Inserção de Bytes]", 
                  f"FLAG[{bits_to_str(FLAG)}] ESC[{bits_to_str(ESC)}]"]
        
        quadro = []
        quadro.extend(FLAG)
        
        conteudo, report_erro = fn_erro(concat(bytes_d))
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

    def quadro_insercao_bit(bytes_d: list[list[int]]):
        bits_d = concat(bytes_d)
        report = [f"[Inserção de Bits com Flag: {bits_to_str(FLAG)}"]

        quadro = []
        bits_tratado, report_err = fn_erro(bits_d)
        report.extend(report_err)
        
        quadro.extend(FLAG)
        count_1 = 0
        escapes = 0
        for bit in bits_tratado:
            quadro.append(bit)

            if bit == 1:
                count_1 += 1
            else:
                count_1 = 0

            # se completou 5 uns, insere o 0 de escape imediatamente
            if count_1 == 5:
                quadro.append(0)
                count_1 = 0 
                escapes += 1

        quadro.extend(FLAG)
        report.append(f"Número de 0 inseridos p/ escape: {escapes}")
        report.append(f"Quadro: {bits_to_str(quadro)}")

        return quadro, report

    enquadradores = {
            "contagem de caracteres": quadro_contagem,
            "inserção de bytes": quadro_insercao_byte,
            "inserção de bits": quadro_insercao_bit
            }

    return enquadradores.get(enquadramento.lower(), quadro_contagem)
