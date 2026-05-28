import sys
import os
import json
import ctypes
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame,
                             QMessageBox, QScrollArea, QSizePolicy, QLineEdit,
                             QTreeWidget, QTreeWidgetItem, QProgressBar,
                             QDialog, QFormLayout, QComboBox, QDialogButtonBox,
                             QColorDialog, QFileDialog, QSlider)
from PyQt6.QtCore import Qt, QSize, QSharedMemory, QTimer, QUrl
from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap, QPainter, QPainterPath
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

APP_VERSION = "2026.1.1.1H"

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(APP_DIR, filename)

class SystemInfoDLL:
    def __init__(self):
        self.dll = None
        self.load_dll()
    
    def load_dll(self):
        try:
            dll_path = get_path("sys_info.dll")
            if os.path.exists(dll_path):
                self.dll = ctypes.CDLL(dll_path)
                return True
        except Exception:
            pass
        return False
    
    def call_string_function(self, func_name):
        if not self.dll:
            return None
        try:
            func = getattr(self.dll, func_name)
            func.restype = ctypes.c_char_p
            result = func()
            if result:
                return result.decode('utf-8', errors='replace')
        except:
            pass
        return None
    
    def call_json_function(self, func_name):
        result = self.call_string_function(func_name)
        if result:
            try:
                return json.loads(result)
            except:
                pass
        return None
    
    def get_windows_version(self):
        return self.call_string_function('GetWindowsVersion') or "Windows"
    
    def get_disk_info(self):
        return self.call_json_function('GetDiskInfoJson') or []
    
    def get_gpu_info(self):
        return self.call_json_function('GetGPUInfoJson') or []
    
    def get_cpu_info(self):
        return self.call_json_function('GetCPUInfoJson') or {}
    
    def get_ram_info(self):
        return self.call_json_function('GetRAMInfoJson') or {}

class ChangesSysDLL:
    def __init__(self):
        self.dll = None
        self.load_dll()
    
    def load_dll(self):
        try:
            dll_path = get_path("changes_sys.dll")
            if os.path.exists(dll_path):
                self.dll = ctypes.CDLL(dll_path)
                return True
        except Exception:
            pass
        return False
    
    def call_string_function(self, func_name, arg=None):
        if not self.dll:
            return None
        try:
            func = getattr(self.dll, func_name)
            func.restype = ctypes.c_char_p
            if arg:
                func.argtypes = [ctypes.c_char_p]
                result = func(arg.encode('utf-8'))
            else:
                result = func()
            if result:
                return result.decode('utf-8', errors='replace')
        except:
            pass
        return None
    
    def call_json_function(self, func_name, arg=None):
        result = self.call_string_function(func_name, arg)
        if result:
            try:
                return json.loads(result)
            except:
                pass
        return None
    
    def get_startup_entries(self):
        return self.call_json_function('GetStartupEntries') or []
    
    def get_registry_key(self, path):
        return self.call_json_function('GetRegistryKey', path) or []
    
    def get_process_list(self):
        return self.call_json_function('GetProcessList') or []
    
    def get_file_list(self, path):
        return self.call_json_function('GetFileList', path) or []
    
    def get_users_list(self):
        return self.call_json_function('GetUsersList') or []
    
    def get_drivers_list(self):
        return self.call_json_function('GetDriversList') or []
    
    def get_key_locks(self):
        return self.call_json_function('GetKeyLocks') or {}
    
    def set_registry_value(self, key_path, value_name, new_value):
        if not self.dll:
            return False
        try:
            func = self.dll.SetRegistryValue
            func.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
            func.restype = ctypes.c_bool
            return func(key_path.encode('utf-8'), value_name.encode('utf-8'), new_value.encode('utf-8'))
        except:
            return False
    
    def set_startup_value(self, section, name, new_value):
        if not self.dll:
            return False
        try:
            func = self.dll.SetStartupValue
            func.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
            func.restype = ctypes.c_bool
            return func(section.encode('utf-8'), name.encode('utf-8'), new_value.encode('utf-8'))
        except:
            return False
    
    def kill_process(self, pid):
        if not self.dll:
            return False
        try:
            func = self.dll.KillProcess
            func.argtypes = [ctypes.c_ulong]
            func.restype = ctypes.c_bool
            return func(pid)
        except:
            return False
    
    def add_startup_entry(self, section, name, path):
        if not self.dll:
            return False
        try:
            func = self.dll.AddStartupEntry
            func.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
            func.restype = ctypes.c_bool
            return func(section.encode('utf-8'), name.encode('utf-8'), path.encode('utf-8'))
        except:
            return False
    
    def remove_startup_entry(self, section, name):
        if not self.dll:
            return False
        try:
            func = self.dll.RemoveStartupEntry
            func.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
            func.restype = ctypes.c_bool
            return func(section.encode('utf-8'), name.encode('utf-8'))
        except:
            return False
    
    def add_user(self, username, password, is_admin):
        if not self.dll:
            return False
        try:
            func = self.dll.AddUser
            func.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool]
            func.restype = ctypes.c_bool
            return func(username.encode('utf-8'), password.encode('utf-8'), is_admin)
        except:
            return False
    
    def remove_user(self, username):
        if not self.dll:
            return False
        try:
            func = self.dll.RemoveUser
            func.argtypes = [ctypes.c_char_p]
            func.restype = ctypes.c_bool
            return func(username.encode('utf-8'))
        except:
            return False
    
    def set_driver_state(self, service_name, enable):
        if not self.dll:
            return False
        try:
            func = self.dll.SetDriverState
            func.argtypes = [ctypes.c_char_p, ctypes.c_bool]
            func.restype = ctypes.c_bool
            return func(service_name.encode('utf-8'), enable)
        except:
            return False
    
    def delete_driver(self, service_name):
        if not self.dll:
            return False
        try:
            func = self.dll.DeleteDriver
            func.argtypes = [ctypes.c_char_p]
            func.restype = ctypes.c_bool
            return func(service_name.encode('utf-8'))
        except:
            return False
    
    def add_auto_kill(self, process_name):
        if not self.dll:
            return False
        try:
            func = self.dll.AddAutoKillProcess
            func.argtypes = [ctypes.c_char_p]
            func.restype = ctypes.c_bool
            return func(process_name.encode('utf-8'))
        except:
            return False
    
    def unlock_key(self, key_name):
        if not self.dll:
            return False
        try:
            func = self.dll.UnlockKey
            func.argtypes = [ctypes.c_char_p]
            func.restype = ctypes.c_bool
            return func(key_name.encode('utf-8'))
        except:
            return False
    
    def set_wallpaper(self, path):
        if not self.dll:
            return False
        try:
            func = self.dll.SetWallpaper
            func.argtypes = [ctypes.c_char_p]
            func.restype = ctypes.c_bool
            return func(path.encode('utf-8'))
        except:
            return False
    
    def set_accent_color(self, color):
        if not self.dll:
            return False
        try:
            func = self.dll.SetAccentColor
            func.argtypes = [ctypes.c_ulong]
            func.restype = ctypes.c_bool
            return func(color)
        except:
            return False

class PerformanceDLL:
    def __init__(self):
        self.dll = None
        self.load_dll()
    
    def load_dll(self):
        try:
            dll_path = get_path("performance.dll")
            if os.path.exists(dll_path):
                self.dll = ctypes.CDLL(dll_path)
                return True
        except Exception:
            pass
        return False
    
    def call_string_function(self, func_name):
        if not self.dll:
            return None
        try:
            func = getattr(self.dll, func_name)
            func.restype = ctypes.c_char_p
            result = func()
            if result:
                return result.decode('utf-8', errors='replace')
        except:
            pass
        return None
    
    def call_json_function(self, func_name):
        result = self.call_string_function(func_name)
        if result:
            try:
                return json.loads(result)
            except:
                pass
        return None
    
    def run_cpu_benchmark(self):
        return self.call_json_function('RunCPUBenchmark') or {}
    
    def run_ram_benchmark(self):
        return self.call_json_function('RunRAMBenchmark') or {}
    
    def run_full_benchmark(self):
        return self.call_json_function('RunFullBenchmark') or {}
    
    def start_stress_test(self):
        return self.call_json_function('StartStressTest') or {}
    
    def stop_stress_test(self):
        return self.call_json_function('StopStressTest') or {}
    
    def get_stress_test_status(self):
        return self.call_json_function('GetStressTestStatus') or {}

class RoundedImageLabel(QLabel):
    def __init__(self, image_path, size=280, radius=20):
        super().__init__()
        self.setFixedSize(size, size)
        pixmap = QPixmap(image_path).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        rounded = QPixmap(size, size)
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, size, size, radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        self.setPixmap(rounded)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class WinHelperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.system_dll = SystemInfoDLL()
        self.changes_dll = ChangesSysDLL()
        self.performance_dll = PerformanceDLL()
        self.nav_buttons = []
        self.current_content = None
        self.current_registry_value_name = ""
        self.media_player = None
        self.audio_output = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Win Helper")
        self.setGeometry(100, 100, 900, 580)
        
        ico = get_path(os.path.join("icon", "rtx.ico"))
        if os.path.exists(ico):
            self.setWindowIcon(QIcon(ico))
        
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; }
            QWidget { background-color: transparent; }
            QWidget#mainWidget { background-color: #1a1a1a; border: none; }
            QWidget#leftPanel {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 10px; padding: 10px;
                min-width: 220px; max-width: 220px;
            }
            QWidget#rightPanel {
                background-color: rgba(255, 255, 255, 0.03);
                border-radius: 10px; padding: 8px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px; padding: 10px;
                color: white; font-size: 14px;
                text-align: left; min-height: 40px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(96, 205, 255, 0.3);
            }
            QPushButton[active="true"] {
                background-color: rgba(96, 205, 255, 0.2);
                border: 1px solid rgba(96, 205, 255, 0.5);
            }
            QPushButton#playBtn {
                background-color: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
                min-height: 45px;
                min-width: 120px;
                max-width: 120px;
                text-align: center;
            }
            QPushButton#playBtn:hover {
                background-color: rgba(255, 255, 255, 0.25);
                border: 2px solid rgba(96, 205, 255, 0.5);
            }
            QLabel { background-color: transparent; }
            QLabel#titleLabel {
                color: white; font-size: 20px; font-weight: bold; padding: 8px;
            }
            QLabel#sectionLabel {
                color: white; font-size: 16px; font-weight: bold; padding: 8px;
            }
            QFrame#infoBox {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px; padding: 12px;
            }
            QFrame#infoBox QLabel {
                color: white; font-size: 12px;
            }
            QScrollArea {
                border: none; background-color: transparent;
            }
            QScrollArea QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.05);
                width: 6px; border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 3px; min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QTreeWidget {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                color: white; font-size: 11px;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QTreeWidget::item:hover {
                background-color: rgba(96, 205, 255, 0.1);
            }
            QTreeWidget QHeaderView::section {
                background-color: rgba(255, 255, 255, 0.1);
                color: white; padding: 4px;
                border: none; font-weight: bold;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                color: white; padding: 6px; font-size: 12px;
            }
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                text-align: center; color: white; font-size: 11px;
                max-height: 15px;
            }
            QProgressBar::chunk {
                background-color: rgba(96, 205, 255, 0.7);
                border-radius: 3px;
            }
            QSlider::groove:horizontal {
                background: rgba(255, 255, 255, 0.1);
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: rgba(96, 205, 255, 0.7);
                border-radius: 2px;
            }
        """)
        
        main_widget = QWidget()
        main_widget.setObjectName("mainWidget")
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        self.right_panel = self.create_right_panel()
        main_layout.addWidget(self.right_panel, 1)
        
        self.show_system_info()
        
    def create_left_panel(self):
        left_widget = QWidget()
        left_widget.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(4)
        
        title_label = QLabel("Win Helper")
        title_label.setObjectName("titleLabel")
        left_layout.addWidget(title_label)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: rgba(255, 255, 255, 0.1);")
        left_layout.addWidget(separator)
        
        self.system_btn = self.create_nav_button("O системе", "rtx.ico")
        self.system_btn.clicked.connect(lambda: self.set_active_section("system"))
        left_layout.addWidget(self.system_btn)
        self.nav_buttons.append(("system", self.system_btn))
        
        self.editor_btn = self.create_nav_button("Редактор системы", "comm.ico")
        self.editor_btn.clicked.connect(lambda: self.set_active_section("editor"))
        left_layout.addWidget(self.editor_btn)
        self.nav_buttons.append(("editor_menu", self.editor_btn))
        
        self.about_btn = self.create_nav_button("O программе", "about.ico")
        self.about_btn.clicked.connect(lambda: self.set_active_section("about"))
        left_layout.addWidget(self.about_btn)
        self.nav_buttons.append(("about", self.about_btn))
        
        left_layout.addStretch()
        return left_widget
    
    def create_nav_button(self, text, icon_name):
        btn = QPushButton()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        icon_label = QLabel()
        ico_path = get_path(os.path.join("icon", icon_name))
        if os.path.exists(ico_path):
            pixmap = QIcon(ico_path).pixmap(QSize(20, 20))
            if not pixmap.isNull():
                icon_label.setPixmap(pixmap)
        icon_label.setFixedWidth(26)
        layout.addWidget(icon_label)
        
        text_label = QLabel(text)
        text_label.setStyleSheet("background: transparent; color: white; border: none; font-size: 13px;")
        layout.addWidget(text_label)
        layout.addStretch()
        
        btn.setLayout(layout)
        return btn
    
    def set_active_section(self, section):
        for sec, btn in self.nav_buttons:
            btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        target = "editor_menu" if section == "editor" else section
        for sec, btn in self.nav_buttons:
            if sec == target:
                btn.setProperty("active", "true")
                btn.style().unpolish(btn)
                btn.style().polish(btn)
        
        self.show_section(section)
    
    def create_right_panel(self):
        right_panel = QWidget()
        right_panel.setObjectName("rightPanel")
        self.right_layout = QVBoxLayout(right_panel)
        self.right_layout.setContentsMargins(5, 5, 5, 5)
        self.right_layout.setSpacing(8)
        
        self.section_label = QLabel("Информация о системе")
        self.section_label.setObjectName("sectionLabel")
        self.right_layout.addWidget(self.section_label)
        
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.right_layout.addWidget(self.content_area, 1)
        
        return right_panel
    
    def clear_content(self):
        self.stop_music()
        if self.current_content:
            self.current_content.setParent(None)
            self.current_content.deleteLater()
            self.current_content = None
        
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
    
    def set_content_widget(self, widget):
        self.clear_content()
        self.current_content = widget
        self.content_layout.addWidget(widget)
    
    def show_section(self, section):
        if section == "system":
            self.show_system_info()
        elif section == "editor":
            self.show_editor_menu()
        elif section == "about":
            self.show_about_info()
    
    def show_system_info(self):
        self.section_label.setText("Информация о системе")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        self.btn_info = QPushButton("Информация")
        self.btn_info.clicked.connect(lambda: self.show_system_content("info"))
        self.btn_info.setMinimumHeight(45)
        layout.addWidget(self.btn_info)
        
        self.btn_stress = QPushButton("Стресс тест")
        self.btn_stress.clicked.connect(lambda: self.show_system_content("stress"))
        self.btn_stress.setMinimumHeight(45)
        layout.addWidget(self.btn_stress)
        
        layout.addStretch()
        
        self.set_content_widget(widget)
    
    def show_system_content(self, content_type):
        self.btn_info.setProperty("active", "false")
        self.btn_stress.setProperty("active", "false")
        self.btn_info.style().unpolish(self.btn_info)
        self.btn_info.style().polish(self.btn_info)
        self.btn_stress.style().unpolish(self.btn_stress)
        self.btn_stress.style().polish(self.btn_stress)
        
        if content_type == "info":
            self.btn_info.setProperty("active", "true")
            self.btn_info.style().unpolish(self.btn_info)
            self.btn_info.style().polish(self.btn_info)
            self.show_system_information()
        elif content_type == "stress":
            self.btn_stress.setProperty("active", "true")
            self.btn_stress.style().unpolish(self.btn_stress)
            self.btn_stress.style().polish(self.btn_stress)
            self.show_stress_test()
    
    def show_system_information(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)
        
        version = self.system_dll.get_windows_version()
        box = self.create_info_box("Windows", [
            f"Версия: {version}",
            "Поддерживаемые версии: Windows 11, 10, 8, 7"
        ], "win.ico")
        scroll_layout.addWidget(box)
        scroll_layout.addWidget(self.create_separator())
        
        cpu = self.system_dll.get_cpu_info()
        if cpu:
            temp = cpu.get('temperature', 0)
            box = self.create_info_box("Процессор", [
                f"Модель: {cpu.get('name', 'Unknown')}",
                f"Ядер: {cpu.get('cores', 0)}",
                f"Частота: {cpu.get('frequency', 0)} MHz",
                f"Загрузка: {cpu.get('usage', 0):.1f}%",
                f"Температура: {temp:.1f} C"
            ], "process.ico")
            scroll_layout.addWidget(box)
            scroll_layout.addWidget(self.create_separator())
        
        disks = self.system_dll.get_disk_info()
        if disks:
            for disk in disks:
                disk_type = "SSD" if disk.get('ssd', False) else "HDD"
                icon = "ssd.ico" if disk.get('ssd', False) else None
                box = self.create_info_box(
                    f"Диск {disk.get('drive', 'Unknown')}: {disk_type}",
                    [
                        f"Общий объем: {disk.get('total', 0):.1f} GB",
                        f"Свободно: {disk.get('free', 0):.1f} GB",
                        f"Занято: {disk.get('used', 0):.1f} GB"
                    ],
                    icon
                )
                scroll_layout.addWidget(box)
            scroll_layout.addWidget(self.create_separator())
        
        gpus = self.system_dll.get_gpu_info()
        if gpus:
            for gpu in gpus:
                box = self.create_info_box("Видеокарта", [
                    f"Модель: {gpu.get('name', 'Unknown')}",
                    f"Видеопамять: {gpu.get('vram', 0):.1f} GB"
                ], "videom.ico")
                scroll_layout.addWidget(box)
            scroll_layout.addWidget(self.create_separator())
        
        ram = self.system_dll.get_ram_info()
        if ram:
            box = self.create_info_box("Оперативная память", [
                f"Тип: DDR{ram.get('ddr', 4)} {ram.get('frequency', 3200)} MHz",
                f"Общий объем: {ram.get('total', 0):.1f} GB",
                f"Занято: {ram.get('used', 0):.1f} GB",
                f"Свободно: {ram.get('free', 0):.1f} GB"
            ], "ozy.ico")
            scroll_layout.addWidget(box)
        
        scroll_layout.addWidget(self.create_separator())
        
        version_box = QFrame()
        version_box.setObjectName("infoBox")
        version_box.setStyleSheet("QFrame#infoBox { background-color: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 12px; } QFrame#infoBox QLabel { color: white; font-size: 12px; background-color: transparent; }")
        version_layout = QVBoxLayout(version_box)
        version_layout.setSpacing(4)
        version_title = QLabel("О приложении")
        version_title.setStyleSheet("color: white; font-size: 14px; font-weight: bold; background-color: transparent;")
        version_layout.addWidget(version_title)
        version_label = QLabel(f"Версия: {APP_VERSION}")
        version_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 12px; background-color: transparent;")
        version_layout.addWidget(version_label)
        scroll_layout.addWidget(version_box)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.set_content_widget(widget)
    
    def create_info_box(self, title, content, icon_name=None):
        box = QFrame()
        box.setObjectName("infoBox")
        box.setStyleSheet("QFrame#infoBox { background-color: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 12px; } QFrame#infoBox QLabel { color: white; font-size: 12px; background-color: transparent; }")
        layout = QVBoxLayout(box)
        layout.setSpacing(6)
        
        header_layout = QHBoxLayout()
        
        if icon_name:
            ico_path = get_path(os.path.join("icon", icon_name))
            if os.path.exists(ico_path):
                icon_label = QLabel()
                pixmap = QIcon(ico_path).pixmap(QSize(28, 28))
                if not pixmap.isNull():
                    icon_label.setPixmap(pixmap)
                    icon_label.setFixedWidth(36)
                    header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; background-color: transparent;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        for line in content:
            label = QLabel(line)
            label.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 12px; background-color: transparent;")
            label.setWordWrap(True)
            layout.addWidget(label)
        
        return box
    
    def create_separator(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: rgba(255, 255, 255, 0.08); margin: 3px 0px;")
        return sep
    
    def show_editor_menu(self):
        self.section_label.setText("Редактор системы")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(6)
        
        buttons = [
            ("Автозагрузка", self.show_startup),
            ("Редактор реестра", self.show_registry_editor),
            ("Проводник", self.show_file_explorer),
            ("Процессы", self.show_processes),
            ("Пользователи", self.show_users),
            ("Драйвера", self.show_drivers),
            ("Персонализация", self.show_personalization),
            ("Разблокировка", self.show_unlock_keys),
            ("Обходы вирусов", self.show_virus_bypass),
        ]
        
        for text, handler in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            btn.setMinimumHeight(38)
            layout.addWidget(btn)
        
        layout.addStretch()
        self.set_content_widget(widget)
    
    def show_personalization(self):
        self.section_label.setText("Персонализация")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        color_btn = QPushButton("Изменить цвет Windows")
        color_btn.clicked.connect(self.change_accent_color)
        layout.addWidget(color_btn)
        
        wallpaper_btn = QPushButton("Установить обои")
        wallpaper_btn.clicked.connect(self.set_wallpaper_dialog)
        layout.addWidget(wallpaper_btn)
        
        default_wallpaper_btn = QPushButton("Стандартные обои Windows")
        default_wallpaper_btn.clicked.connect(self.set_default_wallpaper)
        layout.addWidget(default_wallpaper_btn)
        
        layout.addStretch()
        self.set_content_widget(widget)
    
    def change_accent_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            rgb = (color.red() << 16) | (color.green() << 8) | color.blue()
            if self.changes_dll.set_accent_color(rgb):
                QMessageBox.information(self, "Успех", "Цвет Windows изменен. Перезайдите в систему для применения.")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось изменить цвет")
    
    def set_wallpaper_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.jpg *.png *.bmp)")
        if file_path:
            if self.changes_dll.set_wallpaper(file_path):
                QMessageBox.information(self, "Успех", "Обои установлены")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось установить обои")
    
    def set_default_wallpaper(self):
        default_path = "C:\\Windows\\Web\\Wallpaper\\Windows\\img0.jpg"
        if os.path.exists(default_path):
            if self.changes_dll.set_wallpaper(default_path):
                QMessageBox.information(self, "Успех", "Стандартные обои установлены")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось установить обои")
        else:
            QMessageBox.warning(self, "Ошибка", "Стандартные обои не найдены")
    
    def show_unlock_keys(self):
        self.section_label.setText("Разблокировка клавиш")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        locks = self.changes_dll.get_key_locks()
        
        keys = [
            ("Ctrl+Alt+Del", "ctrlaltdel"),
            ("Ctrl+Shift+Esc", "ctrlshiftesc"),
            ("Диспетчер задач", "taskmgr"),
            ("Редактор реестра", "regedit"),
            ("Командная строка", "cmd"),
        ]
        
        for display_name, key_name in keys:
            is_locked = locks.get(key_name, False)
            status = "ЗАБЛОКИРОВАНО" if is_locked else "Разблокировано"
            status_color = "#ff5252" if is_locked else "#4caf50"
            
            key_widget = QWidget()
            key_layout = QHBoxLayout(key_widget)
            key_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(f"{display_name}: <span style='color:{status_color};'>{status}</span>")
            label.setStyleSheet(f"color: white; font-size: 13px;")
            key_layout.addWidget(label)
            
            if is_locked:
                unlock_btn = QPushButton("Разблокировать")
                unlock_btn.setFixedWidth(130)
                unlock_btn.clicked.connect(lambda checked, k=key_name: self.unlock_specific_key(k))
                key_layout.addWidget(unlock_btn)
            
            key_layout.addStretch()
            layout.addWidget(key_widget)
        
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.show_unlock_keys)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        self.set_content_widget(widget)
    
    def unlock_specific_key(self, key_name):
        if self.changes_dll.unlock_key(key_name):
            QMessageBox.information(self, "Успех", "Клавиша разблокирована")
            self.show_unlock_keys()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось разблокировать")
    
    def show_virus_bypass(self):
        self.section_label.setText("Обходы вирусов")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(6)
        
        btn_auto_kill = QPushButton("Авто отключение программы")
        btn_auto_kill.clicked.connect(self.show_auto_kill)
        layout.addWidget(btn_auto_kill)
        
        btn_auto_start = QPushButton("Авто запуск программы поверх всего")
        btn_auto_start.clicked.connect(self.show_auto_start)
        layout.addWidget(btn_auto_start)
        
        btn_gribi = QPushButton("Грибы")
        btn_gribi.clicked.connect(self.show_gribi)
        layout.addWidget(btn_gribi)
        
        layout.addStretch()
        self.set_content_widget(widget)
    
    def show_gribi(self):
        self.stop_music()
        self.section_label.setText("Грибы")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        
        layout.addStretch()
        
        img_path = get_path(os.path.join("icon", "gribi.png"))
        if os.path.exists(img_path):
            img_label = RoundedImageLabel(img_path, 220, 16)
            layout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel("Тает лёд")
        title_label.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel("Грибы, Sимптом")
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.45); font-size: 16px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        self.btn_player = QPushButton("PLAY")
        self.btn_player.setObjectName("playBtn")
        self.btn_player.clicked.connect(self.toggle_music)
        layout.addWidget(self.btn_player, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.music_slider = QSlider(Qt.Orientation.Horizontal)
        self.music_slider.setRange(0, 100)
        self.music_slider.setValue(0)
        self.music_slider.setFixedWidth(300)
        self.music_slider.sliderMoved.connect(self.seek_music)
        layout.addWidget(self.music_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setStyleSheet("color: rgba(255, 255, 255, 0.4); font-size: 11px;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)
        
        layout.addStretch()
        
        scroll.setWidget(scroll_content)
        self.init_music_player()
        self.set_content_widget(scroll)
    
    def init_music_player(self):
        mp3_path = get_path(os.path.join("sounds", "taetled.mp3"))
        if not os.path.exists(mp3_path):
            return
        
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setSource(QUrl.fromLocalFile(mp3_path))
        
        self.media_player.positionChanged.connect(self.update_music_position)
        self.media_player.durationChanged.connect(self.update_music_duration)
        self.media_player.playbackStateChanged.connect(self.update_play_button)
    
    def toggle_music(self):
        if not self.media_player:
            return
        
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def stop_music(self):
        if self.media_player:
            self.media_player.stop()
            self.media_player.setPosition(0)
    
    def seek_music(self, position):
        if self.media_player and self.media_player.duration() > 0:
            new_pos = int(position / 100.0 * self.media_player.duration())
            self.media_player.setPosition(new_pos)
    
    def update_music_position(self, position):
        if self.media_player and self.media_player.duration() > 0:
            slider_pos = int(position / self.media_player.duration() * 100)
            self.music_slider.blockSignals(True)
            self.music_slider.setValue(slider_pos)
            self.music_slider.blockSignals(False)
            
            pos_sec = position // 1000
            dur_sec = self.media_player.duration() // 1000
            self.time_label.setText(f"{pos_sec//60}:{pos_sec%60:02d} / {dur_sec//60}:{dur_sec%60:02d}")
    
    def update_music_duration(self, duration):
        pass
    
    def update_play_button(self, state):
        if hasattr(self, 'btn_player'):
            if state == QMediaPlayer.PlaybackState.PlayingState:
                self.btn_player.setText("PAUSE")
            else:
                self.btn_player.setText("PLAY")
    
    def show_auto_kill(self):
        self.section_label.setText("Авто отключение программы")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        info = QLabel("Укажите процессы для автоматического завершения при запуске Windows\n"
                       "Они будут добавлены в Winlogon и завершаться при каждом запуске")
        info.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        input_layout = QHBoxLayout()
        self.kill_process_input = QLineEdit()
        self.kill_process_input.setPlaceholderText("notepad.exe")
        input_layout.addWidget(self.kill_process_input)
        
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_auto_kill_process)
        input_layout.addWidget(add_btn)
        
        layout.addLayout(input_layout)
        
        layout.addStretch()
        self.set_content_widget(widget)
    
    def add_auto_kill_process(self):
        process_name = self.kill_process_input.text().strip()
        if not process_name:
            QMessageBox.warning(self, "Ошибка", "Введите имя процесса")
            return
        
        if self.changes_dll.add_auto_kill(process_name):
            QMessageBox.information(self, "Успех", f"Процесс {process_name} будет завершаться при запуске")
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить правило")
    
    def show_auto_start(self):
        self.section_label.setText("Авто запуск программы поверх всего")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        info = QLabel("Программа определит своё местоположение и запустится при логине\n"
                       "с обходом ограничений безопасности Windows")
        info.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        add_btn = QPushButton("Добавить в автозапуск")
        add_btn.clicked.connect(self.add_self_to_startup)
        layout.addWidget(add_btn)
        
        layout.addStretch()
        self.set_content_widget(widget)
    
    def add_self_to_startup(self):
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        if self.changes_dll.add_startup_entry("Run", "WinHelperAutoStart", exe_path):
            QMessageBox.information(self, "Успех", "Программа добавлена в автозапуск")
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить в автозапуск")
    
    def show_startup(self):
        self.section_label.setText("Автозагрузка")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(5)
        
        entries = self.changes_dll.get_startup_entries()
        
        sections = {}
        for entry in entries:
            section = entry.get('section', 'Other')
            if section not in sections:
                sections[section] = []
            sections[section].append(entry)
        
        tree = QTreeWidget()
        tree.setHeaderLabels(["Имя", "Путь", "Статус"])
        tree.setColumnWidth(0, 180)
        tree.setColumnWidth(1, 350)
        tree.setColumnWidth(2, 60)
        self.startup_tree = tree
        
        section_order = ["Winlogon", "AppInit", "Run", "RunOnce", "IE", "ShellExt", "BHO"]
        
        for section_name in section_order:
            if section_name in sections:
                section_item = QTreeWidgetItem(tree, [section_name, "", ""])
                section_item.setForeground(0, QColor(96, 205, 255))
                section_item.setFlags(section_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                
                for entry in sections[section_name]:
                    item = QTreeWidgetItem(section_item, [
                        entry.get('name', ''),
                        entry.get('path', ''),
                        "Вкл" if entry.get('enabled', True) else "Откл"
                    ])
                    item.setData(0, Qt.ItemDataRole.UserRole, section_name)
        
        layout.addWidget(tree)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_startup_dialog)
        btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Изменить")
        edit_btn.clicked.connect(self.edit_startup_entry)
        btn_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("Удалить")
        remove_btn.clicked.connect(self.remove_startup_entry)
        btn_layout.addWidget(remove_btn)
        
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.show_startup)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        scroll.setWidget(scroll_content)
        self.set_content_widget(scroll)
    
    def edit_startup_entry(self):
        if not hasattr(self, 'startup_tree'):
            return
        
        selected = self.startup_tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для изменения")
            return
        
        item = selected[0]
        if not item.parent():
            return
        
        name = item.text(0)
        section = item.data(0, Qt.ItemDataRole.UserRole)
        current_path = item.text(1)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Изменить значение")
        dialog.setStyleSheet("""
            QDialog { background-color: #2a2a2a; }
            QLabel { color: white; }
            QLineEdit { background-color: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 5px; color: white; padding: 5px; }
            QPushButton { background-color: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.1); border-radius: 5px; color: white; padding: 8px 16px; }
        """)
        
        layout = QFormLayout(dialog)
        layout.addRow("Раздел:", QLabel(section))
        layout.addRow("Имя:", QLabel(name))
        
        path_edit = QLineEdit(current_path)
        layout.addRow("Новое значение:", path_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_value = path_edit.text()
            if new_value and self.changes_dll.set_startup_value(section, name, new_value):
                QMessageBox.information(self, "Успех", "Значение изменено")
                self.show_startup()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось изменить значение")
    
    def add_startup_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить автозагрузку")
        dialog.setStyleSheet("""
            QDialog { background-color: #2a2a2a; }
            QLabel { color: white; }
            QLineEdit { background-color: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 5px; color: white; padding: 5px; }
            QComboBox { background-color: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 5px; color: white; padding: 5px; }
            QComboBox QAbstractItemView { background-color: #2a2a2a; color: white; }
            QPushButton { background-color: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.1); border-radius: 5px; color: white; padding: 8px 16px; }
        """)
        
        layout = QFormLayout(dialog)
        
        section_combo = QComboBox()
        section_combo.addItems(["Run", "RunOnce"])
        layout.addRow("Раздел:", section_combo)
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Название программы")
        layout.addRow("Имя:", name_edit)
        
        path_edit = QLineEdit()
        path_edit.setPlaceholderText("C:\\Program Files\\App\\app.exe")
        layout.addRow("Путь:", path_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            section = section_combo.currentText()
            name = name_edit.text()
            path = path_edit.text()
            
            if name and path:
                if self.changes_dll.add_startup_entry(section, name, path):
                    QMessageBox.information(self, "Успех", f"Запись '{name}' добавлена")
                    self.show_startup()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось добавить запись")
    
    def remove_startup_entry(self):
        if not hasattr(self, 'startup_tree'):
            return
        
        selected = self.startup_tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
            return
        
        item = selected[0]
        if not item.parent():
            return
        
        name = item.text(0)
        section = item.data(0, Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, 'Подтверждение', f'Удалить запись "{name}" из раздела {section}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.changes_dll.remove_startup_entry(section, name):
                QMessageBox.information(self, "Успех", f"Запись '{name}' удалена")
                self.show_startup()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить запись")
    
    def show_registry_editor(self):
        self.section_label.setText("Редактор реестра")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        
        addr_layout = QHBoxLayout()
        self.reg_path = QLineEdit("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion")
        addr_layout.addWidget(self.reg_path)
        
        go_btn = QPushButton("Перейти")
        go_btn.setFixedWidth(70)
        go_btn.clicked.connect(lambda: self.load_registry())
        addr_layout.addWidget(go_btn)
        
        layout.addLayout(addr_layout)
        
        self.reg_tree = QTreeWidget()
        self.reg_tree.setHeaderLabels(["Имя", "Тип", "Значение"])
        self.reg_tree.setColumnWidth(0, 180)
        self.reg_tree.setColumnWidth(1, 100)
        self.reg_tree.itemDoubleClicked.connect(self.on_registry_item_double_clicked)
        layout.addWidget(self.reg_tree)
        
        edit_layout = QHBoxLayout()
        edit_layout.addWidget(QLabel("Новое значение:"))
        self.reg_value_edit = QLineEdit()
        edit_layout.addWidget(self.reg_value_edit)
        
        self.reg_save_btn = QPushButton("OK")
        self.reg_save_btn.setFixedWidth(50)
        self.reg_save_btn.clicked.connect(self.save_registry_value)
        edit_layout.addWidget(self.reg_save_btn)
        
        layout.addLayout(edit_layout)
        
        self.reg_info_label = QLabel("")
        self.reg_info_label.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 11px;")
        layout.addWidget(self.reg_info_label)
        
        self.set_content_widget(widget)
        self.current_registry_value_name = ""
        self.load_registry()
    
    def load_registry(self):
        path = self.reg_path.text()
        keys = self.changes_dll.get_registry_key(path)
        
        self.reg_tree.clear()
        if keys:
            for key in keys:
                item = QTreeWidgetItem(self.reg_tree, [
                    key.get('name', ''),
                    key.get('type', ''),
                    key.get('value', '')
                ])
                if key.get('type') == 'Key':
                    item.setForeground(0, QColor(100, 200, 255))
    
    def on_registry_item_double_clicked(self, item):
        item_type = item.text(1)
        item_name = item.text(0)
        item_value = item.text(2)
        
        if item_type == 'Key':
            current_path = self.reg_path.text()
            new_path = current_path + "\\" + item_name
            self.reg_path.setText(new_path)
            self.load_registry()
        else:
            self.reg_value_edit.setText(item_value)
            self.reg_value_edit.setFocus()
            self.current_registry_value_name = item_name
            self.reg_info_label.setText(f"Редактирование: {item_name} (тип: {item_type})")
    
    def save_registry_value(self):
        if not self.current_registry_value_name:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите значение для редактирования")
            return
        
        new_value = self.reg_value_edit.text()
        key_path = self.reg_path.text()
        
        if self.changes_dll.set_registry_value(key_path, self.current_registry_value_name, new_value):
            QMessageBox.information(self, "Успех", f"Значение '{self.current_registry_value_name}' сохранено")
            self.load_registry()
            self.reg_info_label.setText(f"Значение сохранено: {new_value}")
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить значение")
    
    def show_file_explorer(self):
        self.section_label.setText("Проводник")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        
        addr_layout = QHBoxLayout()
        self.file_path = QLineEdit("C:\\Windows")
        addr_layout.addWidget(self.file_path)
        
        go_btn = QPushButton("Перейти")
        go_btn.setFixedWidth(70)
        go_btn.clicked.connect(lambda: self.load_files())
        addr_layout.addWidget(go_btn)
        
        up_btn = QPushButton("Вверх")
        up_btn.setFixedWidth(55)
        up_btn.clicked.connect(self.go_up_directory)
        addr_layout.addWidget(up_btn)
        
        layout.addLayout(addr_layout)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Имя", "Тип", "Размер (KB)"])
        self.file_tree.setColumnWidth(0, 280)
        self.file_tree.setColumnWidth(1, 90)
        self.file_tree.itemDoubleClicked.connect(self.on_file_double_clicked)
        layout.addWidget(self.file_tree)
        
        self.set_content_widget(widget)
        self.load_files()
    
    def load_files(self):
        path = self.file_path.text()
        files = self.changes_dll.get_file_list(path)
        
        self.file_tree.clear()
        if files:
            for file in files:
                item = QTreeWidgetItem(self.file_tree, [
                    file.get('name', ''),
                    file.get('type', ''),
                    f"{file.get('size', 0):.1f}"
                ])
                if file.get('type') == 'Directory':
                    item.setForeground(0, QColor(100, 200, 255))
    
    def go_up_directory(self):
        current = self.file_path.text().rstrip('\\')
        parent = os.path.dirname(current)
        if parent and parent != current:
            self.file_path.setText(parent)
            self.load_files()
    
    def on_file_double_clicked(self, item):
        if item.text(1) == 'Directory':
            current = self.file_path.text().rstrip('\\')
            new_path = os.path.join(current, item.text(0))
            self.file_path.setText(new_path)
            self.load_files()
    
    def show_processes(self):
        self.section_label.setText("Процессы")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        
        processes = self.changes_dll.get_process_list()
        
        tree = QTreeWidget()
        tree.setHeaderLabels(["Имя", "PID", "Потоки", "Память (MB)", "Тип"])
        tree.setColumnWidth(0, 180)
        tree.setColumnWidth(1, 60)
        tree.setColumnWidth(2, 60)
        tree.setColumnWidth(3, 90)
        tree.setColumnWidth(4, 70)
        
        self.process_tree = tree
        
        if processes:
            for proc in processes:
                proc_type = proc.get('type', 'User')
                item = QTreeWidgetItem([
                    proc.get('name', ''),
                    str(proc.get('pid', 0)),
                    str(proc.get('threads', 0)),
                    f"{proc.get('memory', 0):.1f}",
                    proc_type
                ])
                
                if proc_type == 'System':
                    for col in range(5):
                        item.setForeground(col, QColor(255, 255, 100))
                elif proc_type == 'Hidden':
                    for col in range(5):
                        item.setForeground(col, QColor(255, 100, 100))
                
                tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        
        btn_layout = QHBoxLayout()
        kill_btn = QPushButton("Завершить процесс")
        kill_btn.clicked.connect(self.kill_selected_process)
        btn_layout.addWidget(kill_btn)
        
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.show_processes)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.set_content_widget(widget)
    
    def kill_selected_process(self):
        if not hasattr(self, 'process_tree'):
            return
        
        selected = self.process_tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите процесс для завершения")
            return
        
        item = selected[0]
        proc_name = item.text(0)
        proc_pid = int(item.text(1))
        proc_type = item.text(4)
        
        if proc_type == 'System':
            QMessageBox.warning(self, "Ошибка", f"Нельзя завершить системный процесс: {proc_name}")
            return
        
        reply = QMessageBox.question(self, 'Подтверждение', f'Завершить {proc_name} (PID: {proc_pid})?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.changes_dll.kill_process(proc_pid):
                QMessageBox.information(self, "Успех", f"Процесс {proc_name} завершен")
                self.show_processes()
            else:
                QMessageBox.critical(self, "Ошибка", f"Не удалось завершить процесс {proc_name}")
    
    def show_users(self):
        self.section_label.setText("Пользователи")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        
        users = self.changes_dll.get_users_list()
        
        tree = QTreeWidget()
        tree.setHeaderLabels(["Имя", "Тип"])
        tree.setColumnWidth(0, 180)
        tree.setColumnWidth(1, 90)
        self.users_tree = tree
        
        sections = {"System": [], "Admin": [], "User": [], "Disabled": []}
        
        for user in users:
            user_type = user.get('type', 'User')
            if user_type not in sections:
                sections[user_type] = []
            sections[user_type].append(user)
        
        section_names = {"System": "Системные", "Admin": "Администраторы", "User": "Обычные пользователи", "Disabled": "Отключенные"}
        
        for section_key, section_title in section_names.items():
            if sections[section_key]:
                section_item = QTreeWidgetItem(tree, [section_title, ""])
                section_item.setForeground(0, QColor(96, 205, 255))
                section_item.setFlags(section_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                
                for user in sections[section_key]:
                    QTreeWidgetItem(section_item, [user.get('name', ''), user.get('type', '')])
        
        layout.addWidget(tree)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self.add_user_dialog)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Удалить")
        remove_btn.clicked.connect(self.remove_selected_user)
        btn_layout.addWidget(remove_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.set_content_widget(widget)
    
    def add_user_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить пользователя")
        dialog.setStyleSheet("""
            QDialog { background-color: #2a2a2a; }
            QLabel { color: white; }
            QLineEdit { background-color: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 5px; color: white; padding: 5px; }
            QComboBox { background-color: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 5px; color: white; padding: 5px; }
            QComboBox QAbstractItemView { background-color: #2a2a2a; color: white; }
            QPushButton { background-color: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.1); border-radius: 5px; color: white; padding: 8px 16px; }
        """)
        
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        layout.addRow("Имя:", name_edit)
        
        pass_edit = QLineEdit()
        pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Пароль:", pass_edit)
        
        type_combo = QComboBox()
        type_combo.addItems(["Обычный", "Администратор"])
        layout.addRow("Тип:", type_combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = name_edit.text()
            password = pass_edit.text()
            is_admin = type_combo.currentText() == "Администратор"
            
            if name and password:
                if self.changes_dll.add_user(name, password, is_admin):
                    QMessageBox.information(self, "Успех", f"Пользователь '{name}' создан")
                    self.show_users()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось создать пользователя")
    
    def remove_selected_user(self):
        if not hasattr(self, 'users_tree'):
            return
        
        selected = self.users_tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя")
            return
        
        item = selected[0]
        if not item.parent():
            return
        
        username = item.text(0)
        
        reply = QMessageBox.question(self, 'Подтверждение', f'Удалить пользователя {username}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.changes_dll.remove_user(username):
                QMessageBox.information(self, "Успех", f"Пользователь '{username}' удален")
                self.show_users()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить пользователя")
    
    def show_drivers(self):
        self.section_label.setText("Драйвера")
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        
        drivers = self.changes_dll.get_drivers_list()
        
        tree = QTreeWidget()
        tree.setHeaderLabels(["Имя", "Служба", "Путь", "Статус", "Подпись"])
        tree.setColumnWidth(0, 160)
        tree.setColumnWidth(1, 110)
        tree.setColumnWidth(2, 220)
        tree.setColumnWidth(3, 70)
        tree.setColumnWidth(4, 70)
        self.drivers_tree = tree
        
        signed_drivers = []
        unsigned_drivers = []
        
        for driver in drivers:
            if driver.get('signed', '') == 'Unsigned':
                unsigned_drivers.append(driver)
            else:
                signed_drivers.append(driver)
        
        if signed_drivers:
            signed_item = QTreeWidgetItem(tree, ["Подписанные драйвера", "", "", "", ""])
            signed_item.setForeground(0, QColor(76, 175, 80))
            signed_item.setFlags(signed_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            
            for driver in signed_drivers:
                QTreeWidgetItem(signed_item, [
                    driver.get('name', ''),
                    driver.get('service', ''),
                    driver.get('path', ''),
                    driver.get('status', ''),
                    driver.get('signed', '')
                ])
        
        if unsigned_drivers:
            unsigned_item = QTreeWidgetItem(tree, ["Не подписанные драйвера", "", "", "", ""])
            unsigned_item.setForeground(0, QColor(255, 152, 0))
            unsigned_item.setFlags(unsigned_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            
            for driver in unsigned_drivers:
                QTreeWidgetItem(unsigned_item, [
                    driver.get('name', ''),
                    driver.get('service', ''),
                    driver.get('path', ''),
                    driver.get('status', ''),
                    driver.get('signed', '')
                ])
        
        layout.addWidget(tree)
        
        btn_layout = QHBoxLayout()
        enable_btn = QPushButton("Включить")
        enable_btn.clicked.connect(lambda: self.set_driver_state(True))
        btn_layout.addWidget(enable_btn)
        
        disable_btn = QPushButton("Отключить")
        disable_btn.clicked.connect(lambda: self.set_driver_state(False))
        btn_layout.addWidget(disable_btn)
        
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_selected_driver)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.set_content_widget(widget)
    
    def set_driver_state(self, enable):
        if not hasattr(self, 'drivers_tree'):
            return
        
        selected = self.drivers_tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите драйвер")
            return
        
        item = selected[0]
        if not item.parent():
            return
        
        service_name = item.text(1)
        
        if self.changes_dll.set_driver_state(service_name, enable):
            action = "включен" if enable else "отключен"
            QMessageBox.information(self, "Успех", f"Драйвер {action}")
            self.show_drivers()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось изменить состояние драйвера")
    
    def delete_selected_driver(self):
        if not hasattr(self, 'drivers_tree'):
            return
        
        selected = self.drivers_tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите драйвер")
            return
        
        item = selected[0]
        if not item.parent():
            return
        
        service_name = item.text(1)
        
        reply = QMessageBox.question(self, 'Подтверждение', f'Удалить драйвер {service_name}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.changes_dll.delete_driver(service_name):
                QMessageBox.information(self, "Успех", "Драйвер удален")
                self.show_drivers()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить драйвер")
    
    def show_stress_test(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        btn_layout = QHBoxLayout()
        
        self.btn_start_stress = QPushButton("Начать стресс тест")
        self.btn_start_stress.clicked.connect(self.start_stress_test)
        btn_layout.addWidget(self.btn_start_stress)
        
        self.btn_stop_stress = QPushButton("Остановить")
        self.btn_stop_stress.clicked.connect(self.stop_stress_test)
        self.btn_stop_stress.setEnabled(False)
        btn_layout.addWidget(self.btn_stop_stress)
        
        self.btn_run_benchmarks = QPushButton("Тесты производительности")
        self.btn_run_benchmarks.clicked.connect(self.run_benchmarks)
        btn_layout.addWidget(self.btn_run_benchmarks)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.stress_status_label = QLabel("Стресс тест не запущен")
        self.stress_status_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 13px;")
        layout.addWidget(self.stress_status_label)

        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(6)
        
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU:"))
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setValue(0)
        cpu_layout.addWidget(self.cpu_progress)
        self.cpu_label = QLabel("0%")
        self.cpu_label.setStyleSheet("color: white; min-width: 35px;")
        cpu_layout.addWidget(self.cpu_label)
        progress_layout.addLayout(cpu_layout)
        
        ram_layout = QHBoxLayout()
        ram_layout.addWidget(QLabel("RAM:"))
        self.ram_progress = QProgressBar()
        self.ram_progress.setRange(0, 100)
        self.ram_progress.setValue(0)
        ram_layout.addWidget(self.ram_progress)
        self.ram_label = QLabel("0%")
        self.ram_label.setStyleSheet("color: white; min-width: 35px;")
        ram_layout.addWidget(self.ram_label)
        progress_layout.addLayout(ram_layout)
        
        layout.addLayout(progress_layout)

        self.benchmark_results = QLabel("")
        self.benchmark_results.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 12px;")
        self.benchmark_results.setWordWrap(True)
        layout.addWidget(self.benchmark_results)
        
        layout.addStretch()
        
        self.set_content_widget(widget)

        self.update_stress_status()
    
    def start_stress_test(self):
        result = self.performance_dll.start_stress_test()
        if result.get('status') == 'started':
            self.btn_start_stress.setEnabled(False)
            self.btn_stop_stress.setEnabled(True)
            self.stress_status_label.setText(f"Стресс тест запущен")
    
    def stop_stress_test(self):
        result = self.performance_dll.stop_stress_test()
        if result.get('status') == 'stopped':
            self.btn_start_stress.setEnabled(True)
            self.btn_stop_stress.setEnabled(False)
            self.stress_status_label.setText("Стресс тест остановлен")
            self.cpu_progress.setValue(0)
            self.ram_progress.setValue(0)
            self.cpu_label.setText("0%")
            self.ram_label.setText("0%")
    
    def run_benchmarks(self):
        self.btn_run_benchmarks.setEnabled(False)
        self.benchmark_results.setText("Выполняются тесты...")

        def benchmark_thread():
            try:
                result = self.performance_dll.run_full_benchmark()
                cpu_score = result.get('cpu', {}).get('score', 0)
                ram_score = result.get('ram', {}).get('score', 0)
                cpu_time = result.get('cpu', {}).get('time_ms', 0)
                ram_bandwidth = result.get('ram', {}).get('bandwidth_mbps', 0)
                
                results_text = f"""Результаты:
CPU: {cpu_score:.2f} ({cpu_time} мс)
RAM: {ram_score:.2f} ({ram_bandwidth:.1f} МБ/с)
Общая: {(cpu_score + ram_score) / 2:.2f}"""
                self.benchmark_results.setText(results_text)
            except:
                self.benchmark_results.setText("Ошибка тестов")
            finally:
                self.btn_run_benchmarks.setEnabled(True)
        
        threading.Thread(target=benchmark_thread, daemon=True).start()
    
    def update_stress_status(self):
        if hasattr(self, 'stress_status_label'):
            status = self.performance_dll.get_stress_test_status()
            if status.get('running', False):
                cpu_usage = status.get('cpu_usage', 0)
                memory_usage = status.get('memory_usage', 0)
                self.cpu_progress.setValue(int(cpu_usage))
                self.ram_progress.setValue(int(memory_usage))
                self.cpu_label.setText(f"{cpu_usage:.0f}%")
                self.ram_label.setText(f"{memory_usage:.0f}%")
            QTimer.singleShot(800, self.update_stress_status)
    
    def show_about_info(self):
        self.section_label.setText("O программе")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        box = self.create_info_box("Win Helper", [
            "Сделано: WindowsMan",
            "Telegram: @pfevi",
            f"Версия: {APP_VERSION}",
            "",
            "Возможности:",
            "- Информация о системе",
            "- Тесты производительности",
            "- Стресс тест системы",
            "- Редактор автозагрузки",
            "- Редактор реестра",
            "- Проводник",
            "- Менеджер процессов",
            "- Пользователи",
            "- Драйвера",
            "- Персонализация",
            "- Разблокировка клавиш",
            "- Обходы вирусов"
        ])
        scroll_layout.addWidget(box)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        self.set_content_widget(scroll)

def main():
    shared_memory = QSharedMemory("WinHelperAppInstance")
    if shared_memory.attach():
        sys.exit(0)
    shared_memory.create(1)
    
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, 
            " ".join([f'"{arg}"' for arg in sys.argv]), None, 1
        )
        sys.exit(0)
    
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    
    window = WinHelperApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()