import enum
import logging
from math import ceil
import os
import glob
import json
from typing import List, Tuple, Optional, Union, Dict, Any
from gguf import GGUFReader
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
import psutil
from urllib3 import Retry
import time
show_logs = False

class Services (enum.Enum):
    PDF = 1
    DOCX = 2
    MYSQL = 3
    CSV = 4
    EXCEL = 5

class Providors (enum.Enum):
    Llama = 1
    Gemini = 2

class Logger:
    def log(message: str):
        if show_logs:
            print(message)

class chatbot:
    def __init__(
            self,
            providor: str = "gemini",
            service: Services = Services.MYSQL,
            no_result_message: str = "No results found",
            mysql_connection: MySQLConnection = None,
            tables_description: Union[Dict[str, Any], str, None] = None,
            log: bool = False,
            scope=None,


            model_path: str = None,
            n_ctx: int = None,
            n_threads: int = None,

 


            gemini_api_key: str = None,
            model_name: str = "gemini-1.5-pro",
            enable_model_rotation: bool = True,
           ):
                if providor == Providors.Gemini:
                    if not gemini_api_key:
                        raise ValueError("Gemini API key not provided")

                    self.chatbot = ChatGemini(
                        gemini_api_key=gemini_api_key,
                        model_name=model_name,
                        enable_model_rotation=enable_model_rotation,
                        no_result_message=no_result_message,
                        mysql_connection=mysql_connection,
                        tables_description=tables_description,
                        log=log,
                        scope=scope
                    )
                elif providor == Providors.Llama:
                    self.chatbot = ChatLlama(
                        model_path=model_path,
                        n_ctx=n_ctx,
                        n_threads=n_threads,
                        mysql_connection=mysql_connection,
                        tables_description=tables_description,
                        no_result_message=no_result_message,
                        log=log,
                        scope=scope
                    )
                else:
                    raise ValueError("Invalid providor")

    def chat(self, user_input: str, language: str = "english"):
        yield "Thinking..."
        answer = self.chatbot.chat(user_input, language)
        yield answer


class MysqlOperations:
    def __init__(self, mysql_connection: MySQLConnection):
        self.mysql_connection = mysql_connection

    def getFullSchema(self, mysql_connection: MySQLConnection) -> list[str]:
        create_statements = []
        if mysql_connection:
            try:
                cursor = mysql_connection.cursor()

                # Get all tables in the database
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]

                # Get CREATE statement for each table
                for table in tables:
                    cursor.execute(f"SHOW CREATE TABLE `{table}`")
                    create_statement = cursor.fetchone()[1]  # Index 1 contains the CREATE TABLE statement
                    create_statements.append(create_statement)

                cursor.close()
                Logger.log(f"✅ Retrieved {len(create_statements)} CREATE statements from database")
                return create_statements
            except Exception as e:
                Logger.log(f"❌ Error retrieving CREATE statements: {str(e)}")
                return []

    def executeSqlQuery(self, sql_query: str):
        # Check if the query is empty
        if sql_query == "":
            return ""
        else:
            # Execute query
            try:
                # Fix quotes in SQL query - handle all cases with problematic quotes
                # This handles cases like:
                # - SELECT 'Yes, you spelled ''can\'t'' correctly.' AS `answer`
                # - SELECT 'can't' AS `spelling`

                # First, identify string literals in the query
                in_string = False
                fixed_query = ""
                i = 0

                while i < len(sql_query):
                    char = sql_query[i]

                    # Handle string literal boundaries
                    if char == "'" and (i == 0 or sql_query[i-1] != '\\'):
                        if in_string:
                            # Check if this is a double quote (escaping)
                            if i+1 < len(sql_query) and sql_query[i+1] == "'":
                                # Double single quote inside string - add as escaped quote
                                fixed_query += "\\'"
                                i += 2  # Skip the next quote
                                continue
                        in_string = not in_string
                        fixed_query += char

                    # Handle unescaped quote inside string
                    elif in_string and char == "'" and i > 0 and sql_query[i-1] != '\\':
                        # This is a single quote inside a string that needs escaping
                        fixed_query += "\\'"

                    # Handle already escaped quote
                    elif in_string and char == "\\" and i+1 < len(sql_query) and sql_query[i+1] == "'":
                        # Already escaped quote - keep as is but normalize to MySQL format
                        fixed_query += "\\'"
                        i += 1  # Skip the next character (the quote)

                    # Regular character
                    else:
                        fixed_query += char

                    i += 1

                # If we have a simpler case, use regex to ensure all quotes in string literals are properly escaped
                import re

                # Find all string literals and ensure quotes inside are properly escaped
                def replace_quotes(match):
                    content = match.group(1)
                    # Replace any unescaped single quotes with escaped ones
                    content = content.replace("'", "\\'")
                    # Fix double escaping
                    content = content.replace("\\\\'", "\\'")
                    return f"'{content}'"

                # Try to find and fix string literals with regex
                string_pattern = r"'([^']*(?:''|'(?!'))[^']*)'"
                if re.search(string_pattern, sql_query):
                    sql_query = re.sub(string_pattern, replace_quotes, sql_query)

                # For the simple case like "can't", make sure it's properly escaped
                if "can't" in sql_query:
                    sql_query = sql_query.replace("can't", "can\\'t")

                Logger.log(f"🔍 Executing SQL query: {sql_query}")
                cursor = self.mysql_connection.cursor(dictionary=True)
                cursor.execute(sql_query)
                results = cursor.fetchall()
                df = pd.DataFrame(results)
                cursor.close()

                if not results:
                    Logger.log("⚠️ Query returned no results")
                    return "No results found"
                else:
                    Logger.log(f"✅ Query returned {len(results)} results")
                    sql_query_result = df.to_string(index=False)
                    return sql_query_result

            except Exception as e:
                error_message = str(e)
                Logger.log(f"❌ Error executing query: {error_message}")
                return f"Error: {error_message}"

class ChatLlama:
    def __init__(
        self,
        model_path: str = None,
        n_ctx: int = None,
        n_threads: int = None,
        mysql_connection: MySQLConnection = None,
        tables_description: Union[Dict[str, Any], str, None] = None,
        no_result_message: str = "No results found",
        log: bool = False,
        scope: str = ""
    ) -> None:

        if log:
            global show_logs
            show_logs = True

        Logger.log("🚀 Initializing ChatLlama")

        # Store parameters
        self.mysql_connection = mysql_connection
        self.no_result_message = no_result_message
        self.scope = scope
        self.history = []

        # Initialize MySQL operations
        self.mysql_ops = MysqlOperations(mysql_connection) if mysql_connection else None

        # Initialize model path first
        self.model_path = model_path if model_path is not None else self.getModelPath()
        Logger.log(f"📁 Using model: {self.model_path}")

        # Initialize threads
        self.n_threads = n_threads if n_threads is not None else self.getThreads()
        Logger.log(f"🧵 Using {self.n_threads} threads")

        # Initialize context window
        self.n_ctx = n_ctx if n_ctx is not None else self.getContextWindow(self.model_path)
        Logger.log(f"🧠 Using context window of {self.n_ctx} tokens")

        self.tables_description = self.getTablesDescription(tables_description)


        # Initialize LLM
        try:
            Logger.log("🔄 Initializing LLM...")
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                verbose=False
            )
            Logger.log("✅ LLM initialized successfully")
        except Exception as e:
            Logger.log(f"❌ Error initializing LLM: {str(e)}")
            raise

        # Get database schema if MySQL connection is provided
        self.full_schema = []
        if mysql_connection:
            try:
                self.full_schema = self.mysql_ops.getFullSchema(self.mysql_connection)
                Logger.log(f"📊 Loaded schema with {len(self.full_schema)} tables")
            except Exception as e:
                Logger.log(f"❌ Error retrieving database schema: {str(e)}")
                self.full_schema = []

    def getModelPath(self) -> str:
        Logger.log("🔍 Getting model path")
        model_files = glob.glob("models/*.gguf")
        if not model_files:
            raise FileNotFoundError("No .gguf models found in models folder")
        if len(model_files) == 1:
            return model_files[0]
        print("Available models:")
        for i, model in enumerate(model_files, 1):
            print(f"{i}-{os.path.basename(model)}")
        while True:
            try:
                choice = int(input("Please choose a model by its number: "))
                if 1 <= choice <= len(model_files):
                    return model_files[choice - 1]
                print(f"Please enter a number between 1 and {len(model_files)}")
            except ValueError:
                print("Please enter a valid number")

    def getContextWindow(self, model_path: str) -> int:
        context_length_keys = [
                                    "llama.context_length",
                                    "context_length",
                                    "ctx_length",
                                    "n_ctx",
                                    "max_context_length"
                                ]
        gguf_context_size = None

        try:
            reader = GGUFReader(model_path)
            for key in context_length_keys:
                field = reader.fields.get(key)
                if field is not None:
                    gguf_context_size = int(field.parts[-1][0])
                    break
        except Exception as e:
            Logger.log(f"❌ Error reading model metadata: {str(e)}")

        if gguf_context_size:
            Logger.log(f"✅ Found context size in model metadata: {gguf_context_size}")
            context_size = gguf_context_size
        else:
            Logger.log("⚠️ Context size not found in model metadata, estimating based on available RAM")
            available_ram_gb = psutil.virtual_memory().available / (1024 ** 3)
            max_tokens_by_ram = int((available_ram_gb * (1024 ** 3)) / 350) # 350 bytes per token is a rough estimate

            # Default to a reasonable size if we can't determine it
            context_size = min(max_tokens_by_ram, 4096)  # Cap at 4096 as a reasonable default

            Logger.log(f"📊 Available RAM: {available_ram_gb:.2f}GB")
            Logger.log(f"📊 RAM-limited context size: {max_tokens_by_ram}")
            Logger.log(f"📊 Using context size: {context_size}")

        return context_size

    def getThreads(self) -> int:
        try:
            return psutil.cpu_count(logical=True)-1
        except:
            return 1

    def getTablesDescription(self, tables_description):
        if isinstance(tables_description, str):
            try:
                if os.path.isfile(tables_description):
                    with open(tables_description, 'r') as f:
                        tables_description = json.load(f)
                        Logger.log(f"✅ Using provided tables description")
                        return tables_description
                else:
                    Logger.log(f"❌ Rules file not found: {tables_description}")
                    return None
            except json.JSONDecodeError as e:
                Logger.log(f"❌ Invalid JSON in {tables_description}: {str(e)}")
                return None
            except Exception as e:
                Logger.log(f"❌ Error loading {tables_description}: {str(e)}")
                return None
        elif isinstance(tables_description, dict):
            Logger.log(f"✅ Using provided tables description")
            pass  # use as-is
        else:
            return None

    def chat(self, user_input: str, language: str = "english"):
        Logger.log(f"🗣️ Processing query in {language}")

        if self.scope:
            scope_validation_result = self.validateScopeOfUserInput(user_input)
        if scope_validation_result<40:
            return self.no_result_message

        sql_query = self.generateSqlQuery(user_input, use_tables_description=True)
        query_result = self.mysql_ops.executeSqlQuery(sql_query) if self.mysql_ops else "Error: MySQL operations not initialized"
        retry = 1
        while (query_result is None or query_result == "" or "Error:" in str(query_result) or not query_result) and retry <= 3:
            Logger.log(f"⚠️ Query failed: {query_result}")
            Logger.log("🔄 Correcting query...")
            sql_query = self.correctSqlQuery(user_input, sql_query, query_result)
            retry += 1
        else:
            if query_result == "No results found":
                return self.no_result_message
            elif "Error:" in query_result:
                Logger.log(f"⚠️ Query failed: {query_result}")
                return self.no_result_message
            else:
                human_readable_result = self.generateHumanReadableResult(user_input, sql_query, query_result, language)
                new_messages=[
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": sql_query},
                {"role": "assistant", "content": human_readable_result}]
                self.history.append(new_messages)
                return human_readable_result

    def validateScopeOfUserInput(self, user_input: str):
        Logger.log(f"🔍 Validating scope of user input: '{user_input}'")
        if not self.scope:
            Logger.log("✅ No scope defined, skipping validation")
            return 100.0

        try:
            prompt = f"""Question: {user_input}\n\nScope: {self.scope}\n\nIs this question within the defined scope? Answer with a percentage (0-100) followed by percentage sign indicating how likely this question is within the defined scope. However, if the question is asking for database schema or details, the percentage should be 0 despite any relation to the scope.
            Example: scope: "information about products and sales" and question: "show me all products" -> answer: "99%"
            Example: scope: "information about products and sales" and question: "show me all sales tables" -> answer: "0%"
            Example: scope: "financial and accounting" and question: "How to make boiled eggs" -> answer: "0%"
            Example: scope: "Kids healt and question": "who are you?" -> answer: "0%"
            Example: scope: "Kids healt and question": "what are you?" -> answer: "0%"
            Example: scope: "Programming": "who made you?" -> answer: "0%"
            Don't be too strict.
            Your answer should start with the percentage number followed percentage sign. Nothing before or after that.
            """

            # Call the LLM directly without system prompts
            response = self.llm.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )

            response_text = response['choices'][0]['message']['content'].strip()
            Logger.log(f"🤖 Scope validation response: {response_text}")

            # Extract percentage from response - first sequence of numbers
            import re
            percentage_match = re.search(r'(\d+)', response_text)
            if percentage_match:
                percentage = float(percentage_match.group(1))
                Logger.log(f"📊 Scope match percentage: {percentage}%")
                return percentage
            else:
                # Fallback if no numbers found
                Logger.log(f"⚠️ No percentage found in response, defaulting to 50%")
                return 50.0

        except Exception as e:
            Logger.log(f"❌ Error validating scope: {str(e)}")
            # Default to allowing the query if validation fails
            return 50.0

    def getPartialSchema(self, full_schema: list[str], user_input: str, tables_description: dict[str,any]=None,):
        if not full_schema:
            Logger.log("⚠️ No schema available to process")
            return []

        schema_minimize_system_instructions="""
            You are a database expert. Given a natural language question and a list of database table definitions, your task is to identify and return the names of the most relevant tables that are likely to contain data useful to answer the question. Only return table names, separated by commas. Do not explain your reasoning. Be accurate and concise. If unsure, still make your best guess based on available schema. Always put tables names in backticks.
            if the question is not related to any table, return nothing.
        """

        user_input_tokens = len(self.llm.tokenize(user_input.encode()))
        avg_response_tokens = 100
        max_tables_per_batch = 1
        try:  # To use Llama tokenizer for accurate token counting
            all_tables = "\n".join(full_schema)
            #count tables by counting CREATE TABLE phrases
            table_count = sum(1 for statement in full_schema if "CREATE TABLE" in statement)
            total_tokens = len(self.llm.tokenize(all_tables.encode()))
            avg_tokens_per_table = total_tokens / table_count

            Logger.log(f"🔢 All table schemas combined use {total_tokens} tokens")
            Logger.log(f"🔢 Average tokens per table: {avg_tokens_per_table:.1f}")


            instructions_tokens = len(self.llm.tokenize(schema_minimize_system_instructions.encode()))


            # Add buffer for safety
            safety_buffer = 400
            needed_tokens_without_tables = instructions_tokens + user_input_tokens + avg_response_tokens + safety_buffer
            remaining_tokens = self.n_ctx - needed_tokens_without_tables

            # Calculate max tables per batch
            if avg_tokens_per_table > 0:
                # Add safety margin - use only 80% of available tokens
                safe_remaining_tokens = remaining_tokens * 0.8
                max_tables_per_batch = max(1, int(safe_remaining_tokens / avg_tokens_per_table))

                # Double-check that our calculation won't exceed context window
                estimated_batch_tokens = max_tables_per_batch * avg_tokens_per_table + needed_tokens_without_tables
                if estimated_batch_tokens > self.n_ctx:
                    # If still too large, reduce further
                    max_tables_per_batch = max(1, int((self.n_ctx * 0.7 - needed_tokens_without_tables) / avg_tokens_per_table))

                Logger.log(f"📊 Estimated tokens per batch: {max_tables_per_batch * avg_tokens_per_table:.1f}")

            Logger.log(f"📊 System message: {instructions_tokens} tokens")
            Logger.log(f"📊 Reserved tokens: {needed_tokens_without_tables} tokens")
            Logger.log(f"📊 Available tokens: {remaining_tokens} tokens")
            Logger.log(f"📊 Maximum tables per batch: {max_tables_per_batch}")

        except Exception as e:
            # Fallback to character-based estimation if tokenization fails
            Logger.log(f"❌ Error using tokenizer: {str(e)}. Falling back to character-based estimation.")

            # Estimate using character count (roughly 4 chars per token)
            all_tables = "\n".join(full_schema)
            total_chars = len(all_tables)
            avg_chars_per_table = total_chars / len(full_schema)
            avg_tokens_per_table = avg_chars_per_table / 4

            safety_buffer = 100
            instructions_tokens = len(schema_minimize_system_instructions)/4
            needed_tokens_without_tables = instructions_tokens + user_input_tokens + avg_response_tokens + safety_buffer
            remaining_tokens = self.n_ctx - needed_tokens_without_tables

            # Calculate max tables per batch
            max_tables_per_batch = max(1, int(remaining_tokens / avg_tokens_per_table))

            Logger.log(f"📊 Estimated tokens per table (fallback): {avg_tokens_per_table:.1f}")
            Logger.log(f"📊 Maximum tables per batch (fallback): {max_tables_per_batch}")




        # Process each batch and collect relevant tables
        relevant_tables_names = []
        safe_batch_size = max_tables_per_batch
        safe_batch_size_changed = False
        full_schema_copy = full_schema.copy() #used to keep track of the tables that are left to process, without modyfing
        while safe_batch_size > 0 or safe_batch_size_changed:
            Logger.log(f"🪟 Tables count: {len(full_schema_copy)}")
            safe_batch_size_changed = False
            safe_batch_size = int(safe_batch_size/1.5)
            batches=[]

            # Handle edge cases for batch size
            safe_batch_size = max(1, safe_batch_size)  # Ensure minimum batch size of 1
            safe_batch_size = min(safe_batch_size, len(full_schema_copy))  # Cap at available schema size

            if len(full_schema_copy) == 0:
                Logger.log("⚠️ No tables to process")
                break

            for i in range(0, len(full_schema_copy), safe_batch_size):
                batch = full_schema_copy[i:i + safe_batch_size]
                batches.append(batch)

            Logger.log(f"🔄 Split schema into {len(batches)} batches")

            for i, batch in enumerate(batches):
                Logger.log(f"🔍 Processing batch {i+1}/{len(batches)} with {len(batch)}")

                # Create system message with instructions + batch of tables
                batch_schema = "\n".join(batch)

                #extract batch tables names and store them in batch_tables_names
                batch_tables_names = []
                for statement in batch:
                    # Extract table name from CREATE statement (first word after CREATE TABLE)
                    table_name = statement.split()[2].strip('`')
                    batch_tables_names.append(table_name)

                #get tables description if provided
                batch_tables_description = []
                if tables_description and 'tables' in tables_description:
                    for table in tables_description['tables']:
                        if table["table"] in batch_tables_names:
                            batch_tables_description.append(table)

                batch_tables_description = ""
                if batch_tables_description:
                    for table in batch_tables_description:
                        batch_tables_description += f"Table: {table['table']}\n"
                        batch_tables_description += f"Description: {table['description']}\n"
                        batch_tables_description += "Columns:\n"
                        for col, desc in table['columns'].items():
                            batch_tables_description += f"- {col}: {desc}\n"
                        batch_tables_description += "Use Cases:\n"
                        for use_case in table['use_cases']:
                            batch_tables_description += f"- {use_case}\n"
                        batch_tables_description += "\n"

                # Create messages with proper roles
                user_content_with_schema = f"Based on the following database schema:\n{batch_schema}\n\n and the following tables description:\n{batch_tables_description}\n\nWhat are names of the tables that most likely contain data to answer this question: {user_input}\n\nReturn only table names in backticks and separated by commas. Example response: `table1`, `table2`, `table3`. If no tables found to be relevant, return nothing and Never return tables that are not related to the question."

                messages = [
                    {"role": "system", "content": schema_minimize_system_instructions},
                    {"role": "user", "content": user_content_with_schema}
                ]

                try:
                    # Feed to LLM and get response
                    response = self.llm.create_chat_completion(
                        messages=messages,
                        max_tokens=100,
                        temperature=0.0,
                    )

                    response_text = response['choices'][0]['message']['content'].strip()

                    Logger.log(f"✅ Batch {i+1} response: {response_text}")

                    # Parse the response to extract table names
                    # The response should be a comma-separated list of table names
                    if response_text:
                        # Find all text between backticks using regex
                        import re
                        batch_tables = re.findall(r'`([^`]+)`', response_text)
                        relevant_tables_names.extend(batch_tables)
                        # Also remove CREATE statements from the full schema
                        for table_name in batch_tables:
                            full_schema_copy = [stmt for stmt in full_schema_copy if f'`{table_name}`' not in stmt]

                except Exception as e:
                    Logger.log(f"❌ Error processing batch {i+1}: {str(e)}")
                    Logger.log(f"🔁 Reducing batch size and retrying...")
                    safe_batch_size -= 1
                    safe_batch_size_changed=True #used to break the outer while
                    break
            else: #for-else, # This block runs **only if the loop completes without `break`
                Logger.log(f"✅ All batches processed successfully")
                break # Exit the while loop


        # Remove duplicates while preserving order
        unique_relevant_tables_names = []
        for table in relevant_tables_names:
            if table and table not in unique_relevant_tables_names:
                unique_relevant_tables_names.append(table)

        # Filter tables_description to only include relevant tables
        try:
            filtered_tables_description = [t for t in tables_description['tables'] if t['table'] in unique_relevant_tables_names]
        except:
            filtered_tables_description = []

        flattened_filtered_tables_description_text = "\n".join(
            f"Table: {table['table']}\n\n"
            f"Description:\n{table['description']}\n\n"
            "Columns:\n" + "\n".join([f"- {col} — {desc}" for col, desc in table['columns'].items()]) + "\n\n"
            "Use Cases:\n" + "\n".join([f"- {uc}" for uc in table['use_cases']])
            for table in filtered_tables_description
        )

        # Filter full_schema to only include relevant tables
        filtered_schema = []
        for statement in full_schema:
            # Extract table name from CREATE statement (first word after CREATE TABLE)
            table_name = statement.split()[2].strip('`')
            if table_name in unique_relevant_tables_names:
                filtered_schema.append(statement)

        try:
            schema_tokens = len(self.llm.tokenize("\n".join(filtered_schema).encode()))
            description_tokens = len(self.llm.tokenize(flattened_filtered_tables_description_text.encode()))
            buffer_tokens = 400
            combined_tokens = schema_tokens + description_tokens + buffer_tokens
            combined_schema_and_tables_description = "\n".join(filtered_schema) + "\n\n" + flattened_filtered_tables_description_text
            while (combined_tokens > self.n_ctx):
                Logger.log("🔖 Context window overflow. Reducing tables schema & description.")
                reduction_ratio = (self.n_ctx - schema_tokens - buffer_tokens) / description_tokens
                # Truncate the description text
                truncated_length = int(len(combined_schema_and_tables_description[0]) * reduction_ratio)
                combined_schema_and_tables_description = combined_schema_and_tables_description[0][:truncated_length]
                Logger.log(f"✂️ Truncated description from {description_tokens} to ~{int(description_tokens * reduction_ratio)} tokens")
                combined_tokens = len(self.llm.tokenize(combined_schema_and_tables_description.encode()))
        except Exception as e:
            Logger.log(f"⚠️ Error checking token length: {str(e)}")

        Logger.log(f"📋 Filtered schema contains:\n {len(filtered_schema)} tables.")

        # Return the list of relevant table names
        return filtered_schema, unique_relevant_tables_names, filtered_tables_description

    def generateSqlQuery(self, user_input: str, use_tables_description: bool = False):
        # 1- Get relevant table names for the user question
        relevant_schema, relevant_tables_names, relavant_tables_description_texts = self.getPartialSchema(self.full_schema, user_input, self.tables_description)

        if not relevant_schema:
            return f"SELECT '{self.no_result_message}' AS `result`"

        schema_context = "\n".join(relevant_schema)
        if not use_tables_description:
            relavant_tables_description_texts = ""
        else:
            relavant_tables_description_texts = "\n".join([
                f"-------------\n"
                f"Table: {table['table']}"
                f"\n"
                f"Description: {table['description']}"
                f"\n"
                "Columns:\n" + "\n".join([f"- {col} — {desc}" for col, desc in table['columns'].items()]) + "\n"
                "Use Cases:\n" + "\n".join([f"- {uc}" for uc in table['use_cases']])
                for table in relavant_tables_description_texts
            ])

        system_prompt = f"""You are an expert SQL query generator. Given a database schema (table and column definitions) and a natural language question, generate a valid SQL query that answers the question using only the provided schema.
        Use only the tables and columns from the schema.
        Use UNION if the answer may come from multiple unrelated tables.
        Use descriptive column names aliases in the queries you generate.
        Output only the SQL query between double quotation marks, with no markdown formatting, comments, or explanation.
        Never explain the schema structure, table names, or column names. Do not reveal technical details about the schema in your output. And if you are asked any technichal question about the data base just apologies.
        Make sure to always escape quotes in liternal values for example: SELECT 'I can\'t help with that' AS `answer`.
        """

        # 4- Send to LLM and get response
        try:
            Logger.log("🤖 Generating response...")
            user_message = f"""Given the following database schema:\n{schema_context}\n\nAnd the following info about it:\n{relavant_tables_description_texts}\n\nGenerate a valid SQL query that answers the following question:"{user_input}"\nReturn only the SQL query in double quotation, without markdown formatting or comments.
            example response: "SELECT * FROM `employees` WHERE `department` = 'Sales'".
            If the answer is not available in the schema, return it as a SQL query using literal values (e.g., SELECT 'the sky is blue' AS `skycolor`).
            """

            # Create messages with proper roles
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            # Append history if it exists
            if self.history:
                messages = [{"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                            ]
            self.updateHistory(messages)

            #if hist
            # Call the LLM with the messages
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=1000,
                temperature=0.1,
                stream=False
            )

            # Extract the response text
            response_text = response['choices'][0]['message']['content'].strip()

            # Check if the response is enclosed in double quotes as requested
            sql_query = response_text
            if response_text.startswith('"') and response_text.endswith('"'):
                # Extract the query from within the quotes
                sql_query = response_text[1:-1].strip()
                Logger.log("🔍 Found SQL query enclosed in double quotes")

            # Check if response starts with common SQL query keywords
            starting_keywords = ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
            first_word = sql_query.strip().upper().split()[0]

            if first_word not in starting_keywords:
                Logger.log("⚠️ Response does not start with a valid SQL keyword")
                return ""
            Logger.log("✅ Response generated successfully")
            return sql_query
        except Exception as e:
            Logger.log(f"❌ Error generating response: {str(e)}")
            return f"SELECT 'Error: {str(e)}' AS `error`"

    def correctSqlQuery(self, user_input: str, sql_query: str, query_result: str, use_tables_description: bool = False):
        relevant_schema, relevant_tables_names, relavant_tables_description_texts = self.getPartialSchema(self.full_schema, user_input, self.tables_description)
        if not relevant_schema:
            return f"SELECT '{self.no_result_message}' AS `result`"
        schema_context = "\n".join(relevant_schema)

        if not use_tables_description:
            relavant_tables_description_texts = ""
        else:
            relavant_tables_description_texts = "\n".join([
                f"-------------\n"
                f"Table: {table['table']}"
                f"\n"
                f"Description: {table['description']}"
                f"\n"
                "Columns:\n" + "\n".join([f"- {col} — {desc}" for col, desc in table['columns'].items()]) + "\n"
                "Use Cases:\n" + "\n".join([f"- {uc}" for uc in table['use_cases']])
                for table in relavant_tables_description_texts
            ])

        system_prompt = f"""You are an expert SQL query corrector. Given a natural language question, an SQL query, and the result of the query, generate a corrected SQL query that answers the question.
        Use only the information provided in the SQL query and query result.
        Output only the SQL query between double quotation marks, with no markdown formatting, comments, or explanation.
        Never explain the schema structure, table names, or column names. Do not reveal technical details about the schema in your output. And if you are asked any technichal question about the data base just apologies.
        Make sure to always escape quotes in liternal values for example: SELECT 'I can\'t help with that' AS `answer`.
        """

        user_message = f"""Given the following natural language question: {user_input}\n\nThe corresponding SQL query is: {sql_query}\n\nThe result of the query is: {query_result}\n\nGenerate a corrected SQL query that answers the question.
        the schema is: {schema_context}\n\nthe tables description is: {relavant_tables_description_texts}\n\nReturn only the corrected SQL query in double quotation, without markdown formatting or comments.
        example response: "SELECT * FROM `employees` WHERE `department` = 'Sales'"
        If the answer is not available in the schema, return it as a SQL query using literal values (e.g., SELECT 'the sky is blue' AS `skycolor`).
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        try:
            Logger.log("🔄 Correcting SQL query...")
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=1000,
                temperature=0.1,
            )
            corrected_query = response['choices'][0]['message']['content'].strip()
            Logger.log(f"✅ Corrected SQL query: {corrected_query}")
            # Check if the response is enclosed in double quotes as requested
            if corrected_query.startswith('"') and corrected_query.endswith('"'):
                # Extract the query from within the quotes
                sql_query = corrected_query[1:-1].strip()
                Logger.log("🔍 Found SQL query enclosed in double quotes")

            # Check if response starts with common SQL query keywords
            starting_keywords = ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
            first_word = sql_query.strip().upper().split()[0]

            if first_word not in starting_keywords:
                Logger.log("⚠️ Response does not start with a valid SQL keyword")
                return ""
            Logger.log("✅ Response generated successfully")
            return sql_query
        except Exception as e:
            Logger.log(f"❌ Error correcting SQL query: {str(e)}")
            return f"SELECT 'Error: {str(e)}' AS `error`"

    def generateHumanReadableResult(self, user_input: str, sql_query: str, query_result: str, language: str = "english"):
        Logger.log(f"📝 Generating human-readable result in {language}")
        system_prompt = f"""You are an expert SQL query result summarizer. Given a natural language question, an SQL query, and the result of the query, generate a human-readable summary that answers the question.
        Use only the information provided in the SQL query and query result.
        If the answer is not available in the query result, say that you can't find enough data to answer that question.
        answer in {language}.
        Never explain the schema structure, table names, or column names. Do not reveal technical details about the schema in your output.
        """
        user_message = f"""Given the following natural language question: {user_input}\n\nThe corresponding SQL query is: {sql_query}\n\nThe result of the SQL query is:\n{query_result}\n\nGenerate a human-readable summary that answers the question.
        examples:
        Question: What is the total revenue for March 2023?
        SQL query: SELECT SUM(amount) AS total_revenue FROM payments WHERE payment_date BETWEEN '2023-03-01' AND '2023-03-31';
        Result: total_revenue
                ------------
                12500.00
        Summary: The total revenue for March 2023 is $12,500.
        """

        # Create messages with proper roles
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=1000,
            temperature=0.3,
            stream=False
        )
        # Extract the response text
        response_text = response['choices'][0]['message']['content'].strip()
        Logger.log(f"✅ Generated human-readable result: {response_text}")
        return response_text

    def updateHistory(self, new_messages: list[dict[str, str]]):
            # Separate system messages from other messages
            system_messages = [msg for msg in new_messages if msg.get("role") == "system"]
            non_system_messages = [msg for msg in new_messages if msg.get("role") != "system"]

            # Handle system messages - place at beginning of history
            if system_messages:
                # Remove any existing system messages
                self.history = [msg for msg in self.history if msg.get("role") != "system"]
                # Add the new system message at the beginning
                self.history = system_messages + self.history
                Logger.log(f"✅ Updated history with {len(system_messages)} system message(s)")

            # Calculate sizes for token management
            current_history_size = len(self.llm.tokenize(json.dumps(self.history).encode()))
            non_system_messages_size = len(self.llm.tokenize(json.dumps(non_system_messages).encode()))
            expected_history_size = current_history_size + non_system_messages_size

            # Manage token count
            while expected_history_size > self.n_ctx:
                Logger.log(f"❌ History size exceeds context window. Cleaning up old messages...")
                Logger.log(f"📊 Current history size: {current_history_size} tokens")
                Logger.log(f"📊 New messages size: {non_system_messages_size} tokens")
                Logger.log(f"📊 Expected total size: {expected_history_size} tokens")
                Logger.log(f"📊 Context window limit: {self.n_ctx} tokens")

                # Keep system messages if they exist
                system_msgs = [msg for msg in self.history if msg.get("role") == "system"]
                non_system_msgs = [msg for msg in self.history if msg.get("role") != "system"]

                Logger.log(f"📋 System messages count: {len(system_msgs)}")
                Logger.log(f"📋 Non-system messages count: {len(non_system_msgs)}")

                if len(non_system_msgs) > 0:
                    # Calculate token size of the message being removed
                    message_to_remove = non_system_msgs[0]
                    message_size = len(self.llm.tokenize(json.dumps(message_to_remove).encode()))
                    Logger.log(f"🗑️ Removing oldest non-system message ({message_size} tokens)")

                    # Remove the oldest non-system message
                    non_system_msgs = non_system_msgs[1:]
                    Logger.log(f"📋 Remaining non-system messages: {len(non_system_msgs)}")
                else:
                    Logger.log(f"⚠️ No non-system messages to remove!")
                    # If we can't remove any more messages but still exceed context window
                    # We need to either truncate system messages or reject new messages
                    if len(system_msgs) > 0:
                        # Remove the oldest system message as a last resort
                        message_to_remove = system_msgs[0]
                        message_size = len(self.llm.tokenize(json.dumps(message_to_remove).encode()))
                        Logger.log(f"🗑️ Removing oldest system message as last resort ({message_size} tokens)")
                        system_msgs = system_msgs[1:]
                    else:
                        # If there are no messages at all to remove, we must break the loop
                        # to avoid an infinite loop situation
                        Logger.log(f"⚠️ Cannot reduce history size further. Rejecting new messages.")
                        return  # Exit the method without adding new messages

                # Recombine messages
                self.history = system_msgs + non_system_msgs
                current_history_size = len(self.llm.tokenize(json.dumps(self.history).encode()))
                expected_history_size = current_history_size + non_system_messages_size
                Logger.log(f"📊 New history size after cleanup: {current_history_size} tokens")
                Logger.log(f"📊 Expected total size after cleanup: {expected_history_size} tokens")

            # Append other messages to history
            self.history = self.history + non_system_messages
            Logger.log(f"✅ Updated history with {len(non_system_messages)} non-system messages")
            Logger.log(f"History size: {len(self.llm.tokenize(json.dumps(self.history).encode()))}")

class ChatGemini:
    def __init__(
        self,
        gemini_api_key: str = None,
        model_name: str = "gemini-1.5-pro",
        enable_model_rotation: bool = True,
        no_result_message: str = "No results found",
        mysql_connection: MySQLConnection = None,
        tables_description: Union[Dict[str, Any], str, None] = None,
        log: bool = False,
        scope=None
    ):
        if log:
            global show_logs
            show_logs = True
        if not gemini_api_key:
            Logger.log("🔑 No API key provided.")
            raise ValueError("Gemini API key not provided")
        else:
            genai.configure(api_key=gemini_api_key)

        self.no_result_message = no_result_message
        self.tables_description = tables_description
        self.enable_model_rotation = enable_model_rotation
        self.gemini_api_key = gemini_api_key
        self.model_name_for_sql_genertion = model_name
        self.model_name_for_human_response = model_name
        self.mysql_connection = mysql_connection

        # Initialize MySQL operations
        self.mysql_ops = MysqlOperations(mysql_connection) if mysql_connection else None

        self.full_schema = self.mysql_ops.getFullSchema(mysql_connection) if mysql_connection else []
        self.tables_description = self.getTablesDescription(tables_description)
        self.scope=scope
        self.sql_chat=None
        self.human_reponse_chat=None
        self.updateSqlChat()
        self.updateHumanResponseChat()
        self.api_calls=0

    def chat(self, user_input: str = None, language: str = "english"):
        if not user_input:
            return

        sql_query = self.generateSqlQuery(user_input)
        query_result = self.mysql_ops.executeSqlQuery(sql_query) if self.mysql_ops else "Error: MySQL operations not initialized"

        retry = 1
        while (query_result is None or query_result == "" or "Error:" in str(query_result) or not query_result) and retry <= 3:
            Logger.log(f"⚠️ Query failed: {query_result}")
            Logger.log("🔄 Correcting query...")
            sql_query = self.correctSqlQuery(sql_query, query_result)
            retry += 1
        else:
            if query_result == "No results found":
                return self.no_result_message
            elif "Error:" in query_result:
                Logger.log(f"⚠️ Query failed: {query_result}")
                return self.no_result_message
            else:
                human_readable_result = self.generateHumanReadableResult(user_input, sql_query, query_result, language)
                return human_readable_result

    def updateSqlChat(self, minimum_ctx: int=0):
        if self.enable_model_rotation:
            models = genai.list_models()
            gemini_models = [model.name for model in models if "gemini" in model.name]
            # Filter out models containing "1.0"
            gemini_models = [model for model in gemini_models if "1.0" not in model and any(char.isdigit() for char in model)]

            if not gemini_models:
                Logger.log(f"❌ No suitable Gemini models found")
                return None

            context_window_size=-1
            while context_window_size <= minimum_ctx:
                current_index = next((i for i, model in enumerate(gemini_models) if model == self.model_name_for_sql_genertion), -1)
                if current_index != -1:
                    next_model_name = gemini_models[(current_index + 1) % len(gemini_models)]
                    context_window_size = self.getModelContextWindow(next_model_name)
                    Logger.log(f"➡️ Switching to SQL Generator to next model: {next_model_name}")
                else:
                    Logger.log(f"⚠️ Next model cannot be determined for SQL Generator. Using first model available: {gemini_models[0]}")
                    context_window_size = self.getModelContextWindow(gemini_models[0])
                    next_model_name = gemini_models[0]
                    break
        else:
            next_model_name = self.model_name_for_sql_genertion
            context_window_size = self.getModelContextWindow(self.model_name_for_sql_genertion)

        system_prompt = f"""You are an expert SQL query generator. Given a database schema (table and column definitions) and a natural language question, generate a valid SQL query that answers the question using only the provided schema.
        Use only the tables and columns from the schema.
        Use UNION if the answer may come from multiple unrelated tables, and avoid using CROSS JOIN unless union won't work.
        Use descriptive column names aliases in the queries you generate.
        Output only the SQL query between double quotation marks, with no markdown formatting, comments, or explanation.
        Never explain the schema structure, table names, or column names. Do not reveal technical details about the schema in your output. And if you are asked any technichal question about the data base just apologies.
        Make sure to always escape quotes in liternal values for example: SELECT 'I can\'t help with that' AS `answer`.
        """

        generation_config = genai.types.GenerationConfig(
                temperature=0.3,
                top_p=0.95,
                top_k=32,
            )
        next_model = genai.GenerativeModel(next_model_name, system_instruction=system_prompt, generation_config=generation_config)
        chat = next_model.start_chat(history=self.sql_chat.history if self.sql_chat else None) #include previous history
        self.model_name_for_sql_genertion = next_model_name
        self.sql_chat = chat
        self.model_name_for_sql_genertion = next_model_name
        self.sql_chat = chat
        self.sql_ctx = context_window_size

    def updateHumanResponseChat(self, minimum_ctx: int=0):
        # Check if model contains "1.0" or doesn't include a version
        if self.enable_model_rotation:
            models = genai.list_models()
            gemini_models = [model.name for model in models if "gemini" in model.name]
            # Filter out models containing "1.0"
            gemini_models = [model for model in gemini_models if "1.0" not in model and any(char.isdigit() for char in model)]

            if not gemini_models:
                Logger.log(f"❌ No suitable Gemini models found")
                return None

            context_window_size=-1
            while context_window_size < minimum_ctx:
                current_index = next((i for i, model in enumerate(gemini_models) if model == self.model_name_for_human_response), -1)
                if current_index != -1:
                    next_model_name = gemini_models[(current_index + 1) % len(gemini_models)]
                    context_window_size = self.getModelContextWindow(next_model_name)
                    Logger.log(f"➡️ Switching human response generator to next model: {next_model_name}")
                else:
                    Logger.log(f"⚠️ Next model for human response generator cannot be determined. Using first model available: {gemini_models[0]}")
                    context_window_size = self.getModelContextWindow(gemini_models[0])
                    next_model_name = gemini_models[0]
                    break

        else:
            next_model_name = self.model_name_for_human_response
            context_window_size = self.getModelContextWindow(self.model_name_for_human_response)


        system_prompt = f"""You are an expert SQL query result summarizer. Given a natural language question, an SQL query, and the result of the query, generate a human-readable summary that answers the question.
        Use only the information provided in the SQL query and query result.
        If the answer is not available in the query result, say that you can't find enough data to answer that question.
        Never explain the schema structure, table names, or column names. Do not reveal technical details about the schema in your output.
        """
        next_model = genai.GenerativeModel(next_model_name, system_instruction=system_prompt)
        chat = next_model.start_chat(history=self.human_reponse_chat.history if self.human_reponse_chat else None) #include previous history if exists
        self.model_name_for_human_response = next_model_name
        self.human_reponse_chat = chat
        self.human_reponse_ctx = context_window_size

    def getModelContextWindow(self, model_name: str) -> int:
        # Gemini model context window sizes
        context_window_families = {
            "gemini-1.5-pro": 1000000,  # 1M tokens
            "gemini-1.5-flash": 1000000,  # 1M tokens
            "gemini-1.0-pro": 32768,  # 32K tokens
            "gemini-pro": 32768,  # 32K tokens
            "gemini-2.0-pro": 1000000,  # 1M tokens
            "gemini-2.0-flash": 1000000,  # 1M tokens
            "gemini-2.5-pro": 1000000,  # 1M tokens
            "gemini-2.5-flash": 1000000,  # 1M tokens
        }

        if model_name in context_window_families:
            window_size = context_window_families[model_name]
            Logger.log(f"✅ Found exact match for {model_name}: {window_size} tokens")
            return window_size

        # If no exact match, try to match by family
        for family, window_size in context_window_families.items():

            if model_name.startswith(family):
                Logger.log(f"✅ Found family match for {model_name}: {window_size} tokens (family: {family})")
                return window_size

            # For models with version numbers like gemini-1.5-flash-002
            parts = model_name.split('-')
            if len(parts) >= 3:
                # Create potential family name from the first 3 parts (e.g., "gemini-1.5-flash")
                potential_family = '-'.join(parts[:3])
                if potential_family == family:
                    Logger.log(f"✅ Found family match for {model_name}: {window_size} tokens (family: {family})")
                    return window_size

        # Default fallback for unknown models
        # For Gemini 1.5 models, use 1M tokens
        if "gemini-1.5" in model_name:
            Logger.log(f"⚠️ Unknown Gemini 1.5 model: {model_name}. Using {1000000} tokens as context window.")
            return 1000000
        # For Gemini 2.0 or higher models, use 1M tokens
        elif any(x in model_name for x in ["gemini-2", "gemini-3"]):
            Logger.log(f"⚠️ Unknown Gemini 2.0+ model: {model_name}. Using {1000000} tokens as context window.")
            return 1000000
        # For other unknown models, use 32K tokens as a safe default
        else:
            Logger.log(f"⚠️ Unknown Gemini model: {model_name}. Using default context window size of {32768} tokens.")
            return 32768

    def getTablesDescription(self, tables_description):
        if isinstance(tables_description, str):
            try:
                if os.path.isfile(tables_description):
                    with open(tables_description, 'r') as f:
                        tables_description = json.load(f)
                        Logger.log(f"✅ Using provided tables description")
                        return tables_description
                else:
                    Logger.log(f"❌ Rules file not found: {tables_description}")
                    return None
            except json.JSONDecodeError as e:
                Logger.log(f"❌ Invalid JSON in {tables_description}: {str(e)}")
                return None
            except Exception as e:
                Logger.log(f"❌ Error loading {tables_description}: {str(e)}")
                return None
        elif isinstance(tables_description, dict):
            Logger.log(f"✅ Using provided tables description")
            pass  # use as-is
        else:
            return None

    def generateSqlQuery(self, user_input: str, use_tables_description: bool = False):
        Logger.log("🤖 Generating SQL query...")

        if not user_input:
            Logger.log("❌ No user input provided")
            return ""

        if use_tables_description and self.tables_description:
            user_message = f"""Given the following database schema:\n{self.full_schema}\n\nAnd the following info about it:\n{self.tables_description}\n\nGenerate a valid SQL query that answers the following question:"{user_input}"\nReturn only the SQL query in double quotation, without markdown formatting or comments.
            example response: "SELECT * FROM `employees` WHERE `department` = 'Sales'".
            If the answer is not available in the schema, return it as a SQL query using literal values (e.g., SELECT 'the sky is blue' AS `skycolor`).
            If the answer requires data from unrelated tables, use UNION to combine the results.
            """
        else:
            user_message = f"""Given the following database schema:\n{self.full_schema}\n\nGenerate a valid SQL query that answers the following question:"{user_input}"\nReturn only the SQL query in double quotation, without markdown formatting or comments.
            example response: "SELECT * FROM `employees` WHERE `department` = 'Sales'".
            If the answer is not available in the schema, return it as a SQL query using literal values (e.g., SELECT 'the sky is blue' AS `skycolor`).
            """

        if self.scope:
            user_message+= f"\nAlso, if the answer can't be found in the tables of the given schema and its info, and you're gonna return sql query of literal values, the query should answer questions that are related to {self.scope} only! otherwise, return SELECT 'I can't help with that because [fill this whith appropriate response] is out of my knowledge' AS `answer`."

        retry_count = 0
        while retry_count < 5:
            retry_count += 1
            try:
                response = self.sql_chat.send_message(user_message)
                response_text = response.text
                Logger.log(f"🤖 SQL Generator Response: {response_text}")
                self.api_calls += 1

                if '"' in response_text:
                    start = response_text.find('"')
                    end = response_text.find('"', start + 1)
                    if start != -1 and end != -1:
                        sql_query = response_text[start + 1:end].strip()
                    else:
                        sql_query = response_text.strip()
                    Logger.log("🔍 Found SQL query enclosed in double quotes")
                else:
                    sql_query = response_text.strip()

                starting_keywords = ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
                first_word = sql_query.strip().upper().split()[0]
                if first_word not in starting_keywords:
                    Logger.log("⚠️ Response does not start with a valid SQL keyword")
                Logger.log("✅ Respoand nse generated successfully")
                return sql_query
            except Exception as e:
                if "retry_delay" in str(e):
                    Logger.log(f"❌ Error generating sql response: {str(e)}")
                    match = re.search(r'seconds:\s*(\d+)', str(e))
                    if match and not self.api_calls>0 and not self.enable_model_rotation:
                        seconds = int(match.group(1))
                        time.sleep(seconds)
                Logger.log(f"🔁 Trying with next model.")
                self.updateSqlChat()

    def correctSqlQuery(self, sql_query: str, query_result: str):
        Logger.log("🔄 Correcting SQL query...")
        user_message = f"""The previous sql query was incorrect. when executing an error saying: {query_result} was returned.
        please correct it.
        If the answer requires data from unrelated tables, use UNION to combine the results.
        """

        if self.scope:
            user_message+= f"\nAlso, if the answer can't be found in the tables of the given schema and its info, and you're gonna return sql query of literal values, the query should answer questions that are related to {self.scope} only! otherwise, return SELECT 'I can't help with that because [fill this whith appropriate response] is out of my knowledge' AS `answer`."
        retry_count = 0
        while retry_count < 5:
            retry_count += 1
            try:
                response = self.sql_chat.send_message(user_message)
                response_text = response.text
                Logger.log(f"🤖 SQL Corrector Response: {response_text}")
                self.api_calls += 1

                if '"' in response_text:
                    start = response_text.find('"')
                    end = response_text.find('"', start + 1)
                    if start != -1 and end != -1:
                        sql_query = response_text[start + 1:end].strip()
                    else:
                        sql_query = response_text.strip()
                    Logger.log("🔍 Found SQL query enclosed in double quotes")
                else:
                    sql_query = response_text.strip()

                starting_keywords = ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
                first_word = sql_query.strip().upper().split()[0]
                if first_word not in starting_keywords:
                    Logger.log("⚠️ Response does not start with a valid SQL keyword")
                Logger.log("✅ Response generated successfully")
                return sql_query
            except Exception as e:
                Logger.log(f"❌ Error generating sql response: {str(e)}")
                if "retry_delay" in str(e):
                    match = re.search(r'seconds:\s*(\d+)', str(e))
                    if match and not self.api_calls>0 and not self.enable_model_rotation:
                        seconds = int(match.group(1))
                        time.sleep(seconds)
                Logger.log(f"🔁 Trying with next model.")
                self.updateSqlChat()

    def generateHumanReadableResult(self, user_input: str, sql_query: str, query_result: str, language: str = "english"):
        Logger.log(f"📝 Generating human-readable result in {language}")

        user_message = f"""Given the following natural language question: {user_input}\n\nThe corresponding SQL query is: {sql_query}\n\nThe result of the SQL query is:\n{query_result}\n\nGenerate a human-readable summary that answers the question.
        examples:
        Question: What is the total revenue for March 2023?
        SQL query: SELECT SUM(amount) AS total_revenue FROM payments WHERE payment_date BETWEEN '2023-03-01' AND '2023-03-31';
        Result: total_revenue
                ------------
                12500.00
        Summary: The total revenue for March 2023 is $12,500.
        _____________________________________________________
        Answer in {language}.
        """
        retry_count = 0
        while retry_count < 5:
            retry_count += 1
            try:
                response = self.human_reponse_chat.send_message(user_message)
                response_text = response.text
                Logger.log(f"✅ Generated human-readable result: {response_text}")
                self.api_calls += 1
                return response_text
            except Exception as e:
                Logger.log(f"❌ Error generating human response: {str(e)}")
                if "retry_delay" in str(e):
                    match = re.search(r'seconds:\s*(\d+)', str(e))
                    if match and not self.api_calls>0 and not self.enable_model_rotation:
                        seconds = int(match.group(1))
                        time.sleep(seconds)
                Logger.log(f"🔁 Trying with next model.")
                self.updateHumanResponseChat()