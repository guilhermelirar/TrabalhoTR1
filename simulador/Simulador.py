# simulador/Simulador.py
import matplotlib.pyplot as plt

from CamadaFisica import *
from Utils import plot


def main():
    info = [1, 1, 0, 1]

    # Testando modulações implementadas
    nrz = modularNRZ_Polar(info)
    manchester = modularManchester(info)
    bipolar = modularBipolar(info)
    ask = modularASK(info)
    bpsk = modularPSK(info)
    qpsk = modularPSK(info, bits_por_simbolo=2)

    plot([
        (nrz, "NRZ"), 
        (manchester, "Manchester"),
        (bipolar, "Bipolar"),
        (ask, "Amplitude Shift Keying"),
        (bpsk, "Binary Phase Shift Keying"),
        (qpsk, "Quadrature Phase Shift Keying")
          ])
    
    plt.show()
    

if __name__ == "__main__":
    main()
