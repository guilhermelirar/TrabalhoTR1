# simulador/Simulador.py
import matplotlib.pyplot as plt
import threading

from Interface import JanelaSimulador  
from tx import CamadaFisica as tx_cf
from Utils import plot
from modelos.Sinal import Sinal
from modelos.Canal import Canal


def rx(canal: Canal):
    niveis = []

    while True:
        data = canal.get()

        if data is None:
            break
        niveis.extend(data)

def tx(canal: Canal, msg):
    sinal = tx_cf.modularASK(msg)
    canal.put(sinal)
    canal.buffer.put(None)
    pass

def main():
    canal = Canal()

    rx_t = threading.Thread(target=rx, args=(canal, ))
    tx_t = threading.Thread(target=tx, args=(canal, [1,1,0,1]))

    janela = JanelaSimulador(canal, tx_t, rx_t)
    janela.start()

if __name__ == "__main__": 
    main()
