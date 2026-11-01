import math
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPolygonF, QPainter, QFont
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsSimpleTextItem

BOX_W, BOX_H = 120, 50
X_GAP, Y_GAP = 90, 30


def build_scene(dag):
    scene = QGraphicsScene()
    level = dag.levels()          # node id -> column number

    # Group nodes into columns
    columns = {}
    for n in dag.nodes:
        columns.setdefault(level[n.id], []).append(n)

    # Position each node (columns are centred vertically)
    tallest = max(len(c) for c in columns.values())
    pos = {}
    for lvl, nodes in columns.items():
        offset = (tallest - len(nodes)) * (BOX_H + Y_GAP) / 2
        for i, n in enumerate(nodes):
            pos[n.id] = (lvl * (BOX_W + X_GAP), offset + i * (BOX_H + Y_GAP))

    # Edges first, so boxes are drawn on top
    edge_pen = QPen(QColor("#aaaaaa"), 2)
    edge_brush = QBrush(QColor("#aaaaaa"))
    for n in dag.nodes:
        for c in n.child:
            x1, y1 = pos[n.id]
            x2, y2 = pos[c.id]
            start = QPointF(x1 + BOX_W, y1 + BOX_H / 2)   # right side of producer
            end = QPointF(x2, y2 + BOX_H / 2)             # left side of consumer
            scene.addLine(start.x(), start.y(), end.x(), end.y(), edge_pen)

            angle = math.atan2(end.y() - start.y(), end.x() - start.x())
            size = 12
            p1 = QPointF(end.x() - size * math.cos(angle - 0.4),
                         end.y() - size * math.sin(angle - 0.4))
            p2 = QPointF(end.x() - size * math.cos(angle + 0.4),
                         end.y() - size * math.sin(angle + 0.4))
            scene.addPolygon(QPolygonF([end, p1, p2]), edge_pen, edge_brush)

    # Nodes
    font = QFont("Times", 10)
    for n in dag.nodes:
        x, y = pos[n.id]
        fill = QColor("#cfe8ff") if n.op in ("input", "const") else QColor("#ffe9b3")
        scene.addRect(x, y, BOX_W, BOX_H, QPen(QColor("black"), 2), QBrush(fill))

        text = f"{n.op}\n{n.result or ''}"
        label = QGraphicsSimpleTextItem(text)
        label.setFont(font)
        label.setBrush(QBrush(QColor("black")))     # dark text on light boxes
        rect = label.boundingRect()
        label.setPos(x + (BOX_W - rect.width()) / 2, y + (BOX_H - rect.height()) / 2)
        scene.addItem(label)

    return scene


class DagView(QGraphicsView):
    def __init__(self, dag):
        super().__init__()
        self._scene = build_scene(dag)     
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def fit(self):
        self.fitInView(self._scene.itemsBoundingRect().adjusted(-20, -20, 20, 20),
                       Qt.AspectRatioMode.KeepAspectRatio)