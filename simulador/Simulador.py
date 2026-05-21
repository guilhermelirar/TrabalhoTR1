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

    plot([
        (nrz, "NRZ"), 
        (manchester, "Manchester"),
        (bipolar, "Bipolar"),
        (ask, "Amplitude Shift Keying")
          ])
    
    plt.show()
    

if __name__ == "__main__":
    main()
