import sys
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
                             QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel,
                             QFileDialog, QComboBox, QCheckBox)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QImage, QPainter, QFont

from djikstra_geometrico import carregar_mapa_poly, dijkstra, construir_grafo, Vertice, Aresta
from config import FATOR_ESCALA


class Janela(QMainWindow):
    def __init__(self):
        super().__init__()
        self.btn_limpar = None
        self.btn_copiar = None
        self.btn_calcular = None
        self.btn_importar = None
        self.lbl_status = None
        self.chk_numerar = None
        self.lbl_modo = None
        self.chk_pesos = None
        self.lbl_estatisticas = None
        self.lbl_titulo = None
        self.view = None
        self.painel = None
        self.scene = None
        self.combo_modo = None
        self.setWindowTitle("Trabalho de AED2 - Sistema de Navegação")
        self.setGeometry(100, 100, 1200, 800)

        self.origem_selecionada = None
        self.destino_selecionado = None
        self.vertice_temp = None
        self.estado = "Aguardando importação"
        self.caminho_resultado = []
        self.resultado = None

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

        self.chk_numerar = QCheckBox("Mostrar IDs dos Vértices")
        self.chk_numerar.stateChanged.connect(self.desenhar_grafo)

        self.chk_pesos = QCheckBox("Mostrar Pesos das Arestas")
        self.chk_pesos.stateChanged.connect(self.desenhar_grafo)

        self.lbl_modo = QLabel("<b>Modo de Interação:</b>")
        self.combo_modo = QComboBox()
        self.combo_modo.addItems([
            "Buscar Caminho (Origem/Destino)",
            "Adicionar Vértice",
            "Remover Vértice",
            "Adicionar Aresta (Mão Única)",
            "Adicionar Aresta (Mão Dupla)",
            "Remover Aresta"
        ])
        self.combo_modo.currentIndexChanged.connect(self.resetar_selecao_temporaria)

        self.btn_importar = QPushButton("Importar Mapa (.poly)")
        self.btn_importar.clicked.connect(self.importar_mapa)

        self.btn_calcular = QPushButton("Calcular Menor Caminho")
        self.btn_calcular.clicked.connect(self.calcular_caminho)

        self.btn_copiar = QPushButton("Copiar Grafo (Ctrl+C)")
        self.btn_copiar.clicked.connect(self.copiar_imagem_grafo)

        self.btn_limpar = QPushButton("Desfazer Seleção")
        self.btn_limpar.clicked.connect(self.limpar_selecoes)

        self.painel.addWidget(self.lbl_titulo)
        self.painel.addWidget(self.btn_importar)
        self.painel.addWidget(self.btn_copiar)
        self.painel.addWidget(QLabel("<hr>"))

        self.painel.addWidget(self.chk_numerar)
        self.painel.addWidget(self.chk_pesos)
        self.painel.addWidget(QLabel("<hr>"))

        self.painel.addWidget(self.lbl_modo)
        self.painel.addWidget(self.combo_modo)
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

    def resetar_selecao_temporaria(self):
        self.vertice_temp = None
        self.estado = f"Modo: {self.combo_modo.currentText()}"
        self.atualizar_interface_status()

    def desenhar_grafo(self):
        self.scene.clear()

        dir_mao_dupla = QPen(QColor("#2980b9"), 2)
        dir_mao_unica = QPen(QColor("#16a085"), 2)
        vertice_normal = QBrush(QColor("#e5e5e6"))
        vertice_origem = QBrush(QColor("#11ff00"))
        vertice_destino = QBrush(QColor("#ff0000"))
        vertice_selecionado_temp = QBrush(QColor("#f39c12"))
        fonte_rotulos = QFont("Arial", 8)

        mostrar_numeros = self.chk_numerar.isChecked()
        mostrar_pesos = self.chk_pesos.isChecked()

        for aresta in self.arestas:
            x1 = self.vertices[aresta.orig].x
            y1 = self.vertices[aresta.orig].y
            x2 = self.vertices[aresta.dest].x
            y2 = self.vertices[aresta.dest].y
            dir_caneta = dir_mao_unica if aresta.tipo == 1 else dir_mao_dupla
            self.scene.addLine(x1, y1, x2, y2, dir_caneta)

            if mostrar_pesos:
                dist_pixels = math.hypot(x2 - x1, y2 - y1)
                dist_metros = dist_pixels * FATOR_ESCALA
                texto_peso = self.scene.addText(f"{dist_metros:.1f}m", fonte_rotulos)
                texto_peso.setDefaultTextColor(QColor("#8e44ad"))
                texto_peso.setPos((x1 + x2) / 2, (y1 + y2) / 2)

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
                vertice_tipo = vertice_origem
                tamanho = 14
            elif vertice.id == self.destino_selecionado:
                vertice_tipo = vertice_destino
                tamanho = 14
            elif self.vertice_temp and vertice.id == self.vertice_temp.id:
                vertice_tipo = vertice_selecionado_temp
                tamanho = 14

            self.scene.addEllipse(vertice.x - tamanho / 2, vertice.y - tamanho / 2, tamanho, tamanho,
                                  QPen(Qt.GlobalColor.black), vertice_tipo)

            if mostrar_numeros:
                texto_id = self.scene.addText(str(vertice.id), fonte_rotulos)
                texto_id.setDefaultTextColor(QColor("#2c3e50"))
                texto_id.setPos(vertice.x + 5, vertice.y - 15)

    def tratar_clique_mapa(self, x, y):
        modo = self.combo_modo.currentText()

        # Encontrar vértice mais próximo ao clique
        limite = 15.0
        v_prox = None
        menor_dist = float('inf')
        for v in self.vertices:
            dist = math.hypot(v.x - x, v.y - y)
            if dist < menor_dist and dist < limite:
                menor_dist = dist
                v_prox = v

        if modo == "Buscar Caminho (Origem/Destino)":
            if v_prox is not None:
                if self.origem_selecionada is None:
                    self.origem_selecionada = v_prox.id
                    self.estado = "Selecione o destino"
                elif self.destino_selecionado is None and v_prox.id != self.origem_selecionada:
                    self.destino_selecionado = v_prox.id
                    self.estado = "Pronto para calcular"

        elif modo == "Adicionar Vértice":
            if v_prox is None:
                novo_id = len(self.vertices)
                self.vertices.append(Vertice(novo_id, x, y))
                self.estado = f"Vertice adicionado: {novo_id} ."
                self.atualizar_estrutura_grafo()

        elif modo == "Remover Vértice":
            if v_prox is not None:
                self.vertices = [v for v in self.vertices if v.id != v_prox.id]
                self.refatorar_indices()
                self.estado = f"Vertice removido: {v_prox.id} ."
                if self.origem_selecionada == v_prox.id: self.origem_selecionada = None
                if self.destino_selecionado == v_prox.id: self.destino_selecionado = None
                self.atualizar_estrutura_grafo()

        elif "Adicionar Aresta" in modo:
            if v_prox is not None:
                if self.vertice_temp is None:
                    self.vertice_temp = v_prox
                    self.estado = f"Vertice {v_prox.id}) selecionado. Clique no proximo vertice"
                else:
                    if self.vertice_temp.id != v_prox.id:
                        tipo = 1 if "Mão Única" in modo else 2
                        self.arestas.append(Aresta(self.vertice_temp.id, v_prox.id, tipo))
                        self.estado = f"Aresta criada entre vertices {self.vertice_temp.id} e {v_prox.id}."
                        self.vertice_temp = None
                        self.atualizar_estrutura_grafo()

        elif modo == "Remover Aresta":
            if v_prox is not None:
                if self.vertice_temp is None:
                    self.vertice_temp = v_prox
                    self.estado = f"Selecione a outra ponta da aresta para deletar."
                else:
                    if self.vertice_temp.id != v_prox.id:
                        id1, id2 = self.vertice_temp.id, v_prox.id
                        self.arestas = [a for a in self.arestas if not (
                                (a.orig == id1 and a.dest == id2) or (a.orig == id2 and a.dest == id1)
                        )]
                        self.estado = f"Aresta removida entre vertice {id1} e {id2}."
                        self.vertice_temp = None
                        self.atualizar_estrutura_grafo()

        self.atualizar_interface_status()
        self.desenhar_grafo()

    def refatorar_indices(self):
        mapa_novo_id = {}
        novos_vertices = []

        for i, v in enumerate(self.vertices):
            mapa_novo_id[v.id] = i
            v.id = i
            novos_vertices.append(v)

        novas_arestas = []
        for a in self.arestas:
            if a.orig in mapa_novo_id and a.dest in mapa_novo_id:
                a.orig = mapa_novo_id[a.orig]
                a.dest = mapa_novo_id[a.dest]
                novas_arestas.append(a)

        self.vertices = novos_vertices
        self.arestas = novas_arestas

    def atualizar_interface_status(self):
        origem_txt = f"<font color='green'><b>{self.origem_selecionada}</b></font>" if self.origem_selecionada is not None else "Não selecionada"
        destino_txt = f"<font color='red'><b>{self.destino_selecionado}</b></font>" if self.destino_selecionado is not None else "Não selecionado"
        self.lbl_status.setText(f"Origem: {origem_txt}<p>Destino: {destino_txt}</p><p>Estado: {self.estado}</p>")

    def atualizar_estrutura_grafo(self):
        self.grafo = construir_grafo(self.vertices, self.arestas)
        self.mapa_vertices = {v.id: v for v in self.vertices}
        self.caminho_resultado = []

    def importar_mapa(self):
        caminho_arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Mapa", "", "Arquivos (*.poly)")
        if not caminho_arquivo:
            return

        self.vertices, self.arestas = carregar_mapa_poly(caminho_arquivo)
        self.atualizar_estrutura_grafo()
        self.limpar_selecoes()
        self.estado = "Mapa importado."
        self.atualizar_interface_status()

    def limpar_selecoes(self):
        self.origem_selecionada = None
        self.destino_selecionado = None
        self.vertice_temp = None
        self.estado = "Seleções limpas."
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

                self.estado = "Caminho Encontrado"
                self.lbl_estatisticas.setText(estatistica_texto)
                self.caminho_resultado = self.resultado.get("caminho_ids", [])
            else:
                self.estado = "Caminho Não Encontrado."
                self.caminho_resultado = []

            self.atualizar_interface_status()
            self.desenhar_grafo()

    def copiar_imagem_grafo(self):
        area_cena = self.scene.itemsBoundingRect()
        if area_cena.isEmpty():
            self.estado = "Mapa vazio."
            self.atualizar_interface_status()
            return

        imagem = QImage(area_cena.size().toSize(), QImage.Format.Format_ARGB32)
        imagem.fill(Qt.GlobalColor.white)

        painter = QPainter(imagem)
        alvo_rect = QRectF(imagem.rect())
        self.scene.render(painter, target=alvo_rect, source=area_cena)
        painter.end()

        clipboard = QApplication.clipboard()
        clipboard.setImage(imagem)

        self.estado = "Imagem copiada."
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