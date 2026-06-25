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

    def enlace(self, msg, enquadramento, detec_erro, corr_erro, historico):
        # Transforma o texto em bitstream inicial
        bits = tx_ce.str_to_bitstream(msg)
        
        enq_limpo = str(enquadramento).lower()
        detec_limpo = str(detec_erro).lower() if detec_erro else "nenhum"
        corr_limpo = str(corr_erro).lower() if corr_erro else "nenhum"
        
        # --- 1. PASSO: ENQUADRAMENTO ---
        report_enq = "ERRO: Nenhum enquadramento foi selecionado corretamente."
        if "contagem" in enq_limpo:
            bits, report_enq = tx_ce.enquadrar_contagem(bits)
        elif "bytes" in enq_limpo:
            bits, report_enq = tx_ce.enquadrar_bytes_flag(bits)
        elif "bits" in enq_limpo:
            bits, report_enq = tx_ce.enquadrar_bits_flag(bits)
            
        historico["report_enquadramento_tx"] = report_enq

        # --- 2. PASSO: TRATAMENTO DE ERROS (DETECÇÃO + CORREÇÃO) ---
        reports_erro_lista = []
        
        if "hamming" in corr_limpo:
            if "paridade" in detec_limpo:
                detec_limpo = "crc"  
        if "hamming" in corr_limpo:
            bits, rep_corr = tx_ce.aplicar_hamming(bits)
            reports_erro_lista.append(rep_corr)
            
        if "paridade" in detec_limpo and "hamming" not in corr_limpo:
            bits, rep_detec = tx_ce.aplicar_paridade(bits)
            reports_erro_lista.append(rep_detec)
        elif "checksum" in detec_limpo:
            bits, rep_detec = tx_ce.aplicar_checksum(bits)
            reports_erro_lista.append(rep_detec)
        elif "crc" in detec_limpo or "32" in detec_limpo:
            bits, rep_detec = tx_ce.aplicar_crc32(bits)
            reports_erro_lista.append(rep_detec)
            
        if not reports_erro_lista:
            reports_erro_lista.append(
                    "Nenhum mecanismo de controle de erro aplicado.")
            
        historico["report_erro_tx"] = "\n".join(reports_erro_lista)
        return bits

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
        detec_erro = config.get("detec_erro") 
        corr_erro = config.get("corr_erro", "Nenhum")  
        bitstream = self.enlace(msg, enquadramento, 
                                detec_erro, corr_erro, historico)
        sinal = self.camada_fisica(bitstream, modulacao, historico)
        
        if not self.shutdown_event.is_set():
            try:
                self.canal.put(sinal)
            except Exception as e:
                print(f"Erro no canal.put: {e}")
            
            self.canal.buffer.put(None)
