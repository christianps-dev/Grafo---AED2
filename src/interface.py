import sys
from math import sqrt

from PyQt5.QtGui import QClipboard, QPainter
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QVBoxLayout, QHBoxLayout, \
    QPushButton, QWidget, QLabel, QFileDialog
from PyQt6.QtCore import Qt

from PyQt6.QtGui import QPen, QBrush, QColor, QImage, QPainter

from djikstra_geometrico import carregar_mapa_poly, dijkstra, construir_grafo


class Janela(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trabalho de AED2 - Caminho Mínimo")
        self.setGeometry(100, 100, 1200, 800)

        self.origem_selecionada = None
        self.destino_selecionado = None
        self.estado = "Aguardando importação"
        self.caminho_resultado = []
        self.resultado = None
        self.copiado = QClipboard

        self.vertices = []
        self.arestas = []
        self.grafo = []
        self.mapa_vertices = {}

        self.init_ui()
        self.desenhar_grafo()

    def init_ui(self):
        self.scene = QGraphicsScene()
        self.view = VisualizadorMapa(self.scene, self)

        self.painel = QVBoxLayout()

        self.lbl_titulo = QLabel("<b>Algoritmo de Dijkstra</b>")
        self.lbl_status = QLabel(
            "Origem: Não selecionada<p>Destino: Não selecionado</p><p>Estado: Aguardando importação</p>")
        self.lbl_estatisticas = QLabel("<b>Estatísticas:</b><br>Tempo: -<br>Nós explorados: -<br>Custo: -")

        self.btn_importar = QPushButton("Importar Mapa (.poly)")
        self.btn_importar.clicked.connect(self.importar_mapa)

        self.btn_calcular = QPushButton("Calcular Menor Caminho")
        self.btn_calcular.clicked.connect(self.calcular_caminho)

        self.btn_copiar = QPushButton("Copiar Mapa (Ctrl+C)")
        self.btn_copiar.clicked.connect(self.copiar_imagem_grafo)

        self.btn_limpar = QPushButton("Desfazer Seleção")
        self.btn_limpar.clicked.connect(self.limpar_selecoes)

        self.painel.addWidget(self.lbl_titulo)
        self.painel.addWidget(self.btn_importar)
        self.painel.addWidget(self.lbl_status)
        self.painel.addWidget(self.btn_copiar)
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
            dir_caneta = dir_mao_unica if aresta.tipo == 1 else dir_mao_dupla
            self.scene.addLine(x1, y1, x2, y2, dir_caneta)

        if self.caminho_resultado and len(self.caminho_resultado) > 1:
            pen_rota = QPen(QColor("#e67e22"), 4, Qt.PenStyle.SolidLine)

            for i in range(len(self.caminho_resultado) - 1):
                u = self.caminho_resultado[i]
                v = self.caminho_resultado[i + 1]

                v_u = self.mapa_vertices.get(u)
                v_v = self.mapa_vertices.get(v)

                if v_u and v_v:
                    self.scene.addLine(v_u.x, v_u.y, v_v.x, v_v.y, pen_rota)

        for vertice in self.vertices:
            vertice_tipo = vertice_normal
            tamanho = 10

            if vertice.id == self.origem_selecionada:
                if vertice_tipo == vertice_origem:
                    vertice_tipo = vertice_normal
                else:
                    vertice_tipo = vertice_origem
                tamanho = 14

            elif vertice.id == self.destino_selecionado:
                vertice_tipo = vertice_destino
                tamanho = 14

            self.scene.addEllipse(vertice.x - tamanho / 2, vertice.y - tamanho / 2, tamanho, tamanho,
                                  QPen(Qt.GlobalColor.black), vertice_tipo)

    def tratar_clique_mapa(self, x, y):
        if not self.vertices:
            return

        proximidade_limite = 10.0
        vertice_proximo = None
        menor_distancia = float('inf')

        for vertice in self.vertices:
            dist = sqrt(((vertice.x - x) ** 2 + (vertice.y - y) ** 2))
            if dist < menor_distancia and dist < proximidade_limite:
                menor_distancia = dist
                vertice_proximo = vertice.id

        if vertice_proximo is not None:
            if self.origem_selecionada is None:
                self.origem_selecionada = vertice_proximo
                self.estado = "Selecione o destino"
            elif self.destino_selecionado is None and vertice_proximo != self.origem_selecionada:
                self.destino_selecionado = vertice_proximo
                self.estado = "Pronto para calcular"

            self.atualizar_interface_status()
            self.desenhar_grafo()

    def atualizar_interface_status(self):
        origem_txt = f"<font color='green'><b>{self.origem_selecionada}</b></font>" if self.origem_selecionada is not None else "Não selecionada"
        destino_txt = f"<font color='red'><b>{self.destino_selecionado}</b></font>" if self.destino_selecionado is not None else "Não selecionado"
        self.lbl_status.setText(f"Origem: {origem_txt}<p>Destino: {destino_txt}</p><p>Estado: {self.estado}</p>")

    def importar_mapa(self):
        caminho_arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Mapa", "", "Arquivos (*.poly)")
        if not caminho_arquivo:
            return

        print(f"Arquivo selecionado: {caminho_arquivo}")
        self.vertices, self.arestas = carregar_mapa_poly(caminho_arquivo)
        self.grafo = construir_grafo(self.vertices, self.arestas)

        self.mapa_vertices = {v.id: v for v in self.vertices}

        self.limpar_selecoes()
        self.estado = "Selecione a origem"
        self.atualizar_interface_status()

    def limpar_selecoes(self):
        self.origem_selecionada = None
        self.destino_selecionado = None
        self.estado = "Selecione a origem" if self.vertices else "Aguardando importação"
        self.caminho_resultado = []
        self.resultado = None
        self.lbl_estatisticas.setText("<b>Estatísticas:</b><br>Tempo: -<br>Nós explorados: -<br>Custo: -")
        self.atualizar_interface_status()
        self.desenhar_grafo()

    def calcular_caminho(self):
        if (self.origem_selecionada is not None) and (self.destino_selecionado is not None):
            self.resultado = dijkstra(self.grafo, self.vertices, self.origem_selecionada, self.destino_selecionado)

            if self.resultado is not None:
                tempo = self.resultado.get('tempo_ms', 0.0)
                nos = self.resultado.get('nos_explorados', 0)
                dist = self.resultado.get('distancia_metros', 0.0)

                estatistica_texto = (
                    f"<b>Estatísticas:</b>"
                    f"<br>Tempo: {tempo:.2f} ms"
                    f"<br>Nós explorados: {nos} nós"
                    f"<br>Custo: {dist:.2f} metros"
                )

                self.estado = "Concluído"
                self.lbl_estatisticas.setText(estatistica_texto)

                self.caminho_resultado = self.resultado.get("caminho_ids", [])
                self.desenhar_grafo()
            else:
                self.estado = "Não Encontrado"
                self.caminho_resultado = []
                self.desenhar_grafo()

            self.atualizar_interface_status()

    def copiar_imagem_grafo(self):
        # Pega o conteudo até as bordas
        area_cena = self.scene.itemsBoundingRect()

        if area_cena.isEmpty():
            self.estado = "Mapa vazio."
            self.atualizar_interface_status()
            return

        # Pega essa cena (tela) e transforma em uma image
        imagem = QImage(area_cena.size().toSize(), QImage.Format.Format_ARGB32)
        # Cobre o restante da imagem com a cor branco
        imagem.fill(Qt.GlobalColor.white)

        painter = QPainter(imagem)
        self.scene.render(painter, target=imagem.rect().toRectF(), source=area_cena)
        painter.end()

        # Copia essa imagem para a clipboard
        clipboard = QApplication.clipboard()
        clipboard.setImage(imagem)

        self.estado = "Imagem copiada para a área de transferência!"
        self.atualizar_interface_status()


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = Janela()
    janela.show()
    sys.exit(app.exec())