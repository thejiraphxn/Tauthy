from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit,
    QPushButton, QFileDialog, QMessageBox, QHBoxLayout,
    QListWidget, QPlainTextEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import fitz  # PyMuPDF
from database import save_input, update_feedback, get_user_history
from ai_checker import predict_text  # ML Model
from ollama_checker import query_ollama  # Ollama API
from history_window import HistoryWindow


class MainAppWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Tauthy (A Python Application Text Checker)")
        self.setGeometry(1000, 100, 800, 800)
        self.setStyleSheet(open('qss/style.qss').read())

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Input your text or upload a PDF file")
        title.setFont(QFont('Arial', 25))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        content_layout = QHBoxLayout()
        layout.addLayout(content_layout)

        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText("Paste your text here or upload a PDF file...")
        self.text_input.setMinimumWidth(500)
        content_layout.addWidget(self.text_input)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlaceholderText("Result will appear here.")
        self.result_box.setMinimumWidth(500)
        content_layout.addWidget(self.result_box)

        button_layout = QHBoxLayout()

        upload_button = QPushButton("Upload PDF")
        upload_button.clicked.connect(self.upload_pdf)
        button_layout.addWidget(upload_button)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_text)
        button_layout.addWidget(submit_button)

        reanalyze_button = QPushButton("Reanalyze with Ollama")
        reanalyze_button.clicked.connect(self.reanalyze_ollama)
        button_layout.addWidget(reanalyze_button)

        layout.addLayout(button_layout)

        history_button = QPushButton("View History")
        history_button.clicked.connect(self.open_history_window)
        layout.addWidget(history_button)

    def upload_pdf(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)", options=options)

        if filename:
            try:
                pdf_text = self.extract_text_from_pdf(filename)
                self.text_input.setText(pdf_text)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read PDF: {e}")

    def extract_text_from_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def submit_text(self):
        text = self.text_input.toPlainText().strip()

        if not text:
            QMessageBox.warning(self, "Error", "Please enter or upload some text.")
            return

        result = predict_text(text)
        label = result["label"]
        confidence = result["confidence"]
        details = result["details"]  # {'ai': 88.0, 'human': 12.0}

        # Ollama
        ollama = query_ollama(text)

        # Save to database
        hs_id = save_input(self.user_id, text, details['ai'], details['human'])

        self.result_box.setText(
            f"<b>System Prediction</b><br>"
            f"<u>Final Label:</u> <b>{label.upper()}</b> ({confidence:.2f}% confident)<br>"
            f"AI: {details['ai']:.2f}% | Human: {details['human']:.2f}%<br><br>"
            f"<b>Ollama Analysis</b><br>"
            f"AI: {ollama['ai']:.2f}% | Human: {ollama['human']:.2f}%<br>"
            f"Reason: {ollama['reason']}"
        )

        self.ask_feedback(hs_id)

    def reanalyze_ollama(self):
        text = self.text_input.toPlainText().strip()

        if not text:
            QMessageBox.warning(self, "Error", "No text to analyze.")
            return

        try:
            ollama = query_ollama(text)

            lines = self.result_box.toPlainText().split("\n")

            ollama_text = (
                f"Ollama Analysis\n"
                f"AI: {ollama['ai']:.2f}% | Human: {ollama['human']:.2f}%\n"
                f"Reason: {ollama['reason']}"
            )

            if any("Ollama Analysis" in line for line in lines):
                start = next(i for i, l in enumerate(lines) if "Ollama Analysis" in l)
                new_lines = lines[:start] + ollama_text.split("\n")
            else:
                new_lines = lines + ["", ollama_text]

            self.result_box.setText("\n".join(new_lines))

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to reanalyze: {e}")

    def ask_feedback(self, hs_id):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Your Opinion")
        msg.setText("What do you think this text is?")
        ai_button = msg.addButton("AI", QMessageBox.YesRole)
        human_button = msg.addButton("Human", QMessageBox.NoRole)
        msg.exec_()

        if msg.clickedButton() == ai_button:
            update_feedback(hs_id, "ai")
        elif msg.clickedButton() == human_button:
            update_feedback(hs_id, "human")

    def open_history_window(self):
        self.history_window = HistoryWindow(self.user_id)
        self.history_window.show()
