# simulador/Utils.py
from itertools import chain

def concat(lista: list) -> list:
    return list(chain.from_iterable(lista))

def bits_to_str(bits: list[int]):
    """ Converte uma lista de bits em string """
    str_list = [str(bit) for bit in bits]
    return "".join(str_list)

def bits_to_int(bits: list[int]) -> int:
    """ Converte uma lista de bits em um número inteiro"""
    return int("".join(map(str, bits)), 2)

def int_to_byte(c: int) -> list[int]:
    """ Converte um caractere ascii (ord(str)) em uma lista de bits """
    return [int(i) for i in format(c, '08b')]

def str_to_bytes(string: str) -> list[list[int]]:
    """ Converte uma string em uma lista de bytes"""
    return [int_to_byte(ord(c)) for c in string]

def slice_list(l, slice_size: int):
    """ Fatia uma lista em uma lista de elementos de até slice_size """
    return [l[i:i+slice_size] for i in range(0, len(l), slice_size)]

def bytes_to_ascii(l_bytes: list[list[int]]):
    """ Retorna string ascii dado por lista de bytes """
    return "".join([chr(bits_to_int(byte)) for byte in l_bytes])
