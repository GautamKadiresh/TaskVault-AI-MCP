# VECTOR DB CONSTANTS
VECTOR_DB_CONFIG = {
    "DB_LOCATION": "chroma_vector_db",
    "EMBEDDING_MODEL": "mxbai-embed-large",
    "MAX_RESULTS": 3,
    "SRC_FILES_LOCATION": "vector_db",
    "VECTORS_CHUNK_SIZE": 1000,
    "VECTOR_OVERLAP_SIZE": 200,
}

# CHAT LLM CONFIG
CHAT_LLM_CONFIG = {
    "MODEL": "llama3.2",
    "SYSTEM_PROMPT": """            
    You are a helpful task managing assistant. 
    You have an mcp server for managing tasks and its storage at your disposal. 
    The interaction is as follows: user submits prompt then you have one pass to use the mcp tools and then using those information to reply to user.
    Always present info to user in human readable format.
    Only present information you know.
    """,
}
