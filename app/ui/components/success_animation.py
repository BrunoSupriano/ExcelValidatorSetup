
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath

class SuccessAnimation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self.progress = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        
    def start(self):
        self.progress = 0
        self.timer.start(10) # 10ms interval
        
    def update_animation(self):
        self.progress += 2
        if self.progress > 100:
            self.timer.stop()
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x, center_y = self.width() / 2, self.height() / 2
        radius = 40
        
        # Pen Setup
        pen = QPen(QColor("#00C853")) # Success Green
        pen.setWidth(4)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # 1. Draw Circle (0 to 60ish % of progress)
        # We want the circle to draw fully first? Or fast?
        # Let's say circle draws from 0 to 70
        
        circle_progress = min(self.progress, 70) / 70
        if circle_progress > 0:
            angle_span = int(360 * 16 * circle_progress)
            painter.drawArc(center_x - radius, center_y - radius, radius*2, radius*2, 90 * 16, -angle_span)
            
        # 2. Draw Checkmark (70 to 100 % of progress)
        if self.progress > 70:
            check_progress = (self.progress - 70) / 30
            
            # Checkmark path
            # Coordinates relative to center
            # Start: (-10, 5), Mid: (-5, 15), End: (15, -15)
            
            path = QPainterPath()
            p1 = (center_x - 12, center_y + 4)
            p2 = (center_x - 4, center_y + 12)
            p3 = (center_x + 16, center_y - 12)
            
            path.moveTo(*p1)
            
            # Draw first leg
            if check_progress > 0:
                # Interpolate p1 to p2
                t1 = min(check_progress * 2, 1.0)
                curr_x = p1[0] + (p2[0] - p1[0]) * t1
                curr_y = p1[1] + (p2[1] - p1[1]) * t1
                path.lineTo(curr_x, curr_y)
                
            # Draw second leg
            if check_progress > 0.5:
                # Interpolate p2 to p3
                t2 = (check_progress - 0.5) * 2
                curr_x = p2[0] + (p3[0] - p2[0]) * t2
                curr_y = p2[1] + (p3[1] - p2[1]) * t2
                path.lineTo(curr_x, curr_y)
                
            painter.drawPath(path)
