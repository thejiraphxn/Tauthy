from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QTextEdit
from PyQt5.QtCore import Qt
from database import get_user_history

class HistoryWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("History Viewer")
        self.setGeometry(500, 150, 900, 600)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("Select an entry to view its content:"))

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.show_detail)
        main_layout.addWidget(self.list_widget)

        box_layout = QHBoxLayout()
        main_layout.addLayout(box_layout)

        self.input_box = QTextEdit()
        self.input_box.setReadOnly(True)
        self.input_box.setPlaceholderText("Input text will appear here.")
        self.input_box.setMinimumWidth(400)
        box_layout.addWidget(self.input_box)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlaceholderText("Result will appear here.")
        box_layout.addWidget(self.result_box)

        self.load_history()

    def load_history(self):
        history = get_user_history(self.user_id)
        self.entries = history
        for entry in history:
            short = entry['hs_input_text'][:50].replace('\n', ' ') + "..."
            date = entry['hs_created_at']
            self.list_widget.addItem(f"[{date}] {short}")

        if history:
            self.show_detail_by_index(0)

    def show_detail(self, item):
        index = self.list_widget.currentRow()
        self.show_detail_by_index(index)

    def show_detail_by_index(self, index):
        entry = self.entries[index]

        self.input_box.setPlainText(entry['hs_input_text'])

        result = (
            f"<b>AI Score:</b> {entry['hs_result_ai']*100:.2f}%<br>"
            f"<b>Human Score:</b> {entry['hs_result_human']*100:.2f}%<br>"
            f"<b>Feedback:</b> {entry.get('hs_user_feedback', 'N/A')}<br>"
            f"<b>Time:</b> {entry['hs_created_at']}"
        )
        self.result_box.setHtml(result)
