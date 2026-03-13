from rag.core.dependencies import vector_store
from rag.services.llm_service import LLMService

class AgenticService:
    def __init__(self):
        self.llm = LLMService()
        self.vector_store = vector_store

    def ask(self, question: str):

        ## Retrive documents
        docs = self.vector_store.similarity_search(question)

        ## Generate response
        context = "\n".join([doc.page_content for doc in docs])
        
        prompt=f"""
You are an AI assistant answering questions using provided context.

Context: {context}

Question: {question}

Answer clearly using the context.
If the answer is not in the context, say "I don't know".
        """

        answer = self.llm.generate(prompt)

        return {
            "answer": answer,
            "sources": [doc.metadata for doc in docs]
        }

        

