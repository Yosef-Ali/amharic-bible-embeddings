"""
Amharic Bible Q&A System using Late Chunking Embeddings
"""

import sys
sys.path.append('/Users/mekdesyared/Embedding/amharic-bible-embeddings')

from src.vector_db.chroma_manager import ChromaBibleDB
from config.llm_config import llm_manager
import asyncio
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AmharicBibleQA:
    """
    Question-Answering system for the Amharic Bible using late chunking embeddings
    """
    
    def __init__(self, chroma_db_path: str = "./data/embeddings/chroma_db"):
        """Initialize Q&A system"""
        self.db = ChromaBibleDB(chroma_db_path)
        self.db.create_collection()
        self.llm_manager = llm_manager
        
    async def ask_question(self, 
                          question: str, 
                          max_results: int = 5,
                          book_filter: Optional[List[str]] = None,
                          testament_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask a question about the Bible and get contextual answers
        """
        
        try:
            # Step 1: Semantic search for relevant passages
            search_results = self.db.semantic_search(
                query=question,
                n_results=max_results,
                book_filter=book_filter,
                testament_filter=testament_filter
            )
            
            if not search_results:
                return {
                    "question": question,
                    "answer": "No relevant passages found for your question.",
                    "passages": [],
                    "success": False
                }
            
            # Step 2: Prepare context for LLM
            context_passages = []
            for i, result in enumerate(search_results, 1):
                books_str = ", ".join(result['books'])
                context_passages.append(
                    f"Passage {i} (from {books_str}, similarity: {result['similarity']:.3f}):\n"
                    f"{result['document']}\n"
                )
            
            combined_context = "\n".join(context_passages)
            
            # Step 3: Generate comprehensive answer using LLM
            qa_prompt = f"""
Based on the following passages from the Amharic Bible, answer this question comprehensively:

Question: {question}

Relevant Bible Passages:
{combined_context}

Please provide:
1. A direct answer to the question
2. Supporting evidence from the passages
3. Any relevant cross-references or connections
4. Brief theological context if applicable

Answer in English but preserve important Amharic terms. Be thorough but concise.
"""
            
            try:
                answer = await self.llm_manager.generate_context(qa_prompt, "biblical")
            except Exception as e:
                logger.warning(f"LLM answer generation failed: {e}")
                answer = self._create_basic_answer(question, search_results)
            
            return {
                "question": question,
                "answer": answer,
                "passages": search_results,
                "search_settings": {
                    "max_results": max_results,
                    "book_filter": book_filter,
                    "testament_filter": testament_filter
                },
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Q&A failed: {e}")
            return {
                "question": question,
                "answer": f"Error processing question: {str(e)}",
                "passages": [],
                "success": False
            }
    
    def _create_basic_answer(self, question: str, results: List[Dict]) -> str:
        """Create basic answer when LLM is unavailable"""
        
        if not results:
            return "No relevant passages found."
        
        answer = f"Based on the Bible search, here are the most relevant passages for '{question}':\n\n"
        
        for i, result in enumerate(results[:3], 1):
            books = ", ".join(result['books'])
            similarity = result['similarity']
            text = result['document'][:200] + "..." if len(result['document']) > 200 else result['document']
            
            answer += f"{i}. From {books} (similarity: {similarity:.3f}):\n{text}\n\n"
        
        return answer
    
    async def ask_multiple_questions(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Process multiple questions efficiently"""
        
        tasks = [self.ask_question(q) for q in questions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append({
                    "question": questions[i],
                    "answer": f"Error: {str(result)}",
                    "passages": [],
                    "success": False
                })
            else:
                final_results.append(result)
        
        return final_results
    
    def search_by_book(self, book_name: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for passages from a specific book"""
        
        return self.db.semantic_search(
            query=book_name,
            n_results=max_results,
            book_filter=[book_name]
        )
    
    def get_random_verses(self, count: int = 3) -> List[Dict[str, Any]]:
        """Get random verses for exploration"""
        
        # Simple random search using common Amharic terms
        search_terms = ["ፍቅር", "አምላክ", "ጌታ", "ሰላም", "መንግሥት"]
        import random
        
        results = []
        for _ in range(count):
            term = random.choice(search_terms)
            search_result = self.db.semantic_search(term, n_results=1)
            if search_result:
                results.extend(search_result)
        
        return results[:count]

async def main():
    """Interactive Q&A demo"""
    
    print("🙏 Amharic Bible Q&A System (Late Chunking)")
    print("=" * 50)
    
    qa_system = AmharicBibleQA()
    
    # Test questions in Amharic and English
    test_questions = [
        "ፍቅር ምንድን ነው?",  # What is love?
        "What does the Bible say about love?",
        "የወንጌል ተናገሩ", # Tell me about the Gospel
        "Who is Jesus Christ?"
    ]
    
    print("Testing with sample questions...\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"Q{i}: {question}")
        
        try:
            result = await qa_system.ask_question(question, max_results=2)
            
            if result['success']:
                print(f"A{i}: {result['answer'][:300]}...\n")
                print(f"   Relevant passages: {len(result['passages'])}")
                for j, passage in enumerate(result['passages'], 1):
                    books = ', '.join(passage['books'])
                    print(f"     {j}. {books} (similarity: {passage['similarity']:.3f})")
            else:
                print(f"A{i}: {result['answer']}")
            
            print()
            
        except Exception as e:
            print(f"A{i}: Error - {e}\n")
    
    print("Q&A system ready for interactive use!")

if __name__ == "__main__":
    asyncio.run(main())