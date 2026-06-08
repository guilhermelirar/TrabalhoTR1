# simulador/Simulador.py
import matplotlib.pyplot as plt
import threading

from tx.CamadaFisica import *
from Utils import plot
from modelos.Sinal import Sinal


def rx():
    pass

def tx():
    pass

def main():
    threads = (
            threading.Thread(target=rx()),
            threading.Thread(target=tx())
            )

    for t in threads:
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__": 
    main()
