import threading
from rx import CamadaFisica as rx_cf
from rx import CamadaEnlace as rx_ce
from Utils import *

class Rx:
    def __init__(self, canal, shutdown_event: threading.Event, 
                 callback_fim) -> None:
        self.canal = canal
        self.shutdown_event = shutdown_event
        self.callback_fim = callback_fim

    def demodular(self, modulacao, amostras: list[float]):
        """
        Seleciona função da camada de enlace de acordo com a 
        configuração
        """
        demoduladores = {
                "NRZ Polar": rx_cf.demodularNRZ_Polar,
                "Manchester": rx_cf.demodularManchester,
                "Bipolar": rx_cf.demodularBipolar,
                "ASK": rx_cf.demodularASK,
                "FSK": rx_cf.demodularFSK,
                "BPSK": rx_cf.demodularBPSK,
                "QPSK": rx_cf.demodularQPSK,
                "16-QAM": rx_cf.demodular16QAM
                }

        demodulador_fn = demoduladores.get(modulacao, None)
        # Fallback
        if demodulador_fn is None:
            demodulador_fn = rx_cf.demodularNRZ_Polar

        return demodulador_fn(amostras)

    def receber(self, config: dict, historico: dict): 
        modulacao = config.get("modulacao", "NRZ Polar")
        enquadramento = config.get("enquadramento", 
                                   "Contagem de Caracteres").lower()
        tratamento_erro = config.get("tratamento_erro", "nenhum").lower()
        
        amostras = []
        bitstream = []

        # --- CAMADA FÍSICA ---
        # recebe os dados do canal
        while not self.shutdown_event.is_set():
            try:
                janela_amostras = self.canal.buffer.get(timeout=.1)
                if janela_amostras is None:
                    break
                amostras.extend(janela_amostras)
                bitstream.extend(self.demodular(modulacao, janela_amostras))
            except:
                continue

        # para interface
        historico["sinal_canal"] = amostras[:10000]

        # --- CAMADA DE ENLACE ---
        fn_desenquadrar = rx_ce.desenquadrador(enquadramento,
                                                    4, tratamento_erro) 
        bytes_rx, report_rx = fn_desenquadrar(bitstream) 

        historico["report_rx"] = report_rx
        historico["report_enquadramento_rx"] = report_rx 

        try:           
            msg_final = bytes_to_ascii(bytes_rx)
        except Exception as _:
            msg_final = "<nada recebido>"

        historico["mensagem_final"] = msg_final
        self.callback_fim(historico)
