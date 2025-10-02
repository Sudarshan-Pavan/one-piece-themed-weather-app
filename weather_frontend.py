# main_gui.py
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFrame, QGridLayout, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QPixmap, QFont, QFontDatabase, QColor, QRegion, QPainterPath
from PyQt6.QtCore import Qt, QTimer, QTime
from weather_backend import get_current_weather, get_forecast, get_location
from PyQt6.QtCore import QPropertyAnimation, QSequentialAnimationGroup, QEasingCurve, QPoint, QTimer
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation


class WeatherApp(QWidget):

    def start_character_animation(self):
        # Starting position
        start_y = self.char_label.y()
        float_distance = 16  # pixels to move up and down

        # Move up animation
        anim_up = QPropertyAnimation(self.char_label, b"pos")
        anim_up.setDuration(1300)  
        anim_up.setStartValue(QPoint(self.char_label.x(), start_y))
        anim_up.setEndValue(QPoint(self.char_label.x(), start_y - float_distance))
        anim_up.setEasingCurve(QEasingCurve.Type.InOutSine)

        # Tiny pause at top
        pause_top = QTimer()
        pause_top.setInterval(1)  # 1 ms
        pause_top.timeout.connect(lambda: None)  # dummy

        # Move down animation
        anim_down = QPropertyAnimation(self.char_label, b"pos")
        anim_down.setDuration(1300)  # 1 second
        anim_down.setStartValue(QPoint(self.char_label.x(), start_y - float_distance))
        anim_down.setEndValue(QPoint(self.char_label.x(), start_y))
        anim_down.setEasingCurve(QEasingCurve.Type.InOutSine)

        # Sequential animation group
        self.anim_group = QSequentialAnimationGroup()
        self.anim_group.addAnimation(anim_up)
        self.anim_group.addAnimation(anim_down)
        self.anim_group.setLoopCount(-1)  # infinite
        self.anim_group.start()

    # --- Mouse drag to move widget ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # --- Window Setup ---
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(270, 270)
        
        # Container
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 250, 250)
        self.container.setStyleSheet("""
            background-color: white;
            border-radius: 20px;
        """)

        self.opacity_effect = QGraphicsOpacityEffect()
        self.container.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

        # Rounded mask
        path = QPainterPath()
        path.addRoundedRect(0, 0, 250, 250, 15, 15)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.container.setMask(region)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.container.setGraphicsEffect(shadow)

        # --- Load Custom Font ---
        font_path = r"UI\core\assets\fonts\pixelify sans\static\PixelifySans-Regular.ttf"
        #font_path = r"UI\core\assets\fonts\Jersey10-Regular.ttf"
        font_id = QFontDatabase.addApplicationFont(font_path)
        app_font = QFont("Pixelify Sans", 12) if font_id != -1 else QFont("Arial", 12)
        self.setFont(app_font)

        # --- Background ---
        self.bg_label = QLabel(self.container)
        self.bg_label.setGeometry(0, 0, 250, 250)
        self.bg_label.setScaledContents(True)

        # --- Character ---
        self.char_label = QLabel(self.container)
        self.char_label.setGeometry(85, 175, 75, 75)  # bottom-center
        self.char_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.char_label.setScaledContents(True)

        # --- Themes ---
        self.themes = {
            "sunny": {
                "bg": r"UI\core\assets\bg\sunny.png",
                "icon": r"UI\core\assets\icons\sunny icon.png",
                "character": r"UI\core\assets\characters\zoro.png",
                "color": "007E8C",
            },
            "partly cloudy": {
                "bg": r"UI\core\assets\bg\partly cloudy.png",
                "icon": r"UI\core\assets\icons\partly cloudy icon.png",
                "character": r"UI\core\assets\characters\zoro.png",
                "color": "FFB348",
            },
            "cloudy": {
                "bg": r"UI\core\assets\bg\cloudy.png",
                "icon": r"UI\core\assets\icons\cloudy icon.png",
                "character": r"UI\core\assets\characters\zoro.png",
                "color": "FFFFFF",
            },
            "rainy": {
                "bg": r"UI\core\assets\bg\rainy.png",
                "icon": r"UI\core\assets\icons\rainy icon.png",
                "character": r"UI\core\assets\characters\zoro.png",
                "color": "FFFFFF",
            },
            "stormy": {
                "bg": r"UI\core\assets\bg\stormy.png",
                "icon": r"UI\core\assets\icons\stormy icon.png",
                "character": r"UI\core\assets\characters\zoro.png",
                "color": "FFFFFF",
            },
            "snowy": {
                "bg": r"UI\core\assets\bg\snowy.png",
                "icon": r"UI\core\assets\icons\snowy icon.png",
                "character": r"UI\core\assets\characters\zoro.png",
                "color": "4470B2",
            },
            "foggy": {
                "bg": r"UI\core\assets\bg\foggy.png",
                "icon": r"UI\core\assets\icons\foggy icon.png",
                "character": r"UI\core\assets\characters\zoro.png",
                "color": "182E71",
            },
        }

        # Labels
        self.dynamic_labels = []

        #weather layout
        self.weather_info = QLabel("Weather: Sunny", self.container)
        self.weather_info.setGeometry(3, 50, 250, 30)  
        self.weather_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weather_info.setFont(QFont("Pixelify Sans", 11))
        self.weather_info.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.dynamic_labels.append(self.weather_info)

        #temp and humidity layout
        self.temp_humidity = QLabel("21°c | 60 %", self.container)
        self.temp_humidity.setGeometry(3, 65, 250, 30)
        self.temp_humidity.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_humidity.setFont(QFont("Pixelify Sans", 11))
        self.temp_humidity.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.dynamic_labels.append(self.temp_humidity)


        #time layout
        self.time_label = QLabel(self.container)
        self.time_label.setGeometry(5, 5, 75, 15)  # top-left
        self.time_label.setFont(QFont("Pixelify Sans", 7))
        self.dynamic_labels.append(self.time_label)
        self.time_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.update_time()  # set initial time
        
        # Forecast layout
        self.forecast_widget = QWidget(self.container)
        self.forecast_widget.setGeometry(0, 95, 250, 50)
        self.forecast_layout = QGridLayout(self.forecast_widget)
        self.forecast_layout.setContentsMargins(0, 0, 0, 0)
        self.forecast_layout.setSpacing(0)  # remove extra space
        self.forecast_widget.setStyleSheet("background-color: transparent;")

        # equal column stretch
        for i in range(4):
            self.forecast_layout.setColumnStretch(i, 1)

        self.forecast_time_labels = []
        self.forecast_icon_labels = []
        self.forecast_temp_labels = []

        for i in range(4):
            t_label = QLabel("--")
            font = QFont("Pixelify Sans", 9)
            font.setBold(True)  # Make it bold
            t_label.setFont(font)
            t_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.forecast_layout.addWidget(t_label, 0, i)
            self.forecast_time_labels.append(t_label)
            self.dynamic_labels.append(t_label)

            i_label = QLabel()
            i_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.forecast_layout.addWidget(i_label, 1, i)
            self.forecast_icon_labels.append(i_label)


            temp_label = QLabel("--°C")
            temp_label.setFont(QFont("Pixelify Sans", 9))
            temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.forecast_layout.addWidget(temp_label, 2, i)
            self.forecast_temp_labels.append(temp_label)
            self.dynamic_labels.append(temp_label)

        # --- Custom Close & Minimize Buttons ---
        self.close_button = QPushButton("✕", self.container)
        self.close_button.setGeometry(233, 0, 15, 15)  # top-right corner
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 15px;
                color: red;
            }
            QPushButton:hover {
                background-color: rgba(255,0,0,50);
            }
        """)

        self.min_button = QPushButton("–", self.container)
        self.min_button.setGeometry(218, 0, 15, 15)  # left of close
        self.min_button.clicked.connect(self.showMinimized)
        self.min_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
                color: yellow;
            }
            QPushButton:hover {
                background-color: rgba(255,255,0,50);
            }
        """)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # Load weather data
        self.load_weather()

        self.start_character_animation()

    def update_theme(self, theme_name):
        theme = self.themes.get(theme_name, self.themes["cloudy"])

        # Background + Character
        self.bg_label.setPixmap(QPixmap(theme["bg"]))
        self.char_label.setPixmap(QPixmap(theme["character"]))

        # Text color
        text_color = "#" + theme["color"]
        for label in self.dynamic_labels:
            label.setStyleSheet(f"color:{text_color};")

    def update_time(self):
        current_time = QTime.currentTime().toString("hh:mm AP")
        self.time_label.setText(f"TIME: {current_time}")

    def load_weather(self):
        lat, lon, city, country = get_location()
        if not city:
            self.weather_info.setText("Location error ❌")
            return

        current = get_current_weather(city)
        forecast = get_forecast(city)

        if current:
            cond = current["condition"]
            temp = round(current["temp"])
            humidity = current["humidity"]
            self.weather_info.setText(f"Weather: {cond.capitalize()}")
            self.temp_humidity.setText(f"{temp}°C | {humidity}%")
            self.update_theme(cond)

        for i, f in enumerate(forecast[:4]):
            self.forecast_time_labels[i].setText(f["time"])
            self.forecast_temp_labels[i].setText(f"{round(f['temp'])}°C")

            cond = f["condition"]
            icon_path = self.themes[cond]["icon"] if cond in self.themes else self.themes["cloudy"]["icon"]
            pix = QPixmap(icon_path).scaled(13, 13, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            self.forecast_icon_labels[i].setPixmap(pix)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec())
