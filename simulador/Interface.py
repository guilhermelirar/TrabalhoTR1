# simulador/Interface.py
import threading

import gi 
import time 

from modelos.Canal import Canal
from modelos.Config import Config

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

class JanelaSimulador(Gtk.Window):

    def __init__(self, canal: Canal, tx: threading.Thread, 
                 rx: threading.Thread):
        super().__init__(title="Simulador de Camada Física e Enlace")
        self.set_default_size(400, 300)
        self.set_border_width(10)

        self.canal = canal
        self.rx = rx
        self.tx = tx 

        self._setup_main_box()

        self.sim_conf = Config()

    def _setup_main_box(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(main_box)

        lbl_txt = Gtk.Label(label="Mensagem para transmitir:")
        lbl_txt.set_halign(Gtk.Align.START)
        main_box.pack_start(lbl_txt, False, False, 0)

        self.campo_msg = Gtk.Entry()
        self.campo_msg.set_text("Ola Mundo")
        main_box.pack_start(self.campo_msg, False, False, 0)

        self.botao_sim = Gtk.Button(label="Iniciar simulação")
        self.botao_sim.connect("clicked", self.iniciar_simulacao) 
        main_box.pack_start(self.botao_sim, False, False, 0)

        main_box.pack_start(
                Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
                False, 
                False, 
                10
                )

        opcoes_menus = {
            "Tipo de Enquadramento": ["Contagem de Caracteres", 
                                  "Inserção de Bytes"],
            "Detecção/Correção de Erros": ["Bit de Paridade",
                                           "CRC-32"],
            "Modulação": ["NRZ Polar", "Manchester", 
                        "Bipolar", "ASK", "FSK", "BPSK",
                        "QPSK", "16-QAM"]
        }


        for titulo, opcoes in opcoes_menus.items():
            lbl = Gtk.Label(label=titulo, halign=Gtk.Align.START) 
            combo = Gtk.ComboBoxText()
            
            for opcao in opcoes:
                combo.append_text(opcao)
                
            combo.set_active(0)
            
            main_box.pack_start(lbl, False, False, 0)
            main_box.pack_start(combo, False, False, 0)

        campos_numericos = {
            "Tamanho Máximo do Quadro": (1024, 64, 4096, 64),
            "Desvio Padrão do Ruído (σ)": (0.5, 0.0, 5.0, 0.1)
        }

        for titulo, (inicial, minimo, 
                     maximo, passo) in campos_numericos.items():
            lbl = Gtk.Label(label=titulo, halign=Gtk.Align.START)
            main_box.pack_start(lbl, False, False, 0)
            
            ajuste = Gtk.Adjustment(value=inicial, 
                                    lower=minimo, 
                                    upper=maximo, 
                                    step_increment=passo)

            seletor_num = Gtk.SpinButton(adjustment=ajuste, 
                                         digits=1 
                                         if type(inicial) == float 
                                         else 0)

            main_box.pack_start(seletor_num, False, False, 0)

    def iniciar_simulacao(self, botao):
        print(f"Simulação iniciada {botao.get_label()}")

    def start(self):
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()

