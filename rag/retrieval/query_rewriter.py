class QueryRewriter:

    def rewrite(self, query):
        prompt= f"""
        Rewrite the query to improve document retrieval.

        Query: {query}

        Rewritten Query:    
        """
        ## TODO
        ## Call LLM Here
        return prompt