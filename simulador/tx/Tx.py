import threading
from tx import CamadaFisica as tx_cf
from tx import CamadaEnlace as tx_ce
from Utils import *

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

    def enlace(self, msg, enquadramento, tratamento_erro, 
               tam_quadro, historico):
        # Transforma o texto em bitstream inicial
        bytes_msg = str_to_bytes(msg) 
        enq_limpo = str(enquadramento).lower()
        tratamento_limpo = str(tratamento_erro).lower() if tratamento_erro\
                else "nenhum"
        
        # enquadramento
        fn_erro_tx = tx_ce.obter_fn_erro(tratamento_limpo)
        fn_gera_quadros = tx_ce.obter_enquadrador(enq_limpo, fn_erro_tx)

        report = []
        bits_tx = []
        for bloco in slice_list(bytes_msg, tam_quadro):
            bits_quadro, report_quadro = fn_gera_quadros(bloco)
            bits_tx.extend(bits_quadro)
            report.extend(report_quadro)
            
        historico["report_tx"] = report 
        return bits_tx

    def camada_fisica(self, bitstream, modulacao, historico):
        amostras_p_bit = 100 
        
        if modulacao == "QPSK":
            amostras_p_bit = 50
        
        elif modulacao == "16-QAM":
            amostras_p_bit = 25

        nrz_puro = tx_cf.modularNRZ_Polar(bitstream,
                                              amostras_p_bit=amostras_p_bit,
                                              volt_low=0.) 
        sinal_tx = self.modular(modulacao, bitstream)
        
        historico["sinal_nrz_puro"] = nrz_puro.tolist()[:10000]
        return sinal_tx 

    def transmitir(self, config: dict, historico: dict):
        msg = config.get("mensagem", "Ola Mundo")
        modulacao = config.get("modulacao", "NRZ Polar")
        enquadramento = config.get("enquadramento", "Contagem de Caracteres")
        tratamento_erro = config.get("tratamento_erro") 
        tam_quadro = config.get("tam_quadro", 4)  
        bits = self.enlace(msg, enquadramento, tratamento_erro, 
                                tam_quadro, historico)

        sinal = self.camada_fisica(bits, modulacao, historico)
        
        if not self.shutdown_event.is_set():
            try:
                self.canal.put(sinal)
            except Exception as e:
                print(f"Erro no canal.put: {e}")
            
            self.canal.buffer.put(None)
    
