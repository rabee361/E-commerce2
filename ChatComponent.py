from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint, QVariantAnimation, QRect

class TypingIndicator(QtWidgets.QWidget):
    """A widget that shows the typing animation (three dots)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        
        # Create dot labels
        self.dots = []
        self.dot_layout = QtWidgets.QHBoxLayout(self)
        self.dot_layout.setContentsMargins(15, 5, 15, 5)
        
        # Add three dots with space between them
        for i in range(3):
            dot = QtWidgets.QLabel("•")
            dot.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #888888;
                }
            """)
            self.dot_layout.addWidget(dot)
            self.dots.append(dot)
            
        # Add spacing between dots
        self.dot_layout.setSpacing(5)
        
        # Add stretching to align dots to the left
        self.dot_layout.addStretch()
        
        # Animation timer
        self.animation_step = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_dots)
        self.timer.start(300)  # Update every 300ms
        
        # Style the container
        self.setStyleSheet("""
            TypingIndicator {
                background-color: #E8E8E8;
                border-radius: 15px;
                margin: 5px;
                margin-right: 80px;
            }
        """)
        
    def animate_dots(self):
        """Animate the dots by changing their opacity"""
        for i, dot in enumerate(self.dots):
            # Create a pulsing effect with different timings for each dot
            if (self.animation_step + i) % 3 == 0:
                dot.setStyleSheet("QLabel { font-size: 24px; font-weight: bold; color: #555555; }")
            else:
                dot.setStyleSheet("QLabel { font-size: 24px; font-weight: bold; color: #BBBBBB; }")
        
        self.animation_step += 1
        if self.animation_step > 9:
            self.animation_step = 0
            
    def stop(self):
        """Stop the animation timer"""
        self.timer.stop()

class ChatBubble(QtWidgets.QLabel):
    """A custom label styled as a chat bubble"""
    
    def __init__(self, text, is_user=False, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setWordWrap(True)
        self.is_user = is_user
        self.original_pos = None
        
        # Set text direction to left-to-right for all messages
        self.setLayoutDirection(Qt.RightToLeft)
        self.setTextFormat(Qt.RichText)
        
        # Style based on whether it's a user message or bot message
        if is_user:
            self.setStyleSheet("""
                QLabel {
                    background-color: #DCF8C6;
                    border-radius: 15px;
                    padding: 10px;
                    margin: 5px;
                    font-family: "Segoe UI";
                    font-size: 12px;
                    color: #000000;
                    border: none;
                }
            """)
            self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: #E8E8E8;
                    border-radius: 15px;
                    padding: 10px;
                    margin: 5px;
                    font-family: "Segoe UI";
                    font-size: 12px;
                    color: #000000;
                    border: none;
                }
            """)
            self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
        # Set size policy to ensure the bubble fits the content
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred if is_user else QtWidgets.QSizePolicy.Preferred, 
            QtWidgets.QSizePolicy.Minimum
        )
        self.setSizePolicy(size_policy)
        self.setMinimumWidth(10)  # Allow very small width for short messages
        self.setMaximumWidth(280)  # Limit maximum width
        
        # Calculate a more appropriate width based on text length
        font_metrics = QtGui.QFontMetrics(self.font())
        text_width = font_metrics.horizontalAdvance(text)
        
        # Set width based on text length, with minimums and maximums
        ideal_width = min(max(text_width, 10), 225)
        self.setMinimumWidth(ideal_width)
        
        # Create the opacity effect
        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity_effect)

    def showEvent(self, event):
        """Override showEvent to start animations after widget is positioned"""
        super().showEvent(event)
        
        # Now animate both user and bot messages
        if not hasattr(self, 'animated'):
            self.animated = True
            # Start animations with a small delay to ensure widget is fully laid out
            QTimer.singleShot(10, self.start_animations)
            
    def start_animations(self):
        """Start the animations for the chat bubble"""
        # Save original position for animation
        self.original_pos = self.pos()
        
        # 1. Fade-in animation
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # 2. Slide-in animation
        if self.original_pos is not None:
            self.slide_anim = QPropertyAnimation(self, b"pos")
            self.slide_anim.setDuration(350)
            
            # Different animation direction based on message type
            if self.is_user:
                # User messages slide in from the right
                start_pos = self.original_pos + QtCore.QPoint(50, 0)
            else:
                # Bot messages slide in from the left
                start_pos = self.original_pos + QtCore.QPoint(-50, 0)
                
            self.slide_anim.setStartValue(start_pos)
            self.slide_anim.setEndValue(self.original_pos)
            self.slide_anim.setEasingCurve(QEasingCurve.OutBack)  # Slight bounce effect
            
            # Move to start position instantly
            self.move(start_pos)
            
            # Start animations
            self.fade_anim.start()
            self.slide_anim.start()

class ChatComponent(QtWidgets.QWidget):
    """A component that handles chat UI and functionality"""
    
    message_sent = pyqtSignal(str)  # Signal emitted when a message is sent
    
    def __init__(self, messages_layout=None, message_input=None, scroll_area=None, parent=None):
        super().__init__(parent)
        # self.setup_ui()
        self.typing_indicator = None
        self.response_timer = QTimer()
        self.response_timer.setSingleShot(True)
        self.response_timer.timeout.connect(self.show_response)
        self.pending_response = None
        self.messages_layout = messages_layout
        self.message_input = message_input
        self.scroll_area = scroll_area

        
    def send_message(self, message):
        """Send a message from the user"""
        if not message:
            return
            
        # Add user message
        self.add_message(message, is_user=True)
        
        # Clear input
        self.message_input.clear()
        
        # Emit signal with the message
        self.message_sent.emit(message)
        
        # Show typing indicator
        self.show_typing_indicator()
        
    def show_typing_indicator(self):
        """Show the typing indicator"""
        if self.typing_indicator is None:
            self.typing_indicator = TypingIndicator()
            self.messages_layout.addWidget(self.typing_indicator)
            self.scroll_to_bottom()
    
    def hide_typing_indicator(self):
        """Hide the typing indicator"""
        if self.typing_indicator:
            self.typing_indicator.stop()
            self.typing_indicator.deleteLater()
            self.typing_indicator = None
    
    def show_response(self):
        """Show the bot response"""
        if self.pending_response:
            # Hide typing indicator
            self.hide_typing_indicator()
            
            # Add bot message
            self.add_message(self.pending_response, is_user=False)
            
            # Clear pending response
            self.pending_response = None
            
    def add_message(self, text, is_user=False):
        """Add a message to the chat"""
        # Create chat bubble
        bubble = ChatBubble(text, is_user)
        
        # Create a container widget for proper alignment
        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Align based on sender
        if is_user:
            # User message - right aligned
            container_layout.addStretch()
            container_layout.addWidget(bubble)
        else:
            # Bot message - left aligned
            container_layout.addWidget(bubble)
            container_layout.addStretch()
        
        # Add container to messages layout
        self.messages_layout.addWidget(container)
        
        # Scroll to bottom
        self.scroll_to_bottom()
        
    def set_pending_response(self, response, delay=1500):
        """Set a response to be shown after a delay"""
        self.pending_response = response
        self.response_timer.start(delay)
        
    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat"""
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))