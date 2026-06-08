# simulador/Simulador.py
import matplotlib.pyplot as plt
import threading

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

    threads = (
            threading.Thread(target=rx, args=(canal, )),
            threading.Thread(target=tx, args=(canal, [1,1,0,1]))
            )

    for t in threads:
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__": 
    main()
