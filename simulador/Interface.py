# simulador/Interface.py
import gi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg \
        import FigureCanvasGTK3Agg as FigureCanvas
from numpy import zeros_like

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

class JanelaSimulador(Gtk.Window):

    def __init__(self):
        super().__init__(title="Simulador de Camada Física e Enlace")
        self.set_default_size(400, 300)
        self.set_border_width(10)

        self.combos = {}
        self.seletores = {}

        self.dados_grafico = ([], [])

        self._setup_main_box()
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
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(main_box)

        # ---- área de configuração ---- #
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self._setup_caixa_mensagem(left_box)
        self._setup_combobox(left_box)
        self._setup_spinbutton(left_box)

        self.botao_sim = Gtk.Button(label="Iniciar simulação")
        self.botao_sim.connect("clicked", self.iniciar_simulacao) 
        left_box.pack_start(self.botao_sim, False, False, 0)

        # ---- Caixa para os botões de navegação do gráfico ---- #
        caixa_navegacao = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, 
                                  spacing=6)
        
        btn_esquerda = Gtk.Button(label="<= Voltar")
        btn_direita = Gtk.Button(label="Avançar =>")
        
        btn_esquerda.connect("clicked", self.mover_janela_grafico)
        btn_direita.connect("clicked", self.mover_janela_grafico)
        
        caixa_navegacao.pack_start(btn_esquerda, True, True, 0)
        caixa_navegacao.pack_start(btn_direita, True, True, 0)
        
        left_box.pack_start(caixa_navegacao, False, False, 0)

        # ---- separador visual ---- #
        left_box.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
            False,
            False,
            10,
        )

        scroll_win = Gtk.ScrolledWindow()
        # ---- aba de relatório do TX-RX ---- #
        report = Gtk.TextView()
        report.set_editable(False)
        scroll_win.add(report)

        left_box.pack_start(scroll_win, True, True, 0)
        self.report_txview = report

        # ---- Canvas ----  #
        self.fig, (self.ax_nrz, self.ax_canal) =\
                plt.subplots(nrows=2, ncols=1, sharex=True)

        # ---- Gráfico 1: sinal nrz puro ---- #
        self.ax_nrz.set_title("Sinal NRZ puro")
        self.ax_nrz.set_xlabel("Amostras")
        self.ax_nrz.set_ylabel("Tensão (V)")
        self.ax_nrz.grid(True)

        self.linha_nrz, = self.ax_nrz.plot([], [], 
                                           label="NRZ Puro", color="green")
        self.ax_nrz.legend()

        # ---- Gráfico 2: sinal no canal (com ruído) ---- #
        self.ax_canal.set_title("Sinal transmitido")
        self.ax_canal.set_xlabel("Amostras")
        self.ax_canal.set_ylabel("Tensão (V)")
        self.ax_canal.grid(True)

        self.linha_canal, = self.ax_canal.plot([], [], 
                                           label="Sinal", color="blue")
        self.ax_canal.legend()

        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(400, 300)

        # --- colocando na main_box ---- #
        main_box.pack_start(left_box, False, False, 0) # não expande
        main_box.pack_start(self.canvas, True, True, 0)

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

    def mover_janela_grafico(self, botao):
        if not hasattr(self, 'offset_atual'):
            return
            
        PASSO = 500  
        direcao = botao.get_label()
        
        if "=>" in direcao:
            novo_offset = self.offset_atual + PASSO
        else:
            novo_offset = max(0, self.offset_atual - PASSO)             
        self.desenhar_grafico(offset=novo_offset)

    def desenhar_grafico(self, offset=0):
        nrz_referencia = self.dados_grafico[0]
        amostras_canal = self.dados_grafico[1]
       
        # amostras vistas por janela de gráfico
        TAMANHO_JANELA = 500  
        
        self.offset_atual = offset 

        if amostras_canal:
            x_canal = range(len(amostras_canal))
            self.linha_canal.set_data(x_canal, amostras_canal)
            
            # Aplica o zoom/slice visual no eixo X usando o offset
            self.ax_canal.set_xlim(offset, offset + TAMANHO_JANELA)
            self.ax_canal.set_ylim(min(amostras_canal) - 0.5, 
                                   max(amostras_canal) + 0.5)

        if nrz_referencia:
            x_nrz = range(len(nrz_referencia))
            self.linha_nrz.set_data(x_nrz, nrz_referencia)
            
            self.ax_nrz.set_xlim(offset, offset + TAMANHO_JANELA)
            self.ax_nrz.set_ylim(min(nrz_referencia) - 0.5, 
                                 max(nrz_referencia) + 0.5)
        
        self.canvas.draw()

    def finalizar_simulacao(self, historico: dict):
        # 1. Gráficos
        self.dados_grafico = (historico.get("sinal_nrz_puro", []), 
                              historico.get("sinal_canal", []))
        self.desenhar_grafico(offset=0)
        
        # 2. Montagem do painel centralizando as strings prontas
        msg_final = historico.get("mensagem_final", "[Sem dados]")
        
        linhas = [
            "=========================================",
            f"  MENSAGEM RECEBIDA: \"{msg_final}\"",
            "=========================================\n",
            "--- SEÇÃO DE TRANSMISSÃO (TX) ---",
            historico.get("report_enquadramento_tx", 
                          "Sem dados de enquadramento."),
            historico.get("report_erro_tx", 
                          "Sem dados de controle de erro."),
            "\n" + "-"*40 + "\n",
            "--- SEÇÃO DE RECEPÇÃO (RX) ---",
            historico.get("report_erro_rx", 
                          "Sem dados de controle de erro rx."),
            historico.get("report_enquadramento_rx", 
                          "Sem dados de desenquadramento.")
        ]
        
        # Junta todas as partes com uma quebra de linha
        texto_relatorio = "\n".join(linhas)

        # 3. Exibe na tela
        buffer = self.report_txview.get_buffer()
        buffer.set_text(texto_relatorio)
        
        return False        

    def start(self):
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        Gtk.main()
