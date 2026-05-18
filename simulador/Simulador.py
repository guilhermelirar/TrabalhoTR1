import numpy as np
import matplotlib.pyplot as plt

from CamadaFisica import modularManchester, modularNRZ_Polar
from Utils import plot


def main():
    info = [1, 1, 0, 1]

    # Testando modulações implementadas
    nrz = modularNRZ_Polar(info)
    manchester = modularManchester(info)
    plot([(nrz, "NRZ"), 
          (manchester, "Manchester")])
    
    plt.show()
    

if __name__ == "__main__":
    main()
