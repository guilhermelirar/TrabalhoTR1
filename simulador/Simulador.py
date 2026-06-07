# simulador/Simulador.py
import matplotlib.pyplot as plt

from tx.CamadaFisica import *
from Utils import plot
from modelos.Sinal import Sinal


def testa():
    info = [1, 1, 0, 1]

    #bitstreams de teste
    bitstream_teste_qam = [
    0, 0, 0, 0,  # Menor amplitude possível (Centro) -> Pico em ~2.35V
    0, 0, 1, 0,  # Amplitude média-baixa
    0, 0, 0, 1,  # Amplitude média-alta
    0, 0, 1, 1   # Maior amplitude possível (Borda)  -> Pico em 5.0V
    ]

    # Testando modulações implementadas
    nrz = modularNRZ_Polar(info)
    manchester = modularManchester(info)
    bipolar = modularBipolar(info)
    ask = modularASK(info)
    fsk = modularFSK(info)
    bpsk = modularPSK(info)
    qpsk = modularPSK(info, bits_por_simbolo=2)
    qam = modular16QAM(bitstream_teste_qam)

    nrz_plot = (nrz, "NRZ") 
    plots = [
        (manchester, "Manchester"),
        (bipolar, "Bipolar"),
        (ask, "Amplitude Shift Keying"),
        (fsk, "Frequency Shift Keying"),
        (bpsk, "Binary Phase Shift Keying"),
        (qpsk, "Quadrature Phase Shift Keying"),
        (qam, "16-QAM")
          ]

    for p in plots:
        plot([nrz_plot, p])
        plt.show()
    

def testa_ruido():
    from modelos.Canal import Canal
    canal = Canal()
    info = [1, 1, 0, 0, 1, 0, 0, 1]
    #sinal = modularNRZ_Polar(info)
    #sinal = modularFSK(info)
    sinal = modularPSK(info, bits_por_simbolo=2)
    #sinal = modular16QAM(info)

    canal.put(sinal)
    amostras_ruidoso: list[float] = []
    while not canal.empty():
        amostras_ruidoso.extend(canal.get())

    sinal_ruidoso = Sinal(np.array(amostras_ruidoso), sinal.amostras_p_bit)

    plot([(sinal, "Sinal Original 11001001"),
         (sinal_ruidoso, "Sinal Ruidoso")])

    plt.show()

    pass

def main():
    # testa()
    testa_ruido()
    pass

if __name__ == "__main__":
    main()
