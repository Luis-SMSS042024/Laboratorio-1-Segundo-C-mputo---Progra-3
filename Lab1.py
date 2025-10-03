import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFileDialog, QMessageBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt

class ControlNotas(QWidget):


    W_LAB1 = 0.25
    W_LAB2 = 0.25
    W_PARCIAL = 0.50
    UMBRAL_APROB = 6.0  # mínimo para aprobar

    def __init__(self):
        super().__init__()
        self._construir_ui()

    def _construir_ui(self):
        self.setWindowTitle("Control de Notas - PyQt5")
        self.setMinimumWidth(800)

        lbl_titulo = QLabel("Control de Notas de Estudiantes")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold;")

        lbl_nombre = QLabel("Nombre:")
        self.inp_nombre = QLineEdit()
        self.inp_nombre.setPlaceholderText("Ej.: Juan Pérez")

        lbl_seccion = QLabel("Sección:")
        self.cmb_seccion = QComboBox()
        self.cmb_seccion.addItems(["A", "B", "C", "D"])

        # Notas
        self.sp_lab1 = self._spin_nota("Laboratorio 1")
        self.sp_lab2 = self._spin_nota("Laboratorio 2")
        self.sp_parcial = self._spin_nota("Parcial")

        # Botones
        btn_agregar = QPushButton("Agregar")
        btn_actualizar = QPushButton("Actualizar seleccionado")
        btn_eliminar = QPushButton("Eliminar seleccionado")
        btn_limpiar = QPushButton("Limpiar")
        btn_exportar = QPushButton("Exportar CSV")
        btn_importar = QPushButton("Importar CSV")

        btn_agregar.clicked.connect(self.agregar_registro)
        btn_actualizar.clicked.connect(self.actualizar_registro)
        btn_eliminar.clicked.connect(self.eliminar_registro)
        btn_limpiar.clicked.connect(self.limpiar_form)
        btn_exportar.clicked.connect(self.exportar_csv)
        btn_importar.clicked.connect(self.importar_csv)

        # Tabla
        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels([
            "Nombre", "Sección", "Lab 1", "Lab 2", "Parcial", "Promedio / Estado"
        ])
        self.tabla.setSelectionBehavior(self.tabla.SelectRows)
        self.tabla.setEditTriggers(self.tabla.NoEditTriggers)

        # Layouts
        grid = QGridLayout()
        grid.addWidget(lbl_nombre, 0, 0)
        grid.addWidget(self.inp_nombre, 0, 1, 1, 3)
        grid.addWidget(lbl_seccion, 1, 0)
        grid.addWidget(self.cmb_seccion, 1, 1)
        grid.addWidget(self._wrap_labeled("Laboratorio 1", self.sp_lab1), 2, 0)
        grid.addWidget(self._wrap_labeled("Laboratorio 2", self.sp_lab2), 2, 1)
        grid.addWidget(self._wrap_labeled("Parcial", self.sp_parcial), 2, 2)

        hbtns1 = QHBoxLayout()
        hbtns1.addWidget(btn_agregar)
        hbtns1.addWidget(btn_actualizar)
        hbtns1.addWidget(btn_eliminar)
        hbtns1.addStretch()
        hbtns1.addWidget(btn_limpiar)

        hbtns2 = QHBoxLayout()
        hbtns2.addStretch()
        hbtns2.addWidget(btn_importar)
        hbtns2.addWidget(btn_exportar)

        root = QVBoxLayout()
        root.addWidget(lbl_titulo)
        root.addLayout(grid)
        root.addLayout(hbtns1)
        root.addWidget(self.tabla)
        root.addLayout(hbtns2)

        self.setLayout(root)

    # SpinBox helper
    def _spin_nota(self, tooltip: str) -> QDoubleSpinBox:
        sb = QDoubleSpinBox()
        sb.setRange(0.0, 10.0)
        sb.setDecimals(2)
        sb.setSingleStep(0.1)
        sb.setToolTip(tooltip)
        return sb

    def _wrap_labeled(self, texto: str, widget):
        cont = QVBoxLayout()
        lbl = QLabel(texto)
        cont.addWidget(lbl)
        cont.addWidget(widget)
        w = QWidget()
        w.setLayout(cont)
        return w

    # ---- Lógica ----
    def calcular_promedio_estado(self, lab1, lab2, parcial):
        prom = (lab1 * self.W_LAB1) + (lab2 * self.W_LAB2) + (parcial * self.W_PARCIAL)
        estado = "Aprobado" if prom >= self.UMBRAL_APROB else "Reprobado"
        return round(prom, 2), estado

    def agregar_registro(self):
        nombre = self.inp_nombre.text().strip()
        if len(nombre) < 3:
            QMessageBox.warning(self, "Atención", "El nombre es obligatorio (mínimo 3 caracteres).")
            return

        seccion = self.cmb_seccion.currentText()
        lab1 = self.sp_lab1.value()
        lab2 = self.sp_lab2.value()
        parcial = self.sp_parcial.value()

        prom, estado = self.calcular_promedio_estado(lab1, lab2, parcial)

        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)
        self._set_row(fila, [nombre, seccion, lab1, lab2, parcial, f"{prom} ({estado})"])
        self.limpiar_form()

    def actualizar_registro(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Selecciona una fila para actualizar.")
            return

        nombre = self.inp_nombre.text().strip()
        if len(nombre) < 3:
            QMessageBox.warning(self, "Atención", "El nombre es obligatorio.")
            return

        seccion = self.cmb_seccion.currentText()
        lab1 = self.sp_lab1.value()
        lab2 = self.sp_lab2.value()
        parcial = self.sp_parcial.value()

        prom, estado = self.calcular_promedio_estado(lab1, lab2, parcial)
        self._set_row(fila, [nombre, seccion, lab1, lab2, parcial, f"{prom} ({estado})"])
        self.limpiar_form()

    def eliminar_registro(self):
        fila = self.tabla.currentRow()
        if fila >= 0:
            self.tabla.removeRow(fila)

    def limpiar_form(self):
        self.inp_nombre.clear()
        self.cmb_seccion.setCurrentIndex(0)
        self.sp_lab1.setValue(0.0)
        self.sp_lab2.setValue(0.0)
        self.sp_parcial.setValue(0.0)

    # CSV funciones
    def exportar_csv(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "notas.csv", "CSV (*.csv)")
        if not ruta:
            return
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            headers = [self.tabla.horizontalHeaderItem(i).text() for i in range(self.tabla.columnCount())]
            writer.writerow(headers)
            for r in range(self.tabla.rowCount()):
                fila = [self.tabla.item(r, c).text() for c in range(self.tabla.columnCount())]
                writer.writerow(fila)

    def importar_csv(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Abrir CSV", "", "CSV (*.csv)")
        if not ruta:
            return
        with open(ruta, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            self.tabla.setRowCount(0)
            for row in reader:
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                for c, val in enumerate(row):
                    self.tabla.setItem(fila, c, QTableWidgetItem(val))

    def _set_row(self, fila, valores):
        for c, val in enumerate(valores):
            item = QTableWidgetItem(str(val))
            if c >= 2 and c <= 4:  # notas numéricas
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(fila, c, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ControlNotas()
    win.show()
    sys.exit(app.exec_())
