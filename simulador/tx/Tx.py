# modelos/Tx.py
import threading
from tx import CamadaFisica as tx_cf

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
                }

        modulador_fn = moduladores.get(modulacao, None)
        if modulador_fn is None:
            if modulacao == "BPSK":
                return tx_cf.modularPSK(bitstream, bits_por_simbolo=1)
            else:
                return tx_cf.modularPSK(bitstream, bits_por_simbolo=2)

        return modulador_fn(bitstream)

    def transmitir(self, msg: str, modulacao: str, historico: dict):
        # --- CAMADA DE ENLACE ---
        
        # --- CAMADA FÍSICA ---
        bitstream_exemplo = [1, 0, 1, 1, 0, 0, 1, 0] # TMP
        
        objeto_sinal = self.modular(modulacao, bitstream_exemplo)
        
        historico["sinal_tx"] = objeto_sinal.amostras.tolist()[:1000]

        if not self.shutdown_event.is_set():
            try:
                self.canal.put(objeto_sinal)
            except Exception as e:
                print(f"Erro no canal.put: {e}")
            
            self.canal.buffer.put(None)    
