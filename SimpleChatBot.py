import random
from PyQt5.QtCore import QObject, pyqtSignal

class SimpleChatBot(QObject):
    """A class that handles chat logic and responses"""
    
    response_ready = pyqtSignal(str)  # Signal emitted when a response is ready
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.greeting_responses = [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Hey! I'm here to assist you. How can I help?",
            "Greetings! How may I assist you today?"
        ]
        
        self.farewell_responses = [
            "Goodbye! Have a great day!",
            "Bye! Feel free to chat again if you need help.",
            "See you later! Take care!",
            "Farewell! I'm here if you need anything else."
        ]
        
        self.default_responses = [
            "I'm not sure how to respond to that. Can you ask something else?",
            "I didn't quite understand. Could you rephrase that?",
            "I'm still learning. Could you try asking something else?",
            "I'm not sure I can help with that. Is there something else you'd like to know?"
        ]
        
        self.how_are_you_responses = [
            "I'm doing well, thanks for asking! How can I help you today?",
            "I'm great! How about you? Is there something I can assist you with?",
            "I'm functioning perfectly! What can I do for you?",
            "All systems operational! How may I assist you today?"
        ]
        
        self.help_responses = [
            "I can help you with various tasks. What do you need assistance with?",
            "I'm here to help! What kind of information are you looking for?",
            "I can assist with many things. Just let me know what you need.",
            "How can I be of service today? Just ask away!"
        ]
        
        self.thanks_responses = [
            "You're welcome! Is there anything else I can help with?",
            "Happy to help! Let me know if you need anything else.",
            "Anytime! Do you have any other questions?",
            "No problem at all! Anything else you need?"
        ]
        
    def get_response(self, message):
        """Generate a response based on the message"""
        message = message.lower()
        
        # Check for greetings
        if any(word in message for word in ["hi", "hello", "hey", "greetings"]):
            return random.choice(self.greeting_responses)
        
        # Check for farewell
        elif any(word in message for word in ["bye", "goodbye", "farewell", "see you"]):
            return random.choice(self.farewell_responses)
        
        # Check for "how are you" type questions
        elif "how are you" in message or "how're you" in message or "how r u" in message:
            return random.choice(self.how_are_you_responses)
        
        # Check for help requests
        elif any(word in message for word in ["help", "assist", "support"]):
            return random.choice(self.help_responses)
        
        # Check for thanks
        elif any(word in message for word in ["thanks", "thank you", "thx", "appreciate"]):
            return random.choice(self.thanks_responses)
        
        # Default response
        else:
            return random.choice(self.default_responses)
    
    def process_message(self, message):
        """Process a message and emit a response signal"""
        response = self.get_response(message)
        self.response_ready.emit(response) 