import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, QFileDialog

class Janela(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trabalho de AED2")
        self.setGeometry(100, 100, 1200, 800)

        self.origem_selecionada = None
        self.destino_selecionado = None
        
        self.init_ui()

    def init_ui(self):
        self.scene = QGraphicsScene()

        self.painel = QVBoxLayout()
        
        self.lbl_titulo = QLabel("Algoritmo de Dijkstra")
        

        self.lbl_status = QLabel("Origem: Não selecionada\nDestino: Não selecionado")
        
        
        self.lbl_estatisticas = QLabel("<b>Estatísticas:</b>\nTempo: -\nNós explorados: -\nCusto: -")

        self.btn_importar = QPushButton("Importar Mapa (.osm)")

        self.btn_calcular = QPushButton("Calcular Caminho")

        self.btn_limpar = QPushButton("Desfazer Seleção")


        self.painel.addWidget(self.lbl_titulo)
        self.painel.addWidget(self.btn_importar)
        self.painel.addWidget(self.lbl_status)
        self.painel.addWidget(self.btn_calcular)
        self.painel.addWidget(self.btn_limpar)
        self.painel.addWidget(self.lbl_estatisticas)
        self.painel.addStretch()

        layout_horizontal = QHBoxLayout()
        
        widget_lateral = QWidget()
        widget_lateral.setLayout(self.painel)
        layout_horizontal.addWidget(widget_lateral, stretch=2)

        conteudo_central = QWidget()
        conteudo_central.setLayout(layout_horizontal)
        self.setCentralWidget(conteudo_central)


app = QApplication(sys.argv)
janela = Janela()
janela.show()
sys.exit(app.exec())