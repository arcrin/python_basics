from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QWidget, QInputDialog, QDialog, QComboBox, QDialogButtonBox, QLineEdit
)
from PyQt5.QtGui import QFont
from domain_layer import IProductService, Product
from typing import List, Any
from datetime import datetime

def get_text_with_custom_font(title: str, label: str, font: QFont, style: str):
    dialog = QInputDialog()
    dialog.setFont(font)
    dialog.setWindowTitle(title)
    dialog.setLabelText(label)
    dialog.setStyleSheet(style)
    dialog.setFixedSize(400, 200)
    if dialog.exec_() == QInputDialog.Accepted:
        return dialog.textValue(), True
    else:
        return "", False


class ProductScannerUI(QMainWindow):
    def __init__(self, product_service: IProductService):
        """
        Initialize the UI and inject the ProductService dependency.
        :param product_service: An instance of the ProductService.
        """
        super().__init__()
        self.product_service = product_service  # Injected dependency
        self.work_order: str | None = None


        self.setWindowTitle("Product Scanner")
        self.setGeometry(100, 100, 800, 600)  # Increased window size

        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Set font size
        font = QFont()
        font.setPointSize(12)  # Increase font size
        self.setFont(font)

        # Start Workflow Button
        self.start_button = QPushButton("Start Workflow")
        self.start_button.setFont(font)
        self.start_button.clicked.connect(self.start_workflow)
        self.layout.addWidget(self.start_button)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Serial Number")
        self.search_bar.setFont(font)
        self.search_bar.textChanged.connect(self.filter_tree)
        self.layout.addWidget(self.search_bar)

        # Tree Widget for Product Hierarchy
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Serial Number", "Part Number", "Revision", "Description"])
        self.tree_widget.setFont(font)
        self.layout.addWidget(self.tree_widget)

        # Error Display
        # TODO: Replace error_label with error_prompt 
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setFont(font)
        self.layout.addWidget(self.error_label)

        # Counter Display
        self.counter_label = QLabel("Primary Assemblies Scanned: 0")
        self.counter_label.setFont(font)
        self.layout.addWidget(self.counter_label)

        self.parent_item = None  # Placeholder for the parent product item
        self.primary_assembly_count = 0


    def start_workflow(self):
        """
        Triggered when 'Start Workflow' button is clicked.
        Prompts the user to enter the parent serial number and child serial number.
        """
        # TODO: I don't think clearing the tree is necessary
        # self.tree_widget.clear()

        # Create a custom font
        font = QFont()
        font.setPointSize(12)  # Increase font size

        # Create the input dialog for ConfigMO
        dialog = QInputDialog(self)
        dialog.setFont(font)
        dialog.setWindowTitle("ConfigMO")
        dialog.setLabelText("Scan or enter the ConfigMO:")
        dialog.setFixedSize(400, 200)  # Increase dialog size

        # Execute the dialog and get the ConfigMO
        if dialog.exec_() == QInputDialog.Accepted:
            self.work_order = dialog.textValue()
            if not self.work_order.strip():
                self.error_label.setText("ConfigMO cannot be empty.")
                return
        else:
            self.error_label.setText("ConfigMO cannot be empty.")
            return
        # TODO: Find all subassemblies based on the ConfigMO 
        list_of_assemblies = self.product_service.query_product_config(self.work_order)

        # TODO: Need a prompot to ask user which board is the primary assembly.
        # Create the custom dialog for selecting assembly
        dialog = QDialog(self)
        dialog.setFont(font)
        dialog.setWindowTitle("Select Assembly")
        layout = QVBoxLayout(dialog)
        label = QLabel("Please select the primary assembly:")
        label.setFont(font)
        layout.addWidget(label)
        combo_box = QComboBox(dialog)
        combo_box.addItems(list_of_assemblies)
        layout.addWidget(combo_box)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layout.addWidget(button_box)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog.setLayout(layout)
        # dialog.setFixedSize(400, 200)  # Increase dialog size

        # Execute the dialog and get the selected item
        if dialog.exec_() == QDialog.Accepted:
            selected_index = combo_box.currentIndex()
            item = combo_box.currentText()
            self.error_label.setText(f"Selected Assembly: {item}")
            self.primary_assembly = item
            list_of_assemblies.pop(selected_index)  # Remove the selected item by index
            self.primary_assembly = item
        else:
            self.error_label.setText("No primary assembly selected")
            return

        while True:
            self.error_label.setText("")

            # Prompt for Parent Serial Number
            parent_serial, ok = get_text_with_custom_font(f"{self.primary_assembly}", f"Scan or enter the parent serial number for {self.primary_assembly}:", font, "background-color: lightblue;")
            if not ok or not parent_serial.strip():
                self.error_label.setText("Primary assembly serial number can not be empty")
                return

            # Validate Parent Serial Number
            # TODO: validation should confirm the serial number matches the expected part number
            validation_result = self.product_service.validate_serial_number(parent_serial)
            if not validation_result:
                self.error_label.setText(f"Serial Number {parent_serial} does not exist.")
                return

            list_of_children: List[str] = []
            for item in list_of_assemblies:

                child_serial, ok = get_text_with_custom_font(f"{item}", f"Scan or enter the child serial number for {item} (or leave blank to finish):", font, "background-color: lightgreen;")
                if not ok or not child_serial.strip():
                   self.error_label.setText("Secondary assembly serial number can not be empty.") 
                   return

                # Validate Child Serial Number
                child_serial_number_validation_result = self.product_service.validate_serial_number(child_serial)
                if not child_serial_number_validation_result:
                    self.error_label.setText(f"Serial Number {child_serial} does not exist.")
                    return
                
                list_of_children.append(child_serial)

            try:
                # Push the product info to the database first. Then retrieve them for display. There should only be one source of truth
                parent_product_id = self.product_service.add_product(parent_serial, None, self.work_order)
                for child_serial in list_of_children:
                    self.product_service.add_product(child_serial, parent_product_id, self.work_order)
            except ValueError as e:
                self.error_label.setText(str(e))
                return
            
            # Add Parent to Tree
            # TODO: Query the information from the database directly
            product_info = self.product_service.query_product_info(parent_serial)
            if not product_info:
                self.error_label.setText(f"Product information is not available for {parent_serial}")
                return
            self.parent_item = QTreeWidgetItem([product_info.serial_number, product_info.part_number, product_info.revision, product_info.description])
            self.tree_widget.addTopLevelItem(self.parent_item)
            # Add Child to Parent
            for child_serial in list_of_children:
                if self.parent_item:
                    child_product_info = self.product_service.query_product_info(child_serial)
                    if not child_product_info:
                        self.error_label.setText(f"Product information is not available for {child_serial}")
                        return
                    child_item = QTreeWidgetItem([child_product_info.serial_number, child_product_info.part_number, child_product_info.revision, child_product_info.description])
                    self.parent_item.addChild(child_item)
            
            self.tree_widget.expandAll() 
                 
            for i in range(self.tree_widget.columnCount()):
                self.tree_widget.resizeColumnToContents(i)
                
            self.primary_assembly_count += 1
            self.counter_label.setText(f"Primary Assemblies Scanned: {self.primary_assembly_count}")

    def filter_tree(self, text: str):
        """
        Filter the tree items based on the search text.
        """
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            self.filter_tree_item(item, text)
            
    def filter_tree_item(self, item, text):
        """
        Recursively filter tree items.
        """
        match = text.lower() in item.text(0).lower()
        for i in range(item.childCount()):
            child = item.child(i)
            child_match = self.filter_tree_item(child, text)
            match = match or child_match
        item.setHidden(not match)
        return match