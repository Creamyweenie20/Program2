from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QFileDialog, QScrollArea
from logic_synth.gui import MainWindow, FileWindow
from PySide6.QtGui import QGuiApplication, QFont
from func import singleStaticAssign
from Dag import Node, DAG
import os 
from dag_view import *
from schedules import * 

class LogicSynthesis(QPushButton):
    def __init__(self, text = "Logic Synthesis", parent = None):
        super().__init__(text, parent)
        self._window = None
        self.clicked.connect(self.open)

    def open(self): 

        if self._window is None: 
            self._window = MainWindow()
            self._window.destroyed.connect(self.clear)

        self._window.show()
        self._window.raise_()
        self._window.activateWindow()


    def clear(self): 
        self._window = None


class HardwareSynthesis(QPushButton):
    
    def __init__(self, text = "Hardware Synthesis", parent = None): 
        super().__init__(text, parent)
        self._window = None
        self.clicked.connect(self.open)
        self.text = None

    def open(self):
        if self._window is None:
            self._window = QMainWindow()
            self._window.setWindowTitle("Hardware Synthesis")
            self._window.setStyleSheet("""
                QWidget {
                    background-color: #222222;
                    color: #ffffff;
                }
            """)

            (width,height) = QGuiApplication.primaryScreen().size().toTuple()
            self._window.resize(width, height)

            self._window.destroyed.connect(self.clear)

            self._window.prompt = QLabel("Find your text file")
            self._window.prompt.setAlignment(Qt.AlignCenter)
            self._window.prompt.setStyleSheet("font-size: 18pt;")

            self._window.browse_button = QPushButton("Find file")
            self._window.browse_button.clicked.connect(self.find_file)

            layout = QVBoxLayout()
            layout.addWidget(self._window.prompt)
            layout.addWidget(self._window.browse_button)

            container = QWidget()
            container.setLayout(layout)
            self._window.setCentralWidget(container)

        self._window.show()
        self._window.raise_()
        self._window.activateWindow()

    def clear(self):
        self._window = None

    def find_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self._window,
            "Select a file containing your Boolean function",
            os.getcwd(),
            "Text files (*.txt)",
        )

        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()
        except OSError as e:
            self._window.prompt.setText(
                f"Could not open file:\n{e}"
            )
            return

        self.function_text = text
        self._window.prompt.setText(
            f"Your assignments are:\n\n{text}"
        )

        self._window.browse_button.setText("Single Static Assignment")
        self._window.browse_button.clicked.disconnect()
        self._window.browse_button.clicked.connect(
            lambda: self.ssa(path)
            )

    def ssa(self, path): 
        self.text = singleStaticAssign(path)
        self._window.prompt.setText(f"Your Single Static Assignments are: \n \n {self.text}")
        self._window.prompt.setWordWrap(True)
        self._window.prompt.setAlignment(Qt.AlignCenter)



        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(Qt.AlignCenter)
        layout = self._window.centralWidget().layout()
        layout.removeWidget(self._window.prompt)

        layout.removeWidget(self._window.browse_button)
        self._window.browse_button.deleteLater()

        self.button_row = QHBoxLayout()
        self.actions = ['Export', "Continue"]
        for action in self.actions: 
            button = QPushButton(action)
            button.clicked.connect(
                lambda _checked = False, l = action: self.action_button(l)
            )
            self.button_row.addWidget(button)

        layout.addLayout(self.button_row)

        self.scrollArea.setWidget(self._window.prompt)
        layout.insertWidget(0, self.scrollArea)
        
    def action_button(self, action):

        if action == "Export":
            self._window.prompt.setText(
                f"The Single Static Assignment: \n \n  {self.text} \n \n is saved to SSA.txt"
            )
            with open("SSA.txt", "w") as f:
                f.write(self.text)

            layout = self._window.centralWidget().layout()
            layout.removeWidget(self._window.prompt)
            self.clear_buttons(layout)

            self.button_row = QHBoxLayout()
            button = QPushButton("Continue")
            button.clicked.connect(
                lambda _checked=False: self.action_button("Continue")
            )
            self.button_row.addWidget(button)
            layout.addLayout(self.button_row)

            self.scrollArea.setWidget(self._window.prompt)
            layout.insertWidget(0, self.scrollArea)

        elif action == "Continue":
            self.dag = DAG()
            for line in self.text.strip().splitlines():
                if line.strip() == "":
                    continue
                self.dag.add_statemnt(line.strip())

            self.dag.save_json("DAG.json")

            layout = self._window.centralWidget().layout()
            self.clear_buttons(layout)            
            self.scrollArea.hide()                

            self.dag_view = DagView(self.dag)
            layout.insertWidget(0, self.dag_view)
            self.dag_view.fit()

            self.button_row = QHBoxLayout()
            self.schedules = ["ASAP", "ALAP"]
            for schedule in self.schedules:
                button = QPushButton(schedule)
                button.clicked.connect(
                    lambda _checked=False, l = schedule: self.schedule_buttons(l)
                )
                self.button_row.addWidget(button)
            layout.addLayout(self.button_row)

    def schedule_buttons(self, schedule): 
        if schedule == "ASAP": 
            layout = self._window.centralWidget().layout()
            self.clear_buttons(layout)            
            self.scrollArea.hide() 

            t = ASAP(self.dag)
            self.dag_view.setScene(build_scene(self.dag, t))
            self.dag_view.fit()
            layout.insertWidget(0, self.dag_view)
            self.dag_view.fit()

            self.button_row = QHBoxLayout()
            self.schedules = ["ASAP", "ALAP"]
            for s in self.schedules:
                button = QPushButton(schedule)
                button.clicked.connect(
                    lambda _checked=False, l = s: self.schedule_buttons(l)
                )
                self.button_row.addWidget(button)
            layout.addLayout(self.button_row)

        elif schedule == "ALAP": 
            layout = self._window.centralWidget().layout()
            self.clear_buttons(layout)            
            self.scrollArea.hide() 

            t = ALAP(self.dag)
            self.dag_view.setScene(build_scene(self.dag, t))
            self.dag_view.fit()
            layout.insertWidget(0, self.dag_view)
            self.dag_view.fit()

            self.button_row = QHBoxLayout()
            self.schedules = ["ASAP", "ALAP"]
            for s in self.schedules:
                button = QPushButton(schedule)
                button.clicked.connect(
                    lambda _checked=False, l = s: self.schedule_buttons(l)
                )
                self.button_row.addWidget(button)
            layout.addLayout(self.button_row)

    def clear_buttons(self, layout):
        while self.button_row.count():
            self.button_row.takeAt(0).widget().deleteLater()
        # Removes the row full of empty buttons
        layout.removeItem(self.button_row)

class Program2(QMainWindow): 
    def __init__(self): 
        super().__init__() 

        self.setStyleSheet("""
        QWidget {
            background-color: #222222;
            color: #ffffff;
        }

        QPushButton {
            background-color: #000000;
            color: white; 
            border: 1px solid #ffffff; 
            padding: 5px; 
            border-radius: 5px;
        }
""")
        self.setWindowTitle("Synthesizer")

        serifFont = QFont("Times", 32)
        self.setFont(serifFont)

        (width,height) = QGuiApplication.primaryScreen().size().toTuple()
        self.resize(width, height)

        self.prompt = QLabel("Select what to synthesize")
        self.prompt.setAlignment(Qt.AlignCenter)
        self.prompt.setStyleSheet("font-size: 24pt")


        layout = QVBoxLayout()
        layout.addWidget(self.prompt)
        BottomLayout = QHBoxLayout()
        BottomLayout.addWidget(HardwareSynthesis("Hardware Synthesis"))
        BottomLayout.addWidget(LogicSynthesis("Open Logic Synthesizer"))
        layout.addLayout(BottomLayout)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
