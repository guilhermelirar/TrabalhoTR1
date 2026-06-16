import threading
from concurrent.futures import ThreadPoolExecutor
from gi.repository import GLib
import numpy as np

from Interface import JanelaSimulador  
from tx.Tx import Tx
from tx import CamadaFisica as tx_cf
from modelos.Canal import Canal

def tx_worker(canal: Canal, msg: str, modulação: str, 
              shutdown_event: threading.Event, historico: dict):
    bitstream_exemplo = [1, 0, 1, 1, 0, 0, 1, 0] 
    
    objeto_sinal = tx_cf.modularASK(bitstream_exemplo)
    
    historico["sinal_tx"] = objeto_sinal.amostras.tolist()[:1000]

    if not shutdown_event.is_set():
        try:
            canal.put(objeto_sinal)
        except Exception as e:
            print(f"Erro no canal.put: {e}")
        
        canal.buffer.put(None)

def rx_worker(canal: Canal, shutdown_event: threading.Event, historico: dict, callback_fim):
    niveis = []

    while not shutdown_event.is_set():
        try:
            data = canal.buffer.get(timeout=0.1)
            
            if data is None:
                break
                
            if isinstance(data, np.ndarray):
                niveis.extend(data.tolist())
            else:
                niveis.extend(data)
        except:
            continue

    historico["sinal_canal"] = niveis[:1000]
    historico["mensagem_final"] = "Mensagem Decodificada com Sucesso"

    GLib.idle_add(callback_fim, historico)

class Simulador:
    def __init__(self) -> None:
        self.canal = Canal()
        self.pool = ThreadPoolExecutor(max_workers=2)
        self.shutdown_event = threading.Event()
        
        self.historico = {
            "sinal_tx": [],
            "sinal_canal": [],
            "mensagem_final": ""
        }

        self.win = JanelaSimulador()
        self.win.set_iniciar_sim(self.iniciar_sim)
        
        self.tx = Tx(self.canal, self.shutdown_event)
        self.win.start()

    def iniciar_sim(self, config: dict):
        print("Simulação iniciada com as configurações:", config)

        self.shutdown_event.set()
        
        while not self.canal.empty():
            self.canal.get()

        self.shutdown_event.clear()

        self.canal.desvio_ruido = config.get("ruido_sigma", 0.5)
        self.canal.media_ruido = config.get("ruido_media", 0.0)

        self.historico["sinal_tx"] = []
        self.historico["sinal_canal"] = []
        self.historico["mensagem_final"] = ""

        self.pool.submit(
            self.tx.transmitir, 
            config.get("mensagem", "Ola Mundo"), 
            config.get("modulacao", "ASK"),
            self.historico
        )
        
        self.pool.submit(
            rx_worker, 
            self.canal, 
            self.shutdown_event, 
            self.historico, 
            self.win.finalizar_simulacao
        )

if __name__ == "__main__":
    Simulador()
