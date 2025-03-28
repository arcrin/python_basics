from ui_layer import ProductScannerUI
from data_access_layer import SqlProductRepository
from domain_layer import ProductService
from PyQt5.QtWidgets import QApplication


DATABASE_URL = "mssql+pyodbc://@localhost\\SQLEXPRESS/DCIERP?driver=ODBC+Driver+17+for+SQL+Server"

app = QApplication([])
window = ProductScannerUI(ProductService(SqlProductRepository(DATABASE_URL)))
window.show()
app.exec_()