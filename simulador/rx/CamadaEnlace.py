from Utils import *

# === DESENQUADRAMENTO === #
"""""
def desenquadrar_contagem(bitstream: list[int]):
    bitstream_out = []
    i = 0
    bitstream_len = len(bitstream)
    report_l = []

    while i < bitstream_len:
        # Se não há 1 byte
        if i + 8 > bitstream_len:
            break
            
        # lê byte 
        bits_contagem = bitstream[i:i+8]
        tamanho_quadro_bits = bitstream_to_int(bits_contagem)
        i += 8
        
        # 2. Extrai o conteúdo útil com base no tamanho lido
        final_quadro = i + tamanho_quadro_bits
        quadro_util = bitstream[i:final_quadro]
        
        # Salva os bits originais de volta
        bitstream_out.extend(quadro_util)
        
        report_l.append(
                f"[{tamanho_quadro_bits // 8}] {bits_para_hexa(quadro_util)}")
        
        i = final_quadro

    report = "\n".join(report_l)
    return bitstream_out, report



def desenquadrar_bytes_flag(bitstream: list[int]):
    FLAG = str_to_bitstream("B")
    ESC = str_to_bitstream("\\")

    bitstream_out = []
    i = 0
    bitstream_len = len(bitstream)
    report_l = []

    while i < bitstream_len:
        byte_atual = bitstream[i:i+8]
        
        if byte_atual == FLAG:
            report_str = "[FLAG] "
            i += 8
            
            quadro_recuperado = []
            while i < bitstream_len:
                byte_interno = bitstream[i:i+8]
                
                if byte_interno == FLAG:
                    # fim do quadro
                    report_str += bits_para_hexa(quadro_recuperado) + " [FLAG]"
                    i += 8
                    break
                elif byte_interno == ESC:
                    # se ESC, registra, pega próximo byte como útil
                    report_str += "[ESC] "
                    i += 8
                    byte_dado = bitstream[i:i+8]
                    quadro_recuperado.extend(byte_dado)
                    bitstream_out.extend(byte_dado)
                    i += 8
                else:
                    # dado útil normal
                    quadro_recuperado.extend(byte_interno)
                    bitstream_out.extend(byte_interno)
                    i += 8
            

            report_l.append(report_str)
        else:
            i += 8

    report = "\n".join(report_l)
    return bitstream_out, report

def desenquadrar_bits_inseridos(bitstream: list[int]):
    FLAG = [0, 1, 1, 1, 1, 1, 1, 0]
    
    bitstream_out = []
    i = 0
    bitstream_len = len(bitstream)
    report_l = []

    while i < bitstream_len:
        if bitstream[i:i+8] == FLAG:
            report_str = "[FLAG] "
            i += 8 
            
            quadro_recuperado = []
            contador_1 = 0
            
            while i < bitstream_len:
                if bitstream[i:i+8] == FLAG:
                    report_str += bits_para_hexa(quadro_recuperado) + " [FLAG]"
                    i += 8
                    break
                
                # Processamento bit a bit com remoção do bit stuffing
                bit = bitstream[i]
                quadro_recuperado.append(bit)
                bitstream_out.append(bit)
                i += 1
                
                if bit == 1:
                    contador_1 += 1
                    if contador_1 == 5:
                        if i < bitstream_len and bitstream[i] == 0:
                            i += 1 # avança o indice sem salvar o 0 atual 

                        contador_1 = 0
                else:
                    contador_1 = 0

            report_l.append(report_str)
        else:
            i += 1

    report = "\n".join(report_l)
    return bitstream_out, report

# === TRATAMENTO DE RROS === 
def verificar_paridade(bits):
    STEP = 8 # bits onde a paridade deve ser inserida
    bits_o = []

    report_l = []
    report_str_count = 0
    report_str = ""
    for i in range(0, len(bits), STEP + 1):
        fim = min(len(bits), i + STEP + 1)
        janela = bits[i:fim]
        n_1s = sum(bit for bit in janela if bit == 1)
        
        p = n_1s % 2 # bit de paridade

        byte_report = ""
        if p == 0:
            byte_report = f"[OK] {bits_para_hexa(janela[:STEP])}"
            bits_o.extend(janela[:STEP])

        else:
            byte_report = f"[ERRO] {bits_para_hexa(janela[:STEP])}"

        if report_str_count < 4:
            report_str_count += 1 
            report_str += byte_report 
        else: 
            report_l.append(report_str)
            report_str = byte_report
            report_str_count = 1
        
    report = "\n".join(report_l) 

    return bits_o, report


def verificar_checksum(bits):
    STEP = 8
    
    if len(bits) < STEP:
        return [], "[ERRO] Fluxo de bits muito curto para conter Checksum"

    # byte de checksum é isolado
    bits_dados = bits[:-STEP]
    bits_checksum_recebido = bits[-STEP:]
    
    report_l = ["(Checksum)"]
    report_str_count = 0
    report_str = ""
    
    soma_total = 0

    for i in range(0, len(bits_dados), STEP):
        janela = bits_dados[i:(min(len(bits_dados), i + STEP))]
        
        valor_byte = int("".join(map(str, janela)), 2)
        soma_total += valor_byte

        if report_str_count == 4:
            report_l.append(report_str)
            report_str = f"{bits_para_hexa(janela)} "
            report_str_count = 1
        else:
            report_str_count += 1
            report_str += f"{bits_para_hexa(janela)} "

    checksum_calculado = (~(soma_total % 256)) & 0xFF
    checksum_recebido_val = int("".join(map(str, bits_checksum_recebido)), 2)

    if checksum_calculado == checksum_recebido_val:
        report_str += f"[OK CS: {bits_para_hexa(bits_checksum_recebido)}]"
        report_l.append(report_str)
        bits_o = bits_dados  
    else:
        report_str += f"[ERRO CS: REC {bits_para_hexa(bits_checksum_recebido)}"\
                f"!= EXP {checksum_calculado:02X}h]"

        report_l.append(report_str)
        bits_o = []  

    report = "\n".join(report_l) 

    return bits_o, report


def verificar_crc32(bits):
    if len(bits) < 32:
        return [], "[ERRO] Fluxo muito curto para conter CRC-32"
        
    bits_dados = bits[:-32]
    bits_crc_recebido = bits[-32:]
    
    report_l = ["Verificação de CRC-32: "]
    STEP = 8
    report_str = ""
    report_str_count = 0
    
    # Mostra os bytes de dados no relatório
    for i in range(0, len(bits_dados), STEP):
        janela = bits_dados[i:min(len(bits_dados), i + STEP)]
        if report_str_count == 4:
            report_l.append(report_str)
            report_str = f"{bits_para_hexa(janela)} "
            report_str_count = 1
        else:
            report_str_count += 1
            report_str += f"{bits_para_hexa(janela)} "
            
    crc = 0xFFFFFFFF
    for i in range(0, len(bits_dados), 8):
        janela = bits_dados[i:i+8]
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
    
    crc_recebido_val = int("".join(map(str, bits_crc_recebido)), 2)
    
    if crc_final == crc_recebido_val:
        report_str += f"[OK CRC: {bits_para_hexa(bits_crc_recebido)}]"
        report_l.append(report_str)
        bits_o = bits_dados
    else:
        report_str += f"[ERRO CRC: REC {bits_para_hexa(bits_crc_recebido)} != EXP {crc_final:08X}h]"
        report_l.append(report_str)
        bits_o = [] 
        
    report = "\n".join(report_l)
    return bits_o, report

def verificar_hamming(bits):
    bits_o = []
    report_l = ["Verificação/Correção de Hamming (7,4): "]
    report_str = ""
    report_str_count = 0
    erros_corrigidos = 0
    
    # ler em passos de 7 bits
    for i in range(0, len(bits), 7):
        bloco = bits[i:i+7]
        if len(bloco) < 7:
            break  
        
        # bits de paridade
        p1, p2, d1, p3, d2, d3, d4 = bloco[0], bloco[1],\
                bloco[2], bloco[3], bloco[4], bloco[5], bloco[6]
        
        s1 = p1 ^ d1 ^ d2 ^ d4
        s2 = p2 ^ d1 ^ d3 ^ d4
        s3 = p3 ^ d2 ^ d3 ^ d4
       
        # posição do erro se houver
        sindrome_pos = (s3 << 2) | (s2 << 1) | s1
        
        bloco_corrigido = bloco.copy()
        status = "[OK]"
        
        if sindrome_pos != 0:
            # erro de 1 bit encontrado
            status = f"[CORR {sindrome_pos}]"
            bloco_corrigido[sindrome_pos - 1] ^= 1
            erros_corrigidos += 1
            
            p1, p2, d1, p3, d2, d3, d4 = bloco_corrigido[0],\
                    bloco_corrigido[1], bloco_corrigido[2],\
                    bloco_corrigido[3], bloco_corrigido[4],\
                    bloco_corrigido[5], bloco_corrigido[6]
            
        dados_puros = [d1, d2, d3, d4]
        bits_o.extend(dados_puros)
        
        if report_str_count == 4:
            report_l.append(report_str)
            report_str = f"{status} {bits_para_hexa(dados_puros)} "
            report_str_count = 1
        else:
            report_str_count += 1
            report_str += f"{status} {bits_para_hexa(dados_puros)} "
            
    report_l.append(report_str)
    report = "\n".join(report_l)
    return bits_o, report
"""""
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

    report.append(f"ERR {bits[:-1]}|{bits[len(bits)-1]} resulta em ímpar")
    report.append("RETRANSMISSÃO NECESSÁRIA")
    return [], report        

def obter_fn_erro(tipo_tratamento: str):
    detectadores = {
            "bit de paridade": verifica_paridade,
            "hamming": corrigir_hamming
            }
    return detectadores.get(tipo_tratamento.lower(), verifica_paridade) 

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
