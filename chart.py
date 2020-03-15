# import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtWidgets, QtGui


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, outcomes, heroes):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )
        self.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight,
                QtCore.Qt.AlignCenter,
                QtCore.QSize(640, 480),
                QtWidgets.qApp.desktop().availableGeometry()
            )
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.outcomes = outcomes
        self.heroes = heroes

    def mousePressEvent(self, event):
        QtWidgets.qApp.quit()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 0, QtCore.Qt.SolidLine))
        painter.setFont(QtGui.QFont('Helvetica', 10))
        self.paint_win_chance(painter)
        self.paint_outcomes(painter)

    def drawOutlineText(self, painter, x, y, font, text):
        path = QtGui.QPainterPath()
        path.addText(x, y, font, text)
        painter.drawPath(path)

    def paint_win_chance(self, painter):
        probs = (
            len([k for k in self.outcomes if k > 0]) / len(self.outcomes),
            len([k for k in self.outcomes if k == 0]) / len(self.outcomes),
            len([k for k in self.outcomes if k < 0]) / len(self.outcomes),
        )
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0, QtCore.Qt.SolidLine))
        painter.setBrush(QtGui.QBrush(QtCore.Qt.white, QtCore.Qt.SolidPattern))
        font = QtGui.QFont('Arial', 32)
        x_min = 0
        x_max = 200
        y_min = 21
        for i, prob in enumerate(probs):
            y = y_min + (i * 32)
            w = (x_max - x_min - 30) * prob
            painter.drawRect(x_min + 30, y, w, 32)
            self.drawOutlineText(painter, w + 30, y + 28, font, str(round(prob * 100, 2)) + '%')

        for i, hero in enumerate(self.heroes):
            y = y_min + (i * 64)
            pixmap = QtGui.QPixmap(f'card_art/{hero[0]}.jpg')
            path = QtGui.QPainterPath()
            path.addEllipse(x_min, y - 5, 32, 42)
            painter.setClipPath(path)
            painter.drawEllipse(x_min, y - 6, 34, 44)
            painter.drawPixmap(
                x_min,
                y - 5,
                64,
                84,
                pixmap,
                64,
                0,
                256,
                512
            )
            painter.drawPixmap
            painter.setClipRect(0, 0, 400, 400)  # reset clip on painter

        # for i, hero in enumerate(self.heroes):
        #     self.drawOutlineText(painter, 0, (i * 100) + 50, font, f'{hero[1]}: {round(probs[i] * 100, 2)}%')
        # self.drawOutlineText(painter, 0, 100, font, f'Draw: {round(probs[2] * 100, 2)}%')

    def paint_outcomes(self, painter):
        min_damage = min(self.outcomes)
        max_damage = max(self.outcomes)
        damages = list(range(min_damage - 1, max_damage + 1))
        max_prob = max([len([o for o in self.outcomes if o == i]) / len(self.outcomes) for i in damages])

        x_min = 0
        x_max = 400
        block_width = min(20, (x_max - x_min) / len(damages))
        y_min = 150
        y_max = 400

        painter.setBrush(QtGui.QBrush(QtCore.Qt.white, QtCore.Qt.SolidPattern))
        # painter.drawRect(x_min, y_min, (x_max - x_min), (y_max - y_min))

        for x, i in enumerate(damages):
            value = len([o for o in self.outcomes if o == i]) / len(self.outcomes)
            bar_height = ((value / max_prob) * (y_max - y_min))

            if i < 0:
                painter.setBrush(QtGui.QBrush(QtCore.Qt.red, QtCore.Qt.SolidPattern))
            elif i > 0:
                painter.setBrush(QtGui.QBrush(QtCore.Qt.green, QtCore.Qt.SolidPattern))
            else:
                painter.setBrush(QtGui.QBrush(QtCore.Qt.yellow, QtCore.Qt.SolidPattern))

            painter.drawRect(x_min + (x * block_width), y_max, block_width, -bar_height)
            if value > 0.0:
                rect = QtCore.QRect(x_min + (x * block_width), y_max - bar_height + 10, block_width, 10)
                painter.drawText(rect, QtCore.Qt.AlignCenter, str(i))


def plot_probabilities(outcomes, heroes):
    # plt.xticks(range(min(outcomes), max(outcomes) + 1))
    # tick_range = range(min(min(outcomes), 0), max(max(outcomes), 0) + 1)
    # plt.xticks([])
    # plt.xticks(tick_range)
    # # plt.xticks([i + 0.5 for i in tick_range], [str(s) for s in tick_range], minor=True)

    # plt.axvspan(min(0, min(outcomes) - 1), 0, facecolor='r', alpha=0.2)
    # plt.axvspan(0, 1, facecolor='b', alpha=0.2)
    # plt.axvspan(1, max(1, max(outcomes) + 1), facecolor='g', alpha=0.2)
    # plt.hist(outcomes, density=True)
    # plt.gca().set(xlabel='Damage')
    # plt.show()
    app = QtWidgets.QApplication([])
    window = MainWindow(outcomes, heroes)
    window.show()
    app.exec_()
