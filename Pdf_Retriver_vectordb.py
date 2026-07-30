# from langchain_chroma import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings


# # Load embedding model
# embedding = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )


# # Load existing vector database
# vectordb = Chroma(
#     persist_directory="pdf_vector_db",
#     embedding_function=embedding,
#     collection_name="fmg_documents"
# )


# def retrieve_pdf_context(query, k=5):

#     docs = vectordb.similarity_search(
#         query,
#         k=k
#     )

#     results = []

#     for doc in docs:

#         results.append({
#             "source": doc.metadata.get(
#                 "source_file",
#                 "Unknown"
#             ),

#             "page": doc.metadata.get(
#                 "page",
#                 "Unknown"
#             ),

#             "content": doc.page_content
#         })

#     return results



import os
import chromadb
from sentence_transformers import SentenceTransformer


# ============================================
# Configuration
# ============================================

VECTOR_DB_PATH = "../data/vector_store"

COLLECTION_NAME = "pdf_documents"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# ============================================
# Load Embedding Model
# ============================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

print("Embedding model loaded.")


# ============================================
# Load Existing ChromaDB
# ============================================

print("Loading existing PDF vector database...")

client = chromadb.PersistentClient(
    path=VECTOR_DB_PATH
)


collection = client.get_collection(
    name=COLLECTION_NAME
)


print(
    f"Vector database loaded successfully."
)

print(
    f"Total documents in collection: "
    f"{collection.count()}"
)


# ============================================
# PDF Retrieval Function
# ============================================

def retrieve_pdf_context(
    query,
    k=5
):

    # ----------------------------------------
    # Convert user question into embedding
    # ----------------------------------------

    query_embedding = embedding_model.encode(
        [query]
    )[0].tolist()


    # ----------------------------------------
    # Search ChromaDB
    # ----------------------------------------

    results = collection.query(

        query_embeddings=[
            query_embedding
        ],

        n_results=k

    )


    # ----------------------------------------
    # Format results
    # ----------------------------------------

    retrieved_documents = []


    documents = results.get(
        "documents",
        [[]]
    )[0]


    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]


    for document, metadata in zip(
        documents,
        metadatas
    ):

        retrieved_documents.append({

            "content": document,

            "source": metadata.get(
                "source_file",
                "Unknown"
            ),

            "page": metadata.get(
                "page",
                "Unknown"
            )

        })


    return retrieved_documents