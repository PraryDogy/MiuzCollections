import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout
from PyQt5.QtGui import QPixmap
import os


class ImageGridApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Создаем сетку
        grid_layout = QGridLayout()

        # Пример изображений (замените путями к вашим изображениям)
        p = "/Users/Loshkarev/Downloads/MiuzCollections"
        image_paths = [os.path.join(p, i) for i in os.listdir(p)]

        row, col = 0, 0

        # Добавляем изображения в сетку
        for image_path in image_paths:
            pixmap = QPixmap(image_path)
            label = QLabel(self)
            label.setPixmap(pixmap)
            grid_layout.addWidget(label, row, col)

            col += 1
            if col == 3:  # Устанавливаем количество столбцов
                col = 0
                row += 1

        self.setLayout(grid_layout)

        self.setWindowTitle('Image Grid')
        self.setGeometry(100, 100, 600, 400)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageGridApp()
    window.show()
    sys.exit(app.exec_())
