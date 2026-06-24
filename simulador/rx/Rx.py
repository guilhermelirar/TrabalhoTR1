from logging import shutdown
import threading
from rx import CamadaFisica as rx_cf
from rx import CamadaEnlace as rx_ce  # <--- IMPORTADO AQUI

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
                "QPSK": rx_cf.demodularQPSK,
                "16-QAM": rx_cf.demodular16QAM
                }

        demodulador_fn = demoduladores.get(modulacao, None)
        if demodulador_fn is None:
            demodulador_fn = rx_cf.demodularNRZ_Polar

        return demodulador_fn(amostras)

    def receber(self, config: dict, historico: dict): 
        # --- CAMADA FÍSICA ---
        modulacao = config.get("modulacao", "NRZ Polar")
        enquadramento = config.get("enquadramento", "Contagem de Caracteres")
        detec = config.get("detec_erro", "Nenhum")
        corr = config.get("corr_erro", "Nenhum")
        
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

        # --- CAMADA DE ENLACE ---
        report_rx = "Desenquadramento não ocorreu"
        reports_erro_rx = []
        
        detec_limpo = str(detec).lower()
        corr_limpo = str(corr).lower()
        enq_limpo = str(enquadramento).lower()
        
        bits_fase_erro = bitstream.copy()

        # REGRA: Força o mesmo fallback do TX no receptor para as strings baterem
        if "hamming" in corr_limpo and "paridade" in detec_limpo:
            detec_limpo = "crc"

        # =====================================================================
        # PASSO 1: TRATAMENTO DE ERROS (Inverso exato do TX)
        # =====================================================================
        
        # A) Verifica primeiro a Detecção Externa (CRC ou Checksum)
        if "crc" in detec_limpo or "32" in detec_limpo:
            bits_fase_erro, rep_detec = rx_ce.verificar_crc32(bits_fase_erro)
            reports_erro_rx.append(rep_detec)
        elif "checksum" in detec_limpo:
            bits_fase_erro, rep_detec = rx_ce.verificar_checksum(bits_fase_erro)
            reports_erro_rx.append(rep_detec)
        elif "paridade" in detec_limpo and "hamming" not in corr_limpo:
            bits_fase_erro, rep_detec = rx_ce.verificar_paridade(bits_fase_erro)
            reports_erro_rx.append(rep_detec)

        # B) Passa os bits de volta pela Correção (Hamming)
        if "hamming" in corr_limpo and len(bits_fase_erro) > 0:
            bits_fase_erro, rep_corr = rx_ce.verificar_hamming(bits_fase_erro)
            reports_erro_rx.append(rep_corr)

        if not reports_erro_rx:
            reports_erro_rx.append("Nenhuma detecção ou correção foi processada.")

        bits_limpos = bits_fase_erro

        # =====================================================================
        # PASSO 2: DESENQUADRAMENTO (Em cima dos bits decodificados/corrigidos)
        # =====================================================================
        if len(bits_limpos) > 0:
            if "contagem" in enq_limpo: 
                bits_uteis, report_rx = rx_ce.desenquadrar_contagem(bits_limpos)
            elif "bytes" in enq_limpo:
                bits_uteis, report_rx = rx_ce.desenquadrar_bytes_flag(bits_limpos)
            elif "bits" in enq_limpo:
                bits_uteis, report_rx = rx_ce.desenquadrar_bits_inseridos(bits_limpos)
            else:
                bits_uteis = bits_limpos
        else:
            bits_uteis = []
            report_rx = "[ERRO RX] Dados descartados ou zerados no controle de erros."

        # Atualiza o histórico para exibição na tela
        historico["report_erro_rx"] = "\n".join(reports_erro_rx)
        historico["report_enquadramento_rx"] = report_rx 

        # --- CONVERSÃO FINAL EM STRING ---
        try:
            bytes_list = [bits_uteis[i:i+8] for i in range(0, len(bits_uteis), 8)]
            mensagem_final = "".join(chr(int("".join(map(str, b)), 2)) 
                                     for b in bytes_list if len(b) == 8)
            historico["mensagem_final"] = mensagem_final
        except Exception as e:
            print(f"Erro ao decodificar a mensagem final: {e}")
            historico["mensagem_final"] = "Erro de Decodificação"

        # Notifica o fim da simulação passando o dicionário atualizado
        self.callback_fim(historico)
