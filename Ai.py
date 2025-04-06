# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 14:45:46 2025

@author: shaha
"""

import os
import time
import schedule
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.player import AudioPlayer
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QStackedLayout,
    QLineEdit, QHBoxLayout, QMessageBox, QDateEdit, QTimeEdit
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QIcon
import speech_recognition as sr

# Initialize global variables
dictionary = {}
current_job = None
reminder_job = None
is_working = False  # Track whether the work session is active or not

def server_initiation():
    load_dotenv()
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))
    sse = client.tts.SSEClient()
    tts_config = TTSConfig(
        speed=1.05,
        lang_code='en',
        voice_id='e564ba7e-aa8d-46a2-96a8-8dffedade48f'
    )
    return tts_config, sse

tts_config, sse = server_initiation()

def text_to_speech(text): 
    with AudioPlayer() as player:
        response = sse.send(text, tts_config=tts_config)
        player.play(response)

def break_timer():
    global current_job
    schedule.every(45).minutes.do(start_timer)

def start_timer():
    global current_job
    text = "It is time for a 15 minutes break"
    text_to_speech(text)
    if current_job:
        schedule.cancel_job(current_job)
    current_job = schedule.every(15).minutes.do(end_break)

def end_break():
    text = "Break is over! Time to get back to work!"
    text_to_speech(text)
    schedule.cancel_job(current_job)
    break_timer()

class VoiceAIApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceAI")
        self.setGeometry(100, 100, 1000, 700)

        self.stack = QStackedLayout()
        self.setLayout(self.stack)

        self.init_welcome_ui()
        self.init_main_ui()
        self.init_stay_focused_ui()
        
        app_style = """
            QWidget {
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                font-size: 18px;
            }
            QLabel {
                font-size: 20px;
            }
        """
        self.setStyleSheet(app_style)

        self.stack.setCurrentIndex(0)  # Start with welcome screen

    def init_welcome_ui(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        self.label = QLabel("Welcome to VoiceAI!")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.start_button = QPushButton("Set a Task")
        self.start_button.setStyleSheet("font-size: 18px; padding: 12px; background-color: #d0f0c0;")
        self.start_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        self.stay_focused_button = QPushButton("Stay Focused")
        self.stay_focused_button.setStyleSheet("font-size: 18px; padding: 12px; background-color: #d0f0c0;")
        self.stay_focused_button.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        layout.addWidget(self.label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stay_focused_button)

        page.setLayout(layout)
        page.setStyleSheet("background-color: #f2fbf5;")
        self.stack.addWidget(page)

    def init_stay_focused_ui(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        back_button = QPushButton("⬅ Back to Home")
        back_button.setStyleSheet("padding: 6px; background-color: #d0f0c0;")
        back_button.clicked.connect(self.stop_working)
    
        self.task_label = QLabel("Start working now...")
        self.task_label.setStyleSheet("font-size: 16px; color: #333;")
    
        self.task_status_button = QPushButton("Mark Task Completed")
        self.task_status_button.setStyleSheet("font-size: 16px; padding: 12px; background-color: #d0f0c0;")
        self.task_status_button.clicked.connect(self.mark_task_complete)
    
        layout.addWidget(back_button, alignment=Qt.AlignLeft)
        layout.addWidget(self.task_label)
        layout.addWidget(self.task_status_button)
    
        page.setLayout(layout)
        page.setStyleSheet("background-color: #f2fbf5;")
        self.stack.addWidget(page)

    def init_main_ui(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        back_button = QPushButton("⬅ Back to Home")
        back_button.setStyleSheet("padding: 6px; background-color: #d0f0c0;")
        back_button.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter your task here...")
        self.task_input.setStyleSheet("font-size: 16px; padding: 10px;")
        
        self.transcription_label = QLabel("Transcribed Text:")
        self.transcription_label.setWordWrap(True)
        self.transcription_label.setStyleSheet("font-size: 16px; color: #333;")
        layout.addWidget(self.transcription_label)

        self.record_btn = QPushButton()
        self.record_btn.setIcon(QIcon("icons/play.png"))
        self.record_btn.setToolTip("Start recording")
        self.record_btn.setFixedSize(60, 40)
        self.record_btn.clicked.connect(self.start_recording)

        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(QIcon("icons/stop.png"))
        self.stop_btn.setToolTip("Stop recording")
        self.stop_btn.setFixedSize(60, 40)
        self.stop_btn.clicked.connect(self.stop_recording)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.record_btn)
        btn_row.addWidget(self.stop_btn)

        self.schedule_button = QPushButton("Send to Schedule")
        self.schedule_button.setStyleSheet("font-size: 16px; padding: 12px; background-color: #d0f0c0;")
        self.schedule_button.clicked.connect(self.send_schedule)

        layout.addWidget(back_button, alignment=Qt.AlignLeft)
        layout.addWidget(QLabel("Task"))
        layout.addWidget(self.task_input)
        layout.addLayout(btn_row)
        layout.addStretch()
        layout.addWidget(self.schedule_button, alignment=Qt.AlignRight)

        page.setLayout(layout)
        page.setStyleSheet("background-color: #f2fbf5;")
        self.stack.addWidget(page)

    def start_recording(self):
        text_to_speech("Recording started.")
        print("🎙 Start recording...")
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            self.transcription_label.setText("Listening...")
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                self.transcription_label.setText(f"🗣 You said: {text}")
            except sr.UnknownValueError:
                self.transcription_label.setText("Could not understand the audio.")
            except sr.WaitTimeoutError:
                self.transcription_label.setText("Listening timed out.")
            except Exception as e:
                self.transcription_label.setText(f"Error: {str(e)}")

    def stop_recording(self):
        text_to_speech("Recording stopped.")
        print("⏹ Stop recording.")

    def send_schedule(self):
        task = self.task_input.text()
        dictionary[task] = False
        text_to_speech(f"{task} has been added to your tasks.")
        QMessageBox.information(self, "Task Added", f"🗓 Task '{task}' has been added.")

    def mark_task_complete(self):
        task = self.get_current_task()
        if task:
            dictionary[task] = True
            text_to_speech(f"Task {task} marked as complete.")
            self.task_label.setText(f"Current Task: {task} - Completed")
            self.check_and_update_task()

    def get_current_task(self):
        for key, value in dictionary.items():
            if not value:
                return key
        return None

    def check_and_update_task(self):
        task = self.get_current_task()
        if task is None:
            text_to_speech("All tasks are completed.")
        else:
            self.task_label.setText(f"Current Task: {task}")

    def stop_working(self):
        global is_working
        is_working = False
        schedule.clear()
        text_to_speech("You have returned to the home page.")
        self.stack.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication([])
    window = VoiceAIApp()
    window.show()
    app.exec_()
    break_timer()
    while True:
        schedule.run_pending()
        time.sleep(1)
