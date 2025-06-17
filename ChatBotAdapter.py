import asyncio
import threading
from chatbot import ChatBot, Services
from PyQt5.QtCore import QObject, pyqtSignal

class ChatBotAdapter(QObject):
    """
    Adapter class that bridges the ChatBot implementation with the UI components.
    
    This adapter provides a Qt-compatible interface with signals for asynchronous 
    communication between the chatbot backend and the UI. It handles the conversion
    between the async ChatBot API and the synchronous Qt framework.
    
    The adapter supports different data sources (CSV, MySQL) and manages its own
    background thread for non-blocking operation.
    """
    
    response_ready = pyqtSignal(str)  # Signal emitted when a response is ready
    
    def __init__(self, service=None, ai_rules_path="", mysql_connection=None, parent=None):
        super().__init__(parent)
        
        # Initialize the ChatBot with the specified service
        self.chatbot = ChatBot(
            service=service if service else Services.CSV,  # Default to CSV if no service specified
            ai_rules_path=ai_rules_path, 
            mysql_connection=mysql_connection,
            terminal=False
        )
        
        # Create a new event loop for async operations
        self.loop = asyncio.new_event_loop()
        
        # Start a background thread to run the asyncio event loop
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
    
    def _run_event_loop(self):
        """Run the asyncio event loop in a background thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def process_message(self, message):
        """
        Process a message from the user and emit a response
        
        Args:
            message (str): User's input message
        """
        # Schedule the coroutine to run in the event loop without blocking
        asyncio.run_coroutine_threadsafe(
            self._process_message_async(message),
            self.loop
        )
    
    async def _process_message_async(self, message):
        """
        Async method to process the message and emit the response
        
        Args:
            message (str): User's input message
        """
        try:
            # Get response from chatbot
            print(message)
            response = await self.chatbot._chat_with_return(message)
            # Emit the signal with the response
            self.response_ready.emit(response)
        except Exception as e:
            self.response_ready.emit(f"Error processing message: {str(e)}")
    
    def __del__(self):
        """Destructor to clean up resources."""
        # Stop the event loop
        if hasattr(self, 'loop') and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        # Wait for the thread to finish if it exists
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)
            
        # Close the event loop
        if hasattr(self, 'loop') and not self.loop.is_closed():
            self.loop.close() 
