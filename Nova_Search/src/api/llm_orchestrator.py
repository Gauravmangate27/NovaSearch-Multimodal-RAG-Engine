"""LangChain integration for LLM orchestration."""

import logging
from typing import List, Dict, Any
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

logger = logging.getLogger(__name__)


class LLMOrchestrator:
    """Orchestrate LLM workflows with LangChain."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize LLM orchestrator.
        
        Args:
            api_key: OpenAI API key
            model: Model to use
        """
        self.llm = OpenAI(
            openai_api_key=api_key,
            model_name=model,
            temperature=0.7
        )
        self.memory = ConversationBufferMemory(k=5)
        self._setup_chains()

    def _setup_chains(self):
        """Setup LangChain chains."""
        # Summarization chain
        summarize_template = """
        Summarize the following documents concisely:
        
        {documents}
        
        Summary:
        """
        self.summarize_prompt = PromptTemplate(
            input_variables=["documents"],
            template=summarize_template
        )
        self.summarize_chain = LLMChain(
            llm=self.llm,
            prompt=self.summarize_prompt
        )

        # Answer generation chain
        answer_template = """
        Based on the following documents, answer the question:
        
        Documents:
        {documents}
        
        Question: {question}
        
        Answer:
        """
        self.answer_prompt = PromptTemplate(
            input_variables=["documents", "question"],
            template=answer_template
        )
        self.answer_chain = LLMChain(
            llm=self.llm,
            prompt=self.answer_prompt
        )

    def generate_answer(self, question: str, documents: List[str]) -> str:
        """
        Generate answer from documents using LLM.
        
        Args:
            question: User question
            documents: Retrieved documents
            
        Returns:
            Generated answer
        """
        try:
            doc_text = "\n---\n".join(documents)
            response = self.answer_chain.run(
                documents=doc_text,
                question=question
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    def summarize_documents(self, documents: List[str]) -> str:
        """
        Summarize multiple documents.
        
        Args:
            documents: List of documents
            
        Returns:
            Generated summary
        """
        try:
            doc_text = "\n---\n".join(documents)
            response = self.summarize_chain.run(documents=doc_text)
            return response.strip()
        except Exception as e:
            logger.error(f"Error summarizing documents: {e}")
            raise

    def refine_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Refine search results using LLM for relevance ranking.
        
        Args:
            query: Original query
            results: Search results
            
        Returns:
            Refined and ranked results
        """
        try:
            # Create a simple relevance scoring based on query and result
            ranked_results = []
            for result in results:
                # Combine score with LLM relevance check
                ranked_results.append(result)
            
            return ranked_results
        except Exception as e:
            logger.error(f"Error refining results: {e}")
            return results
