import sys
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
                             QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel,
                             QFileDialog, QComboBox, QCheckBox, QGraphicsItem)
from PyQt6.QtCore import Qt, QRectF, QTimer, QLineF, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QImage, QPainter, QFont

from djikstra_geometrico import carregar_mapa_poly, dijkstra, construir_grafo, Vertice, Aresta
from config import FATOR_ESCALA

COR_MAO_DUPLA   = QColor("#2980b9")
COR_MAO_UNICA   = QColor("#16a085")
COR_ROTA        = QColor("#e67e22")
COR_NORMAL      = QColor("#e5e5e6")
COR_ORIGEM      = QColor("#11ff00")
COR_DESTINO     = QColor("#ff0000")
COR_TEMP        = QColor("#f39c12")
COR_PESO        = QColor("#8e44ad")
COR_ID          = QColor("#2c3e50")
COR_BORDA       = Qt.GlobalColor.black

BRUSH_NORMAL    = QBrush(COR_NORMAL)
BRUSH_ORIGEM    = QBrush(COR_ORIGEM)
BRUSH_DESTINO   = QBrush(COR_DESTINO)
BRUSH_TEMP      = QBrush(COR_TEMP)

class GrafoItem(QGraphicsItem):
    def __init__(self, janela):
        super().__init__()
        self.janela = janela
        self._bounding_rect = QRectF()
        self.linhas_unica = []
        self.linhas_dupla = []

    def atualizar_geometria(self):
        if not self.janela.vertices:
            self._bounding_rect = QRectF()
            self.linhas_unica = []
            self.linhas_dupla = []
            return

        xs = [v.x for v in self.janela.vertices]
        ys = [v.y for v in self.janela.vertices]
        margem = 50.0
        self._bounding_rect = QRectF(min(xs) - margem, min(ys) - margem,
                                     max(xs) - min(xs) + margem * 2,
                                     max(ys) - min(ys) + margem * 2)

        self.linhas_unica.clear()
        self.linhas_dupla.clear()
        
        mapa = self.janela.mapa_vertices
        for aresta in self.janela.arestas:
            orig = mapa.get(aresta.orig)
            dest = mapa.get(aresta.dest)
            if orig and dest:
                linha = QLineF(orig.x, orig.y, dest.x, dest.y)
                if aresta.tipo == 1:
                    self.linhas_unica.append(linha)
                else:
                    self.linhas_dupla.append(linha)

        self.prepareGeometryChange()

    def boundingRect(self):
        return self._bounding_rect

    def paint(self, painter, option, widget):
        escala = painter.transform().m11()
        escala_linhas = max(escala, 1.0)
        escala_tamanho = max(escala, 1.0)

        pen_dupla = QPen(COR_MAO_DUPLA, 2 / escala_linhas)
        pen_unica = QPen(COR_MAO_UNICA, 2 / escala_linhas)
        pen_borda = QPen(COR_BORDA, 1 / escala_linhas)
        pen_rota = QPen(COR_ROTA, 4 / escala_linhas, Qt.PenStyle.SolidLine)

        tamanho_fonte = max(5, int(8 / escala_linhas))
        fonte_rotulos = QFont("Arial", tamanho_fonte)
        painter.setFont(fonte_rotulos)

        tamanho_normal = max(2.0, 10.0 / escala_tamanho ** 0.5)
        tamanho_especial = max(3.0, 14.0 / escala_tamanho ** 0.5)
        metade_normal = tamanho_normal / 2
        metade_especial = tamanho_especial / 2

        rect_visivel = option.exposedRect

        painter.setPen(pen_unica)
        painter.drawLines(self.linhas_unica)

        painter.setPen(pen_dupla)
        painter.drawLines(self.linhas_dupla)

        if self.janela.chk_pesos.isChecked():
            painter.setPen(QPen(COR_PESO))
            mapa = self.janela.mapa_vertices
            for aresta in self.janela.arestas:
                orig = mapa.get(aresta.orig)
                dest = mapa.get(aresta.dest)
                if orig and dest:
                    if (max(orig.x, dest.x) < rect_visivel.left() or min(orig.x, dest.x) > rect_visivel.right() or
                            max(orig.y, dest.y) < rect_visivel.top() or min(orig.y, dest.y) > rect_visivel.bottom()):
                        continue
                    dist = math.hypot(dest.x - orig.x, dest.y - orig.y) * FATOR_ESCALA
                    x_mid = (orig.x + dest.x) / 2
                    y_mid = (orig.y + dest.y) / 2
                    painter.drawText(QPointF(x_mid, y_mid), f"{dist:.1f}m")

        caminho = self.janela.caminho_resultado
        if caminho and len(caminho) > 1:
            painter.setPen(pen_rota)
            linhas_rota = []
            mapa = self.janela.mapa_vertices
            for i in range(len(caminho) - 1):
                v_u = mapa.get(caminho[i])
                v_v = mapa.get(caminho[i + 1])
                if v_u and v_v:
                    linhas_rota.append(QLineF(v_u.x, v_u.y, v_v.x, v_v.y))
            painter.drawLines(linhas_rota)

        id_origem = self.janela.origem_selecionada
        id_destino = self.janela.destino_selecionado
        id_temp = self.janela.vertice_temp.id if self.janela.vertice_temp else None
        mostrar_numeros = self.janela.chk_numerar.isChecked()

        offset_label = 5 / escala_linhas
        offset_label_y = 5 / escala_linhas

        for vertice in self.janela.vertices:
            vx, vy = vertice.x, vertice.y

            if vx < rect_visivel.left() or vx > rect_visivel.right() or vy < rect_visivel.top() or vy > rect_visivel.bottom():
                continue

            vid = vertice.id
            if vid == id_origem:
                brush, t, m = BRUSH_ORIGEM, tamanho_especial, metade_especial
            elif vid == id_destino:
                brush, t, m = BRUSH_DESTINO, tamanho_especial, metade_especial
            elif vid == id_temp:
                brush, t, m = BRUSH_TEMP, tamanho_especial, metade_especial
            else:
                brush, t, m = BRUSH_NORMAL, tamanho_normal, metade_normal

            painter.setPen(pen_borda)
            painter.setBrush(brush)
            painter.drawEllipse(QRectF(vx - m, vy - m, t, t))

            if mostrar_numeros:
                painter.setPen(QPen(COR_ID))
                painter.drawText(QPointF(vx + offset_label, vy - offset_label_y), str(vid))

class VisualizadorMapa(QGraphicsView):
    def __init__(self, cena, pai):
        super().__init__(cena)
        self.pai = pai
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

    def wheelEvent(self, event):
        fator_zoom = 1.20 if event.angleDelta().y() > 0 else 0.80
        self.scale(fator_zoom, fator_zoom)
        self.pai.grafo_item.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            pos_cena = self.mapToScene(event.pos())
            self.pai.tratar_clique_mapa(pos_cena.x(), pos_cena.y())
        else:
            super().mousePressEvent(event)

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
        self.grafo_item = None
        
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

    def init_ui(self):
        self.scene = QGraphicsScene()
        self.view = VisualizadorMapa(self.scene, self)
        
        self.grafo_item = GrafoItem(self)
        self.scene.addItem(self.grafo_item)

        self.painel = QVBoxLayout()

        self.lbl_titulo = QLabel("<b>Algoritmo de Dijkstra</b>")
        self.lbl_status = QLabel(
            "Origem: Não selecionada<p>Destino: Não selecionado</p><p>Estado: Aguardando importação</p>")
        self.lbl_estatisticas = QLabel("<b>Estatísticas:</b><br>Tempo: -<br>Nós explorados: -<br>Custo: -")

        self.chk_numerar = QCheckBox("Mostrar IDs dos Vértices")
        self.chk_numerar.stateChanged.connect(self.solicitar_redesenho)

        self.chk_pesos = QCheckBox("Mostrar Pesos das Arestas")
        self.chk_pesos.stateChanged.connect(self.solicitar_redesenho)

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

    def solicitar_redesenho(self):
        if self.grafo_item:
            self.grafo_item.update()

    def resetar_selecao_temporaria(self):
        self.vertice_temp = None
        self.estado = f"Modo: {self.combo_modo.currentText()}"
        self.atualizar_interface_status()

    def ajustar_view_ao_mapa(self):
        if not self.vertices:
            return
        rect = self.grafo_item.boundingRect()
        if not rect.isEmpty():
            self.scene.setSceneRect(rect)
            self.view.resetTransform()
            margem = 40
            rect_margem = rect.adjusted(-margem, -margem, margem, margem)
            self.view.fitInView(rect_margem, Qt.AspectRatioMode.KeepAspectRatio)

    def tratar_clique_mapa(self, x, y):
        modo = self.combo_modo.currentText()
        escala = self.view.transform().m11() if self.view else 1.0
        limite = 15.0 / escala
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
                self.estado = f"Vertice adicionado: {novo_id}"
                self.atualizar_estrutura_grafo()

        elif modo == "Remover Vértice":
            if v_prox is not None:
                self.vertices = [v for v in self.vertices if v.id != v_prox.id]
                self.refatorar_indices()
                self.estado = f"Vertice removido: {v_prox.id}"
                if self.origem_selecionada == v_prox.id: self.origem_selecionada = None
                if self.destino_selecionado == v_prox.id: self.destino_selecionado = None
                self.atualizar_estrutura_grafo()

        elif "Adicionar Aresta" in modo:
            if v_prox is not None:
                if self.vertice_temp is None:
                    self.vertice_temp = v_prox
                    self.estado = f"Vertice {v_prox.id} selecionado. Clique no proximo vertice"
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
        self.solicitar_redesenho()

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
        self.grafo_item.atualizar_geometria()
        self.solicitar_redesenho()

    def importar_mapa(self):
        caminho_arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Mapa", "", "Arquivos (*.poly)")
        if not caminho_arquivo:
            return

        self.vertices, self.arestas = carregar_mapa_poly(caminho_arquivo)
        self.atualizar_estrutura_grafo()
        self.limpar_selecoes()
        self.estado = "Mapa importado."
        self.atualizar_interface_status()
        
        QTimer.singleShot(0, self.ajustar_view_ao_mapa)

    def limpar_selecoes(self):
        self.origem_selecionada = None
        self.destino_selecionado = None
        self.vertice_temp = None
        self.estado = "Seleções limpas."
        self.caminho_resultado = []
        self.resultado = None
        self.lbl_estatisticas.setText("<b>Estatísticas:</b><br>Tempo: -<br>Nós explorados: -<br>Custo: -")
        self.atualizar_interface_status()
        self.solicitar_redesenho()

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
            self.solicitar_redesenho()

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = Janela()
    janela.show()
    sys.exit(app.exec())