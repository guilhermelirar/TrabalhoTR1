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
    report = []

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
        
        report.append(
                f"[{tamanho_quadro_bits // 8}] {bits_para_hexa(quadro_util)}")
        
        i = final_quadro

    return bitstream_out, report


def desenquadrar_bytes_flag(bitstream: list[int]):
    # Define as mesmas referências do TX
    FLAG = str_to_bitstream("B")
    ESC = str_to_bitstream("\\")

    report = {
        "FLAG": bits_para_hexa(FLAG), 
        "ESC": bits_para_hexa(ESC), 
        "BITS": []
    }
    bitstream_out = []
    i = 0
    bitstream_len = len(bitstream)

    while i < bitstream_len:
        # Verifica se o byte atual é uma FLAG de início de quadro
        byte_atual = bitstream[i:i+8]
        
        if byte_atual == FLAG:
            report["BITS"].append("[FLAG]")
            i += 8
            
            # Processa o conteúdo do quadro até achar a FLAG de fechamento
            quadro_recuperado = []
            while i < bitstream_len:
                byte_interno = bitstream[i:i+8]
                
                if byte_interno == FLAG:
                    # Achou o fim do quadro!
                    report["BITS"].append(bits_para_hexa(quadro_recuperado))
                    report["BITS"].append("[FLAG]")
                    i += 8
                    break
                elif byte_interno == ESC:
                    # Se for ESC, o próximo byte é dado puro (ignora o ESC)
                    report["BITS"].append("[ESC]")
                    i += 8
                    byte_dado = bitstream[i:i+8]
                    quadro_recuperado.extend(byte_dado)
                    bitstream_out.extend(byte_dado)
                    i += 8
                else:
                    # Dado normal
                    quadro_recuperado.extend(byte_interno)
                    bitstream_out.extend(byte_interno)
                    i += 8
        else:
            # Caso haja lixo fora de quadros
            i += 8

    return bitstream_out, report
