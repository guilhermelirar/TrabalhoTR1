import threading
from concurrent.futures import ThreadPoolExecutor
from Interface import JanelaSimulador  
from rx.Rx import Rx
from tx.Tx import Tx
from modelos.Canal import Canal

class Simulador:
    """
    Classe que instancia Tx e Rx, e executa a simulação 
    a partir de threads
    """
    def __init__(self) -> None:
        self.canal = Canal()
        self.pool = ThreadPoolExecutor(max_workers=2)
        self.shutdown_event = threading.Event()
        
        self.historico = {
            "sinal_canal": [],
            "mensagem_final": ""
        }

        self.win = JanelaSimulador()
        self.win.set_iniciar_sim(self.iniciar_sim)
        
        self.tx = Tx(self.canal, self.shutdown_event)

        self.rx = Rx(self.canal, self.shutdown_event, 
                     self.win.finalizar_simulacao)
       
        self.win.start()

    def finalizar_sim(self, historico: dict):
        self.historico = historico
        
        from gi.repository import GLib
        GLib.idle_add(self.win.finalizar_simulacao, historico)

    def iniciar_sim(self, config: dict):
        print("Simulação iniciada com as configurações:", config)

        self.shutdown_event.set()
        
        while not self.canal.empty():
            self.canal.get()

        self.shutdown_event.clear()

        self.canal.desvio_ruido = config.get("ruido_sigma", 0.5)
        self.canal.media_ruido = config.get("ruido_media", 0.0)

        self.historico["sinal_canal"] = []
        self.historico["mensagem_final"] = ""

        self.pool.submit(
            self.tx.transmitir, 
            config,
            self.historico
        )
        
        self.pool.submit(
            self.rx.receber,
            config,
            self.historico
        )

if __name__ == "__main__":
    Simulador()
