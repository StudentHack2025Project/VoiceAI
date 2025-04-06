# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 14:45:46 2025

@author: shaha
"""

import os
import random
import time
import schedule
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.player import AudioPlayer
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QStackedLayout,
    QLineEdit, QHBoxLayout, QMessageBox, QDateEdit, QTimeEdit, QToolTip
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QIcon
import speech_recognition as sr


def server_initiation():
    load_dotenv()  # Load the environment variables from the .env file
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))
    sse = client.tts.SSEClient()  # Creating a connection between me and the server
    tts_config = TTSConfig(
        speed=1.05,  # speech speed
        lang_code='en',  # replace the lang_code with the desired language code.
        voice_id='e564ba7e-aa8d-46a2-96a8-8dffedade48f'  # use client.voices.list() to view all available voices
    )  # Voice_id is just to choose which voice we want
    voices = client.voices.list()
    # print(voices) to print out the list of voices so we gotta choose between them later
    return tts_config, sse

tts_config, sse = server_initiation()

def text_to_speech(text):
    with AudioPlayer() as player:
        response = sse.send(text, tts_config=tts_config)
        player.play(response)
        player.save_audio('output.wav')  # save the audio to a .wav file

class VoiceAIApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceAI")
        self.setGeometry(100, 100, 1000, 700)

        self.stack = QStackedLayout()
        self.setLayout(self.stack)

        self.init_welcome_ui()
        self.init_main_ui()
        # Apply modern font + style to entire app
        app_style = """
            QWidget {
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                font-size: 18px;
            }
            QLineEdit, QDateEdit, QTimeEdit {
                font-size: 18px;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
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
        page.setStyleSheet("background-color: #f2fbf5;")  # calming color
        self.stack.addWidget(page)


    def init_main_ui(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Back Button
        back_button = QPushButton("⬅ Back to Home")
        back_button.setStyleSheet("padding: 6px; background-color: #d0f0c0;")
        back_button.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        # Text field for task input
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter your task here...")
        self.task_input.setStyleSheet("font-size: 16px; padding: 10px;")
        
        # Transcribed text display
        self.transcription_label = QLabel("Transcribed Text:")
        self.transcription_label.setWordWrap(True)
        self.transcription_label.setStyleSheet("font-size: 16px; color: #333;")
        layout.addWidget(self.transcription_label)

        # Mic button (start recording)
        self.record_btn = QPushButton()
        self.record_btn.setIcon(QIcon("icons/play.png"))
        self.record_btn.setToolTip("Start recording")
        self.record_btn.setFixedSize(60, 40)
        self.record_btn.clicked.connect(self.start_recording)

        # Stop button
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(QIcon("icons/stop.png"))
        self.stop_btn.setToolTip("Stop recording")
        self.stop_btn.setFixedSize(60, 40)
        self.stop_btn.clicked.connect(self.stop_recording)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.record_btn)
        btn_row.addWidget(self.stop_btn)

        # Date input field
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setStyleSheet("font-size: 16px; padding: 5px;")

        # Time input field
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        self.time_input.setStyleSheet("font-size: 16px; padding: 5px;")

        # Schedule button
        self.schedule_button = QPushButton("Send to Schedule")
        self.schedule_button.setStyleSheet("font-size: 16px; padding: 12px; background-color: #d0f0c0;")
        self.schedule_button.clicked.connect(self.send_schedule)

        # Add everything to layout
        layout.addWidget(back_button, alignment=Qt.AlignLeft)
        layout.addWidget(QLabel("Task"))
        layout.addWidget(self.task_input)
        layout.addLayout(btn_row)
        layout.addWidget(QLabel("Date"))
        layout.addWidget(self.date_input)
        layout.addWidget(QLabel("Time"))
        layout.addWidget(self.time_input)
        layout.addStretch()
        layout.addWidget(self.schedule_button, alignment=Qt.AlignRight)

        page.setLayout(layout)
        page.setStyleSheet("background-color: #f2fbf5;")  # calming blue
        self.stack.addWidget(page)

    def start_recording(self):
        text_to_speech("Recording started.")
        print("🎙 Start recording...")
          # Start voice recognition
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
        selected_date = self.date_input.date()
        selected_time = self.time_input.time()

        current_date = QDate.currentDate()
        current_time = QTime.currentTime()

        # Check for empty task
        if not task.strip():
            text_to_speech("Please enter a task first.")
            QMessageBox.warning(self, "Missing Info", "Please enter a task before sending.")
            return

        # Block any past date (yesterday or earlier)
        if selected_date < current_date:
            text_to_speech("You cannot select a past date.")
            QMessageBox.warning(self, "Invalid Date", "Please select today or a future date.")
            return

        # If today, the time must be in the future
        if selected_date == current_date and selected_time <= current_time:
            text_to_speech("The time must be later than now.")
            QMessageBox.warning(self, "Invalid Time", "The time must be in the future.")
            return

        # If all good, confirm schedule
        date_str = selected_date.toString("yyyy-MM-dd")
        time_str = selected_time.toString("HH:mm")
        text_to_speech(f"{task} has been scheduled for {date_str} at {time_str}.")
        QMessageBox.information(self, "Scheduled", f"🗓 {task} on {date_str} at {time_str}")


if __name__ == "__main__":
    app = QApplication([])
    window = VoiceAIApp()
    window.show()
    app.exec_()
    
    
        
        
        


    