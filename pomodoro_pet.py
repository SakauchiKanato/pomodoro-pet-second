import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction, QActionGroup
from PyQt6.QtCore import QTimer

# 🛠️ PyInstaller用：パッケージ内の画像パスを取得する関数
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class PomodoroPetApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # ⏱️ 調整可能なパラメータ（デフォルト値）
        self.selected_focus_duration = 1500  # 25分
        self.selected_rest_duration = 300    # 5分
        
        self.remaining_time = self.selected_focus_duration
        self.is_focus_mode = True
        self.is_running = False
        
        # 🐕 アニメーション管理
        self.animation_index = 1
        
        # システムトレイアイコンの作成
        self.tray_icon = QSystemTrayIcon()
        self.update_icon()
        
        # 右クリックメニューの構築
        self.menu = QMenu()
        self.construct_menu()
        
        # ⏱️ 1. 時間カウントダウン用タイマー（1秒ごと固定）
        self.timer = QTimer()
        self.timer.timeout.connect(self.countdown)
        
        # 🏃 2. コーギーを早く走らせるための高速タイマー（0.18秒ごと）
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.advance_animation)
        
        self.tray_icon.show()
        self.update_tooltip()

    def construct_menu(self):
        """元のSwiftコードのメニュー構成を完全再現"""
        self.menu.clear()
        
        # スタート / 一時停止 / 再開ボタンの動的切り替え
        if not self.is_running:
            if self.remaining_time == self.selected_focus_duration and self.is_focus_mode:
                self.start_action = self.menu.addAction("タイマースタート", self.start_timer)
            else:
                self.start_action = self.menu.addAction("タイマーを再開", self.start_timer)
        else:
            self.start_action = self.menu.addAction("一時停止", self.pause_timer)
            
        # リセットボタン
        self.menu.addAction("リセット", self.reset_timer)
        self.menu.addSeparator()
        
        # ⏱ 集中時間を変更 サブメニュー
        focus_menu = self.menu.addMenu("⏱ 集中時間を変更")
        focus_group = QActionGroup(self.menu)
        focus_times = [("60分", 3600), ("45分", 2700), ("30分", 1800), ("25分", 1500)]
        for title, seconds in focus_times:
            action = QAction(title, focus_menu, checkable=True)
            action.setData(seconds)
            if seconds == self.selected_focus_duration:
                action.setChecked(True)
            action.triggered.connect(self.change_focus_duration)
            focus_group.addAction(action)
            focus_menu.addAction(action)
            
        # ☕️ 休憩時間を変更 サブメニュー
        rest_menu = self.menu.addMenu("☕️ 休憩時間を変更")
        rest_group = QActionGroup(self.menu)
        rest_times = [("15分", 900), ("10分", 600), ("5分", 300), ("3分", 180)]
        for title, seconds in rest_times:
            action = QAction(title, rest_menu, checkable=True)
            action.setData(seconds)
            if seconds == self.selected_rest_duration:
                action.setChecked(True)
            action.triggered.connect(self.change_rest_duration)
            rest_group.addAction(action)
            rest_menu.addAction(action)
            
        self.menu.addSeparator()
        self.menu.addAction("終了", sys.exit)
        self.tray_icon.setContextMenu(self.menu)

    def change_focus_duration(self):
        action = self.sender()
        if action:
            self.selected_focus_duration = action.data()
            # Swiftのロジックを再現：タイマー停止中、または集中モード稼働中ならリセット
            if not self.is_running or self.is_focus_mode:
                self.reset_timer()
            else:
                self.construct_menu()

    def change_rest_duration(self):
        action = self.sender()
        if action:
            self.selected_rest_duration = action.data()
            # Swiftのロジックを再現：タイマー稼働中かつ休憩モード中ならリセット
            if self.is_running and not self.is_focus_mode:
                self.reset_timer()
            else:
                self.construct_menu()

    def update_icon(self):
        if self.is_focus_mode:
            base_image_name = "Focused_Corgi"
            if self.remaining_time == 0:
                base_image_name = "Satisfaction_Corgi"
            elif self.remaining_time <= 300:
                base_image_name = "Hungry_Corgi"
                
            if self.is_running and self.remaining_time > 0 and base_image_name != "Satisfaction_Corgi":
                if self.animation_index > 1:
                    img_name = f"{base_image_name}_{self.animation_index}.png"
                else:
                    img_name = f"{base_image_name}.png"
            else:
                img_name = f"{base_image_name}.png"
        else:
            # 休憩モード中の画像切り替え（画像がない場合はフォールバックされます）
            if self.remaining_time == 0:
                img_name = "Ready_Corgi.png"
            else:
                img_name = "Resting_Corgi.png"

        full_path = get_resource_path(img_name)
        if os.path.exists(full_path):
            self.tray_icon.setIcon(QIcon(full_path))
        else:
            self.tray_icon.setIcon(QSystemTrayIcon.MessageIcon.Information)

    def update_tooltip(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        mode_str = "集中タイム" if self.is_focus_mode else "休憩タイム"
        self.tray_icon.setToolTip(f"ポモドーロペット [{mode_str}] - {time_str}")

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.timer.start(1000)
            self.animation_timer.start(180) # 0.18秒
            self.construct_menu()
            self.update_icon()

    def pause_timer(self):
        if self.is_running:
            self.is_running = False
            self.timer.stop()
            self.animation_timer.stop()
            self.construct_menu()
            self.update_icon()

    def reset_timer(self):
        self.timer.stop()
        self.animation_timer.stop()
        self.is_running = False
        self.is_focus_mode = True
        self.remaining_time = self.selected_focus_duration
        self.animation_index = 1
        self.update_icon()
        self.update_tooltip()
        self.construct_menu()

    def countdown(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_tooltip()
            if self.remaining_time == 300 or self.remaining_time == 0:
                self.update_icon()
        else:
            self.timer.stop()
            self.animation_timer.stop()
            self.is_running = False
            self.animation_index = 1
            
            if self.is_focus_mode:
                self.is_focus_mode = False
                self.remaining_time = self.selected_rest_duration
                self.update_icon()
                self.update_tooltip()
                self.tray_icon.showMessage("🐶 集中終了！", "休憩の時間だワン！しっかり休んでね。", QSystemTrayIcon.MessageIcon.Information, 5000)
            else:
                self.is_focus_mode = True
                self.remaining_time = self.selected_focus_duration
                self.update_icon()
                self.update_tooltip()
                self.tray_icon.showMessage("🐶 休憩終了！", "お休み終了だワン！また一緒に集中しよう！", QSystemTrayIcon.MessageIcon.Information, 5000)
            
            self.construct_menu()

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
