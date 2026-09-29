from rag.context import (
    ContextBuilder,
    PromptContextBuilder,
)

from retrieval.hybrid import HybridRetriever


class RAGService:

    def __init__(self, db):

        self.retriever = HybridRetriever(db)

        self.context_builder = ContextBuilder()

        self.prompt_builder = (
            PromptContextBuilder()
        )

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        candidate_limit: int = 20,
        file_id=None,
        folder_id=None,
        file_ids=None,
    ):

        results = self.retriever.search(
            query=query,
            limit=limit,
            candidate_limit=candidate_limit,
            file_id=file_id,
            folder_id=folder_id,
            file_ids=file_ids,
        )

        contexts = (
            self.context_builder.build(
                results
            )
        )

        prompt_context = (
            self.prompt_builder.build(
                contexts
            )
        )

        return contexts, prompt_context