# simulador/modelos/Config.py
from dataclasses import dataclass

@dataclass
class Config:
    tamanho_max_quadro: int | None = None
    tipo_enquadramento: str | None = None
    tamanho_edc: int | None = None
    tipo_tratamento_erro: str | None = None
    tipo_mod_digital: str | None = None
    tipo_mod_analógica: str | None = None
    ruido_media: float | None = None 
    ruido_desvio: float | None = None

