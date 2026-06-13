# simulador/Interface.py
import threading

import gi 
import time 

from modelos.Canal import Canal

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

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(main_box)

    def start(self):
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()

