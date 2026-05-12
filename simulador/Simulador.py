import numpy as np
import matplotlib.pyplot as plt

from CamadaFisica import modularManchester, modularNRZ_Polar

def subplot(sinal: np.ndarray, amostras_p_bit: int, 
            index: tuple[int, int, int]) -> None:

    plt.subplot(index[0], index[1], index[2])

    plt.step(np.arange(len(sinal)), sinal)
    plt.grid(True, color='0.9', linestyle='--')

    i = 0
    while i * amostras_p_bit <= len(sinal):
        plt.axvline(i * amostras_p_bit, color='r', linestyle=':')
        i += 1

    plt.ylabel("Tensão (V)")
    plt.xlabel("Amostras")


def main():
    info = [1, 1, 0, 1]
    plt.figure(figsize=(10, 8))
    subplot(modularNRZ_Polar(info), 100, index=(2,1,1))
    subplot(modularManchester(info), 100, index=(2,1,2))
    plt.tight_layout()
    plt.show()
    

if __name__ == "__main__":
    main()
