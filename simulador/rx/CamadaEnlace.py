from Utils import *

# === DESENQUADRAMENTO === #
from Utils import *

def remover_hamming(bits: list[int]):
    bits_o = []
    for bloco in slice_list(bits, 7):
        if len(bloco) != 7:
            bits_o.extend(bloco)
            continue

        _, _, d1, _, d2, d3, d4 = bloco[0], bloco[1],\
                bloco[2], bloco[3], bloco[4], bloco[5], bloco[6]

        bits_o.extend([d1, d2, d3, d4])

    return bits_o

def corrigir_hamming(bits: list[int]):
    report = ["Correção (hamming)"]
    bits_corrigido = []
    erros_corrigidos = []
    for bloco in slice_list(bits, 7):
        if len(bloco) != 7:
            bits_corrigido.extend(bloco)
            continue

        p1, p2, d1, p3, d2, d3, d4 = bloco[0], bloco[1],\
                bloco[2], bloco[3], bloco[4], bloco[5], bloco[6]
        
        s1 = p1 ^ d1 ^ d2 ^ d4
        s2 = p2 ^ d1 ^ d3 ^ d4
        s3 = p3 ^ d2 ^ d3 ^ d4
       
        sindrome_pos = (s3 << 2) | (s2 << 1) | s1
        
        bloco_corrigido = bloco.copy()
        if sindrome_pos != 0:
            # erro de 1 bit encontrado
            bloco[sindrome_pos - 1] ^= 1
            erros_corrigidos.append(sindrome_pos)

            bloco_corrigido = [p1, p2, d1, p3, d2, d3, d4]
        
        bits_corrigido.extend(bloco_corrigido)

    report.append(f"Erros corrigidos em {erros_corrigidos}")
    report.append(f"Bits pós correção: {bits_to_str(bits_corrigido)}")

    bits_o = remover_hamming(bits_corrigido)

    report.append(f"Bits finais: {bits_to_str(bits_o)}")
    return bits_o, report
    
def verifica_paridade(bits):
    soma = sum(bits)
    report = ["Verificação de paridade (par):"]

    if soma % 2 == 0:
        report.append(f"OK {bits_to_str(bits[:-1])}|{bits[len(bits)-1]}")
        return bits[:-1], report

    report.append(f"ERR {bits_to_str(bits[:-1])}"
                  f"|{bits[len(bits)-1]} resulta em ímpar")
    report.append("RETRANSMISSÃO NECESSÁRIA")
    return [], report        

def verifica_checksum(bits: list[int]):
    """Calcula checksum"""
    report = ["[Verificando checksum RX]"]
    soma = sum([bits_to_int(byte) for byte in slice_list(bits, 8)])
    
    while soma > 255:
        vai_um = soma >> 8   
        soma = (soma & 0xFF) + vai_um 

    checksum_final = ~soma & 0xFF

    if checksum_final != 0:
        report.append(f"ERR: obteve 0x{checksum_final:02x}, esperado 0x00")
        report.append("RETRANSMISSÃO NECESSÁRIA")
        return [], report

    report.append(f"Checksum OK")
    
    res = bits[:-8]
    report.append(f"Res: {bits_to_str(res)}") 

    return res, report

def obter_fn_erro(tipo_tratamento: str):
    def idle(bits: list[int]):
        return bits, ["(sem tratamento de erro em rx)"]

    detectadores = {
            "bit de paridade": verifica_paridade,
            "hamming": corrigir_hamming,
            "checksum": verifica_checksum,
            "crc-32": verifica_crc32
            }
    return detectadores.get(tipo_tratamento.lower(), idle) 

def verifica_crc32(bits: list[int]):
    """Verifica o CRC-32 no RX"""
    report = ["[Verificando CRC-32 RX]"]
    
    # crc nos ultimos 32 bits
    if len(bits) < 32:
        report.append("ERR: Quadro menor que 32 bits"
        " impossível verificar CRC")
        report.append("RETRANSMISSÃO NECESSÁRIA")
        return [], report

    # separando crc dos bits de dado
    dados_bits = bits[:-32]
    crc_recebido_bits = bits[-32:]
    
    # recalcula o crc par comparar com o recebido 
    crc = 0xFFFFFFFF
    for janela in slice_list(dados_bits, 8):
        byte_val = bits_to_int(janela)
        
        crc ^= byte_val
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xEDB88320 
            else:
                crc >>= 1
                
    crc_recalculado = crc ^ 0xFFFFFFFF
    crc_recebido_int = bits_to_int(crc_recebido_bits)

    if crc_recalculado != crc_recebido_int:
        report.append(f"ERR: CRC recalculado (0x{crc_recalculado:08x}) "
                      f"difere do recebido (0x{crc_recebido_int:08x})")
        report.append("RETRANSMISSÃO NECESSÁRIA")
        return [], report

    report.append("CRC-32 OK")
    report.append(f"Res: {bits_to_str(dados_bits)}") 

    return dados_bits, report

def desenquadrador(enquadramento: str, max_bytes_quadro: int, 
                   tipo_tratamento_erro: str):
    tipo_tratamento_erro = tipo_tratamento_erro.lower()
    fn_erro = obter_fn_erro(tipo_tratamento_erro) 

    FLAG = [0, 1, 1, 1, 1, 1, 1, 0]
    ESC = str_to_bytes("\\")[0]
    
    n_bits_edc = 0
    if "paridade" in tipo_tratamento_erro:
        n_bits_edc = 1
    elif "crc" in tipo_tratamento_erro:
        n_bits_edc = 32
    elif "checksum" in tipo_tratamento_erro:
        n_bits_edc = 8
 
    usar_hamming = "hamming" in tipo_tratamento_erro

    def desenquadrar_contagem(bits: list[int]):
        report = ["[Desenquadrando por contagem de caracteres]"]
        bits_uteis = []
        i = 0
        while i < len(bits):
            header = bits[i:i+8]
            num_bytes = bits_to_int(header)
            num_bits = n_bits_edc

            if usar_hamming:
                num_bits += num_bytes * 14 # hamming(7,4)
            else:
                num_bits += num_bytes * 8

            i += 8
            bits_no_quadro = bits[i:i + num_bits]
            report.append(f"[{num_bytes}]{bits_to_str(bits_no_quadro)}")

            bits_verificados, report_erro = fn_erro(bits_no_quadro)
            i += num_bits
            
            bits_uteis.extend(bits_verificados)
            report.extend(report_erro)
            
            if bits_verificados == []:
                return [], report

        return slice_list(bits_uteis, 8), report
    
    def desenquadrar_insercao_bytes(bits: list[int]):
        report = ["[Desenquadrando por inserção de bytes/flag]"]


        bits_uteis = []
        i = 0

        quadro_bruto = []
        esc_count = 0
        while i < len(bits):
            bloco = bits[i:i+8]

            # inicio ou fim de quadro
            if (bloco == FLAG ):
                i += len(bloco)
                # inicio do quadro
                if quadro_bruto == []:
                    continue
                print("quadro bruto", bits_to_str(quadro_bruto)) 
                # fim do quadro
                report.append(f"Q: {bits_to_str(quadro_bruto)}," 
                              f"{esc_count} escapes")
                esc_count = 0

                tratado, report_erro = fn_erro(quadro_bruto)
                bits_uteis.extend(tratado) 
                report.extend(report_erro)
                
                quadro_bruto = []
                if tratado == []:
                    return tratado, report

                continue
        

            if bloco == ESC:
                esc_count += 1
                i += 8 # pula o esc
                bloco = bits[i:i+8] # novo i, novo bloco
                i += len(bloco)
                quadro_bruto.extend(bloco)
                continue

            quadro_bruto.append(bits[i])
            i += 1

        report.append(f"Bits Uteis: {bits_to_str(bits_uteis)}")
        return slice_list(bits_uteis, 8), report

    def desenquadrar_insercao_bits(bits: list[int]):
        report = ["[Desenquadrando por inserção de bits/flag]"]
        bits_uteis = []
        i = 0
        quadro_bruto = []
        esc_count = 0
        count_1 = 0
        while i < len(bits):
            bloco = bits[i:i+8]

            # inicio ou fim de quadro
            if (bloco == FLAG ):
                i += len(bloco)
                # inicio do quadro
                if quadro_bruto == []:
                    continue

                # fim do quadro
                report.append(f"Q: {bits_to_str(quadro_bruto)}," 
                              f"{esc_count} escapes")
                esc_count = 0

                tratado, report_erro = fn_erro(quadro_bruto)
                bits_uteis.extend(tratado) 
                report.extend(report_erro)
                
                quadro_bruto = []
                if tratado == []:
                    return tratado, report

                continue
            

           # remove 0 após 5 1s seguidos
            if count_1 == 5:
                # O bit atual é o 0 de escape
                count_1 = 0
                esc_count += 1 
                i += 1  # pula o zero de escape
                continue # volta pro inicio do loop 

            if bits[i] == 1:
                count_1 += 1 
            else:
                count_1 = 0

            quadro_bruto.append(bits[i])
            i += 1

        report.append(f"Bits Uteis: {bits_to_str(bits_uteis)}")
        return slice_list(bits_uteis, 8), report
    

    desenquadradores = {
            "contagem de caracteres": desenquadrar_contagem,
            "inserção de bytes": desenquadrar_insercao_bytes,
            "inserção de bits": desenquadrar_insercao_bits
            }

    return desenquadradores.get(enquadramento, desenquadrar_contagem)
