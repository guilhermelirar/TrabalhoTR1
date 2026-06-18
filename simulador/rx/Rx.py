# simulador/rx/Rx.py
from logging import shutdown
import threading
from rx import CamadaFisica as rx_cf
from gi.repository import GLib

class Rx:
    def __init__(self, canal, shutdown_event: threading.Event, 
                 callback_fim) -> None:
        self.canal = canal
        self.shutdown_event = shutdown_event
        self.callback_fim = callback_fim

    def demodular(self, modulacao, amostras: list[float]):
        demoduladores = {
                "NRZ Polar": rx_cf.demodularNRZ_Polar,
                "Manchester": rx_cf.demodularManchester,
                "Bipolar": rx_cf.demodularBipolar,
                #"ASK": tx_cf.modularASK,
                #"FSK": tx_cf.modularFSK,
                #"16-QAM": tx_cf.modular16QAM
                }

        demodulador_fn = demoduladores.get(modulacao, None)
        if demodulador_fn is None:
            demodulador_fn = rx_cf.demodularNRZ_Polar
        #    if modulacao == "BPSK":
        #        return tx_cf.modularPSK(amostras, bits_por_simbolo=1)
        #    else:
        #        return tx_cf.modularPSK(amostras, bits_por_simbolo=2)

        return demodulador_fn(amostras)

    def receber(self, modulacao: str, historico: dict): 
        # --- CAMADA FÍSICA ---
        
        amostras = []
        bitstream = []

        while not self.shutdown_event.is_set():
            try:
                janela_amostras = self.canal.buffer.get(timeout=.1)

                if janela_amostras is None:
                    break

                amostras.extend(janela_amostras)
                bitstream.extend(self.demodular(modulacao, janela_amostras))

            except:
                continue

        historico["sinal_canal"] = amostras[:1000]
        historico["mensagem_final"] = bitstream 

        GLib.idle_add(self.callback_fim, historico)

        # --- CAMADA DE ENLACE ---

