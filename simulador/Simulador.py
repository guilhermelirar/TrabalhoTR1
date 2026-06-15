import matplotlib.pyplot as plt
import threading

from Interface import JanelaSimulador  
from tx import CamadaFisica as tx_cf
from Utils import plot
from modelos.Sinal import Sinal
from modelos.Canal import Canal

from concurrent.futures import ThreadPoolExecutor
from gi.repository import GLib

def tx(canal: Canal, msg, shutdown_event: threading.Event, historico: dict):
    bitstream_exemplo = [1, 0, 1, 1, 0, 0, 1, 0] 
    
    objeto_sinal = tx_cf.modularASK(bitstream_exemplo)
    
    amostras_puras = objeto_sinal.amostras.tolist() 
    historico["sinal_tx"] = amostras_puras[:200]

    if not shutdown_event.is_set():
        canal.put(objeto_sinal)
        canal.buffer.put(None) # Sinaliza o fim da transmissão

def rx(canal: Canal, shutdown_event: threading.Event, historico: dict, callback_fim):
    niveis = []

    while not shutdown_event.is_set():
        try:
            data = canal.buffer.get(timeout=0.1)
            
            if data is None:
                break
                
            niveis.extend(data)
        except:
            continue

    historico["sinal_canal"] = niveis[:1000]
    historico["mensagem_final"] = "Mensagem Decodificada com Sucesso"

    # Avisa a interface gráfica para atualizar a tela e desenhar o gráfico
    from gi.repository import GLib
    GLib.idle_add(callback_fim)

def main():
    canal = Canal()
    pool = ThreadPoolExecutor(max_workers=2)

    janela = JanelaSimulador(canal, tx, rx, pool)
    janela.start()

if __name__ == "__main__": 
    main()
