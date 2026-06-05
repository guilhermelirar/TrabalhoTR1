# simulador/Utils.py
import matplotlib.pyplot as plt

from Modelos import Sinal

"""
Funções utilitárias ex: interface
"""

def plot(sinais: list[tuple[Sinal, str]]):
    """
    Exibe imagem com gráficos dos sinais passados como argumento, usando
    plt.subplot.

    Args:
        sinais: lista de tuplas de objeto Sinal e string com título do subplot
    """
    
    plt.figure(figsize=(10, 8))
    nrows = len(sinais)

    for i, (sinal, titulo) in enumerate(sinais):
        # Gráfico e formatação
        plt.subplot(nrows, 1, i+1)
        
        if sinal.is_digital:
            plt.step(sinal.tempo, sinal.amostras)
        else:
            plt.plot(sinal.tempo, sinal.amostras)
        
        plt.grid(True, color='0.9', linestyle='--')
        
        # 0 até o final do sinal a passos de amostras_p_bit
        for x in range(0, len(sinal.amostras) + 1, sinal.amostras_p_bit):
            plt.axvline(x, color='r', linestyle=':')

        # destacar eixo x 
        plt.axhline(0, color='black', linewidth=.8, alpha=.4)

        # Texto
        plt.ylabel("Tensão (V)")
        plt.xlabel("Amostras")
        plt.title(titulo)

    plt.tight_layout()

