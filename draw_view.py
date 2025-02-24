# -*- coding: utf-8 -*-
"""
Abstrakt uppritnings kontroll för uppritning (QWidget)

Implementerar en abstrakt klass för att rita i en QWidget. Klassen hanterar uppritning i värd- och fönsterkoordinater samt skalning och centrering av innehållet. Metoder för att rita linjer, cirklar, rektanglar, polygoner och text finns implementerade.

Klassen är avsedd att användas som en bas för att skapa anpassade uppritningskontroller i PyQt-applikationer.
"""

from qtpy.QtWidgets import QWidget
from qtpy.QtGui import QPainter, QTransform, QPen, QBrush, QFont
from qtpy.QtCore import Qt, QPointF, QRectF


class DrawView(QWidget):
    def __init__(self):
        """DrawWidget konstruktor"""
        super().__init__()

        # Koordinatgränser
        self.world_bounds = QRectF(-10, -10, 20, 20)  # xmin, ymin, bredd, höjd
        self.__update_transform()

        self.__stroke_color = Qt.black
        self.__fill_color = Qt.white
        self.__stroke_width = 1.0
        self.__text_color = Qt.black
        self.__stroke = True
        self.__fill = True

        self.stroke_pen = QPen(self.__stroke_color, self.__stroke_width)
        self.fill_brush = QBrush(self.__fill_color)
        self.no_fill_brush = QBrush(Qt.NoBrush)
        self.no_stroke_pen = QPen(Qt.NoPen)

        self.__current_pen = self.stroke_pen
        self.__current_brush = self.fill_brush

        self.__attribute_stack = []

        self.font = QFont()
        self.text_pen = QPen(self.__text_color)

        self.setMouseTracking(True)

    def __update_transform(self):
        """Uppdatera transformationsmatrisen mellan världs- och fönsterkoordinater"""
        if not self.width() or not self.height():
            return

        # Skapa vyrektangel (i fönsterkoordinater)
        viewport = QRectF(0, 0, self.width(), self.height())

        # Beräkna transformationsmatrisen
        self.transform = QTransform()

        # Skala för att passa vyn samtidigt som aspektförhållandet bibehålls
        scale_x = viewport.width() / self.world_bounds.width()
        scale_y = viewport.height() / self.world_bounds.height()
        self.scale = min(scale_x, scale_y)

        # Centrera innehållet
        tx = viewport.width() / 2
        ty = viewport.height() / 2

        # Skapa transformationen: översätt till centrum, skala, vänd Y-axeln
        self.transform.translate(tx, ty)
        self.transform.scale(
            self.scale, -self.scale
        )  # Vänd Y-axeln för att matcha matematisk konvention
        self.transform.translate(
            -self.world_bounds.center().x(), -self.world_bounds.center().y()
        )

    def mouseMoveEvent(self, event):
        self.current_mouse_pos = self.window_to_world(event.x(), event.y())
        self.on_mouse_move(self.current_mouse_pos.x(), self.current_mouse_pos.y())
        return super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        self.current_mouse_pos = self.window_to_world(event.x(), event.y())
        self.on_mouse_press(self.current_mouse_pos.x(), self.current_mouse_pos.y())
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        self.current_mouse_pos = self.window_to_world(event.x(), event.y())
        self.on_mouse_release(self.current_mouse_pos.x(), self.current_mouse_pos.y())
        return super().mouseReleaseEvent(event)


    def paintEvent(self, event):
        """Rita kontrollen"""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.current_pen)
        painter.setBrush(self.current_brush)
        painter.setBackground(Qt.white)
        painter.fillRect(0, 0, self.width(), self.height(), Qt.white)

        # Delegera uppritning till underklassen

        self.on_draw()

    def on_mouse_move(self, x, y):
        """Metod för att implementera musrörelse i underklasser"""
        pass

    def on_mouse_press(self, x, y):
        """Metod för att implementera musklick i underklasser"""
        pass

    def on_mouse_release(self, x, y):
        """Metod för att implementera musklick i underklasser"""
        pass

    def on_draw(self):
        """Metod för att implementera uppritning i underklasser"""
        pass

    def resizeEvent(self, event):
        """Hantera storleksändringar av kontrollen"""
        super().resizeEvent(event)

        self.__update_transform()
        self.update()

    def set_world_bounds(self, xmin: float, ymin: float, width: float, height: float):
        """Uppdatera världskoordinater"""
        self.world_bounds = QRectF(xmin, ymin, width, height)
        self.__update_transform()
        self.update()

    def window_to_world(self, x, y):
        """Konvertera fönsterkoordinater till världskoordinater"""
        return self.transform.inverted()[0].map(QPointF(x, y))

    def world_to_window(self, x, y):
        """Konvertera världskoordinater till fönsterkoordinater"""
        return self.transform.map(QPointF(x, y))
    
    def push_attributes(self):
        """Spara aktuella attributinställningar"""
        self.__attribute_stack.append(
            (self.stroke_color, self.fill_color, self.stroke_width, self.text_color, self.stroke, self.fill)
        )

    def pop_attributes(self):
        """Återställ sparade attributinställningar"""
        if self.__attribute_stack:
            (
                self.stroke_color,
                self.fill_color,
                self.stroke_width,
                self.text_color,
                self.stroke,
                self.fill
            ) = self.__attribute_stack.pop()
            self.stroke_pen.setColor(self.stroke_color)
            self.fill_brush.setColor(self.fill_color)
            self.stroke_pen.setWidth(self.stroke_width)
            self.text_pen.setColor(self.text_color)
            self.current_pen = self.stroke_pen if self.stroke else self.no_stroke_pen
            self.current_brush = self.fill_brush if self.fill else self.no_fill_brush

    def painter(self):
        """Returnera ett anpassat QPainter-objekt för kontrollen"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.current_pen)
        painter.setBrush(self.current_brush)
        return painter

    def polygon(self, points):
        """Rita en polygon med punkter"""

        painter = self.painter()
        # Transformera punkterna men inte pennan
        mapped_points = [self.transform.map(QPointF(x, y)) for x, y in points]
        painter.drawPolygon(mapped_points)

    def line(self, x1, y1, x2, y2):
        """Rita en linje"""
        painter = self.painter()
        # Transformera punkterna men inte pennan
        p1 = self.transform.map(QPointF(x1, y1))
        p2 = self.transform.map(QPointF(x2, y2))
        painter.drawLine(p1, p2)

    def arrow(self, x1, y1, x2, y2, arrow_size=5, arrow_start=True, arrow_end=True):
        """Rita en pil"""
        painter = QPainter(self)

        # Transformera punkterna men inte pennan
        p1 = self.transform.map(QPointF(x1, y1))
        p2 = self.transform.map(QPointF(x2, y2))
        painter.drawLine(p1, p2)

        # Rita pilhuvudet i skärmkoordinater
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        length = (dx**2 + dy**2) ** 0.5
        if length == 0:
            return

        # Normalisera riktningsvektorn
        dx /= length
        dy /= length

        s_arrow_size = arrow_size * abs(self.scale)

        # Beräkna pilhuvudpunkter (i skärmkoordinater)

        if arrow_end:
            p3 = QPointF(
                p2.x() - dx * s_arrow_size + dy * s_arrow_size / 2,
                p2.y() - dy * s_arrow_size - dx * s_arrow_size / 2,
            )
            p4 = QPointF(
                p2.x() - dx * s_arrow_size - dy * s_arrow_size / 2,
                p2.y() - dy * s_arrow_size + dx * s_arrow_size / 2,
            )

            painter.drawLine(p2, p3)
            painter.drawLine(p2, p4)

        if arrow_start:
            p5 = QPointF(
                p1.x() + dx * s_arrow_size + dy * s_arrow_size / 2,
                p1.y() + dy * s_arrow_size - dx * s_arrow_size / 2,
            )
            p6 = QPointF(
                p1.x() + dx * s_arrow_size - dy * s_arrow_size / 2,
                p1.y() + dy * s_arrow_size + dx * s_arrow_size / 2,
            )
            painter.drawLine(p1, p5)
            painter.drawLine(p1, p6)

    def rect(self, x, y, w, h):
        """Rita en rektangel"""

        painter = self.painter()
        # Transformera punkterna men inte pennan
        p1 = self.transform.map(QPointF(x, y))
        p2 = self.transform.map(QPointF(x + w, y + h))
        painter.drawRect(QRectF(p1, p2))

    def circle(self, x, y, r):
        """Rita en cirkel"""

        painter = self.painter()
        # Transformera punkterna men inte pennan
        p = self.transform.map(QPointF(x, y))
        screen_r = r * abs(self.scale)
        painter.drawEllipse(
            QRectF(p.x() - screen_r, p.y() - screen_r, 2 * screen_r, 2 * screen_r)
        )

    def triangle(self, x, y, w, h):
        """Rita en triangel"""

        painter = self.painter()
        # Transformera punkterna men inte pennan
        p1 = self.transform.map(QPointF(x, y))
        p2 = self.transform.map(QPointF(x + w / 2, y - h))
        p3 = self.transform.map(QPointF(x - w / 2, y - h))

        painter.drawPolygon([p1, p2, p3])

    def text(self, x, y, text, font_size=12, hor_align="left", vert_align="middle"):
        """
        Rita text i världskoordinater med skärmpixelstorlek på fonten

        Parametrar:
            x, y: Världskoordinater för textposition
            text: Sträng att visa
            font_size: Storlek i skärmpixlar (standard: 12)
            hor_align: Horisontell justering - "left", "right" eller "center" (standard: "left")
            vert_align: Vertikal justering - "top", "middle" eller "bottom" (standard: "middle")
        """
        painter = QPainter(self)

        # Ställ in fonten
        font = painter.font()
        font.setPixelSize(font_size * abs(self.scale))
        painter.setFont(font)

        # Hämta textmått för justering
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()

        # Transformera ankarpunkten från värld till skärmkoordinater
        p = self.transform.map(QPointF(x, y))

        # Justera x-position baserat på horisontell justering
        if hor_align == "right":
            p.setX(p.x() - text_width)
        elif hor_align == "center":
            p.setX(p.x() - text_width / 2)

        # Justera y-position baserat på vertikal justering
        if vert_align == "top":
            p.setY(p.y() + text_height)
        elif vert_align == "middle":
            p.setY(p.y() + text_height / 2)
        # För bottenjustering behövs ingen justering eftersom Qt ritar från botten

        painter.setPen(self.text_pen)
        painter.drawText(p, text)
        painter.setPen(self.stroke_pen)

    @property
    def stroke_color(self):
        return self.__stroke_color

    @stroke_color.setter
    def stroke_color(self, color):
        self.__stroke_color = color
        self.stroke_pen.setColor(color)

    @property
    def fill_color(self):
        return self.__fill_color

    @fill_color.setter
    def fill_color(self, color):
        self.__fill_color = color
        self.fill_brush.setColor(color)

    @property
    def fill(self):
        return self.__fill
    
    @fill.setter
    def fill(self, fill):
        if fill:
            self.current_brush = self.fill_brush
        else:
            self.current_brush = self.no_fill_brush
        self.__fill = fill

    @property
    def stroke(self):
        return self.__stroke
    
    @stroke.setter
    def stroke(self, stroke):
        if stroke:
            self.current_pen = self.stroke_pen
        else:
            self.current_pen = self.no_stroke_pen
        self.__stroke = stroke

    @property
    def stroke_width(self):
        return self.__stroke_width

    @stroke_width.setter
    def stroke_width(self, width):
        self.__stroke_width = width
        self.stroke_pen.setWidth(width)

    @property
    def current_pen(self):
        return self.__current_pen
    
    @current_pen.setter
    def current_pen(self, pen):
        self.__current_pen = pen
        #painter = self.painter()

    @property
    def current_brush(self):
        return self.__current_brush
    
    @current_brush.setter
    def current_brush(self, brush):
        self.__current_brush = brush
        #painter = self.painter()

    @property
    def text_color(self):
        return self.__font_color

    @text_color.setter
    def text_color(self, color):
        self.__font_color = color
        self.text_pen.setColor(color)
