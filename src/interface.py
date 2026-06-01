import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter
from djikstra_geometrico import carregar_mapa_poly, construir_grafo

class Janela(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trabalho de AED2")
        self.setGeometry(100, 100, 1200, 800)

        self.origem_selecionada = None
        self.destino_selecionado = None
        
        arq_poly = "Grafo---AED2\out\mapaUFG.poly"
        self.vertices, self.arestas = carregar_mapa_poly(arq_poly)
        

        self.init_ui()
        self.desenhar_grafo()

    def init_ui(self):
        self.scene = QGraphicsScene()
        self.view = VisualizadorMapa(self.scene, self)

        self.painel = QVBoxLayout()
        
        self.lbl_titulo = QLabel("Algoritmo de Dijkstra")
        

        self.lbl_status = QLabel("Origem: Não selecionada\nDestino: Não selecionado")
        
        
        self.lbl_estatisticas = QLabel("<b>Estatísticas:</b>\nTempo: -\nNós explorados: -\nCusto: -")

        self.btn_importar = QPushButton("Importar Mapa (.txt)")
        # self.btn_importar.clicked.connect(self.importar_mapa)

        self.btn_calcular = QPushButton("Calcular Menor Caminho")
        # self.btn_calcular.clicked.connect(self.simular_calculo_rota)

        self.btn_limpar = QPushButton("Desfazer Seleção")
        # self.btn_limpar.clicked.connect(self.limpar_selecoes)


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

        layout_horizontal.addWidget(self.view, stretch=4)
        conteudo_central = QWidget()
        conteudo_central.setLayout(layout_horizontal)
        self.setCentralWidget(conteudo_central)
    
    def desenhar_grafo(self):
        self.scene.clear()

        dir_mao_dupla = QPen(QColor("#2980b9"), 2)
        dir_mao_unica = QPen(QColor("#16a085"), 2) 
        
        vertice_normal = QBrush(QColor("#e5e5e6"))
        vertice_origem = QBrush(QColor("#11ff00")) 
        vertice_destino = QBrush(QColor("#ff0000")) 

        for aresta in self.arestas:
            x1 = self.vertices[aresta.orig].x
            y1 = self.vertices[aresta.orig].y
            x2 = self.vertices[aresta.dest].x 
            y2 = self.vertices[aresta.dest].y
            dir = dir_mao_unica if aresta.tipo else dir_mao_dupla
            self.scene.addLine(x1, y1, x2, y2, dir)

        for vertice in self.vertices:
            vertice_tipo = vertice_normal
            tamanho = 10
            
            if vertice.id == self.origem_selecionada:
                vertice_tipo = vertice_origem
                tamanho = 14
            elif vertice.id == self.destino_selecionado:
                vertice_tipo = vertice_destino
                tamanho = 14
            
            self.scene.addEllipse(vertice.x - tamanho/2, vertice.y - tamanho/2, tamanho, tamanho, QPen(Qt.GlobalColor.black), vertice_tipo)




class VisualizadorMapa(QGraphicsView):
    def __init__(self, cena, pai):
        super().__init__(cena)
        self.pai = pai
        
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)  
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def wheelEvent(self, event):
        fator_zoom = 1.20 if event.angleDelta().y() > 0 else 0.80
        self.scale(fator_zoom, fator_zoom)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            pos_cena = self.mapToScene(event.pos())
            self.pai.tratar_clique_mapa(pos_cena.x(), pos_cena.y())
        else:
            super().mousePressEvent(event)




app = QApplication(sys.argv)
janela = Janela()
janela.show()
sys.exit(app.exec())