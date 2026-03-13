from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
import os

class BM25Index:
    def __init__(self, index_dir="bm25_index"):
        self.index_dir = index_dir

        if not os.path.exists(index_dir):
            os.mkdir(index_dir)

            schema = Schema(
                id=ID(stored=True),
                content=TEXT(stored=True),
            )

            self.ix = create_in(index_dir, schema)

        else:
            self.ix = open_dir(index_dir)
        
    
    def add_documents(self, documents):
        writer = self.ix.writer()
        for i, doc in enumerate(documents):
            writer.add_document(id=str(i), 
                                content=doc.page_content
                                )
        writer.commit()
    
    def searchg(self, query, k=5):
        with self.ix.searcher() as searcher:
            parser = QueryParser("content", schema=self.ix.schema)
            q = parser.parse(query)
            results = searcher.search(q, limit=k)

            output = []
            
            for r in results:

                output.append({
                    "content": r["content"],
                    "similarity_score": r["score"]
                })

            return output
