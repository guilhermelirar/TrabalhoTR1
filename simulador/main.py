from Utils import *
from tx import CamadaEnlace as TxCe
from rx import CamadaEnlace as RxCe

msg = "ola mundo"

msg_bytes = str_to_bytes(msg) 

paridade_e_hamming_tx = TxCe.obter_fn_erro("paridade", False)
enquadrar = TxCe.obter_enquadrador("contagem", paridade_e_hamming_tx)
desenquadrador = RxCe.desenquadrador("contagem", 
                                          max_bytes_quadro = 4,
                                          tipo_deteccao = "paridade", 
                                          usar_hammnig = False)



print("Msg em bytes: ", msg_bytes)
bits_tx = []
for carga_util in slice_list(msg_bytes, 4):
    bs, report = enquadrar(carga_util)
    print("-------------------------------")
    for line in report:
        print(line)
    print("-------------------------------")
    bits_tx.extend(bs)

print("Será transmitido: ", bits_to_str(bits_tx))

print("RX")
bytes_rx, report = desenquadrador(bits_tx)
print(bytes_rx)
for line in report:
    print(line)
print("Msg que chegou: ", bytes_to_ascii(bytes_rx))
