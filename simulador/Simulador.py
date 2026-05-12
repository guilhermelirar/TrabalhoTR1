import numpy as np
import matplotlib.pyplot as plt

from CamadaFisica import modularNRZ_Polar

def plot(sinal: np.ndarray, amostras_p_bit: int) -> None:
    plt.plot(np.arange(len(sinal)), sinal)
    plt.grid(True)

    i = 0
    while i * amostras_p_bit <= len(sinal):
        plt.axvline(i * amostras_p_bit, color='r', linestyle=':')
        i += 1

    plt.ylabel("Tensão (V)")
    plt.xlabel("Amostras")
    plt.show()


def main():
    info = [1, 1, 0, 1]
    plot(modularNRZ_Polar(info), 100)

    pass
    

if __name__ == "__main__":
    main()
