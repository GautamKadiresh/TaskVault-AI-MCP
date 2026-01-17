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
    Do not reveal internal details like task_id to user. 
    Always present info to user in human readable format.
    Only present information you know.
    """,
}
