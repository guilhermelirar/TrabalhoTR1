# simulador/rx/Tx.py
import threading
from tx import CamadaFisica as tx_cf
from tx import CamadaEnlace as tx_ce

class Tx:
    def __init__(self, canal, shutdown_event: threading.Event) -> None:
        self.canal = canal
        self.shutdown_event = shutdown_event

    def modular(self, modulacao, bitstream):
        moduladores = {
                "NRZ Polar": tx_cf.modularNRZ_Polar,
                "Manchester": tx_cf.modularManchester,
                "Bipolar": tx_cf.modularBipolar,
                "ASK": tx_cf.modularASK,
                "FSK": tx_cf.modularFSK,
                "16-QAM": tx_cf.modular16QAM
                }

        modulador_fn = moduladores.get(modulacao, None)
        if modulador_fn is None:
            if modulacao == "BPSK":
                return tx_cf.modularPSK(bitstream, bits_por_simbolo=1)
            else:
                return tx_cf.modularPSK(bitstream, 
                                        bits_por_simbolo=2)

        return modulador_fn(bitstream)

    def enlace(self, msg, enquadramento, historico):
        bits = tx_ce.str_to_bitstream(msg)
        
        report = {}
        if "Contagem" in enquadramento:
            bits, report = tx_ce.enquadrar_contagem(bits)
        
        elif "Bytes" in enquadramento:
            bits, report = tx_ce.enquadrar_bytes_flag(bits)

        historico["report_enquadramento_tx"] = report
        return bits

    def camada_fisica(self, bitstream, modulacao, historico):
        amostras_p_bit = 100 
        
        if modulacao == "QPSK":
            amostras_p_bit = 50
        
        elif modulacao == "16-QAM":
            amostras_p_bit = 25

        obj_nrz_puro = tx_cf.modularNRZ_Polar(bitstream,
                                              amostras_p_bit=amostras_p_bit,
                                              volt_low=0.) 
        objeto_sinal = self.modular(modulacao, bitstream)
        
        historico["sinal_nrz_puro"] = obj_nrz_puro.amostras.tolist()[:10000]
        return objeto_sinal

    def transmitir(self, config: dict, historico: dict):
        msg = config.get("mensagem", "Ola Mundo")
        modulacao = config.get("modulacao", "NRZ Polar")
        enquadramento = config.get("enquadramento", 
                                   "Contagem de Caracteres")

        bitstream = self.enlace(msg, enquadramento, historico)
        sinal = self.camada_fisica(bitstream, modulacao, historico)
        
        if not self.shutdown_event.is_set():
            try:
                self.canal.put(sinal)
            except Exception as e:
                print(f"Erro no canal.put: {e}")
            
            self.canal.buffer.put(None)   

