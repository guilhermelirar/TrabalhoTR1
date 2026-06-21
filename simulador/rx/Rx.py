from logging import shutdown
import threading
from rx import CamadaFisica as rx_cf
from rx import CamadaEnlace as rx_ce  # <--- IMPORTADO AQUI
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
                "ASK": rx_cf.demodularASK,
                "FSK": rx_cf.demodularFSK,
                "BPSK": rx_cf.demodularBPSK,
                "QPSK": rx_cf.demodularQPSK
                }

        demodulador_fn = demoduladores.get(modulacao, None)
        if demodulador_fn is None:
            demodulador_fn = rx_cf.demodularNRZ_Polar

        return demodulador_fn(amostras)

    def receber(self, config: dict, historico: dict): 
        # --- CAMADA FÍSICA ---
        modulacao = config.get("modulacao", "NRZ Polar")
        enquadramento = config.get("enquadramento", "Contagem de Caracteres")

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

        historico["sinal_canal"] = amostras[:10000]


        # --- CAMADA DE ENLACE (COMPLETADO) ---
        report_rx = {}
        bits_uteis = []

        if "Contagem" in enquadramento: 
            bits_uteis, report_rx = rx_ce.desenquadrar_contagem(bitstream)
            
        elif "Bytes" in enquadramento:
            bits_uteis, report_rx = rx_ce.desenquadrar_bytes_flag(bitstream)

        # Guarda o relatório do receptor no histórico para a interface ler
        historico["report_enquadramento_rx"] = report_rx 

        # --- CAMADA DE APLICAÇÃO (CONVERSÃO FINAL) ---
        # Converte os bits limpos/desenquadrados de volta para string legível
        try:
            # Agrupa os bits de 8 em 8, transforma em caracteres e junta tudo
            bytes_list = [bits_uteis[i:i+8] 
                          for i in range(0, len(bits_uteis), 8)]
            mensagem_final = "".join(chr(int("".join(map(str, b)), 2)) 
                                     for b in bytes_list if len(b) == 8)
            historico["mensagem_final"] = mensagem_final
        except Exception as e:
            print(f"Erro ao decodificar a mensagem final: {e}")
            historico["mensagem_final"] = "Erro de Decodificação"

        # Notifica o fim da simulação passando o dicionário atualizado
        self.callback_fim(historico)
