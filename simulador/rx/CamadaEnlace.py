def bitstream_to_int(bits: list[int]) -> int:
    """Função auxiliar para converter uma 
    lista de bits de volta para inteiro"""
    bin_str = "".join(map(str, bits))
    return int(bin_str, 2)

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

# === DESENQUADRAMENTO === #

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
