from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QTableWidget
from PyQt5.QtWidgets import QPushButton, QTableWidgetItem
from PyQt5.QtGui import QColor
from qt_material import apply_stylesheet

from PyQt5.QtCore import QObject, QThread, pyqtSignal

import time, requests
from datetime import datetime
from early.utils import DequeDict

early_url = "http://127.0.0.1:9400/status?last_time=0.0"

class Worker(QObject):
    finished = pyqtSignal()
    update_label1 = pyqtSignal(str)  # Create a pyqtSignal instance with a str argument
    update_label2 = pyqtSignal(str)  # Create a pyqtSignal instance with a str argument
    update_table = pyqtSignal(list)


    just_started = True

    is_early_okay = False
    msg_printed = False
    latest_n_flows = DequeDict(maxlen=500)
    last_time_updated = 0.0
    wt = 30
    at = 50
    timestamp_format = "%y-%m-%d %H:%M:%S"

    def get_updates(self):
        data = None
        is_early_okay = False
        msg_printed = False
        # early_url = f"http://{self.early_host}/status?last_time={self.last_time_updated}"

        while True:
            try:
                r = requests.get(early_url)
                is_early_okay = True
                break
            except requests.exceptions.ConnectionError:
                if self.just_started:
                    if not msg_printed:
                        print(f"Waiting for the Early tool to start...")
                        self.update_label1.emit("Waiting for the Early tool to start ...")  # Emit the signal

                        msg_printed = True
                    time.sleep(1)
                else:
                    print(f"Early  is stopped.")
                    self.update_label1.emit("Early is stopped.")  # Emit the signal
                    break

        if is_early_okay:
            if self.just_started:
                print("Connected!")
                self.update_label1.emit("Connected!")  # Emit the signal
            if r.status_code != 200:
                print(f"Response status code from Early is not 200. It is {r.status_code}.")
                self.update_label1.emit(f"Response status code from Early is not 200. It is {r.status_code}.")  # Emit the signal
                is_early_okay = False
            else:
                data = r.json()
        self.just_started = False

        return is_early_okay, data

    def start(self):
        raise NotImplemented("Display must implement this method")

    def closing(self):
        # print([d["name"] for d in self.latest_n_flows.values()])
        print("Exiting ...")



    def get_row_style(self, prediction):
        styles = []
        if prediction[1] != "Normal":
            styles.append("bold")
            styles.append("bright_white")
            if prediction[0] >= self.at:
                styles.append("red")
            elif prediction[0] >= self.wt:
                styles.append("yellow")

        if styles:
            return f"[{' '.join(styles)}]"
        else:
            return ""

    def get_remarks(self, prediction):
        if prediction[1] != "Normal":
            if prediction[0] >= self.at:
                return "ALERT"
            elif prediction[0] >= self.wt:
                return "Warning"
        return ""
    

    def update_flows(self, data):
        latest = []
        self.last_time_updated = data["latest_timestamp"]
        for f in data["flows"]:
            name = f["name"]
            latest.append(name)
            f["prediction"][0] = float(f["prediction"][0])
            self.latest_n_flows.put(name, f)
        return latest





    def run(self):
        data = None
        is_early_okay = False
        msg_printed = False
        
        
        while True:
            is_early_okay, data = self.get_updates()
            if not is_early_okay:
                    self.closing()
                    break
            
            updated_flows = self.update_flows(data)

            if self.latest_n_flows:
                # print(f"Latest flows: {len(self.latest_n_flows)}")
                self.update_label2.emit(f"Latest flows: {len(self.latest_n_flows)}")  # Emit the signal


            flows = []  # Create a list of flows
            for k in self.latest_n_flows.ordered_keys:
                f = self.latest_n_flows[k]
                style = self.get_row_style(f["prediction"])
                f["style"] = style
                remarks = self.get_remarks(f["prediction"])
                f["remarks"] = remarks
                timestamp = datetime.fromtimestamp(f['last_updated']).strftime(self.timestamp_format)
                f["timestamp"] = timestamp
                flows.append(f)  # Append each flow to the list
            print(flows[0])
            self.update_table.emit(flows)


            time.sleep(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(960, 600)
        self.setWindowTitle("Early Flow Monitor (Beta)")

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tabs.addTab(self.tab1, "Monitor")
        self.tabs.addTab(self.tab2, "Settings")

        self.setCentralWidget(self.tabs)

        tab1_layout = QVBoxLayout()

        self.label1 = QLabel("Wating to connect...")

        tab1_layout.addWidget(self.label1)

        self.label2 = QLabel("Flow count")
        self.label2.setStyleSheet("""
            border: 2px solid #77dd77;
            font-weight: bold;
            font-size: 20px;
            qproperty-alignment: 'AlignCenter';
        """)
        tab1_layout.addWidget(self.label2)



        # Create table with header and add 
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["Flow ID", "Src IP", "Src Port", "Dst IP", "Dst Port", "Length", "Prediction", "Remarks", "Updated at"])
        tab1_layout.addWidget(self.table)

        self.tab1.setLayout(tab1_layout)
        self.resize(self.table.sizeHint())

    def startWorker(self):
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.update_label1.connect(self.updateLabel1)
        self.worker.update_label2.connect(self.updateLabel2)
        self.worker.update_table.connect(self.updateTable)
        self.thread.start()

    def updateLabel1(self, text):
        # Slot method to update the label
        self.label1.setText(text)

    def updateLabel2(self, text):
        # Slot method to update the label
        self.label2.setText(text)


    def updateTable(self, flows):
        # Slot method to update the table
        self.table.setRowCount(len(flows))
        for i, flow in enumerate(flows):
            # Set the row color based on the row style
            
            color = QColor(flow['style'])
            for j in range(self.table.columnCount()):
                self.table.setItem(i, j, QTableWidgetItem(flow['name']))
                self.table.item(i, j).setBackground(color)

            # Set the selected items
            self.table.setItem(i, 0, QTableWidgetItem(flow['name']))
            self.table.setItem(i, 1, QTableWidgetItem(flow['src_ip']))
            self.table.setItem(i, 2, QTableWidgetItem(str(flow['src_port'])))
            self.table.setItem(i, 3, QTableWidgetItem(flow['dest_ip']))
            self.table.setItem(i, 4, QTableWidgetItem(str(flow['dst_port'])))
            self.table.setItem(i, 5, QTableWidgetItem(str(flow['length'])))
            self.table.setItem(i, 6, QTableWidgetItem(flow['prediction'][1]))
            self.table.setItem(i, 7, QTableWidgetItem(flow['prediction'][0]))
            self.table.setItem(i, 8, QTableWidgetItem(flow["remarks"]))
            self.table.setItem(i, 9, QTableWidgetItem(flow["timestamp"]))


def main():
    app = QApplication([])
    apply_stylesheet(app, theme='dark_teal.xml')  # Apply the material theme
    mainWin = MainWindow()
    mainWin.show()
    mainWin.startWorker()  # Start the worker thread
    app.exec_()

if __name__ == "__main__":
    main()