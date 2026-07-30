import os
from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
#from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path

### Read all the pdf's inside the directory
def process_all_pdfs(Pdf):
    """Process all PDF files in a directory"""
    all_documents = []
    pdf_dir = Path(Pdf)
    
    # Find all PDF files recursively
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        try:
            loader = PyPDFLoader(str(pdf_file))
            documents = loader.load()
            
            # Add source information to metadata
            for doc in documents:
                doc.metadata['source_file'] = pdf_file.name
                doc.metadata['file_type'] = 'pdf'
            
            all_documents.extend(documents)
            print(f"  ✓ Loaded {len(documents)} pages")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\nTotal documents loaded: {len(all_documents)}")
    return all_documents

# Process all PDFs in the data directory
all_pdf_documents = process_all_pdfs(r"E:\Customer_Support_Agent\Pdf")


all_pdf_documents



from pathlib import Path

for pdf in Path("E:/RAG_Pipeline").rglob("*.pdf"):
    print(pdf)




# from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader

# pdf_path = "../data/pdf/DEEP LEARNING (R20A06610).pdf"

# loader = PyPDFLoader(pdf_path)

# documents = loader.load()

# print(f"Number of pages: {len(documents)}")

from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader

pdf_path = r"E:\Customer_Support_Agent\Pdf\FMG_Customer_Support_Documentation.pdf"

loader = PyPDFLoader(pdf_path)
documents = loader.load()

print(f"Number of pages: {len(documents)}")



### Text splitting get into chunks

def split_documents(documents,chunk_size=800,chunk_overlap=100):
    """Split documents into smaller chunks for better RAG performance"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(split_docs)} chunks")
    
    # Show example of a chunk
    if split_docs:
        print(f"\nExample chunk:")
        print(f"Content: {split_docs[0].page_content[:200]}...")
        print(f"Metadata: {split_docs[0].metadata}")
    
    return split_docs


chunks=split_documents(all_pdf_documents)
chunks



import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity





class EmbeddingManager:
    """Handles document embedding generation using SentenceTransformer"""
   
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding manager
         "all-MiniLM-L6-v2"
         "BAAI/bge-base-en-v1.5"
        Args:
            model_name: HuggingFace model name for sentence embeddings
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the SentenceTransformer model"""
        try:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            raise

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        if not self.model:
            raise ValueError("Model not loaded")
        
        print(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings


## initialize the embedding manager

embedding_manager=EmbeddingManager()
embedding_manager






class VectorStore:
    """Manages document embeddings in a ChromaDB vector store"""
    
    def __init__(self, collection_name: str = "pdf_documents", persist_directory: str = "../data/vector_store"):
        """
        Initialize the vector store
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the vector store
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self._initialize_store()

    def _initialize_store(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create persistent ChromaDB client
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "PDF document embeddings for RAG"}
            )
            print(f"Vector store initialized. Collection: {self.collection_name}")
            print(f"Existing documents in collection: {self.collection.count()}")
            
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            raise

    def add_documents(self, documents: List[Any], embeddings: np.ndarray):
        """
        Add documents and their embeddings to the vector store
        
        Args:
            documents: List of LangChain documents
            embeddings: Corresponding embeddings for the documents
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        print(f"Adding {len(documents)} documents to vector store...")
        
        # Prepare data for ChromaDB
        ids = []
        metadatas = []
        documents_text = []
        embeddings_list = []
        
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Generate unique ID
            doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
            ids.append(doc_id)
            
            # Prepare metadata
            metadata = dict(doc.metadata)
            metadata['doc_index'] = i
            metadata['content_length'] = len(doc.page_content)
            metadatas.append(metadata)
            
            # Document content
            documents_text.append(doc.page_content)
            
            # Embedding
            embeddings_list.append(embedding.tolist())
        
        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents_text
            )
            print(f"Successfully added {len(documents)} documents to vector store")
            print(f"Total documents in collection: {self.collection.count()}")
            
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            raise

vectorstore=VectorStore()
vectorstore
    
    
    ### Convert the text to embeddings
texts=[doc.page_content for doc in chunks]

## Generate the Embeddings

embeddings=embedding_manager.generate_embeddings(texts)

##store int he vector dtaabase
vectorstore.add_documents(chunks,embeddings)



class RAGRetriever:
    """Handles query-based retrieval from the vector store"""
    
    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingManager):
        """
        Initialize the retriever
        
        Args:
            vector_store: Vector store containing document embeddings
            embedding_manager: Manager for generating query embeddings
        """
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    def retrieve(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: The search query
            top_k: Number of top results to return
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of dictionaries containing retrieved documents and metadata
        """
        print(f"Retrieving documents for query: '{query}'")
        print(f"Top K: {top_k}, Score threshold: {score_threshold}")
        
        # Generate query embedding
        query_embedding = self.embedding_manager.generate_embeddings([query])[0]
        
        # Search in vector store
        try:
            results = self.vector_store.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            
            # Process results
            retrieved_docs = []
            
            if results['documents'] and results['documents'][0]:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0]
                distances = results['distances'][0]
                ids = results['ids'][0]
                
                for i, (doc_id, document, metadata, distance) in enumerate(zip(ids, documents, metadatas, distances)):
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    similarity_score = 1 - distance
                    
                    if similarity_score >= score_threshold:
                        retrieved_docs.append({
                            'id': doc_id,
                            'content': document,
                            'metadata': metadata,
                            'similarity_score': similarity_score,
                            'distance': distance,
                            'rank': i + 1
                        })
                
                print(f"Retrieved {len(retrieved_docs)} documents (after filtering)")
            else:
                print("No documents found")
            
            return retrieved_docs
            
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []

rag_retriever=RAGRetriever(vectorstore,embedding_manager)



def retrieve_pdf_context(query, k=5):
    """
    Retrieve relevant information from the FMG PDF vector store.
    """

    docs = vectorstore.similarity_search(
        query,
        k=k
    )

    results = []

    for doc in docs:
        results.append({
            "source": doc.metadata.get("source_file", "Unknown"),
            "page": doc.metadata.get("page", "Unknown"),
            "content": doc.page_content
        })

    return results

# import re
# from typing import List, Dict, Any

# class RAGRetriever:

#     def __init__(self, vector_store, embedding_manager):
#         self.vector_store = vector_store
#         self.embedding_manager = embedding_manager

#         # Common abbreviations
#         self.abbreviations = {
#             "dl": "deep learning",
#             "ml": "machine learning",
#             "ai": "artificial intelligence",
#             "nlp": "natural language processing",
#             "cv": "computer vision",
#             "cnn": "convolutional neural network",
#             "rnn": "recurrent neural network",
#             "llm": "large language model",
#             "gpu": "graphics processing unit",
#             "cpu": "central processing unit"
#         }

#     def preprocess_query(self, query: str):

#         query = query.lower().strip()

#         query = re.sub(r"\s+", " ", query)

#         words = query.split()

#         expanded = []

#         for word in words:
#             expanded.append(self.abbreviations.get(word, word))

#         expanded_query = " ".join(expanded)

#         print("=" * 60)
#         print("Original Query :", query)
#         print("Expanded Query :", expanded_query)
#         print("=" * 60)

#         return expanded_query

#     def retrieve(
#         self,
#         query,
#         top_k=5,
#         score_threshold=0.35
#     ):

#         query = self.preprocess_query(query)

#         query_embedding = self.embedding_manager.generate_embeddings([query])[0]

#         # retrieve more candidates internally
#         candidate_results = self.vector_store.collection.query(
#             query_embeddings=[query_embedding.tolist()],
#             n_results=max(top_k * 3, 10)
#         )

#         retrieved_docs = []

#         if candidate_results["documents"] and candidate_results["documents"][0]:

#             docs = candidate_results["documents"][0]
#             metas = candidate_results["metadatas"][0]
#             distances = candidate_results["distances"][0]
#             ids = candidate_results["ids"][0]

#             for i, (doc_id, doc, meta, distance) in enumerate(
#                 zip(ids, docs, metas, distances)
#             ):

#                 similarity = 1 - distance

#                 if similarity < score_threshold:
#                     continue

#                 retrieved_docs.append(
#                     {
#                         "id": doc_id,
#                         "content": doc,
#                         "metadata": meta,
#                         "similarity_score": round(similarity, 4),
#                         "distance": round(distance, 4),
#                         "rank": i + 1,
#                     }
#                 )

#         # sort highest similarity first
#         retrieved_docs = sorted(
#             retrieved_docs,
#             key=lambda x: x["similarity_score"],
#             reverse=True,
#         )

#         return retrieved_docs[:top_k]



# import os
# from dotenv import load_dotenv
# load_dotenv()

# print(os.getenv("GROQ_API_KEY"))




# from langchain_groq import ChatGroq
# from langchain_core.prompts import PromptTemplate
# from langchain_core.messages import HumanMessage, SystemMessage




# class GroqLLM:
#     def __init__(self, model_name: str = "llama-3.3-70b-versatile", api_key: str =None):
#         """
#         Initialize Groq LLM
        
#         Args:
#             model_name: Groq model name (qwen2-72b-instruct, llama3-70b-8192, etc.)
#             api_key: Groq API key (or set GROQ_API_KEY environment variable)
#         """
#         self.model_name = model_name
#         self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        
#         if not self.api_key:
#             raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
#         self.llm = ChatGroq(
#             groq_api_key=self.api_key,
#             model_name=self.model_name,
#             temperature=0.1,
#             max_tokens=1024
#         )
        
#         print(f"Initialized Groq LLM with model: {self.model_name}")

#     def generate_response(self, query: str, context: str, max_length: int = 500) -> str:
#         """
#         Generate response using retrieved context
        
#         Args:
#             query: User question
#             context: Retrieved document context
#             max_length: Maximum response length
            
#         Returns:
#             Generated response string
#         """
        
#         # Create prompt template
#         prompt_template = PromptTemplate(
#             input_variables=["context", "question"],
#             template="""You are a helpful AI assistant. Use the following context to answer the question accurately and concisely.

# Context:
# {context}

# Question: {question}

# Answer: Provide a clear and informative answer based on the context above. If the context doesn't contain enough information to answer the question, say so."""
#         )
        
#         # Format the prompt
#         formatted_prompt = prompt_template.format(context=context, question=query)
        
#         try:
#             # Generate response
#             messages = [HumanMessage(content=formatted_prompt)]
#             response = self.llm.invoke(messages)
#             return response.content
            
#         except Exception as e:
#             return f"Error generating response: {str(e)}"
        
#     def generate_response_simple(self, query: str, context: str) -> str:
#         """
#         Simple response generation without complex prompting
        
#         Args:
#             query: User question
#             context: Retrieved context
            
#         Returns:
#             Generated response
#         """
#         simple_prompt = f"""Based on this context: {context}

# Question: {query}

# Answer:"""
        
#         try:
#             messages = [HumanMessage(content=simple_prompt)]
#             response = self.llm.invoke(messages)
#             return response.content
#         except Exception as e:
#             return f"Error: {str(e)}"
    


# # Initialize Groq LLM (you'll need to set GROQ_API_KEY environment variable)
# try:
#     groq_llm = GroqLLM(api_key=os.getenv("GROQ_API_KEY"))
#     print("Groq LLM initialized successfully!")
# except ValueError as e:
#     print(f"Warning: {e}")
#     print("Please set your GROQ_API_KEY environment variable to use the LLM.")
#     groq_llm = None


# ### Simple RAG pipeline with Groq LLM
# from langchain_groq import ChatGroq
# import os
# from dotenv import load_dotenv
# load_dotenv()

# ### Initialize the Groq LLM (set your GROQ_API_KEY in environment)
# groq_api_key = os.getenv("GROQ_API_KEY")

# llm=ChatGroq(groq_api_key=groq_api_key,model_name="llama-3.3-70b-versatile",temperature=0.1,max_tokens=1024)

# ## 2. Simple RAG function: retrieve context + generate response
# def rag_simple(query,retriever,llm,top_k=3):
#     ## retriever the context
#     results=retriever.retrieve(query,top_k=top_k)
#     context="\n\n".join([doc['content'] for doc in results]) if results else ""
#     if not context:
#         return "No relevant context found to answer the question."
    
#     ## generate the answwer using GROQ LLM
#     prompt=f"""Use the following context to answer the question concisely.
#         Context:
#         {context}

#         Question: {query}

#         Answer:"""
    
#     response=llm.invoke([prompt.format(context=context,query=query)])
#     return response.content


# answer=rag_simple("Give me PDF all data?",rag_retriever,llm)
# print(answer)




# from langchain_core.messages import HumanMessage, AIMessage
# from app import supabase
# import uuid

# #session_id = str(uuid.uuid4())
# session_id = str(uuid.uuid4())
# session_created = False

# chat_history = []

# def chatbot(message, history):

#     global chat_history

#     # Retrieve relevant chunks
#     results = rag_retriever.retrieve(message, top_k=3)

#     context = "\n\n".join(
#         [doc["content"] for doc in results]
#     ) if results else ""

#     prompt = f"""
# You are a helpful AI assistant.

# Use the PDF context whenever it is relevant.

# If the user is just chatting (Hi, Hello, How are you, etc.), respond normally.

# If the user asks about the PDF, answer using ONLY the PDF context.

# If the answer is not found in the PDF, say:
# "I couldn't find that information in the uploaded PDF."

# =========================
# PDF Context
# =========================
# {context}

# User Question:
# {message}

# Answer:
# """

#     # Build conversation history
#     messages = chat_history.copy()
#     messages.append(HumanMessage(content=prompt))

#     # Generate response
#     response = llm.invoke(messages)

#     # Save in chat history
#     chat_history.append(HumanMessage(content=message))
#     chat_history.append(AIMessage(content=response.content))




#     # ---------------------------------------
#     # Create chat title (ONLY FIRST MESSAGE)
#     # ---------------------------------------
#     global session_created

#     if not session_created:
#          supabase.table("chat_sessions").insert({
#             "session_id": session_id,
#             "title": message
#     }).execute()

#     session_created = True


#     # -------------------------
#     # Save to Supabase
#     # -------------------------
#     try:
#         supabase.table("chatbot_conversations").insert({
#             "session_id": session_id,
#             "user_question": message,
#             "chatbot_response": response.content
#         }).execute()

#     except Exception as e:
#         print("Supabase Error:", e)

#     return response.content




# def get_all_sessions():

#     response = (
#         supabase
#         .table("chat_sessions")
#         .select("session_id, title")
#         .order("created_at", desc=True)
#         .execute()
#     )

#     return {
#         row["title"]: row["session_id"]
#         for row in response.data
#     }

# # def get_all_sessions():

# #     response = (
# #         supabase
# #         .table("chatbot_conversations")
# #         .select("session_id")
# #         .execute()
# #     )

# #     sessions = []

# #     for row in response.data:

# #         if row["session_id"] not in sessions:
# #             sessions.append(row["session_id"])

# #     return sessions


# def load_chat(title):

#     # Find session_id using title
#     session = (
#         supabase
#         .table("chat_sessions")
#         .select("session_id")
#         .eq("title", title)
#         .single()
#         .execute()
#     )

#     session_id = session.data["session_id"]

#     # Load conversation
#     response = (
#         supabase
#         .table("chatbot_conversations")
#         .select("*")
#         .eq("session_id", session_id)
#         .order("created_at")
#         .execute()
#     )

#     history = []

#     for row in response.data:

#         history.append({
#             "role": "user",
#             "content": row["user_question"]
#         })

#         history.append({
#             "role": "assistant",
#             "content": row["chatbot_response"]
#         })

    
#     return history

# # def load_chat(session):

# #     response = (
# #         supabase
# #         .table("chatbot_conversations")
# #         .select("*")
# #         .eq("session_id", session)
# #         .order("created_at")
# #         .execute()
# #     )

# #     history = []

# #     for row in response.data:

# #          history.append({
# #                     "role": "user",
# #                     "content": row["user_question"]
# #                 })

# #          history.append({
# #                     "role": "assistant",
# #                     "content": row["chatbot_response"]
# #                 })
# #          return history
#                     # history.append(
#         #     (
#         #         row["user_question"],
#         #         row["chatbot_response"]
#         #     )
        



# # def create_new_chat():

# #     global session_id

# #     session_id = str(uuid.uuid4())

# #     return []

# def create_new_chat():

#     global session_id
#     global session_created
#     global chat_history

#     # Create a new session
#     session_id = str(uuid.uuid4())

#     # Allow the first message of the new chat
#     # to create a new chat_session record
#     session_created = False

#     # Clear chatbot memory
#     chat_history = []

#     return [], gr.update(choices=get_all_sessions())




# # def send_message(message, history):

# #     answer = chatbot(message, history)

# #     history.append({
# #     "role": "user",
# #     "content": message
# # })

# #     history.append({
# #     "role": "assistant",
# #     "content": answer
# # })

# #     return history, ""
# def send_message(message, history):

#     answer = chatbot(message, history)

#     history.append({
#         "role": "user",
#         "content": message
#     })

#     history.append({
#         "role": "assistant",
#         "content": answer
#     })

#     return (
#         history,
#         "",
#         gr.update(choices=get_all_sessions())
#     )


#     # history.append(
#     #     (message, answer)
#     # )


# import gradio as gr

# with gr.Blocks(title="PDF Chatbot") as demo:

#     with gr.Row():

#         with gr.Column(scale=1):

#             new_chat = gr.Button("➕ New Chat")

#             session_list = gr.Radio(
#                 choices=get_all_sessions(),
#                 label="Previous Chats"
#             )

#         with gr.Column(scale=4):

#             chatbot_ui = gr.Chatbot(height=600)

#             msg = gr.Textbox(
#                 placeholder="Type your message..."
#             )

#             send = gr.Button("Send")

#     # send.click(
#     #     send_message,
#     #     inputs=[msg, chatbot_ui],
#     #     outputs=[chatbot_ui, msg]
#     # )
#     send.click(
#     send_message,
#     inputs=[msg, chatbot_ui],
#     outputs=[chatbot_ui, msg, session_list]
#     )

#     session_list.change(
#         load_chat,
#         inputs=session_list,
#         outputs=chatbot_ui
#     )

#     new_chat.click(
#     create_new_chat,
#     outputs=[chatbot_ui, session_list]
#     )

#     # new_chat.click(
#     #     create_new_chat,
#     #     outputs=chatbot_ui
#     # )

# demo.launch()
# # supabase.table("chatbot_conversations").insert({
# #     "session_id": session_id,
# #     "user_question": message,
# #     "chatbot_response": response.content
# # }).execute()
# # from langchain_core.messages import HumanMessage, AIMessage

# # chat_history = []

# # def chatbot(message, history):

# #     global chat_history

# #     # Retrieve relevant chunks
# #     results = rag_retriever.retrieve(message, top_k=3)

# #     context = "\n\n".join([doc["content"] for doc in results]) if results else ""

# #     prompt = f"""
# # You are a helpful AI assistant.

# # Use the PDF context whenever it is relevant.

# # If the user is just chatting (Hi, Hello, How are you, etc.), respond normally.

# # If the user asks about the PDF, answer using ONLY the PDF context.

# # If the answer is not found in the PDF, say:
# # "I couldn't find that information in the uploaded PDF."

# # =========================
# # PDF Context
# # =========================
# # {context}

# # User Question:
# # {message}

# # Answer:
# # """

# #     # Build conversation history
# #     messages = chat_history.copy()
# #     messages.append(HumanMessage(content=prompt))

# #     # Call Groq LLM
# #     response = llm.invoke(messages)

# #     # Save conversation
# #     chat_history.append(HumanMessage(content=message))
# #     chat_history.append(AIMessage(content=response.content))

# #     return response.content

#     # chat_history.append(HumanMessage(content=prompt))

#     # response = llm.invoke(chat_history)

#     # chat_history.append(AIMessage(content=response.content))

#     # return response.content

# # def chatbot(message, history):
# #     """
# #     message = current user question
# #     history = previous conversation (provided by Gradio)
# #     """

# #     answer = rag_simple(
# #         query=message,
# #         retriever=rag_retriever,
# #         llm=llm
# #     )

# #     return answer




# # def chatbot(message, history):
# #     """
# #     message : Current user question
# #     history : Previous chat history from Gradio
# #     """

# #     # Retrieve relevant chunks
# #     results = rag_retriever.retrieve(message, top_k=3)

# #     #context = "\n\n".join([doc["content"] for doc in results]) if results else ""
# #     context = "\n\n".join([doc["content"] for doc in results]) if results else ""

# #     if not context:
# #             return "I couldn't find any relevant information in the uploaded PDF."

# #     # Keep only the last 5 conversations
# #     MAX_HISTORY = 5
# #     recent_history = history[-MAX_HISTORY:]

# #     # Build conversation history
# #     conversation = ""

# #     for user_msg, bot_msg in recent_history:
# #         conversation += f"User: {user_msg}\n"
# #         conversation += f"Assistant: {bot_msg}\n"

# #     # Create prompt (OUTSIDE the loop)
# #     prompt = f"""
# # You are a helpful AI assistant.

# # Answer the user's question ONLY using the information from the PDF context.

# # If the question is a follow-up (e.g. "Explain more", "Who invented it?", "What are its advantages?"), use the conversation history to understand what the user is referring to.

# # If the answer is not available in the PDF, simply reply:

# # "I couldn't find that information in the uploaded PDF."

# # =======================
# # Conversation History
# # =======================

# # {conversation}

# # =======================
# # PDF Context
# # =======================

# # {context}

# # =======================
# # Current Question
# # =======================

# # {message}

# # Answer:
# # """
# #     from langchain_core.messages import HumanMessage

# #     response = llm.invoke([HumanMessage(content=prompt)])

# #     return response.content
# #     # from langchain_core.messages import HumanMessage

# #     # response = llm.invoke([HumanMessage(content=prompt)])

# #     # response = llm.invoke(prompt)

# #     # return response.content

# # import gradio as gr
# # demo = gr.ChatInterface(
# #     fn=chatbot,
# #     title="📄 Conversational PDF Chatbot",
# #     description="Ask anything about your PDF.",
# #     #theme="soft"
# # )

# # demo.launch()   