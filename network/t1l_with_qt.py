import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar
from PyQt5.QtCore import QTimer
from scapy.layers.l2 import arping
from interface.Ethernet import get_jig_iface


class ArpingApp(QWidget):
    def __init__(self):
        super().__init__()
        
        self.target_ip = "169.254.107.3"
        self.iface = get_jig_iface()  # Replace this with your interface name
        
        # Set up the GUI layout
        self.setWindowTitle("Busy Rendering PyQt5 App with arping() Test")
        self.resize(300, 200)
        
        self.layout = QVBoxLayout()
        
        self.label = QLabel("Press the button to start arping()")
        self.layout.addWidget(self.label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.layout.addWidget(self.progress_bar)
        
        self.button = QPushButton("Start arping()")
        self.button.clicked.connect(self.run_arping_thread)
        self.layout.addWidget(self.button)
        
        self.setLayout(self.layout)
        
        # Timer for constant GUI updates (fake animation)
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.update_progress_bar)
        self.render_timer.start(30)  # Update every 30 milliseconds

        self.progress_value = 0
    
    def update_progress_bar(self):
        """Constantly updates the progress bar to simulate heavy GUI rendering."""
        self.progress_value = (self.progress_value + 1) % 101
        self.progress_bar.setValue(self.progress_value)
        
        # Also update label text rapidly
        self.label.setText(f"Rendering... {self.progress_value}%")
    
    def run_arping(self):
        """Run arping() directly in the main thread."""
        try:
            self.label.setText("Running arping() in the main thread...")
            ack, nack = arping(self.target_ip, timeout=2, iface=self.iface, verbose=False)
            
            if ack:
                response_mac = ack[0][1].src.upper()
                result = f"Response received: {response_mac}"
            else:
                result = "No response from device."
            
            self.label.setText(result)
        
        except Exception as e:
            self.label.setText(f"Error: {e}")
    
    def run_arping_thread(self):
        """Start arping() in a separate thread."""
        self.label.setText("Running arping() in a separate thread...")
        
        # Create and start a new thread for arping operation
        thread = threading.Thread(target=self.run_arping)
        thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArpingApp()
    window.show()
    sys.exit(app.exec_())