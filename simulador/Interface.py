# simulador/Interface.py
import threading
import gi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg \
        import FigureCanvasGTK3Agg as FigureCanvas

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from modelos.Canal import Canal
from modelos.Config import Config


class JanelaSimulador(Gtk.Window):

    def __init__(self):
        super().__init__(title="Simulador de Camada Física e Enlace")
        self.set_default_size(400, 300)
        self.set_border_width(10)

        self.combos = {}
        self.seletores = {}

        self._setup_main_box()

        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Sinal Elétrico no Canal")
        self.ax.set_xlabel("Amostras")
        self.ax.set_ylabel("Tensão (V)")
        self.ax.grid(True)

        self.linha_sinal, = self.ax.plot([], [], label="Sinal", color="blue")
        self.ax.legend()

        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(400, 300)
        main_box = self.get_child()
        main_box.pack_start(self.canvas, True, True, 0)
        # -----------------------------------------------------

    def _setup_caixa_mensagem(self, box):
        lbl_txt = Gtk.Label(label="Mensagem para transmitir:")
        lbl_txt.set_halign(Gtk.Align.START)
        box.pack_start(lbl_txt, False, False, 0)

        self.campo_msg = Gtk.Entry()
        self.campo_msg.set_text("Ola Mundo")
        box.pack_start(self.campo_msg, False, False, 0)

    def _setup_combobox(self, box):
        opcoes_menus = {
            "Tipo de Enquadramento": [
                "Contagem de Caracteres",
                "Inserção de Bytes",
            ],
            "Detecção/Correção de Erros": ["Bit de Paridade", "CRC-32"],
            "Modulação": [
                "NRZ Polar",
                "Manchester",
                "Bipolar",
                "ASK",
                "FSK",
                "BPSK",
                "QPSK",
                "16-QAM",
            ],
        }

        for titulo, opcoes in opcoes_menus.items():
            lbl = Gtk.Label(label=titulo, halign=Gtk.Align.START)

            # salvar o combotext na classe
            combo = Gtk.ComboBoxText()
            self.combos[titulo] = combo

            for opcao in opcoes:
                combo.append_text(opcao)

            combo.set_active(0)

            box.pack_start(lbl, False, False, 0)
            box.pack_start(combo, False, False, 0)

    def _setup_spinbutton(self, box):
        campos_numericos = {
            "Tamanho Máximo do Quadro": (1024, 64, 4096, 64),
            "Desvio Padrão do Ruído (σ)": (0.5, 0.0, 5.0, 0.1),
            "Média do Ruído": (0.0, 0.0, 2.5, 0.1),
        }

        caixa_ruido_lado_a_lado = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=12
        )

        for titulo, (inicial, minimo, 
                     maximo, passo) in campos_numericos.items():

            bloco_propriedade = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL, spacing=2
            )

            lbl = Gtk.Label(label=titulo, halign=Gtk.Align.START)
            bloco_propriedade.pack_start(lbl, False, False, 0)

            ajuste = Gtk.Adjustment(
                value=inicial,
                lower=minimo,
                upper=maximo,
                step_increment=passo,
            )

            is_float = isinstance(inicial, float)
            seletor_num = Gtk.SpinButton(
                adjustment=ajuste, digits=1 if is_float else 0
            )

            # Salva a referência do SpinButton no dicionário da classe
            self.seletores[titulo] = seletor_num
            bloco_propriedade.pack_start(seletor_num, False, False, 0)

            if "Ruído" in titulo:
                caixa_ruido_lado_a_lado.pack_start(
                    bloco_propriedade, True, True, 0
                )
            else:
                box.pack_start(bloco_propriedade, False, False, 0)

        box.pack_start(caixa_ruido_lado_a_lado, False, False, 0)

    def _setup_main_box(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(main_box)
        
        self._setup_caixa_mensagem(main_box)
        self._setup_combobox(main_box)
        self._setup_spinbutton(main_box)

        main_box.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
            False,
            False,
            10,
        )

        self.botao_sim = Gtk.Button(label="Iniciar simulação")
        self.botao_sim.connect("clicked", self.iniciar_simulacao) 
        main_box.pack_start(self.botao_sim, False, False, 0)

    def set_iniciar_sim(self, funcao_callback):
        """Guarda a função iniciar_sim do simulador aqui dentro"""
        self.callback_simulador = funcao_callback

    def iniciar_simulacao(self, botao):
        config = {
            "mensagem": self.campo_msg.get_text(),

            "enquadramento": self.combos["Tipo de Enquadramento"]\
                    .get_active_text(),

            "modulacao": self.combos["Modulação"]\
                    .get_active_text(),

            "tam_quadro": int(self.seletores["Tamanho Máximo do Quadro"]\
                    .get_value()),

            "ruido_sigma": self.seletores["Desvio Padrão do Ruído (σ)"]\
                    .get_value(),

            "ruido_media": self.seletores["Média do Ruído"].get_value(),
        }
        
        if hasattr(self, 'callback_simulador'):
            self.callback_simulador(config)

    def finalizar_simulacao(self, historico: dict):
        """Este método recebe o histórico do Simulador e atualiza a tela"""
        dados_grafico = historico.get("sinal_canal", [])
        msg_recebida = historico.get("mensagem_final", "")

        x = range(len(dados_grafico))
        self.linha_sinal.set_data(x, dados_grafico)

        if dados_grafico:
            self.ax.set_xlim(0, len(dados_grafico))
            self.ax.set_ylim(min(dados_grafico) - 
                             0.5, max(dados_grafico) + 0.5)
        
        self.canvas.draw()

        print(f"Gráfico atualizado com {len(dados_grafico)} amostras.")
        print(f"Interface recebeu o texto final: {msg_recebida}")
        
        return False

    def start(self):
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()
