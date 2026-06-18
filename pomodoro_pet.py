import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer

class PomodoroPetApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # ⏱️ パラメータ設定 (25分 = 1500秒)
        self.selected_focus_duration = 1500 
        self.remaining_time = self.selected_focus_duration
        self.is_running = False
        
        # 🐕 アニメーション管理
        self.animation_index = 1
        
        # システムトレイアイコンの作成
        self.tray_icon = QSystemTrayIcon()
        self.update_icon()
        
        # 右クリックメニューの作成
        self.menu = QMenu()
        self.start_action = self.menu.addAction("タイマースタート", self.start_timer)
        self.reset_action = self.menu.addAction("リセット", self.reset_timer)
        self.menu.addSeparator()
        self.menu.addAction("終了", sys.exit)
        self.tray_icon.setContextMenu(self.menu)
        
        # ⏱️ 1. 時間カウントダウン用タイマー（1秒ごと）
        self.timer = QTimer()
        self.timer.timeout.connect(self.countdown)
        
        # 🏃 2. コーギーを早く走らせるための高速タイマー（0.15秒ごと）
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.advance_animation)
        
        self.tray_icon.show()
        self.update_tooltip()

    def update_icon(self):
        # 画像名を組み立てる (Focused_Corgi.png, Focused_Corgi_2.png...)
        if self.is_running and self.animation_index > 1:
            img_name = f"Focused_Corgi_{self.animation_index}.png"
        else:
            img_name = "Focused_Corgi.png"
            
        if os.path.exists(img_name):
            self.tray_icon.setIcon(QIcon(img_name))
        else:
            # 画像がない場合のフォールバック（標準の警告アイコン等）
            self.tray_icon.setIcon(QSystemTrayIcon.MessageIcon.Information)

    def update_tooltip(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.tray_icon.setToolTip(f"ポモドーロペット - {time_str}")

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.timer.start(1000)        # 1秒ごと
            self.animation_timer.start(180) # 0.15秒（150ミリ秒）ごと
            self.start_action.setText("一時停止")
            self.start_action.triggered.disconnect()
            self.start_action.triggered.connect(self.pause_timer)

    def pause_timer(self):
        if self.is_running:
            self.is_running = False
            self.timer.stop()
            self.animation_timer.stop()
            self.start_action.setText("タイマーを再開")
            self.start_action.triggered.disconnect()
            self.start_action.triggered.connect(self.start_timer)

    def reset_timer(self):
        self.timer.stop()
        self.animation_timer.stop()
        self.is_running = False
        self.remaining_time = self.selected_focus_duration
        self.animation_index = 1
        self.update_icon()
        self.update_tooltip()
        
        self.start_action.setText("タイマースタート")
        self.start_action.triggered.disconnect()
        self.start_action.triggered.connect(self.start_timer)

    def countdown(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_tooltip()
        else:
            self.reset_timer()
            self.tray_icon.showMessage("🐶 集中終了！", "休憩の時間だワン！", QSystemTrayIcon.MessageIcon.Information, 5000)

    def advance_animation(self):
        if self.animation_index >= 4:
            self.animation_index = 1
        else:
            self.animation_index += 1
        self.update_icon()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = PomodoroPetApp()
    app.run()