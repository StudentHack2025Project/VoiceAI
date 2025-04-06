import os
import time
import schedule
import sounddevice as sd
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QTimer
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
import threading

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
        self.is_recording = False
        self.audio_buffer = []
        self.stream = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_waveform)


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

        self.stack.setCurrentIndex(0)

        self.schedule_thread = threading.Thread(target=self.run_schedules, daemon=True)
        self.schedule_thread.start()

        self.dictionary = {}
        self.current_job = None
        self.is_working = False

        self.tts_config, self.sse = self.server_initiation()

    def server_initiation(self):
        load_dotenv()
        client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))
        sse = client.tts.SSEClient()
        tts_config = TTSConfig(
            speed=1.05,
            lang_code='en',
            voice_id='e564ba7e-aa8d-46a2-96a8-8dffedade48f'
        )
        return tts_config, sse

    def text_to_speech(self, text): 
        with AudioPlayer() as player:
            response = self.sse.send(text, tts_config=self.tts_config)
            player.play(response)

    def break_timer(self):
        self.current_job = schedule.every(45).minutes.do(self.start_timer)

    def start_timer(self):
        if self.get_current_task() is not None:
            text = "It is time for a 15 minutes break"
            self.text_to_speech(text)
            if self.current_job:
                schedule.cancel_job(self.current_job)
            self.current_job = schedule.every(15).minutes.do(self.end_break)

    def end_break(self):
        if self.get_current_task() is not None:
            text = "Break is over! Time to get back to work!"
            self.text_to_speech(text)
            schedule.cancel_job(self.current_job)
            self.break_timer()

    def run_schedules(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

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
        
        self.plot_widget = pg.PlotWidget(title="Live Microphone Input")
        self.plot_widget.setYRange(-1, 1)
        self.waveform_plot = self.plot_widget.plot(pen='g')
        layout.addWidget(self.plot_widget)
        
        layout.addStretch()
        layout.addWidget(self.schedule_button, alignment=Qt.AlignRight)

        page.setLayout(layout)
        page.setStyleSheet("background-color: #f2fbf5;")
        self.stack.addWidget(page)

    def start_recording(self):
        self.is_recording = True
        self.audio_buffer = []
        
        self.text_to_speech("Recording started.")
        self.transcription_label.setText("🎙 Listening...")

        def callback(indata, frames, time, status):
            if self.is_recording:
                self.audio_buffer.append(indata.copy())

        self.stream = sd.InputStream(callback=callback, channels=1, samplerate=16000)
        self.stream.start()
        self.timer.start(50)


    def stop_recording(self):
        self.is_recording = False
        self.timer.stop()
        self.stream.stop()
        self.stream.close()

        self.text_to_speech("Recording stopped.")
        self.transcription_label.setText("⏹ Transcribing...")

        audio_data = np.concatenate(self.audio_buffer, axis=0)

        import soundfile as sf
        temp_file = "temp.wav"
        sf.write(temp_file, audio_data, 16000)

        # Transcribe
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_file) as source:
            audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio)
                self.transcription_label.setText(f"🗣 You said: {text}")
            except sr.UnknownValueError:
                self.transcription_label.setText("Could not understand the audio.")
            except Exception as e:
                self.transcription_label.setText(f"Error: {str(e)}")

    def update_waveform(self):
        if self.audio_buffer:
            num_chunks = 10
            buffer_window = self.audio_buffer[-num_chunks:] if len(self.audio_buffer) >= num_chunks else self.audio_buffer
            data = np.concatenate(buffer_window).flatten()

            data = data - np.mean(data)

            window_size = 5
            if len(data) > window_size:
                smoothed = np.convolve(data, np.ones(window_size)/window_size, mode='valid')
            else:
                smoothed = data

            # Normalize to prevent overamplification
            max_val = np.max(np.abs(smoothed))
            if max_val != 0:
                smoothed = smoothed / max_val

            self.waveform_plot.setData(smoothed)




    def send_schedule(self):
        task = self.task_input.text()
        self.dictionary[task] = False
        self.text_to_speech(f"{task} has been added to your tasks.")
        QMessageBox.information(self, "Task Added", f"🗓 Task '{task}' has been added.")
        self.break_timer()

    def mark_task_complete(self):
        task = self.get_current_task()
        if task:
            self.dictionary[task] = True
            self.text_to_speech(f"Task {task} marked as complete.")
            self.task_label.setText(f"Current Task: {task} - Completed")
            self.check_and_update_task()

    def get_current_task(self):
        for key, value in self.dictionary.items():
            if not value:
                return key
        return None

    def check_and_update_task(self):
        task = self.get_current_task()
        if task is None:
            self.text_to_speech("All tasks are completed.")
        else:
            self.task_label.setText(f"Current Task: {task}")

    def stop_working(self):
        self.is_working = False
        schedule.clear()
        self.text_to_speech("You have returned to the home page.")
        self.stack.setCurrentIndex(0)

    def closeEvent(self, event):
        schedule.clear()
        self.text_to_speech("Application is closing.")
        event.accept()

if __name__ == "__main__":
    app = QApplication([])  
    window = VoiceAIApp()
    window.show()
    app.exec_()
