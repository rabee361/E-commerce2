import enum
import logging
from math import ceil
import os
import glob
import json
from typing import List, Tuple, Optional, Union, Dict, Any
import asyncio
from llama_cpp import Llama
from mysql.connector import MySQLConnection
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from docx import Document
import chromadb
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted # Added for rate limit handling
import re

# Static strings and constants
# Default messages
DEFAULT_EMPTY_RESULT_MESSAGE = "Not enough data to answer the question"
DEFAULT_ERROR_MESSAGE = "An unexpected error occurred."
DEFAULT_HUMAN_RESPONSE_ERROR = "Error: Could not generate a human-readable response."
DEFAULT_SQL_GENERATION_ERROR = "Error: Could not generate the required SQL query."
DEFAULT_NO_RELEVANT_INFO = "No relevant information found in the document for your query."
DEFAULT_DOCUMENT_RETRIEVAL_ERROR = "Error: Could not retrieve information from the document."
DEFAULT_STRUCTURED_DATA_ERROR = "Error: Could not process the query using the provided data."
DEFAULT_DB_ERROR_MESSAGE = "I encountered an error trying to fetch data from the database."
DEFAULT_UNEXPECTED_ERROR = "Sorry, I encountered an unexpected error while processing your request. Please try again."
DEFAULT_GEMINI_ERROR = "Error: An unexpected issue occurred while processing the Gemini request."
DEFAULT_OLLAMA_ERROR = "Error: Failed to generate a response from the Ollama model."
DEFAULT_GENERIC_ERROR = "Error: Failed to generate a response."
DEFAULT_SQL_SCHEMA_ERROR = "Error: The model could not generate a SQL query. It may need more information about the database schema."
DEFAULT_MAX_SQL_RETRIES_EXCEEDED = "Error: Maximum SQL query retry attempts exceeded. Could not execute the query successfully."

# Configuration values
DEFAULT_MAX_SQL_RETRIES = 5
# When model rotation is enabled and a query fails, the system will try to use a better model
# (with larger context window) for the next retry attempt

# Default context window sizes
DEFAULT_CONTEXT_WINDOW = 2048
DEFAULT_GEMINI_CONTEXT_WINDOW = 32768
DEFAULT_GEMINI_15_CONTEXT_WINDOW = 1000000
DEFAULT_GEMINI_20_CONTEXT_WINDOW = 1000000

# File paths
MODELS_PATH = "models/*.gguf"

# SQL query generation rules
SQL_QUERY_GENERATION_RULES = """IMPORTANT RULES FOR GENERATING SQL QUERIES:
1. ALWAYS use backticks (`) around ALL table names and column names, even if they don't contain special characters.
2. ALWAYS use single quotes (') around string values.
4. Tables or columns with dots (.) in their names MUST be enclosed in backticks.
5. Return ONLY the SQL query without any additional text.
6. ALWAYS use very descriptive column names in your SELECT statements and avoid abbreviations.
7. When data needs to be collected from tables that are not related, use UNION to combine the results.
8. Always use very descriptive column names and avoid abbreviations.
9. Return ONLY the SQL query without any additional text.
10. If user question can be answered without making a new query, make a pseudo query that returns the answer as a static value in a column named answer, for example: SELECT 'The answer is 42' AS answer;
Example of properly formatted query:
SELECT `column1`, `column2` FROM `table.name` WHERE `status` = "active" AND `count` > 5;
"""

# SQL extraction patterns
SQL_EXTRACTION_PATTERNS = [
    r"```sql\s*([\s\S]*?)\s*```",  # Capture multi-line SQL in sql block
    r"```mysql\s*([\s\S]*?)\s*```", # Capture multi-line SQL in mysql block
    r"```\s*([\s\S]*?)\s*```",      # Capture multi-line SQL in any block
    r"(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|SHOW|USE|DESCRIBE|EXPLAIN|SET)\s+[\s\S]+?;", # Match common SQL commands ending with ;
    r"(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|SHOW|USE|DESCRIBE|EXPLAIN|SET)\s+[\s\S]+"    # Fallback for commands without ;
]

# Gemini model context window sizes
GEMINI_CONTEXT_WINDOWS = {
    "gemini-1.5-pro": 1000000,  # 1M tokens
    "gemini-1.5-flash": 1000000,  # 1M tokens
    "gemini-1.0-pro": 32768,  # 32K tokens
    "gemini-pro": 32768,  # 32K tokens
    "gemini-2.0-pro": 1000000,  # 1M tokens
    "gemini-2.0-flash": 1000000,  # 1M tokens
    "gemini-2.5-pro": 1000000,  # 1M tokens
    "gemini-2.5-flash": 1000000,  # 1M tokens
}

# Prompt templates
MYSQL_HUMAN_RESPONSE_PROMPT = """Based on the following conversation history and database query results:

Conversation History:
{history_context}

Database Query Results:
```
{result}
```

Format the SQL results in a human-readable way to answer the user's original question: '{question}'

Provide a clear, concise answer based on the data shown above. If the data is empty or doesn't contain the information needed to answer the question, please state that clearly.

IMPORTANT RULES:
1. NEVER include SQL queries in your response
2. NEVER include technical database information in your response
3. NEVER mention table names, column names, or database structure
4. Focus ONLY on providing a human-friendly answer to the question
5. Please respond in {language} language
"""

STRUCTURED_DATA_RESPONSE_PROMPT = """Based on the following data:
```
{result}
```

Answer the user's question: '{question}'

Provide a concise, natural language answer based on the data shown above.

IMPORTANT RULES:
1. NEVER include technical data structure information in your response
2. NEVER include raw data formats or column names in your response
3. Focus ONLY on providing a human-friendly answer to the question
4. Please respond in {language} language
"""

DOCUMENT_RESPONSE_PROMPT = """Using ONLY the text provided below:
```
{result}
```

Answer the user's question: '{question}'

Do not use any external knowledge. If the answer isn't in the text, say so clearly.

IMPORTANT RULES:
1. NEVER include technical document structure information in your response
2. NEVER include file formats, page numbers, or document metadata in your response
3. Focus ONLY on providing a human-friendly answer to the question
4. Please respond in {language} language
"""

CSV_DATA_PROMPT = """Given the following data (potentially truncated):
{data_context}

Answer the question: {query}

IMPORTANT RULES:
1. NEVER include technical data structure information in your response
2. NEVER include CSV formats, column names, or raw data in your response
3. Focus ONLY on providing a human-friendly answer to the question
4. Please respond in {language} language
"""

COMBINED_SQL_PROMPT = """
{system_instruction}

Create a MySQL query to answer this question: {user_input}

"""

SQL_QUERY_CORRECTION_PROMPT = """
IMPORTANT: The previous SQL query FAILED with the following error:

ERROR: {error_message}

Failed query:
```sql
{original_query}
```

Please generate a completely corrected SQL query that will work properly. Consider the database schema and the original question: '{question}'

The previous query failed, so a different approach may be needed. Carefully analyze the error message and fix all issues.

Return ONLY the corrected SQL query without any additional text or explanations.
"""

class LLM_Type(enum.Enum):
    OLLAMA = 1
    GEMINI = 2

class Services(enum.Enum):
    PDF = 1
    DOCX = 2
    MYSQL = 3
    CSV = 4
    EXCEL = 5


class ChatBot:
    """A chatbot class that can interact with different document types and databases.

    Args:
        service: The type of service to use (PDF, DOCX, MYSQL, CSV, EXCEL)
        file_path: Path to the file to process (for PDF, DOCX, CSV, EXCEL)
        mysql_connection: MySQL connection object (for MYSQL service)
        terminal: Whether to run in terminal mode (interactive)
        ai_rules_path: Path to a file containing AI rules
        llm_type: Type of language model to use (OLLAMA or GEMINI)
        gemini_api_key: API key for Gemini models
        gemini_model_name: Name of the Gemini model to use
        enable_model_rotation: Whether to enable model rotation
        empty_result_message: Custom message for empty results
        response_language: Language for responses
        verbose: Whether to enable verbose logging
        verbose_model_output: Whether to log detailed model output
        custom_rules: Custom rules to append to the system instructions
        status_update: Whether to yield status updates during processing (changes chat method to use yield)
    """

    def __init__(self, service: Services, file_path: str = "", mysql_connection: MySQLConnection = None,
                 terminal:bool = False, ai_rules_path:str = None, llm_type: LLM_Type = LLM_Type.OLLAMA,
                 gemini_api_key: str = None, gemini_model_name: str = "gemini-1.5-pro",
                 enable_model_rotation: bool = False, empty_result_message: str = DEFAULT_EMPTY_RESULT_MESSAGE,
                 response_language: str = "english", verbose: bool = True, verbose_model_output: bool = False,
                 custom_rules: str = None, status_update: bool = False):
        # Initialize chat history and service type
        self._history: List[dict[str, str]] = []  # For Ollama format
        self._gemini_history: List[dict] = []  # For Gemini format with role and parts
        self._service = service
        self._initiated = False
        self._terminal = terminal
        self._llm_type = llm_type
        self._gemini_model_name = gemini_model_name
        self._ai_rules = None
        self._custom_rules = custom_rules # Store custom rules provided during initialization
        self._llm = None
        self._reader = None
        self._text = []
        self._chunks = []
        self._chromaDB = None
        self._collection = None
        self._my_sql_connection = None
        self._mysql_schema = None
        self._system_prompt = None
        self._available_gemini_models = [] # For model list
        self._current_gemini_model_index = 0 # For tracking current model
        self._gemini_api_key = gemini_api_key # Store API key
        self._gemini_chat = None # Store the Gemini chat session
        self._last_query_columns = [] # Store column names from the last executed query
        self._enable_model_rotation = enable_model_rotation # Enable/disable model rotation
        self._empty_result_message = empty_result_message # Custom message for empty results
        self._response_language = response_language # Store the language for responses
        self._verbose = verbose # Control general logging
        self._verbose_model_output = verbose_model_output # Control detailed model output logging
        self._status_update = status_update # Whether to yield status updates
        self._first_question = True # Track if this is the first question

        if self._verbose:
            print("Initializing ChatBot...")
        logging.getLogger('llama_cpp').setLevel(logging.ERROR)

        try:
            # Load AI rules
            if ai_rules_path:
                try:
                    with open(ai_rules_path, 'r') as file:
                        self._ai_rules = file.read()
                        self._ai_rules = self._clean_text(self._ai_rules)
                except FileNotFoundError:
                    self._log_progress(f"AI rules file not found at {ai_rules_path}", "⚠️")
                    self._ai_rules = None # Proceed without rules
                except Exception as e:
                    self._log_progress(f"Error reading AI rules file: {e}", "❌")


            # Service-specific initialization
            if service == Services.PDF:
                if not file_path: raise ValueError("PDF file path is required.")
                if not os.path.exists(file_path): raise FileNotFoundError(f"Error: PDF file not found at {file_path}")
                self._reader = PyPDFLoader(file_path)
                self._chromaDB = chromadb.Client()
                self._collection = self._chromaDB.create_collection("pdf_collection")
                self._log_progress("PDF service initialized.", "📄")
            elif service == Services.DOCX:
                if not file_path: raise ValueError("DOCX file path is required.")
                if not os.path.exists(file_path): raise FileNotFoundError(f"Error: DOCX file not found at {file_path}")
                self._reader = Document(file_path)
                self._chromaDB = chromadb.Client()
                self._collection = self._chromaDB.create_collection("docx_collection")
                self._log_progress("DOCX service initialized.", "📄")
            elif service == Services.CSV:
                if not file_path: raise ValueError("CSV file path is required.")
                if not os.path.exists(file_path): raise FileNotFoundError(f"Error: CSV file not found at {file_path}")
                self._reader = pd.read_csv(file_path)
                self._log_progress("CSV service initialized.", "📊")
            elif service == Services.EXCEL:
                if not file_path: raise ValueError("Excel file path is required.")
                if not os.path.exists(file_path): raise FileNotFoundError(f"Error: Excel file not found at {file_path}")
                self._reader = pd.read_excel(file_path)
                self._log_progress("Excel service initialized.", "📊")
            elif service == Services.MYSQL:
                if not mysql_connection: raise ValueError("MySQL connection object is required.")
                if not mysql_connection.is_connected(): raise ConnectionError("MySQL connection is not active.")
                self._my_sql_connection = mysql_connection
                self._mysql_schema = self._get_database_schema() # Can return "db error"
                if self._mysql_schema == "db error":
                    raise ConnectionError("Failed to fetch MySQL database schema.")
                self._system_prompt = self._create_system_prompt(self._mysql_schema)
                self._log_progress("MySQL service initialized.", "💾")
            else:
                self._log_progress(f"Unsupported service type: {service}", "💾")


            # Model configuration and initialization
            if self._llm_type == LLM_Type.OLLAMA:
                self._model_path = self._select_model() # Can raise SystemExit if no models found
                self._max_tokens = 2048
                self._temperature = 0.1
                self._n_threads = 4
                self._context_window = self._determine_context_window()
                self._llm = self._initialize_model() # Can raise Exception
            elif self._llm_type == LLM_Type.GEMINI:
                if not gemini_api_key:
                    raise ValueError("Gemini API key is required when using Gemini API")
                try:
                    # Configure the genai library with API key
                    genai.configure(api_key=gemini_api_key)
                    self._log_progress("Configured Gemini API", "✅")

                    self._max_tokens = 2048
                    self._temperature = 0.1  # Same as Ollama for consistency
                    # Set context window based on model
                    self._context_window = self._determine_gemini_context_window(self._gemini_model_name)

                    # Fetch available models
                    self._available_gemini_models = self.get_available_gemini_models(self._gemini_api_key)
                    if not self._available_gemini_models:
                        raise ValueError("No suitable Gemini models found or failed to fetch models.")
                    self._log_progress(f"Available Gemini models: {self._available_gemini_models}", "📄")

                    # Sort models by context window size if model rotation is enabled
                    if self._enable_model_rotation:
                        self._sort_models_by_context_window()
                        self._log_progress(f"Model rotation enabled. Models sorted by context window size (largest to smallest)", "🔄")
                        self._log_progress(f"Sorted models: {self._available_gemini_models}", "📄")
                        # When rotation is enabled, always start with the largest context window model
                        self._current_gemini_model_index = 0
                        self._gemini_model_name = self._available_gemini_models[0]
                        self._log_progress(f"Using model with largest context window: {self._gemini_model_name}", "✅")
                    else:
                        # Set initial model and index when rotation is disabled
                        try:
                            self._current_gemini_model_index = self._available_gemini_models.index(self._gemini_model_name)
                        except ValueError:
                            self._log_progress(f"Initial model '{self._gemini_model_name}' not found in available list. Using first available model.", "⚠️")
                            self._current_gemini_model_index = 0
                            self._gemini_model_name = self._available_gemini_models[0]


                    if not self._system_prompt:
                        self._log_progress("Warning: _system_prompt not set", "⚠️")


                    # Create generation config
                    gen_config = genai.GenerationConfig(
                        max_output_tokens=self._max_tokens,
                        temperature=self._temperature
                    )

                    # Create the model with system instruction if available
                    if self._system_prompt:
                        self._llm = genai.GenerativeModel(
                            model_name=self._gemini_model_name,
                            generation_config=gen_config,
                            system_instruction=self._system_prompt
                        )
                        self._log_progress(f"Created model with system instruction ({len(self._system_prompt)} chars)", "💬")
                    else:
                        self._llm = genai.GenerativeModel(
                            model_name=self._gemini_model_name,
                            generation_config=gen_config
                        )
                        self._log_progress("Created model without system instruction", "💬")

                    # Create the chat session
                    self._gemini_chat = self._llm.start_chat()
                    self._log_progress("Created chat session", "💬")

                    self._log_progress(f"Gemini chat session created", "💬")

                    self._log_progress(f"Gemini API configured successfully. Initial model: {self._gemini_model_name}", "✅")

                except Exception as e:
                    self._log_progress(f"Failed to configure or connect to Gemini API: {e}", "❌")
                    raise # Re-raise configuration errors


            # Add initial system message
            if service == Services.MYSQL:
                # System prompt already includes AI rules and custom rules if they exist (handled in _create_system_prompt)
                self._add_message("system", self._system_prompt)
            else:
                # For non-MySQL services, create a system message with AI rules and/or custom rules
                system_content = ""

                # Add AI rules if they exist
                if self._ai_rules:
                    system_content = self._ai_rules

                # Add custom rules if they exist
                if self._custom_rules:
                    if system_content:
                        system_content = f"{system_content}\n\n{self._custom_rules}"
                    else:
                        system_content = self._custom_rules

                # Add the system message if we have any content
                if system_content:
                    self._add_message("system", system_content)

            self._log_progress("ChatBot initialized successfully.", "✅")

        except (ValueError, FileNotFoundError, ConnectionError, SystemExit) as e:
            self._log_progress(f"Initialization Error: {e}", "❌")
            # Re-raise specific errors for clarity upstream
        except Exception as e:
            self._log_progress(f"Unexpected Initialization Error: {e}", "❌")
            # Wrap unexpected errors

    def _load_structured_types(self):
        self._text = self._reader.to_dict(orient="records")

        if not self._text:
            self._log_progress(f"No data found in {self._service.name} file", "⚠️")

        # Split into chunks if needed
        try:
            # Estimate size based on string representation (approximation)
            estimated_size = len(str(self._text))
            # Ensure context_window is positive
            context_window = max(1, self._context_window)
            chunk_count = ceil(estimated_size / context_window)
            self._chunks = self._split_structured_chunks(num_of_chunks=max(1, chunk_count))
            self._log_progress(f"Split data into {len(self._chunks)} chunks.", "📄")
        except Exception as e:
            self._log_progress(f"Error splitting structured data: {e}", "❌")
            # Fallback: treat the whole data as one chunk if splitting fails
            self._chunks = [self._text]
            self._log_progress("Using the entire dataset as a single chunk due to splitting error.", "⚠️")


    def _split_structured_chunks(self , num_of_chunks: int)-> List[List[Dict[str, Any]]]:
        if num_of_chunks <= 0:
             num_of_chunks = 1 # Avoid division by zero

        # Calculate chunk size, ensuring it's at least 1
        total_rows = len(self._text)
        chunk_size = max(1, total_rows // num_of_chunks)
        chunks = []

        # Split the list of dictionaries
        for i in range(0, total_rows, chunk_size):
            chunk = self._text[i:i + chunk_size]
            chunks.append(chunk)
        return chunks

    def _load_document(self):
        if self._service == Services.PDF:
            pages = self._reader.load()
            text = " ".join(page.page_content for page in pages)
            print(text)
        else:  # DOCX
            text = " ".join(para.text for para in self._reader.paragraphs)

        self._text = self._clean_text(text)

        # Create chunks
        chunk_size = min(max(len(self._text) // 20, 1000), 4000)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_size // 4
        )
        chunks = text_splitter.split_text(self._text)

        if not chunks:
            self._log_progress(f"No text chunks created from {self._service.name}", "⚠️")
            raise ValueError(f"Failed to extract text chunks from {self._service.name}")

        # Store in collection
        try:
            self._collection.add(
                ids=[str(i) for i in range(len(chunks))],
                documents=chunks
            )
            self._log_progress(f"Added {len(chunks)} chunks to ChromaDB collection.", "💾")
        except Exception as e:
            self._log_progress(f"Error adding chunks to ChromaDB: {e}", "❌")
            raise Exception(f"Failed to store document chunks: {str(e)}")


    def _clean_text(self, text: str) -> str:
        # Handle whitespace
        text = text.replace('\n', ' ')  # Replace newlines with spaces
        text = ' '.join(text.split())   # Remove extra whitespace
        text = text.strip()             # Remove leading/trailing whitespace

        # Characters to remove
        chars_to_remove = ['*', '`', "'", '"', '(', ')', '[', ']',
                         '{', '}', '#', '|', '~', '^']

        # Remove each character
        for char in chars_to_remove:
            text = text.replace(char, '')

        return text


    def _load_pdf(self):
        try:
            # Load pages
            _pages = self._reader.load()

            # Initialize embeddings and text splitter
            # Adjust chunk size based on text length for optimal processing
            chunk_size = min(max(len(self._text) // 20, 1000), 4000)  # Between 1000-4000 chars
            chunk_overlap = chunk_size // 4  # 25% overlap
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            self._text = ""
            for page in _pages:
                self._text += page.page_content

            self._text = self._clean_text(self._text)

            # Process documents
            chunks = text_splitter.split_text(self._text)


            if not chunks:
                self._log_progress("No text chunks created from PDF", "⚠️")
                raise ValueError("Failed to extract text chunks from PDF")

            # Create vector store
            self._collection.add(
                ids=[str(i) for i in range(len(chunks))],
                documents=[chunk for chunk in chunks],
            )
            self._log_progress(f"Added {len(chunks)} PDF chunks to ChromaDB.", "💾")

        except Exception as e:
            self._log_progress(f"Error initializing PDF components: {e}", "❌")
            raise Exception(f"Failed to process PDF: {str(e)}")

    def query_chunks(self, query: str) -> str:

        if not self._collection:
            self._log_progress("Document collection (ChromaDB) not initialized.", "❌")
            raise RuntimeError("Document retriever is not initialized. Load a document first.")
        try:
            results = self._collection.query(query_texts=[query], n_results=3, include=["documents"])
            if not results or not results.get("documents") or not results["documents"][0]:
                 self._log_progress("No relevant chunks found for the query.", "❓")
                 return DEFAULT_NO_RELEVANT_INFO

            final_response = ""
            # Access the list of documents correctly
            retrieved_docs = results["documents"][0]
            for doc_content in retrieved_docs:
                # Assuming each item in the list is the document content string
                if self._verbose:
                    print(doc_content) # Keep for debugging if needed
                final_response += doc_content + "\n\n" # Add separator
            self._log_progress(f"Retrieved {len(retrieved_docs)} relevant chunks.", "🔍")
            return final_response.strip()
        except Exception as e:
            self._log_progress(f"Error querying ChromaDB collection: {e}", "❌")
            return DEFAULT_DOCUMENT_RETRIEVAL_ERROR


    async def query_csv(self, query: str) -> str:
        if not self._chunks:
            self._log_progress("Structured data (CSV/Excel) not loaded or processed.", "❌")
            raise RuntimeError("Structured data retriever is not initialized. Load a file first.")

        # Simple approach: Combine all chunks for context (consider relevance scoring for large files)
        # This might exceed context limit for very large files. A better approach would involve
        # finding relevant chunks first, similar to document querying.
        combined_data_context = json.dumps(self._chunks, indent=2) # Present data clearly

        # Check context size before sending to LLM
        # Use the current context window size, which will be correct for the current model
        # For Gemini, use the model's count_tokens method for accurate token counting
        if self._llm_type == LLM_Type.GEMINI and hasattr(self, '_llm'):
            try:
                # Create a test prompt with the data to count tokens
                test_prompt = f"""Given the following data:
{combined_data_context}

Answer the question: {query}
"""
                # Count tokens using the model's method
                token_count_result = self._llm.count_tokens(test_prompt)
                token_count = token_count_result.total_tokens
                max_tokens = int(self._context_window * 0.7)  # Use 70% threshold

                self._log_progress(f"Data context size: {token_count} tokens (counted by Gemini)", "📊")

                if token_count > max_tokens:
                    self._log_progress(f"Combined data exceeds context window limit ({token_count} > {max_tokens} tokens). Truncating data.", "⚠️")
                    # Truncate by estimating characters per token (typically ~4 chars per token)
                    chars_per_token = len(combined_data_context) / token_count
                    # Estimate how many characters to keep
                    chars_to_keep = int(max_tokens * chars_per_token * 0.9)  # 90% of the limit to be safe
                    combined_data_context = combined_data_context[:chars_to_keep] + "\n... (data truncated)"

                    # Verify the truncation worked
                    test_prompt_truncated = f"""Given the following data:
{combined_data_context}

Answer the question: {query}
"""
                    new_token_count = self._llm.count_tokens(test_prompt_truncated).total_tokens
                    self._log_progress(f"After truncation: {new_token_count} tokens", "✂️")
            except Exception as e:
                # Fallback to character count if token counting fails
                self._log_progress(f"Error counting tokens with Gemini: {e}. Falling back to character count.", "⚠️")
                if len(combined_data_context) > self._context_window * 0.7:  # Use 70% threshold
                    self._log_progress(f"Combined data exceeds context window limit (char count). Truncating data.", "⚠️")
                    combined_data_context = combined_data_context[:int(self._context_window * 0.7)] + "\n... (data truncated)"
        else:
            # For Ollama or if Gemini token counting fails, use character count as an approximation
            if len(combined_data_context) > self._context_window * 0.7:  # Use 70% threshold
                self._log_progress(f"Combined data exceeds context window limit ({len(combined_data_context)} > {self._context_window * 0.7} chars). Truncating data.", "⚠️")
                combined_data_context = combined_data_context[:int(self._context_window * 0.7)] + "\n... (data truncated)"


        # Create a formatted prompt for the human response
        # Note: We don't need to use this directly as _generate_human_response handles it
        self._log_progress("Querying LLM with structured data context...", "🧠")
        try:
            # Use _generate_human_response directly as it handles LLM calls
            # We are asking the LLM to answer based on the provided data context
            response = await self._generate_human_response(query, combined_data_context)
            return response
        except Exception as e:
            self._log_progress(f"Error querying LLM for structured data: {e}", "❌")
            return DEFAULT_STRUCTURED_DATA_ERROR

    def _add_message(self, role: str, content: str) -> None:
        # For Gemini, store system messages in _system_prompt instead of history
        if self._llm_type == LLM_Type.GEMINI and role == "system":
            self._system_prompt = content
            self._log_progress(f"Stored system content in _system_prompt variable (not added to any history)", "💬")
            return  # Don't add to any history

        # Add to Ollama-format history
        message = {"role": role, "content": content}
        self._history.append(message)

        # For Gemini, also maintain the Gemini-specific format history (non-system messages only)
        if self._llm_type == LLM_Type.GEMINI:
            # Convert role from 'assistant' to 'model' for Gemini format
            gemini_role = "model" if role == "assistant" else role
            gemini_message = {
                "role": gemini_role,
                "parts": [{"text": content}]
            }
            self._gemini_history.append(gemini_message)
            self._log_progress(f"Added {gemini_role} message to Gemini history", "💬")

    def _create_system_prompt(self, db_schema: str) -> str:
        # Start with the base introduction
        base_intro = """You are a highly advanced SQL query generator.
 You are given a complex database schema and a set of rules. Your task is to generate accurate, readable, and production-quality SQL queries. based on that schema and rules."""

        final_prompt = f"{base_intro}\n\n{SQL_QUERY_GENERATION_RULES}"
        final_prompt = f"{final_prompt}\n\nThe database schema is as follows:\n{db_schema}"
        if self._ai_rules:
            final_prompt = f"{final_prompt}\n\n{self._ai_rules}"
        if self._custom_rules:
            final_prompt = f"{final_prompt}\n\n{self._custom_rules}"

        return final_prompt

    def _get_database_schema(self) -> str:
        self._log_progress("Fetching database schema...", "📊")
        result = "no schema"  # Default return value

        try:
            if self._my_sql_connection and self._my_sql_connection.is_connected():
                cursor = self._my_sql_connection.cursor()
                self._log_progress("Executing query to show tables...", "🔍")
                cursor.execute("SHOW TABLES")
                tables: List[Tuple[str]] = cursor.fetchall()

                self._log_progress(f"Found {len(tables)} tables in database", "📋")
                schema_info = []
                self._log_progress(f"Getting schemas for tables", "📑")
                for table in tables:
                    table_name = table[0]
                    # Properly escape table names with backticks
                    cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                    create_stmt = cursor.fetchone()[1]
                    schema_info.append(create_stmt)

                cursor.close()
                self._log_progress("Database schema fetched successfully", "✅")
                return '\n'.join(schema_info)

        except Exception as e:
            self._log_progress(f"Error fetching database schema: {e}", "❌")
            self._log_progress(f"Error fetching database schema: {e}", "❌")
            result = "db error" # Signal error state
        # Ensure cursor is closed even if connection check fails in `finally`
        finally:
            if 'cursor' in locals() and cursor:
                 try:
                     cursor.close()
                 except Exception as close_err:
                     self._log_progress(f"Error closing cursor: {close_err}", "⚠️")
            # No need to close connection here, it's managed externally

        return result

    def _execute_query(self, query: str) -> Union[List[Tuple], str]:
        cursor = None # Initialize cursor to None
        try:
            if not self._my_sql_connection or not self._my_sql_connection.is_connected():
                self._log_progress("MySQL connection is not available or closed.", "❌")
                return "error: MySQL connection is not available or closed."

            # Clean the query slightly (remove leading/trailing whitespace)
            query = query.strip()
            if not query:
                 self._log_progress("Received empty SQL query.", "⚠️")
                 return "error: Empty SQL query received."

            self._log_progress(f"Executing SQL query: {query}", "🔎")

            cursor = self._my_sql_connection.cursor()
            self._log_progress("Sending query to database...", "📤")

            # Store the query for later use in getting column names
            cursor._last_executed = query

            cursor.execute(query)
            result = cursor.fetchall()

            # Store column names from cursor description
            if cursor.description:
                self._last_query_columns = [col[0] for col in cursor.description]
                self._log_progress(f"Retrieved column names: {', '.join(self._last_query_columns)}", "📋")
            else:
                self._last_query_columns = []
                self._log_progress("No column names available from query", "⚠️")

            self._log_progress(f"Query executed successfully, returned {len(result)} rows.", "📥")
            return result # Return the actual data
        except Exception as e: # Catch specific MySQL errors if possible
            error_message = str(e)
            self._log_progress(f"Error executing SQL query: {error_message}", "❌")
            # Return the actual error message prefixed with "error:" for easier parsing
            return f"error: {error_message}"
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as close_err:
                    self._log_progress(f"Error closing cursor: {close_err}", "⚠️")


    def _determine_context_window(self) -> int:
        test_sizes = [
            1000000, 524288, 262144, 131072, 65536,
            49152, 40960, 32768, 24576, 20480, 16384,
            12288, 10240, 8192, 7168, 6144, 5120,
            4096, 3584, 3072, 2560, 2048
        ]

        for size in test_sizes:
            if self._verbose:
                print(f"Trying context window size: {size}...")
            try:
                temp_llm = Llama(model_path=self._model_path, n_ctx=size, verbose=False, use_mmap=False)
                del temp_llm
                return size
            except Exception as e:
                self._log_progress(f"Context window size {size} not supported: {e}", "ℹ️")
                continue

        self._log_progress(f"Could not determine maximum context window size automatically. Using default {DEFAULT_CONTEXT_WINDOW}.", "⚠️")
        return DEFAULT_CONTEXT_WINDOW

    def _determine_gemini_context_window(self, model_name: str) -> int:
        # Use the predefined context window sizes
        context_window_families = GEMINI_CONTEXT_WINDOWS

        # Remove the "models/" prefix if present
        clean_model_name = model_name.replace("models/", "")

        # First, try exact match
        if clean_model_name in context_window_families:
            window_size = context_window_families[clean_model_name]
            self._log_progress(f"Found exact match for {model_name}: {window_size} tokens", "✅")
            return window_size

        # If no exact match, try to match by family
        for family, window_size in context_window_families.items():
            # Check if the model name starts with the family name
            if clean_model_name.startswith(family):
                return window_size

            # For models with version numbers like gemini-1.5-flash-002
            parts = clean_model_name.split('-')
            if len(parts) >= 3:
                # Create potential family name from the first 3 parts (e.g., "gemini-1.5-flash")
                potential_family = '-'.join(parts[:3])
                if potential_family == family:
                    self._log_progress(f"Found family match for {model_name}: {window_size} tokens (family: {family})", "✅")
                    return window_size

        # Default fallback for unknown models
        # For Gemini 1.5 models, use 1M tokens
        if "gemini-1.5" in clean_model_name:
            self._log_progress(f"Unknown Gemini 1.5 model: {model_name}. Using {DEFAULT_GEMINI_15_CONTEXT_WINDOW} tokens as context window.", "⚠️")
            return DEFAULT_GEMINI_15_CONTEXT_WINDOW
        # For Gemini 2.0 or higher models, use 1M tokens
        elif any(x in clean_model_name for x in ["gemini-2", "gemini-3"]):
            self._log_progress(f"Unknown Gemini 2.0+ model: {model_name}. Using {DEFAULT_GEMINI_20_CONTEXT_WINDOW} tokens as context window.", "⚠️")
            return DEFAULT_GEMINI_20_CONTEXT_WINDOW
        # For other unknown models, use 32K tokens as a safe default
        else:
            self._log_progress(f"Unknown Gemini model: {model_name}. Using default context window size of {DEFAULT_GEMINI_CONTEXT_WINDOW} tokens.", "⚠️")
            return DEFAULT_GEMINI_CONTEXT_WINDOW

    def _initialize_model(self) -> Llama:
        if self._verbose:
            print(f"\n🚀 Initializing model with context window of {self._context_window} tokens...")
        try:
            llm = Llama(
                model_path=self._model_path,
                verbose=False,
                n_ctx=self._context_window,
                use_mmap=False, #This means the model will be loaded into RAM
                n_threads=self._n_threads, # Consider making this configurable or detecting CPU cores
            )
            self._log_progress(f"LLaMA model loaded successfully from {self._model_path}", "✅")
            self._log_progress(f"Effective context window: {llm.context_params.n_ctx} tokens", "🧠")
            return llm
        except Exception as e:
            self._log_progress(f"Error initializing LLaMA model: {e}", "❌")
            raise Exception(f"Failed to load LLaMA model: {str(e)}")


    def _select_model(self) -> str:
        # Find all GGUF files in the current directory
        gguf_files = glob.glob(MODELS_PATH)
        if not self._terminal:
            return gguf_files[0]

        print(gguf_files)

        if not gguf_files:
            self._log_progress("No GGUF models found in the 'models' directory!", "❌")
            # Raise an exception instead of exiting directly
            raise FileNotFoundError("No GGUF models found in the 'models' directory. Please place models there.")

        # If not in terminal mode, return the first found model non-interactively
        if not self._terminal:
             selected_model = gguf_files[0] # Or choose based on a pattern/config
             self._log_progress(f"Non-terminal mode: Automatically selected model: {selected_model}", "🤖")
             return selected_model

        # Terminal mode: Interactive selection
        self._log_progress("\n📚 Available LLaMA (GGUF) models:", "🤖")
        for i, model in enumerate(gguf_files, 1):
            size_mb = os.path.getsize(model) / (1024 * 1024)
            print(f"{i}. {model} ({size_mb:.1f} MB)")

        # Get user choice
        while True:
            try:
                choice = int(input("\nSelect model number: "))
                if 1 <= choice <= len(gguf_files):
                    return gguf_files[choice - 1]
                print("❌ Invalid choice. Please select a valid number.")
            except ValueError:
                self._log_progress("Invalid input. Please enter a number corresponding to the model.", "❌")

    def _log_progress(self, message, emoji="ℹ️"):
        # Only print if verbose is enabled
        # For model output logs, also check verbose_model_output flag
        if self._verbose:
            if "Full response from model:" in message and not self._verbose_model_output:
                # Skip detailed model output logs unless specifically enabled
                return

            print(f"{emoji} {message}")

    def _log_history(self, title="Current conversation history"):
        """Log the entire conversation history as a single message.

        Args:
            title: Title to display before the history
        """
        if not self._verbose:
            return

        print(f"📜 {title}:")
        print("-" * 50)

        # For Gemini, use our locally maintained Gemini history
        if self._llm_type == LLM_Type.GEMINI:
            if self._gemini_history:
                for i, msg in enumerate(self._gemini_history):
                    role = msg["role"]
                    # Extract content from parts
                    content = msg["parts"][0]["text"] if msg["parts"] else ""

                    print(f"Message {i+1} ({role}):")
                    print(content)
                    print("-" * 30)
            else:
                print("No Gemini history available.")
            return

        # For non-Gemini models (e.g., Ollama), use internal history
        for i, msg in enumerate(self._history):
            role = msg["role"]
            content = msg["content"]

            print(f"Message {i+1} ({role}):")
            print(content)
            print("-" * 30)

    async def _generate_combined_response(self, user_input: str) -> str:
        self._log_progress("📦 STARTING COMBINED RESPONSE GENERATION 📦", "🔄")
        self._log_progress("Combining instructions + database schema + AI rules + user question into a single request...", "🔄")

        # Get the system instruction (schema + rules)
        system_instruction = ""
        if self._llm_type == LLM_Type.GEMINI:
            # For Gemini, use the dedicated system_prompt variable
            if self._system_prompt:
                system_instruction = self._system_prompt
                self._log_progress(f"Using system instruction from _system_prompt ({len(system_instruction)} chars)", "📋")
            else:
                self._log_progress("No system instruction found in _system_prompt", "⚠️")
        else:
            # For Ollama, get from history
            if self._history and self._history[0]["role"] == "system":
                system_instruction = self._history[0]["content"]
                self._log_progress(f"Retrieved system instruction from history for Ollama ({len(system_instruction)} chars)", "📋")
            else:
                self._log_progress("No system instruction found in history", "⚠️")

        # For Gemini models, we don't want to include the system instruction in the prompt
        # Instead, we'll pass it during model initialization
        if self._llm_type == LLM_Type.GEMINI:
            combined_prompt = f"Based on the schema and meta-data you know, Create a MySQL query to answer this question: {user_input}"
            self._log_progress(f"Created Gemini-compatible prompt with user question: '{user_input[:50]}...'", "📝")
        else:
            # For Ollama, include the system instruction in the prompt
            combined_prompt = COMBINED_SQL_PROMPT.format(
                system_instruction=system_instruction,
                user_input=user_input
            )
            self._log_progress(f"Created combined prompt with system instructions and user question: '{user_input[:50]}...'", "📝")

        # For Gemini, we'll use the existing chat session when possible
        if self._llm_type == LLM_Type.GEMINI:
            # Initialize response variable
            response = "Error: Failed to generate a combined response."

            # --- Gemini Model Rotation Logic for Combined Response ---
            if self._enable_model_rotation:
                initial_model_index = self._current_gemini_model_index
                for attempt in range(len(self._available_gemini_models)):
                    current_model_name = self._available_gemini_models[self._current_gemini_model_index]
                    self._log_progress(f"Attempt {attempt + 1}/{len(self._available_gemini_models)}: Trying Gemini model '{current_model_name}' for combined response...", "📡")

                    try:
                        # Check if we need to create a new model (if model name changed or first attempt)
                        if attempt > 0 or (hasattr(self._llm, 'model_name') and self._llm.model_name != current_model_name):
                            self._log_progress(f"Creating new model instance for '{current_model_name}' (different from current model)", "🔄")

                            # Create a new model with system instruction
                            gen_config = genai.GenerationConfig(
                                max_output_tokens=self._max_tokens,
                                temperature=self._temperature
                            )

                            # Ensure system_instruction is assigned to _system_prompt before creating the model
                            if system_instruction:
                                self._system_prompt = system_instruction

                                self._llm = genai.GenerativeModel(
                                    model_name=current_model_name,
                                    generation_config=gen_config,
                                    system_instruction=self._system_prompt
                                )
                                self._log_progress(f"Created new model with system instruction", "💬")
                            else:
                                self._system_prompt = None
                                self._llm = genai.GenerativeModel(
                                    model_name=current_model_name,
                                    generation_config=gen_config
                                )
                                self._log_progress(f"Created new model without system instruction", "⚠️")

                            # Create a new chat session with history if available
                            if self._gemini_history:
                                self._log_progress("Transferring chat history to new chat session", "🔄")
                                # Filter out any system messages from history to avoid the error
                                filtered_history = [msg for msg in self._gemini_history if msg["role"] != "system"]
                                if len(filtered_history) != len(self._gemini_history):
                                    self._log_progress("Filtered out system messages from history for Gemini compatibility", "⚠️")

                                self._gemini_chat = self._llm.start_chat(history=filtered_history)
                                self._log_progress(f"Created new chat session with transferred history ({len(filtered_history)} messages)", "💬")
                            else:
                                self._gemini_chat = self._llm.start_chat()
                                self._log_progress("Created new chat session (no history to transfer)", "💬")

                            # Update context window for the new model
                            self._context_window = self._determine_gemini_context_window(current_model_name)
                            self._log_progress(f"Updated context window to {self._context_window} tokens", "🪟")
                        else:
                            self._log_progress(f"Using existing model instance and chat session", "💬")

                        # Send the combined prompt to the chat session
                        self._log_progress(f"Sending combined prompt to chat session using model {current_model_name}...", "📤")
                        response_obj = self._gemini_chat.send_message(combined_prompt)
                        response = response_obj.text

                        # Log the pure model response when verbose is enabled
                        if self._verbose:
                            print(f"🔮 Pure model response for SQL query generation:\n{'-' * 50}\n{response}\n{'-' * 50}")

                        self._log_progress(f"Combined response generated successfully with model {current_model_name} ({len(response)} chars)", "✅")

                        # Successful generation, break the retry loop
                        break

                    except ResourceExhausted as e:
                        self._log_progress(f"Rate limit hit for model '{current_model_name}' (combined response). Rotating model.", "⏳")
                        self._current_gemini_model_index = (self._current_gemini_model_index + 1) % len(self._available_gemini_models)

                        if self._current_gemini_model_index == initial_model_index:
                            self._log_progress("All available Gemini models are rate-limited (combined response).", "❌")
                            response = "Error: All Gemini models are currently rate-limited. Could not generate SQL query."
                            break # Exit loop

                    except Exception as e: # Catch other API errors
                        self._log_progress(f"Error with Gemini model '{current_model_name}' (combined response): {e}", "❌")
                        self._current_gemini_model_index = (self._current_gemini_model_index + 1) % len(self._available_gemini_models)

                        if self._current_gemini_model_index == initial_model_index:
                            self._log_progress(f"Failed to get combined response from any Gemini model after error: {e}", "❌")
                            response = f"Error: Failed to generate combined response after trying all models. Last error: {e}"
                            break # Exit loop
            else:
                # No model rotation, just use the current model
                try:
                    # Send the combined prompt to the existing chat session
                    self._log_progress("Sending combined prompt to existing chat session...", "📤")
                    response_obj = self._gemini_chat.send_message(combined_prompt)
                    response = response_obj.text

                    # Log the pure model response when verbose is enabled
                    if self._verbose:
                        print(f"🔮 Pure model response for SQL query generation:\n{'-' * 50}\n{response}\n{'-' * 50}")

                    self._log_progress(f"Combined response generated successfully ({len(response)} chars)", "✅")
                except Exception as e:
                    self._log_progress(f"Error generating combined response: {e}", "❌")
                    response = f"Error: Failed to generate combined response: {e}"
        else:
            # For Ollama, use the existing approach with temporary history
            temp_history = []
            if system_instruction:
                temp_history.append({"role": "system", "content": system_instruction})

            # Always include previous messages in the temporary history
            if len(self._history) > 1:
                # Skip the system message (index 0) and add all other messages
                conversation_context = []
                for i, msg in enumerate(self._history[1:]):  # Skip system message
                    # Don't add the current question again
                    if i == len(self._history) - 1 and msg["role"] == "user":
                        continue
                    conversation_context.append(msg)

                if conversation_context:
                    self._log_progress(f"Adding {len(conversation_context)} previous messages from conversation history", "🔄")
                    temp_history.extend(conversation_context)

            # Add the current question
            temp_history.append({"role": "user", "content": combined_prompt})
            self._log_progress(f"Created temporary history with {len(temp_history)} messages for this request", "🔄")

            # Store the original history
            original_history = self._history.copy()
            self._log_progress(f"Stored original history ({len(original_history)} messages) to restore later", "💾")

            # Replace history with temporary history for this request
            self._history = temp_history

            # Generate the response
            self._log_progress("Sending combined request to model...", "📤")
            response = await self._generate_response()

            # Log the pure model response when verbose is enabled
            if self._verbose:
                print(f"🔮 Pure model response for SQL query generation:\n{'-' * 50}\n{response}\n{'-' * 50}")

            self._log_progress(f"Combined response generated successfully ({len(response)} chars)", "✅")

            # Restore the original history
            self._history = original_history
            self._log_progress("Original conversation history restored", "🔄")

        # Log the conversation history for debugging
        if self._verbose:
            self._log_history("Conversation history after generating SQL query")

        self._log_progress("📦 COMBINED RESPONSE GENERATION COMPLETE 📦", "✅")

        return response

    async def _generate_sql_correction(self, user_input: str, original_query: str, error_message: str) -> str:
        """
        Generate a corrected SQL query based on the error message from a failed query execution.

        Args:
            user_input: The original user question
            original_query: The SQL query that failed
            error_message: The error message from the database

        Returns:
            A corrected SQL query
        """
        self._log_progress(f"Generating SQL query correction for error: {error_message}", "🔧")

        # We'll only switch models if an error occurs with the current model
        # No need to proactively switch to a better model for SQL correction
        # This ensures we use the same model instance for both SQL generation and correction
        if self._enable_model_rotation and self._llm_type == LLM_Type.GEMINI:
            self._log_progress("Model rotation is enabled, but we'll use the current model first", "💬")
            self._log_progress(f"Using current model '{self._gemini_model_name}' for SQL correction", "🔄")

        # Get the system instruction (schema + rules)
        system_instruction = ""
        if self._history and self._history[0]["role"] == "system":
            system_instruction = self._history[0]["content"]

        # Create a correction prompt
        # For both Gemini and Ollama, we use the same correction prompno t format
        # since it doesn't include system instructions
        correction_prompt = SQL_QUERY_CORRECTION_PROMPT.format(
            error_message=error_message,
            original_query=original_query,
            question=user_input
        )
        self._log_progress(f"Created SQL correction prompt for query: '{original_query[:50]}...'", "📝")

        # For Gemini, we'll use the existing chat session when possible
        if self._llm_type == LLM_Type.GEMINI:
            self._log_progress("Using existing chat session for SQL correction", "💬")

            # Send the correction prompt to the existing chat session
            self._log_progress("Sending SQL correction request to chat session...", "📤")
            try:
                response_obj = self._gemini_chat.send_message(correction_prompt)
                response = response_obj.text

                # Log the pure model response when verbose is enabled
                if self._verbose:
                    print(f"🔮 Pure model response for SQL correction:\n{'-' * 50}\n{response}\n{'-' * 50}")

                self._log_progress("SQL correction generated successfully", "✅")
            except Exception as e:
                self._log_progress(f"Error with existing model for SQL correction: {e}", "⚠️")

                # Now is the time to try model rotation if enabled
                if self._enable_model_rotation:
                    self._log_progress("Model rotation is enabled. Trying to use a better model.", "🔄")

                    # Models are already sorted by context window size (largest to smallest)
                    current_index = self._current_gemini_model_index

                    # If we're not already using the best model, switch to a better one
                    if current_index > 0:
                        # Move to a better model (lower index = larger context window)
                        better_index = max(0, current_index - 1)
                        better_model = self._available_gemini_models[better_index]

                        self._log_progress(f"Switching to better model '{better_model}' for SQL correction", "🔄")
                        self._current_gemini_model_index = better_index
                        self._gemini_model_name = better_model
                    else:
                        self._log_progress("Already using the best model. Will recreate it with the same parameters.", "🔄")

                # Create a new model as fallback
                gen_config = genai.GenerationConfig(
                    max_output_tokens=self._max_tokens,
                    temperature=self._temperature
                )

                # Get system instruction from _system_prompt (already set)
                if self._system_prompt:
                    self._log_progress(f"Using system instruction from _system_prompt ({len(self._system_prompt)} chars)", "🔧")
                else:
                    self._log_progress("No system instruction found in _system_prompt", "⚠️")

                # Create a new model with system instruction if available
                if self._system_prompt:
                    self._llm = genai.GenerativeModel(
                        model_name=self._gemini_model_name,
                        generation_config=gen_config,
                        system_instruction=self._system_prompt
                    )
                    self._log_progress(f"Created new model with system instruction", "💬")
                else:
                    self._llm = genai.GenerativeModel(
                        model_name=self._gemini_model_name,
                        generation_config=gen_config
                    )
                    self._log_progress(f"Created new model without system instruction", "⚠️")

                # Update context window for the new model
                self._context_window = self._determine_gemini_context_window(self._gemini_model_name)
                self._log_progress(f"Updated context window to {self._context_window} tokens", "🪟")

                # Create a new chat session with history if available
                if self._gemini_history:
                    self._log_progress("Transferring chat history to new chat session", "🔄")
                    # Filter out any system messages from history to avoid the error
                    filtered_history = [msg for msg in self._gemini_history if msg["role"] != "system"]
                    if len(filtered_history) != len(self._gemini_history):
                        self._log_progress("Filtered out system messages from history for Gemini compatibility", "⚠️")

                    self._gemini_chat = self._llm.start_chat(history=filtered_history)
                    self._log_progress(f"Created new chat session with transferred history ({len(filtered_history)} messages)", "💬")
                else:
                    self._gemini_chat = self._llm.start_chat()
                    self._log_progress("Created new chat session (no history to transfer)", "💬")

                # Try again with the new model
                try:
                    response_obj = self._gemini_chat.send_message(correction_prompt)
                    response = response_obj.text

                    # Log the pure model response when verbose is enabled
                    if self._verbose:
                        print(f"🔮 Pure model response for SQL correction (new model):\n{'-' * 50}\n{response}\n{'-' * 50}")

                    self._log_progress("SQL correction generated successfully with new model", "✅")
                except Exception as e2:
                    self._log_progress(f"Error with new model for SQL correction: {e2}. Giving up.", "❌")
                    return ""  # Return empty string to signal failure
        else:
            # For Ollama, use the existing approach with temporary history
            temp_history = []
            if system_instruction:
                temp_history.append({"role": "system", "content": system_instruction})
            temp_history.append({"role": "user", "content": correction_prompt})

            # Store the original history
            original_history = self._history.copy()

            # Replace history with temporary history for this request
            self._history = temp_history

            # Generate the response
            self._log_progress("Sending SQL correction request to model...", "📤")
            response = await self._generate_response()

            # Log the pure model response when verbose is enabled
            if self._verbose:
                print(f"🔮 Pure model response for SQL correction (Ollama):\n{'-' * 50}\n{response}\n{'-' * 50}")

            # Restore the original history
            self._history = original_history

        # Extract the corrected SQL query
        corrected_query = self._extract_sql_query(response)

        if not corrected_query or "error" in corrected_query.lower():
            self._log_progress("Failed to generate corrected SQL query.", "❌")
            return ""

        self._log_progress(f"Generated corrected SQL query: {corrected_query}", "✅")
        return corrected_query

    async def chat(self, user_input: str):
        """Process a user query and generate a response.

        This method is used when status_update=False (default).
        Returns the response as a string.

        For status updates, use chat_with_status_updates instead.

        Args:
            user_input: The user's question or query

        Returns:
            The response as a string
        """
        if self._status_update:
            raise ValueError("This method should not be called when status_update=True. Use chat_with_status_updates instead.")

        return await self._chat_with_return(user_input)

    async def chat_with_status_updates(self, user_input: str):
        """Process a user query and generate a response with status updates.

        This method is used when status_update=True.
        Yields status updates as "<status>message</status>" and the final response as "<response>content</response>".

        Args:
            user_input: The user's question or query

        Yields:
            Status updates as "<status>message</status>" and the final response as "<response>content</response>"
        """
        if not self._status_update:
            raise ValueError("This method should only be called when status_update=True.")

        yield "<status>Thinking...</status>"
        async for update in self._chat_with_yield(user_input):
            yield update

    async def _chat_with_return(self, user_input: str):
        """Internal implementation of chat that returns a value (no status updates)."""
        final_result = DEFAULT_ERROR_MESSAGE # Default error message

        try:
            # --- Initialization on first use (non-MySQL) ---
            if not self._initiated and self._service != Services.MYSQL:
                self._log_progress(f"Initializing {self._service.name} service for the first time...", "🚀")
                try:
                    loader_map = {
                        Services.CSV: self._load_structured_types,
                        Services.EXCEL: self._load_structured_types,
                        Services.PDF: self._load_document,
                        Services.DOCX: self._load_document
                    }
                    loader_map[self._service]() # These methods can raise Exceptions
                    self._initiated = True
                    self._log_progress(f"{self._service.name} service initialized successfully", "✅")
                except (ValueError, FileNotFoundError, Exception) as init_err:
                    self._log_progress(f"Failed to initialize service {self._service.name}: {init_err}", "❌")
                    return f"Error: Could not initialize the {self._service.name} service. Please check the file or configuration."

            # --- Input Processing & History Management ---
            self._log_progress(f"Processing query for {self._service.name}: {user_input}", "💬")
            # Basic input validation/sanitization could be added here
            if not user_input:
                return "Please provide a question or query."

            # Truncate long inputs (especially for MySQL prompt generation)
            max_input_len = 1500
            if len(user_input) > max_input_len:
                original_len = len(user_input)
                user_input = user_input[:max_input_len] + "..."
                self._log_progress(f"User input truncated from {original_len} to {max_input_len} chars.", "✂️")

            # Always in conversation mode now
            if self._first_question:
                self._log_progress("First question - keeping system instructions", "💬")
                self._first_question = False
            else:
                self._log_progress("Preserving chat history", "💬")

            self._log_progress("Truncating chat history if needed...", "✂️")
            self._truncate_history() # Handles logging internally

            # --- Service-Specific Logic ---
            if self._service == Services.MYSQL:
                # 1. Send instructions + schema + rules + user question to the model
                self._log_progress("Generating SQL query with combined context...", "⏳")

                # Generate the SQL query with combined context
                raw_response = await self._generate_combined_response(user_input)

                # Extract SQL query from the response
                sql_query = self._extract_sql_query(raw_response)

                if not sql_query or "error" in sql_query.lower(): # Check if generation failed
                    self._log_progress("Failed to generate SQL query.", "❌")
                    return DEFAULT_SQL_GENERATION_ERROR

                # Add the user's question to history
                self._add_message("user", user_input)

                # Log the conversation history (before adding SQL query)
                if self._verbose:
                    self._log_history("Conversation history after adding user question")

                # Initialize variables for retry logic
                current_query = sql_query
                max_retries = DEFAULT_MAX_SQL_RETRIES
                retry_count = 0
                db_result = None

                # Execute SQL query with retry logic
                while retry_count < max_retries:
                    # Execute the current query
                    self._log_progress(f"Executing SQL query (attempt {retry_count + 1}/{max_retries})...", "📊")
                    db_result = self._execute_query(current_query)

                    # Check if query execution was successful
                    if isinstance(db_result, list):
                        # Query executed successfully
                        self._log_progress(f"SQL query executed successfully on attempt {retry_count + 1}.", "✅")
                        break
                    elif isinstance(db_result, str) and db_result.startswith("error:"):
                        # Query execution failed with an error
                        error_message = db_result[6:].strip()  # Remove "error: " prefix
                        self._log_progress(f"SQL query execution failed with error: {error_message}", "❌")

                        # If we've reached max retries, break the loop
                        if retry_count >= max_retries - 1:
                            self._log_progress(f"Maximum retry attempts ({max_retries}) reached. Giving up.", "⚠️")
                            break

                        # Generate a corrected query
                        # If model rotation is enabled, _generate_sql_correction will try to use a better model
                        self._log_progress("Asking model to fix the SQL query...", "🔄")
                        corrected_query = await self._generate_sql_correction(user_input, current_query, error_message)

                        if not corrected_query:
                            self._log_progress("Failed to generate a corrected SQL query. Giving up.", "❌")
                            break

                        # Update the current query for the next attempt
                        current_query = corrected_query
                        self._log_progress(f"Retrying with corrected SQL query: {current_query}", "🔄")
                        retry_count += 1
                    else:
                        # Unexpected result format
                        self._log_progress(f"Unexpected result from _execute_query: {db_result}", "⚠️")
                        break

                # Add the SQL query to history (original or corrected version)
                self._add_message("assistant", current_query)

                # Log the updated conversation history
                if self._verbose:
                    self._log_history("Conversation history after adding SQL query")

                # 3. Generate Human Response based on DB result
                if not isinstance(db_result, list):
                    # Query execution failed after all retries
                    self._log_progress("SQL query execution failed after all retry attempts.", "❌")
                    # Add error message to history
                    error_msg = DEFAULT_MAX_SQL_RETRIES_EXCEEDED if retry_count >= max_retries else DEFAULT_DB_ERROR_MESSAGE
                    self._add_message("assistant", error_msg)
                    final_result = error_msg
                else:
                    self._log_progress(f"Query returned {len(db_result)} results.", "✅")

                    # Format the database results in a more readable way
                    formatted_result = self._format_db_results(db_result)
                    self._log_progress(f"Formatted database results:\n{'-' * 50}\n{formatted_result}\n{'-' * 50}", "📋")

                    # Check if the query returned any results
                    if len(db_result) == 0:
                        # Use the custom message for empty results
                        self._log_progress("Query returned no results. Using custom empty result message.", "ℹ️")
                        self._add_message("assistant", self._empty_result_message)
                        final_result = self._empty_result_message
                    else:
                        # Only generate human response if there are actual results
                        self._log_progress("Generating human response based on query results and conversation history...", "✅")

                        # Create a prompt that includes the history and formatted results
                        human_response = await self._generate_human_response(user_input, formatted_result)
                        self._add_message("assistant", human_response)
                        final_result = human_response

                        # Log the updated conversation history
                        if self._verbose:
                            self._log_history("Conversation history after adding human response")

                return final_result

            else: # Handle PDF, DOCX, CSV, EXCEL
                # 1. Add user query to history
                self._add_message("user", user_input)

                # 2. Retrieve Relevant Data/Chunks
                self._log_progress("Retrieving relevant information...", "🔍")
                retrieved_data = ""
                if self._service in [Services.CSV, Services.EXCEL]:
                    retrieved_data = await self.query_csv(user_input) # Returns combined response or error string
                else: # PDF, DOCX
                    retrieved_data = self.query_chunks(user_input) # Returns combined chunks or error string

                if "error" in retrieved_data.lower() or "could not retrieve" in retrieved_data.lower():
                     self._log_progress("Failed to retrieve relevant data.", "❌")
                     # Add error to history
                     error_msg = "Sorry, I couldn't retrieve the necessary information to answer your question."
                     self._add_message("assistant", error_msg)
                     final_result = error_msg
                elif "no relevant information found" in retrieved_data.lower():
                     self._log_progress("No relevant information found for the query.", "❓")
                     self._add_message("assistant", retrieved_data) # Add the "not found" message
                     final_result = retrieved_data
                else:
                    # 3. Generate Human Response based on retrieved data
                    self._log_progress("Generating final response based on retrieved data...", "⏳")
                    # The prompt for _generate_human_response already includes the data
                    human_response = await self._generate_human_response(user_input, retrieved_data)
                    self._add_message("assistant", human_response)
                    final_result = human_response

            # --- Return Result ---
            self._log_progress("Processing complete.", "🏁")
            return final_result

        # --- General Exception Handling ---
        except Exception as e:
            self._log_progress(f"An unexpected error occurred during chat processing: {str(e)}", "❌")
            # Log traceback for debugging if needed: import traceback; traceback.print_exc()
            # Add a generic error message to history if possible
            error_for_user = DEFAULT_UNEXPECTED_ERROR
            try:
                # Try adding error to history, but don't fail if history is broken
                if self._history and self._history[-1]["role"] != "assistant": # Avoid duplicate errors
                     self._add_message("assistant", error_for_user)
            except:
                 pass # Ignore errors during error handling
            return error_for_user

    async def _chat_with_yield(self, user_input: str):
        """Internal implementation of chat that yields status updates."""
        final_result = DEFAULT_ERROR_MESSAGE # Default error message

        try:
            # --- Initialization on first use (non-MySQL) ---
            if not self._initiated and self._service != Services.MYSQL:
                self._log_progress(f"Initializing {self._service.name} service for the first time...", "🚀")
                try:
                    loader_map = {
                        Services.CSV: self._load_structured_types,
                        Services.EXCEL: self._load_structured_types,
                        Services.PDF: self._load_document,
                        Services.DOCX: self._load_document
                    }
                    loader_map[self._service]() # These methods can raise Exceptions
                    self._initiated = True
                    self._log_progress(f"{self._service.name} service initialized successfully", "✅")
                except (ValueError, FileNotFoundError, Exception) as init_err:
                    self._log_progress(f"Failed to initialize service {self._service.name}: {init_err}", "❌")
                    error_msg = f"Error: Could not initialize the {self._service.name} service. Please check the file or configuration."
                    yield f"<response>{error_msg}</response>"
                    return

            # --- Input Processing & History Management ---
            self._log_progress(f"Processing query for {self._service.name}: {user_input}", "💬")
            # Basic input validation/sanitization could be added here
            if not user_input:
                error_msg = "Please provide a question or query."
                yield f"<response>{error_msg}</response>"
                return

            # Truncate long inputs (especially for MySQL prompt generation)
            max_input_len = 1500
            if len(user_input) > max_input_len:
                original_len = len(user_input)
                user_input = user_input[:max_input_len] + "..."
                self._log_progress(f"User input truncated from {original_len} to {max_input_len} chars.", "✂️")

            # Always in conversation mode now
            if self._first_question:
                self._log_progress("First question - keeping system instructions", "💬")
                self._first_question = False
            else:
                self._log_progress("Preserving chat history", "💬")

            self._log_progress("Truncating chat history if needed...", "✂️")
            self._truncate_history() # Handles logging internally

            # --- Service-Specific Logic ---
            if self._service == Services.MYSQL:
                # 1. Send instructions + schema + rules + user question to the model
                self._log_progress("Generating SQL query with combined context...", "⏳")

                # Generate the SQL query with combined context
                raw_response = await self._generate_combined_response(user_input)

                # Extract SQL query from the response
                sql_query = self._extract_sql_query(raw_response)

                if not sql_query or "error" in sql_query.lower(): # Check if generation failed
                    self._log_progress("Failed to generate SQL query.", "❌")
                    yield f"<response>{DEFAULT_SQL_GENERATION_ERROR}</response>"
                    return

                # Add the user's question to history
                self._add_message("user", user_input)

                # Log the conversation history (before adding SQL query)
                if self._verbose:
                    self._log_history("Conversation history after adding user question")

                # Initialize variables for retry logic
                current_query = sql_query
                max_retries = DEFAULT_MAX_SQL_RETRIES
                retry_count = 0
                db_result = None

                # Execute SQL query with retry logic
                while retry_count < max_retries:
                    # Execute the current query
                    self._log_progress(f"Executing SQL query (attempt {retry_count + 1}/{max_retries})...", "📊")

                    # Yield querying status
                    yield "<status>Querying database...</status>"

                    db_result = self._execute_query(current_query)

                    # Check if query execution was successful
                    if isinstance(db_result, list):
                        # Query executed successfully
                        self._log_progress(f"SQL query executed successfully on attempt {retry_count + 1}.", "✅")
                        break
                    elif isinstance(db_result, str) and db_result.startswith("error:"):
                        # Query execution failed with an error
                        error_message = db_result[6:].strip()  # Remove "error: " prefix
                        self._log_progress(f"SQL query execution failed with error: {error_message}", "❌")

                        # If we've reached max retries, break the loop
                        if retry_count >= max_retries - 1:
                            self._log_progress(f"Maximum retry attempts ({max_retries}) reached. Giving up.", "⚠️")
                            break

                        # Generate a corrected query
                        # If model rotation is enabled, _generate_sql_correction will try to use a better model
                        self._log_progress("Asking model to fix the SQL query...", "🔄")

                        # Yield improving query status
                        yield "<status>Improving query...</status>"

                        corrected_query = await self._generate_sql_correction(user_input, current_query, error_message)

                        if not corrected_query:
                            self._log_progress("Failed to generate a corrected SQL query. Giving up.", "❌")
                            break

                        # Update the current query for the next attempt
                        current_query = corrected_query
                        self._log_progress(f"Retrying with corrected SQL query: {current_query}", "🔄")
                        retry_count += 1
                    else:
                        # Unexpected result format
                        self._log_progress(f"Unexpected result from _execute_query: {db_result}", "⚠️")
                        break

                # Add the SQL query to history (original or corrected version)
                self._add_message("assistant", current_query)

                # Log the updated conversation history
                if self._verbose:
                    self._log_history("Conversation history after adding SQL query")

                # 3. Generate Human Response based on DB result
                if not isinstance(db_result, list):
                    # Query execution failed after all retries
                    self._log_progress("SQL query execution failed after all retry attempts.", "❌")
                    # Add error message to history
                    error_msg = DEFAULT_MAX_SQL_RETRIES_EXCEEDED if retry_count >= max_retries else DEFAULT_DB_ERROR_MESSAGE
                    self._add_message("assistant", error_msg)
                    final_result = error_msg
                else:
                    self._log_progress(f"Query returned {len(db_result)} results.", "✅")

                    # Format the database results in a more readable way
                    formatted_result = self._format_db_results(db_result)
                    self._log_progress(f"Formatted database results:\n{'-' * 50}\n{formatted_result}\n{'-' * 50}", "📋")

                    # Check if the query returned any results
                    if len(db_result) == 0:
                        # Use the custom message for empty results
                        self._log_progress("Query returned no results. Using custom empty result message.", "ℹ️")
                        self._add_message("assistant", self._empty_result_message)
                        final_result = self._empty_result_message
                    else:
                        # Only generate human response if there are actual results
                        self._log_progress("Generating human response based on query results and conversation history...", "✅")

                        # Create a prompt that includes the history and formatted results
                        human_response = await self._generate_human_response(user_input, formatted_result)
                        self._add_message("assistant", human_response)
                        final_result = human_response

                        # Log the updated conversation history
                        if self._verbose:
                            self._log_history("Conversation history after adding human response")

                # Yield the final result
                yield f"<response>{final_result}</response>"
                return

            else: # Handle PDF, DOCX, CSV, EXCEL
                # 1. Add user query to history
                self._add_message("user", user_input)

                # 2. Retrieve Relevant Data/Chunks
                self._log_progress("Retrieving relevant information...", "🔍")
                retrieved_data = ""
                if self._service in [Services.CSV, Services.EXCEL]:
                    retrieved_data = await self.query_csv(user_input) # Returns combined response or error string
                else: # PDF, DOCX
                    retrieved_data = self.query_chunks(user_input) # Returns combined chunks or error string

                if "error" in retrieved_data.lower() or "could not retrieve" in retrieved_data.lower():
                     self._log_progress("Failed to retrieve relevant data.", "❌")
                     # Add error to history
                     error_msg = "Sorry, I couldn't retrieve the necessary information to answer your question."
                     self._add_message("assistant", error_msg)
                     final_result = error_msg
                elif "no relevant information found" in retrieved_data.lower():
                     self._log_progress("No relevant information found for the query.", "❓")
                     self._add_message("assistant", retrieved_data) # Add the "not found" message
                     final_result = retrieved_data
                else:
                    # 3. Generate Human Response based on retrieved data
                    self._log_progress("Generating final response based on retrieved data...", "⏳")
                    # The prompt for _generate_human_response already includes the data
                    human_response = await self._generate_human_response(user_input, retrieved_data)
                    self._add_message("assistant", human_response)
                    final_result = human_response

            # --- Yield Final Result ---
            self._log_progress("Processing complete.", "🏁")
            yield f"<response>{final_result}</response>"

        # --- General Exception Handling ---
        except Exception as e:
            self._log_progress(f"An unexpected error occurred during chat processing: {str(e)}", "❌")
            # Log traceback for debugging if needed: import traceback; traceback.print_exc()
            # Add a generic error message to history if possible
            error_for_user = DEFAULT_UNEXPECTED_ERROR
            try:
                # Try adding error to history, but don't fail if history is broken
                if self._history and self._history[-1]["role"] != "assistant": # Avoid duplicate errors
                     self._add_message("assistant", error_for_user)
            except:
                 pass # Ignore errors during error handling

            yield f"<response>{error_for_user}</response>"


    async def _generate_response(self) -> str:
        self._log_progress("Starting response generation", "🔄")
        self._log_progress(f"Using LLM type: {self._llm_type.name}", "💬")

        response_text = "Error: Failed to generate a response." # Default error

        try:
            if self._llm_type == LLM_Type.OLLAMA:
                self._log_progress("Generating response with Ollama...", "🤖")
                self._log_progress(f"Using temperature: {self._temperature} for SQL generation", "🌡️")

                # Log the entire request for debugging
                self._log_progress("Sending request to Ollama model", "📤")
                # Log the entire history as one message
                self._log_history("Request to Ollama model")

                response = self._llm.create_chat_completion(
                    messages=self._history,
                    max_tokens=self._max_tokens,
                    temperature=self._temperature,
                    stream=False
                )

                # Extract the response text from the non-streaming response
                if isinstance(response, dict) and 'choices' in response:
                    response_text = response['choices'][0].get('message', {}).get('content', '')
                    self._log_progress("Ollama response complete", "✅")
                else:
                    self._log_progress("Unexpected response format from Ollama", "⚠️")
                    response_text = "Error: Unexpected response format from model."
                # Print the full response for debugging
                self._log_progress(f"Full response from Ollama model:\n{'-' * 50}\n{response_text}\n{'-' * 50}", "📄")
            elif self._llm_type == LLM_Type.GEMINI:
                # For Gemini, we expect the user message to be passed directly
                # We don't need to extract it from history
                user_message = None
                for msg in reversed(self._history):
                    if msg["role"] == "user":
                        user_message = msg["content"]
                        break

                if not user_message:
                    self._log_progress("No user message found in history", "⚠️")
                    return "Error: No user message found in history"

                self._log_progress(f"Sending request to Gemini API ({self._gemini_model_name})...", "📡")

                # --- Gemini Model Rotation Logic ---
                initial_model_index = self._current_gemini_model_index
                for attempt in range(len(self._available_gemini_models)):
                    current_model_name = self._available_gemini_models[self._current_gemini_model_index]
                    self._log_progress(f"Attempt {attempt + 1}/{len(self._available_gemini_models)}: Trying Gemini model '{current_model_name}'...", "📡")

                    try:
                        # Check if we need to recreate the chat session with a different model
                        if attempt > 0 or (hasattr(self._llm, 'model_name') and self._llm.model_name != current_model_name):
                            self._log_progress(f"Switching to model: {current_model_name}", "🔄")

                            # Get the system instruction if available
                            system_instruction = None
                            if self._history and self._history[0]["role"] == "system":
                                system_instruction = self._history[0]["content"]

                            # Update context window for the new model
                            self._context_window = self._determine_gemini_context_window(current_model_name)
                            self._log_progress(f"Switching to model {current_model_name} with context window {self._context_window}", "🔄")

                            # Create generation config
                            gen_config = genai.GenerationConfig(
                                max_output_tokens=self._max_tokens,
                                temperature=self._temperature
                            )

                            # Ensure system_instruction is assigned to _system_prompt before creating the model
                            if system_instruction:
                                self._system_prompt = system_instruction
                                self._llm = genai.GenerativeModel(
                                    model_name=current_model_name,
                                    generation_config=gen_config,
                                    system_instruction=self._system_prompt
                                )
                                self._log_progress(f"Created model with system instruction ({len(self._system_prompt)} chars)", "💬")
                            else:
                                self._system_prompt = None
                                self._llm = genai.GenerativeModel(
                                    model_name=current_model_name,
                                    generation_config=gen_config
                                )
                                self._log_progress("Created model without system instruction", "💬")

                            # Transfer chat history when creating a new chat session
                            if self._gemini_history:
                                # Create new chat with our locally maintained history
                                self._log_progress("Transferring chat history to new model", "🔄")
                                self._gemini_chat = self._llm.start_chat(history=self._gemini_history)
                                self._log_progress(f"Created new chat session with transferred history ({len(self._gemini_history)} messages)", "💬")
                            else:
                                # Create a new chat session without history
                                self._gemini_chat = self._llm.start_chat()
                                self._log_progress("Created new chat session (no history to transfer)", "💬")

                        # Note: Generation config is already set during chat creation
                        self._log_progress(f"Using temperature: {self._temperature} for generation", "🌡️")

                        # Send the user message to the chat session using the client API
                        self._log_progress("Sending user message to Gemini chat session", "📤")
                        response = self._gemini_chat.send_message(user_message)

                        self._log_progress(f"Received response from Gemini API ({current_model_name})", "✅")
                        response_text = response.text

                        # Print the full response for debugging
                        self._log_progress(f"Full response from model:\n{'-' * 50}\n{response_text}\n{'-' * 50}", "📄")

                        # Successful generation, break the retry loop
                        break # Exit the loop on success

                    except ResourceExhausted as e:
                        self._log_progress(f"Rate limit hit for model '{current_model_name}'. Rotating model.", "⏳")
                        self._current_gemini_model_index = (self._current_gemini_model_index + 1) % len(self._available_gemini_models)

                        # Check if we've tried all models and are back to the start
                        if self._current_gemini_model_index == initial_model_index:
                            self._log_progress("All available Gemini models are rate-limited.", "❌")
                            response_text = "Error: All Gemini models are currently rate-limited. Please try again later."
                            break # Exit the loop as all models failed

                        # Otherwise, continue to the next iteration to try the next model

                    except Exception as e: # Catch other API errors for the current model attempt
                        self._log_progress(f"Error with Gemini model '{current_model_name}': {e}", "❌")
                        # Decide if you want to rotate on other errors or just fail
                        # For now, let's treat other errors as fatal for this attempt and rotate
                        self._current_gemini_model_index = (self._current_gemini_model_index + 1) % len(self._available_gemini_models)

                        # Check if we've tried all models and are back to the start
                        if self._current_gemini_model_index == initial_model_index:
                            self._log_progress(f"Failed to get response from any Gemini model after error: {e}", "❌")
                            response_text = f"Error: Failed to generate response after trying all models. Last error: {e}"
                            break # Exit the loop as all models failed

                        # Otherwise, continue to try next model after non-rate-limit error

            # Outer exception handling for non-API call errors within the Gemini block
            # (e.g., history conversion issues, though those should be caught earlier)
            # Note: API call errors are handled within the loop now.

        except Exception as e:
             # This catches errors outside the API call loop within the Gemini logic
             # or errors within the Ollama block
             error_message = str(e)
             self._log_progress(f"Unexpected error during response generation: {error_message}", "❌")
             # Handle specific API errors if possible (e.g., quota, invalid key) - Moved inside loop for Gemini
             if self._llm_type == LLM_Type.GEMINI:
                 # Generic error if it happened outside the loop
                 response_text = DEFAULT_GEMINI_ERROR
             elif self._llm_type == LLM_Type.OLLAMA:
                 response_text = DEFAULT_OLLAMA_ERROR
             else:
                 response_text = DEFAULT_GENERIC_ERROR


        return response_text.strip()




    async def _generate_human_response(self, question: str, result: str) -> str:
        self._log_progress("Generating human-readable response...", "🗣️")
        # Basic prompt construction with language instruction
        # Format the conversation history for context (used for both Gemini and Ollama)
        history_context = ""
        if len(self._history) >= 2:  # We need at least the user question and SQL response
            for msg in self._history:
                if msg["role"] == "system":
                    continue  # Skip system messages
                role_display = "User" if msg["role"] == "user" else "Assistant"
                history_context += f"{role_display}: {msg['content']}\n\n"

        # Create the appropriate prompt based on service type
        if self._service == Services.MYSQL:
            # For MySQL results, provide a more specific prompt that includes conversation history
            prompt = MYSQL_HUMAN_RESPONSE_PROMPT.format(
                history_context=history_context,
                result=result,
                question=question,
                language=self._response_language
            )
        elif self._service in [Services.CSV, Services.EXCEL]:
            # For other structured data results, ask to summarize based on the result
            prompt = STRUCTURED_DATA_RESPONSE_PROMPT.format(
                result=result,
                question=question,
                language=self._response_language
            )
        else: # PDF, DOCX
            # For document chunks, ask to answer using *only* the provided text
            prompt = DOCUMENT_RESPONSE_PROMPT.format(
                result=result,
                question=question,
                language=self._response_language
            )

        # For Gemini, we'll use the prompt as is (system instructions are passed during model initialization)
        # For Ollama, we'll modify the prompt to include system instructions

        # Limit result context size to avoid exceeding limits in this call too
        max_result_len = self._context_window * 0.5 # Use 50% for result context here
        if len(result) > max_result_len:
             result_preview = result[:int(max_result_len)] + "... (data truncated)"
             prompt = prompt.replace(result, result_preview) # Update prompt with truncated data
             self._log_progress("Result data truncated for human response generation prompt.", "✂️")


        response_text = DEFAULT_HUMAN_RESPONSE_ERROR # Default error
        try:
            if self._llm_type == LLM_Type.OLLAMA:
                self._log_progress("Generating human response with Ollama...", "🤖")
                # Use create_chat_completion for consistency if possible, or direct call if needed
                # Direct call example:
                human_response_temp = 0.1  # Lower temperature for more factual responses
                self._log_progress(f"Using temperature: {human_response_temp} for human response generation", "🌡️")

                # Check if we have a system instruction to include
                system_instruction = None
                if self._history and self._history[0]["role"] == "system":
                    system_instruction = self._history[0]["content"]

                # For MySQL service, we need to ensure the system instruction is properly included
                # but we don't want to include the SQL-specific instructions for human responses
                if self._service == Services.MYSQL and system_instruction:
                    # Extract only the database schema part without the SQL generation rules
                    # First split at SQL rules marker
                    parts = system_instruction.split("IMPORTANT RULES FOR GENERATING SQL QUERIES")
                    schema_part = parts[0].strip()

                    # If there are AI rules, they would be after the SQL rules
                    # Check if we have more than one split (meaning we found the marker)
                    # and if there's an AI rules section after that
                    ai_rules_part = ""
                    if len(parts) > 1 and self._ai_rules:
                        # Look for AI rules in the remaining text
                        remaining_text = parts[1]
                        # Find where the AI rules start in the remaining text
                        if self._ai_rules in remaining_text:
                            ai_rules_part = self._ai_rules
                            self._log_progress("Found and preserved AI rules for human response", "📝")

                    # Create a new system instruction with schema and possibly AI rules
                    system_instruction = f"You are a helpful assistant. Use the following database schema to understand the data structure:\n{schema_part}"
                    if ai_rules_part:
                        system_instruction += f"\n\n{ai_rules_part}"

                    self._log_progress("Modified system instruction for human response to exclude SQL generation rules", "📝")

                # For Ollama, we need to include system instructions in the prompt
                # This is different from Gemini where we pass them during model initialization
                modified_prompt = prompt
                if system_instruction:
                    modified_prompt = f"System instruction: {system_instruction}\n\n{prompt}"
                    self._log_progress("Prepended system instruction to Ollama prompt (required for Ollama)", "📝")

                # Log the entire prompt for debugging
                self._log_progress("Sending human response prompt to Ollama model", "📤")
                # Show the raw prompt in a more structured way
                if self._verbose:
                    print(f"📜 Human response prompt to Ollama model:")
                    print("-" * 50)
                    print(modified_prompt)
                    print("-" * 50)

                response = self._llm(modified_prompt, max_tokens=500, temperature=human_response_temp, stream=False)
                response_text = response['choices'][0].get('text', '').strip()
                self._log_progress("Ollama human response generated.", "✅")
                # Print the full response for debugging
                self._log_progress(f"Full response from Ollama model:\n{'-' * 50}\n{response_text}\n{'-' * 50}", "📄")

            elif self._llm_type == LLM_Type.GEMINI:
                self._log_progress("Generating human response with Gemini...", "🤖")

                # --- Gemini Model Rotation Logic ---
                initial_model_index = self._current_gemini_model_index
                for attempt in range(len(self._available_gemini_models)):
                    current_model_name = self._available_gemini_models[self._current_gemini_model_index]
                    self._log_progress(f"Attempt {attempt + 1}/{len(self._available_gemini_models)}: Trying Gemini model '{current_model_name}' for human response...", "📡")

                    try:
                        # Check if we need to create a new model (if model name changed or first attempt failed)
                        if attempt > 0 or (hasattr(self._llm, 'model_name') and self._llm.model_name != current_model_name):
                            self._log_progress(f"Creating new model instance for '{current_model_name}' (different from current model)", "🔄")

                            # For Gemini, use the dedicated system_prompt variable
                            system_instruction = self._system_prompt

                            # For MySQL service, we need to ensure the system instruction is properly included
                            # but we don't want to include the SQL-specific instructions for human responses
                            if self._service == Services.MYSQL:
                                    # Extract only the database schema part without the SQL generation rules
                                    # First split at SQL rules marker
                                    parts = system_instruction.split("IMPORTANT RULES FOR GENERATING SQL QUERIES")
                                    schema_part = parts[0].strip()

                                    # If there are AI rules, they would be after the SQL rules
                                    ai_rules_part = ""
                                    if len(parts) > 1 and self._ai_rules:
                                        # Look for AI rules in the remaining text
                                        remaining_text = parts[1]
                                        # Find where the AI rules start in the remaining text
                                        if self._ai_rules in remaining_text:
                                            ai_rules_part = self._ai_rules
                                            self._log_progress("Found and preserved AI rules for human response", "📝")

                                    # Create a new system instruction with schema and possibly AI rules
                                    system_instruction = f"You are a helpful assistant. Use the following database schema to understand the data structure:\n{schema_part}"
                                    if ai_rules_part:
                                        system_instruction += f"\n\n{ai_rules_part}"

                                    self._log_progress("Modified system instruction for human response to exclude SQL generation rules", "📝")

                            # Create a new model with system instruction
                            gen_config = genai.GenerationConfig(
                                max_output_tokens=500,
                                temperature=0.1  # Lower temperature for more factual responses
                            )

                            # Ensure system_instruction is assigned to _system_prompt before creating the model
                            if system_instruction:
                                self._system_prompt = system_instruction
                                self._llm = genai.GenerativeModel(
                                    model_name=current_model_name,
                                    generation_config=gen_config,
                                    system_instruction=self._system_prompt
                                )
                                self._log_progress(f"Created new model with system instruction", "💬")
                            else:
                                self._system_prompt = None
                                self._llm = genai.GenerativeModel(
                                    model_name=current_model_name,
                                    generation_config=gen_config
                                )
                                self._log_progress(f"Created new model without system instruction", "⚠️")

                            # Create a new chat session with history if available
                            if self._gemini_history:
                                self._log_progress("Transferring chat history to new chat session", "🔄")
                                # Filter out any system messages from history to avoid the error
                                filtered_history = [msg for msg in self._gemini_history if msg["role"] != "system"]
                                if len(filtered_history) != len(self._gemini_history):
                                    self._log_progress("Filtered out system messages from history for Gemini compatibility", "⚠️")

                                self._gemini_chat = self._llm.start_chat(history=filtered_history)
                                self._log_progress(f"Created new chat session with transferred history ({len(filtered_history)} messages)", "💬")
                            else:
                                self._gemini_chat = self._llm.start_chat()
                                self._log_progress("Created new chat session (no history to transfer)", "💬")

                            # Update context window for the new model
                            self._context_window = self._determine_gemini_context_window(current_model_name)
                            self._log_progress(f"Updated context window to {self._context_window} tokens", "🪟")
                        else:
                            self._log_progress("Using existing model instance and chat session", "💬")

                        # Log the prompt for debugging
                        self._log_progress(f"Sending prompt to chat session:\n{'-' * 50}", "📤")
                        self._log_progress(f"Raw prompt: {prompt}", "📤")
                        self._log_progress(f"{'-' * 50}", "📤")

                        # Send the prompt to the chat session
                        response = self._gemini_chat.send_message(prompt)

                        response_text = response.text.strip()
                        self._log_progress(f"Gemini human response generated ({current_model_name}).", "✅")
                        # Print the full response for debugging
                        self._log_progress(f"Full response from model:\n{'-' * 50}\n{response_text}\n{'-' * 50}", "📄")
                        # Successful generation, break the retry loop
                        break # Exit the loop on success

                    except ResourceExhausted as e:
                        self._log_progress(f"Rate limit hit for model '{current_model_name}' (human response). Rotating model.", "⏳")
                        self._current_gemini_model_index = (self._current_gemini_model_index + 1) % len(self._available_gemini_models)

                        if self._current_gemini_model_index == initial_model_index:
                            self._log_progress("All available Gemini models are rate-limited (human response).", "❌")
                            response_text = "Error: All Gemini models are currently rate-limited. Could not generate human-readable response."
                            break # Exit loop

                        # Continue loop

                    except Exception as e: # Catch other API errors
                        self._log_progress(f"Error with Gemini model '{current_model_name}' (human response): {e}", "❌")
                        self._current_gemini_model_index = (self._current_gemini_model_index + 1) % len(self._available_gemini_models)

                        if self._current_gemini_model_index == initial_model_index:
                            self._log_progress(f"Failed to get human response from any Gemini model after error: {e}", "❌")
                            response_text = f"Error: Failed to generate human response after trying all models. Last error: {e}"
                            break # Exit loop

                        # Continue loop

            # Check response after loop completes (or breaks)
            if not response_text or response_text.startswith("Error:"): # Handle empty or error responses from the loop
                # Log specific error if it came from the loop, otherwise generic
                if not response_text.startswith("Error:"):
                    self._log_progress("LLM returned an empty human response.", "⚠️")
                    response_text = "I couldn't formulate a response based on the information."
                # else: response_text already contains the error message from the loop
                # Return the error/empty message
                return response_text

            # If loop completed successfully, return the generated text
            return response_text

        except Exception as e:
             # Catches errors outside the API call loop (e.g., prompt construction)
             # or errors in the Ollama block
            self._log_progress(f"Error generating human response: {str(e)}", "❌")
            # Return the default error message defined at the start
            return DEFAULT_HUMAN_RESPONSE_ERROR


    def _truncate_history(self):
        """Truncate chat history if it exceeds context window size."""
        # Count tokens differently based on the LLM type
        if self._llm_type == LLM_Type.GEMINI and hasattr(self, '_llm'):
            # For Gemini, use the model's count_tokens method for accurate token counting
            try:
                # Use our maintained Gemini history format directly
                # Count tokens using the model's method
                token_count_result = self._llm.count_tokens(self._gemini_history)
                history_token_count = token_count_result.total_tokens
                self._log_progress(f"Current history size: {history_token_count} tokens (counted by Gemini)", "📊")
            except Exception as e:
                # Fallback to character count if token counting fails
                self._log_progress(f"Error counting tokens with Gemini: {e}. Falling back to character count.", "⚠️")
                history_token_count = sum(len(str(message)) for message in self._gemini_history)
                self._log_progress(f"Current history size: {history_token_count} chars (fallback method)", "📊")
        else:
            # For Ollama or if Gemini token counting fails, use character count as an approximation
            history_token_count = sum(len(str(message)) for message in self._history)
            self._log_progress(f"Current history size: {history_token_count} chars", "📊")

        # Get the correct context window size for the current model
        if self._llm_type == LLM_Type.GEMINI and hasattr(self, '_llm'):
            # Re-determine the context window size for the current Gemini model
            current_model_name = self._llm.model_name if hasattr(self._llm, 'model_name') else self._gemini_model_name
            self._context_window = self._determine_gemini_context_window(current_model_name)

        # Log the context window size
        self._log_progress(f"Context window size: {self._context_window} tokens", "🪟")

        if history_token_count <= self._context_window:
            self._log_progress("History size within context window limits, no truncation needed", "✅")
            return

        self._log_progress("History exceeds context window, beginning truncation...", "✂️")
        truncated_messages = 0
        prev_history_size = -1  # To detect when we can't reduce further

        # Maximum iterations to prevent infinite loops
        max_iterations = 100
        iterations = 0

        while history_token_count > self._context_window and iterations < max_iterations:
            iterations += 1

            # If we couldn't reduce size in the last iteration, break loop
            if history_token_count == prev_history_size:
                self._log_progress("Unable to reduce history further, breaking truncation loop", "⚠️")
                break

            prev_history_size = history_token_count

            # Preserve system messages
            if self._ai_rules:
                if len(self._history) > 2:  # Ensure there are at least three messages
                    self._log_progress(f"Removing message: {self._history[2]['role']} (preserving system message)", "🗑️")
                    # Remove from both history formats
                    self._history.pop(2)  # Remove the second message (index 1)
                    if self._llm_type == LLM_Type.GEMINI and len(self._gemini_history) > 2:
                        self._gemini_history.pop(2)
                    truncated_messages += 1
                else:
                    # Can't remove more messages while preserving system message
                    self._log_progress("Cannot remove more messages while preserving system message", "⚠️")
                    break
            else:
                if len(self._history) > 1:  # Ensure there are at least two messages
                    self._log_progress(f"Removing message: {self._history[1]['role']}", "🗑️")
                    # Remove from both history formats
                    self._history.pop(1)  # Remove the first message (index 0)
                    if self._llm_type == LLM_Type.GEMINI and len(self._gemini_history) > 1:
                        self._gemini_history.pop(1)
                    truncated_messages += 1
                else:
                    # Can't remove more messages
                    self._log_progress("Cannot remove more messages, history minimal", "⚠️")
                    break

            # Recalculate token count after removing a message
            if self._llm_type == LLM_Type.GEMINI and hasattr(self, '_llm'):
                try:
                    # Use our maintained Gemini history format directly
                    # Count tokens using the model's method
                    token_count_result = self._llm.count_tokens(self._gemini_history)
                    history_token_count = token_count_result.total_tokens
                    self._log_progress(f"New history size: {history_token_count} tokens (counted by Gemini)", "📏")
                except Exception as e:
                    # Fallback to character count if token counting fails
                    history_token_count = sum(len(str(message)) for message in self._gemini_history)
                    self._log_progress(f"New history size: {history_token_count} chars (fallback method)", "📏")
            else:
                # For Ollama or if Gemini token counting fails, use character count as an approximation
                history_token_count = sum(len(str(message)) for message in self._history)
                self._log_progress(f"New history size: {history_token_count} chars", "📏")

        if iterations >= max_iterations:
            self._log_progress("Maximum iterations reached, forcing truncation to continue", "⚠️")
            # Force truncate to a minimal state to prevent complete failure
            if len(self._history) > 1:
                # Keep only the system message (if any) and the latest user message
                if self._ai_rules and len(self._history) > 0 and self._history[0]["role"] == "system":
                    system_msg = self._history[0]
                    user_msg = self._history[-1] if self._history[-1]["role"] == "user" else None
                    self._history = [system_msg]
                    if user_msg:
                        self._history.append(user_msg)

                    # Also update Gemini history if needed
                    if self._llm_type == LLM_Type.GEMINI:
                        system_gemini_msg = self._gemini_history[0] if self._gemini_history and self._gemini_history[0]["role"] == "system" else None
                        user_gemini_msg = self._gemini_history[-1] if self._gemini_history and self._gemini_history[-1]["role"] == "user" else None
                        self._gemini_history = []
                        if system_gemini_msg:
                            self._gemini_history.append(system_gemini_msg)
                        if user_gemini_msg:
                            self._gemini_history.append(user_gemini_msg)
                else:
                    # Keep just the last message if it's a user message
                    last_msg = self._history[-1] if self._history[-1]["role"] == "user" else None
                    self._history = [last_msg] if last_msg else []

                    # Also update Gemini history if needed
                    if self._llm_type == LLM_Type.GEMINI:
                        last_gemini_msg = self._gemini_history[-1] if self._gemini_history and self._gemini_history[-1]["role"] == "user" else None
                        self._gemini_history = [last_gemini_msg] if last_gemini_msg else []

                # Recalculate token count after forced truncation
                if self._llm_type == LLM_Type.GEMINI and hasattr(self, '_llm'):
                    try:
                        # Use our maintained Gemini history format directly
                        token_count_result = self._llm.count_tokens(self._gemini_history)
                        history_token_count = token_count_result.total_tokens
                        self._log_progress(f"Forced minimal history size: {history_token_count} tokens (counted by Gemini)", "🔄")
                    except Exception as e:
                        # Fallback to character count if token counting fails
                        history_token_count = sum(len(str(message)) for message in self._gemini_history)
                        self._log_progress(f"Forced minimal history size: {history_token_count} chars (fallback method)", "🔄")
                else:
                    # For Ollama or if Gemini token counting fails, use character count as an approximation
                    history_token_count = sum(len(str(message)) for message in self._history)
                    self._log_progress(f"Forced minimal history size: {history_token_count} chars", "🔄")

        self._log_progress(f"Truncation complete, removed {truncated_messages} messages", "✅")

    def _extract_sql_query(self, response_text: str) -> str:
        if not response_text or response_text.startswith("Error:"):
            self._log_progress(f"Cannot extract SQL from error response: {response_text}", "⚠️")
            return response_text

        self._log_progress("Attempting to extract SQL query from model response...", "🧹")

        # Check if the response is already a clean SQL query (no markdown, no explanations)
        if response_text.strip().upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "SHOW", "USE", "DESCRIBE", "EXPLAIN", "SET")) and "```" not in response_text:
            self._log_progress("Response appears to be a clean SQL query already", "✅")
            return response_text.strip()

        # Use the predefined SQL extraction patterns
        sql_patterns = SQL_EXTRACTION_PATTERNS

        extracted_sql = ""
        for pattern in sql_patterns:
            matches = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
            if matches:
                extracted_sql = matches.group(1).strip() if len(matches.groups()) > 0 else matches.group(0).strip()
                # Basic validation: check for common SQL keywords
                if any(keyword in extracted_sql.upper() for keyword in ["SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "SHOW"]):
                    self._log_progress(f"Found SQL query using pattern: {pattern[:30]}...", "🔍")
                    break  # Found a likely SQL query
                else:
                    extracted_sql = ""  # Reset if it doesn't look like SQL

        if extracted_sql:
            self._log_progress(f"Successfully extracted SQL query: {extracted_sql}", "✅")
            return extracted_sql
        else:
            self._log_progress("Could not extract a clean SQL query from the response. Using the full response.", "⚠️")
            # Check if the response contains "I need data" or similar phrases indicating the model is confused
            if "need data" in response_text.lower() or "database is empty" in response_text.lower() or "no data" in response_text.lower():
                self._log_progress("Model response indicates it needs data or schema information", "⚠️")
                # Return a more specific error message
                return DEFAULT_SQL_SCHEMA_ERROR
            return response_text

    def _format_db_results(self, db_result: List[Tuple]) -> str:
        if not db_result:
            return "No results returned from the database."

        try:
            # Use the column names we stored during query execution
            if hasattr(self, '_last_query_columns') and self._last_query_columns:
                column_names = self._last_query_columns
                self._log_progress(f"Using stored column names: {', '.join(column_names)}", "📋")
            else:
                # If we don't have stored column names, try to get them from cursor description
                column_names = []
                if hasattr(self, '_my_sql_connection') and self._my_sql_connection.is_connected():
                    cursor = self._my_sql_connection.cursor()
                    try:
                        # Try to get the last executed query
                        if hasattr(cursor, '_last_executed') and cursor._last_executed:
                            # Re-execute the query to get column names
                            cursor.execute(cursor._last_executed)
                            if cursor.description:
                                column_names = [col[0] for col in cursor.description]
                                self._log_progress(f"Retrieved column names from re-execution: {', '.join(column_names)}", "📋")
                    except Exception as e:
                        self._log_progress(f"Error getting column names: {e}", "⚠️")
                    finally:
                        cursor.close()

            # If we still don't have column names, use generic ones
            if not column_names and db_result:
                column_names = [f"Column_{i}" for i in range(len(db_result[0]))]
                self._log_progress("Using generic column names", "ℹ️")

            # Format as a table with headers
            result_str = "Database Query Results:\n\n"

            # Add column headers if we have them
            if column_names:
                header_row = " | ".join(column_names)
                result_str += header_row + "\n"
                result_str += "-" * len(header_row) + "\n"

            # Add data rows
            for row in db_result:
                # Convert all values to strings and handle None values
                row_values = [str(val) if val is not None else "NULL" for val in row]
                result_str += " | ".join(row_values) + "\n"

            return result_str

        except Exception as e:
            self._log_progress(f"Error formatting database results: {e}", "⚠️")
            # Fall back to simple string representation
            return str(db_result)

    def reset_conversation(self):
        """Reset the conversation history, keeping only the system message if it exists.

        This is useful when you want to start a new conversation.
        """
        # For Ollama, get system message from history
        if self._llm_type == LLM_Type.OLLAMA:
            system_message = None
            if self._history and self._history[0]["role"] == "system":
                system_message = self._history[0]

            # Clear history
            self._history = []

            # Restore system message if it existed
            if system_message:
                self._history.append(system_message)

        # For Gemini, we keep system message in _system_prompt
        elif self._llm_type == LLM_Type.GEMINI:
            # Clear history (system message is already in _system_prompt)
            self._history = []
            self._gemini_history = []

            # No need to add system message to history for Gemini
            # It's already stored in _system_prompt
            if self._system_prompt:
                self._log_progress(f"Kept system message in _system_prompt variable ({len(self._system_prompt)} chars)", "💬")

        # Reset first question flag
        self._first_question = True

        # If using Gemini, recreate the chat session with the existing model
        if self._llm_type == LLM_Type.GEMINI and hasattr(self, '_llm'):
            try:
                # Use the existing model instance but create a new chat session
                self._log_progress("Creating new chat session with existing model instance", "🔄")
                self._gemini_chat = self._llm.start_chat()
                self._log_progress("Recreated Gemini chat session with existing model instance", "💬")
            except Exception as e:
                self._log_progress(f"Error recreating Gemini chat session: {e}. Will try to create a new model.", "⚠️")

                try:
                    # Create a new model as fallback
                    gen_config = genai.GenerationConfig(
                        max_output_tokens=self._max_tokens,
                        temperature=self._temperature
                    )

                    # Create a new model with system instruction if available
                    # _system_prompt is already set at this point
                    if self._system_prompt:
                        self._llm = genai.GenerativeModel(
                            model_name=self._gemini_model_name,
                            generation_config=gen_config,
                            system_instruction=self._system_prompt
                        )
                        self._log_progress(f"Created new model with system instruction", "💬")
                    else:
                        self._llm = genai.GenerativeModel(
                            model_name=self._gemini_model_name,
                            generation_config=gen_config
                        )
                        self._log_progress(f"Created new model without system instruction", "⚠️")

                    # Create a new chat session
                    self._gemini_chat = self._llm.start_chat()
                    self._log_progress("Created new chat session with new model instance", "💬")
                except Exception as e2:
                    self._log_progress(f"Error creating new model and chat session: {e2}", "❌")

        self._log_progress("Conversation history has been reset", "🔄")

        return "Conversation history has been reset."

    def _clean_up(self):
        if hasattr(self, '_my_sql_connection') and self._my_sql_connection:
            self._my_sql_connection.close()
        if hasattr(self, '_chromaDB'):
            del self._chromaDB
        if hasattr(self, '_gemini_chat'):
            del self._gemini_chat
        if hasattr(self, '_llm'):
            del self._llm

    def __del__(self):
        self._clean_up()

    def _sort_models_by_context_window(self):
        if not self._available_gemini_models:
            self._log_progress("No models available to sort", "⚠️")
            return

        # Create a list of (model_name, context_window) tuples
        model_sizes = []
        for model_name in self._available_gemini_models:
            context_size = self._determine_gemini_context_window(model_name)
            model_sizes.append((model_name, context_size))
            self._log_progress(f"Model {model_name}: {context_size} tokens", "📏")

        # Sort by context window size (largest to smallest)
        model_sizes.sort(key=lambda x: x[1], reverse=True)
        self._log_progress(f"Models sorted by context window size: {model_sizes}", "📊")

        # Update the available models list with the sorted models
        self._available_gemini_models = [model[0] for model in model_sizes]

    @staticmethod
    def get_available_gemini_models(api_key: str) -> List[str]:
        try:
            # Configure the genai library with API key
            genai.configure(api_key=api_key)
            # List available models
            models = genai.list_models()
            gemini_models = [model.name for model in models if "gemini" in model.name]
            return gemini_models
        except Exception as e:
            # Log specific Gemini errors if possible
            # Consider filtering models based on supported generation methods if needed
            # e.g., models = [m for m in models if 'generateContent' in m.supported_generation_methods]
            raise Exception(f"Failed to fetch Gemini models: {str(e)}")


# async def main():
#     """Main function to run interactive chat loop in terminal."""
#     print("Initializing ChatBot for interactive session...")
#     try:
#         # --- Configuration ---
#         # Choose service type (e.g., PDF, MYSQL, CSV)
#         service_type = Services.PDF # Example: Use PDF service

#         # Provide necessary details based on service type
#         file_path = "chatbot.md" # Example PDF path (replace with actual path)
#         mysql_conn = None # Set up mysql.connector connection if using MYSQL
#         ai_rules = None # Path to AI rules file (optional)
#         llm_choice = LLM_Type.OLLAMA # Choose OLLAMA or GEMINI
#         gemini_key = os.environ.get("GEMINI_API_KEY") # Get key from environment variable

#         # --- Instantiate ChatBot ---
#         chatbot = ChatBot(
#             service=service_type,
#             file_path=file_path,
#             mysql_connection=mysql_conn,
#             terminal=True, # Enable interactive model selection etc.
#             ai_rules_path=ai_rules,
#             llm_type=llm_choice,
#             gemini_api_key=gemini_key
#             # gemini_model_name="gemini-1.5-flash" # Optional: specify model
#         )
#         print("\nChatBot ready. Type 'quit' to exit.")
#         print("-" * 30)

#         # --- Chat Loop ---
#         while True:
#             question = input("You: ")
#             if question.lower() == 'quit':
#                 print("Exiting chatbot.")
#                 break
#             if not question.strip():
#                 continue

#             print("Bot: ", end="", flush=True) # Prepare for streaming or full response
#             try:
#                 response = await chatbot.chat_with_llama(question)
#                 # Assuming chat_with_llama returns the final string response here
#                 print(response)
#             except Exception as chat_err:
#                 # Catch errors during the chat interaction itself
#                 print(f"\nError during chat: {chat_err}")
#                 # Optionally, try to recover or just continue the loop

#     except (FileNotFoundError, ValueError, ConnectionError, SystemExit, Exception) as init_err:
#          # Catch initialization errors
#          print(f"\n❌ Critical Error during ChatBot setup: {init_err}")
#          print("Exiting application.")
#     except KeyboardInterrupt:
#         print("\n⌨️ User interrupted. Shutting down...")
#     finally:
#         # Perform any final cleanup if needed (though __del__ handles some)
#         print("Chatbot session ended.")
