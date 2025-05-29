# Chatbot

## Overview

This is a chatbot library that uses a language model along with embeddings to "talk" to different data sources asynchronously.

## Features

- [ ] Chat with a mysql database
- [ ] Chat with a pdf file
- [ ] Chat with a csv file
- [ ] Chat with a docx file
- [ ] Chat with a excel file


## Technologies

- [ ] ChromaDB -> Vector Database
- [ ] llama_cpp -> run Llama language models
- [ ] padnas -> data manipulation
- [ ] PyPDFLoader -> load pdf files
- [ ] docx -> load docx files


## File Structure

- [ ] chatbot.py -> main file


## Instructions

1. Install the dependencies

```bash
pip install -r requirements.txt
```
2. Import the chatbot file

```python
from chatbot import Chatbot
```

chatbot.py must be in your directory.

3. Use the chatbot

```python
from chatbot import Chatbot
import asyncio

async def main():
    """Main function to run chat loop."""
    while True:
        question = input("Enter a question (or 'quit' to exit): ")
        if question.lower() == 'quit':
            break
        print(await chatbot.chat_with_llama(question))

if __name__ == "__main__":
    # Initialize the chatbot with the PDF service and the example.pdf file
    chatbot = ChatBot(Services.PDF, file_path="example.pdf")
    try:
        #the chatbot.chat_with_llama function is async, so we need to run it in an asyncio loop
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down chatbot...")
    except Exception as e:
        print(f"\nError occurred: {e}")
```


## Services

- [ ] PDF -> load pdf files
- [ ] DOCX -> load docx files
- [ ] CSV -> load csv files
- [ ] EXCEL -> load excel files
- [ ] MYSQL -> load mysql database

Services are exposed via the `Services` enum.

```python
from chatbot import Services
```

    ### Required Parameters for each service
    - PDF -> service = Services.PDF, file_path = "path/to/file.pdf"
    - DOCX -> service = Services.DOCX, file_path = "path/to/file.docx"
    - CSV -> service = Services.CSV, file_path = "path/to/file.csv"
    - EXCEL -> service = Services.EXCEL, file_path = "path/to/file.xlsx"
    - MYSQL -> service = Services.MYSQL, mysql_connection = mysql_connection

    ### Optional Parameters
    - return_conversation -> bool = False -> whether to return the conversation history
    - ai_rules_path -> str = None -> the path to the ai rules file
    - terminal -> bool = False -> whether to run the chatbot in terminal mode





## Dependencies
mysql-connector-python>=8.0.0 -> MySQL connector for Python
llama-cpp-python>=0.2.0 -> Llama language model
chromadb -> Vector database
langchain-community -> LangChain community
langchain-core -> LangChain core
langchain-text-splitters -> LangChain text splitters
pypdf -> PDF file loader
pandas -> Data manipulation
python-docx -> Docx file loader



## ChromaDB

ChromaDB is a vector database that is used to store the embeddings of the data.
Used to store the embeddings of the PDF and DOCX files.


### ChromaDB Constructor

The ChromaDB constructor takes in the following parameters:

- collection_name -> the name of the collection
- embedding_function -> the embedding function to use


  ### Embeddings

  Embeddings are the vector representations of the data.
  The data is split into chunks and each chunk is embedded.
  The embeddings are stored in the vector database.

  ### ChromaDB Collection

  A collection is a group of embeddings.




## Llama

Llama is a language model that is used to generate the responses.

### LlamaCPP

LlamaCPP is a Python wrapper for the Llama language model. 

### LlamaCPP Constructor

The LlamaCPP constructor takes in the following parameters:

- model_path -> the path to the llama model
- n_ctx -> the context window size
- n_threads -> the number of threads to use

## Classes

### Chatbot

The chatbot is the main class that is used to interact with the user.

#### Chatbot Constructor

The chatbot constructor takes in the following parameters:

- service -> the service to use
- file_path -> the path to the file to use
- mysql_connection -> the mysql connection to use
- return_conversation -> whether to return the conversation history
- terminal -> whether to run the chatbot in terminal mode
- ai_rules_path -> the path to the ai rules file

#### Chatbot Methods

- chat_with_llama -> chat with the llama model -> async def chat_with_llama(self, user_input: str) -> str:
   -- This function is the main function that is used to chat with the llama model.
   -- It takes in a user input which is a question and returns a response.
- _add_message -> add a message to the history -> def _add_message(self, role: str, content: str) -> None:
   -- This function adds a message to the history.
   -- It takes in a role and content and adds it to the history.
- _create_system_prompt -> create the system prompt -> def _create_system_prompt(self, db_schema: str) -> str.
   -- This function creates the system prompt.
   -- It takes in a database schema and returns a system prompt.
- _generate_response -> generate the response -> async def _generate_response(self) -> str:
   -- This function generates the response, this is used to generate the response for the user input by using chat history.

- _generate_human_response -> generate the human response -> async def _generate_human_response(self, question: str, result: str) -> str:
   -- This function generates the human response.
   -- It takes in a question and result and returns a human response.
- _truncate_history -> truncate the history -> def _truncate_history(self):
   -- This function truncates the history.
   -- This is done to prevent the context window from being exceeded.
- _clean_up -> clean up the resources -> def _clean_up(self):
   -- This function cleans up the resources.
   -- It closes the mysql connection.
- _load_structured_types -> load the structured types -> def _load_structured_types(self):
   -- This function loads the structured types.
   -- It takes in a file path and returns a structured types.
- _load_document -> load the document -> def _load_document(self):
   -- This function loads the document.
- _clean_text -> clean the text -> def _clean_text(self, text: str) -> str:
   -- This function cleans the text.
   -- It takes in a text and returns a cleaned text.
- _load_pdf -> load the pdf file -> def _load_pdf(self):
   -- This function loads the pdf file.
- _load_docx -> load the docx file -> def _load_docx(self):
   -- This function loads the docx file.
- _get_database_schema -> get the database schema -> def _get_database_schema(self) -> str.
   -- This function gets the database schema.
   -- It takes in a mysql connection and returns a database schema.
- _execute_query -> execute the query -> def _execute_query(self, query: str) -> str.
   -- This function executes the query.
   -- It takes in a query and returns a result.
- _determine_context_window -> determine the context window -> def _determine_context_window(self) -> int.
   -- This function determines the context window.
   -- It takes in a text and returns a context window.
- _initialize_model -> initialize the model -> def _initialize_model(self) -> Llama.
   -- This function initializes the model.
- _select_model -> select the model -> def _select_model(self) -> str.
   -- This function selects the model.
   -- When in GUI mode, the first model in models folder is selected.









