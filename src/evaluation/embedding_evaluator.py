"""
Evaluation framework for Amharic Bible embeddings quality
"""

import sys
sys.path.append('/Users/mekdesyared/Embedding/amharic-bible-embeddings')

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from src.vector_db.chroma_manager import ChromaBibleDB
import logging

logger = logging.getLogger(__name__)

class EmbeddingEvaluator:
    """Evaluate quality of late chunking embeddings"""
    
    def __init__(self, chroma_db_path: str = "./data/embeddings/chroma_db"):
        self.db = ChromaBibleDB(chroma_db_path)
        self.db.create_collection()
        
    def evaluate_semantic_coherence(self) -> Dict[str, Any]:
        """Evaluate how well embeddings capture semantic coherence"""
        
        print("Evaluating semantic coherence...")
        
        # Test queries with expected results
        test_cases = [
            {
                "query": "ፍቅር",  # Love
                "expected_themes": ["love", "charity", "compassion"],
                "expected_books": ["1ኛ የዮሐንስ መልእክት", "1ኛ ወደ ቆሮንቶስ ሰዎች"]
            },
            {
                "query": "ሰላም",  # Peace
                "expected_themes": ["peace", "reconciliation", "harmony"],
                "expected_books": ["የኤፌሶን ወንጌል", "ወደ ሮሜ ሰዎች"]
            },
            {
                "query": "ጸሎት",  # Prayer
                "expected_themes": ["prayer", "worship", "supplication"],
                "expected_books": ["የማቴዎስ ወንጌል", "የሉቃስ ወንጌል"]
            }
        ]
        
        evaluation_results = []
        
        for test_case in test_cases:
            results = self.db.semantic_search(test_case["query"], n_results=5)
            
            # Calculate relevance scores
            relevant_count = 0
            avg_similarity = 0.0
            books_found = set()
            
            for result in results:
                if result['similarity'] > 0.3:  # Threshold for relevance
                    relevant_count += 1
                avg_similarity += result['similarity']
                books_found.update(result['books'])
            
            avg_similarity = avg_similarity / len(results) if results else 0
            
            evaluation_results.append({
                "query": test_case["query"],
                "relevant_results": relevant_count,
                "total_results": len(results),
                "avg_similarity": avg_similarity,
                "books_found": list(books_found),
                "relevance_ratio": relevant_count / len(results) if results else 0
            })
        
        # Overall metrics
        overall_relevance = np.mean([r["relevance_ratio"] for r in evaluation_results])
        overall_similarity = np.mean([r["avg_similarity"] for r in evaluation_results])
        
        return {
            "test_cases": evaluation_results,
            "overall_relevance_ratio": overall_relevance,
            "overall_avg_similarity": overall_similarity,
            "evaluation_summary": {
                "semantic_coherence": "Good" if overall_relevance > 0.6 else "Needs improvement",
                "embedding_quality": "Good" if overall_similarity > 0.4 else "Needs improvement"
            }
        }
    
    def evaluate_book_coverage(self) -> Dict[str, Any]:
        """Evaluate coverage of all 72 Catholic Bible books"""
        
        print("Evaluating book coverage...")
        
        stats = self.db.get_collection_stats()
        
        if 'error' in stats:
            return {"error": "Could not evaluate book coverage", "details": stats}
        
        # Sample chunks to analyze book distribution
        sample_results = self.db.collection.peek(limit=1000)
        
        book_distribution = {}
        testament_counts = {'old': 0, 'new': 0}
        
        for metadata in sample_results['metadatas']:
            books = json.loads(metadata['books'])
            testament = metadata.get('testament', 'unknown')
            
            testament_counts[testament] += 1
            
            for book in books:
                book_distribution[book] = book_distribution.get(book, 0) + 1
        
        total_books_found = len(book_distribution)
        
        return {
            "total_books_covered": total_books_found,
            "target_books": 72,
            "coverage_ratio": total_books_found / 72,
            "book_distribution": dict(sorted(book_distribution.items())),
            "testament_distribution": testament_counts,
            "coverage_assessment": {
                "status": "Complete" if total_books_found >= 70 else "Incomplete",
                "missing_count": max(0, 72 - total_books_found)
            }
        }
    
    def evaluate_chunk_quality(self) -> Dict[str, Any]:
        """Evaluate quality of chunking"""
        
        print("Evaluating chunk quality...")
        
        # Load chunk data
        chunks_file = "/Users/mekdesyared/Embedding/amharic-bible-embeddings/data/embeddings/production_embeddings.jsonl"
        
        if not Path(chunks_file).exists():
            return {"error": "Chunks file not found"}
        
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = [json.loads(line) for line in f]
        
        # Analyze chunk characteristics
        word_counts = [chunk.get('character_count', len(chunk['text'])) for chunk in chunks]
        text_lengths = [len(chunk['text']) for chunk in chunks]
        
        quality_metrics = {
            "total_chunks": len(chunks),
            "word_count_stats": {
                "mean": np.mean(word_counts),
                "std": np.std(word_counts),
                "min": np.min(word_counts),
                "max": np.max(word_counts)
            },
            "text_length_stats": {
                "mean": np.mean(text_lengths),
                "std": np.std(text_lengths),
                "min": np.min(text_lengths),
                "max": np.max(text_lengths)
            },
            "chunk_consistency": {
                "word_count_cv": np.std(word_counts) / np.mean(word_counts),  # Coefficient of variation
                "quality_score": "Good" if np.std(word_counts) / np.mean(word_counts) < 0.5 else "Variable"
            }
        }
        
        return quality_metrics
    
    def run_comprehensive_evaluation(self) -> Dict[str, Any]:
        """Run all evaluation tests"""
        
        print("\n🔍 Running Comprehensive Evaluation")
        print("=" * 40)
        
        # Run all evaluations
        semantic_eval = self.evaluate_semantic_coherence()
        coverage_eval = self.evaluate_book_coverage()
        quality_eval = self.evaluate_chunk_quality()
        
        # Compile overall assessment
        overall_score = 0
        max_score = 3
        
        # Semantic coherence score (0-1)
        if semantic_eval.get("overall_relevance_ratio", 0) > 0.6:
            overall_score += 1
        
        # Coverage score (0-1)  
        if coverage_eval.get("coverage_ratio", 0) > 0.95:
            overall_score += 1
        
        # Quality score (0-1)
        if not quality_eval.get("error") and quality_eval.get("chunk_consistency", {}).get("quality_score") == "Good":
            overall_score += 1
        
        final_assessment = {
            "overall_score": f"{overall_score}/{max_score}",
            "overall_grade": "Excellent" if overall_score == 3 else "Good" if overall_score >= 2 else "Needs Improvement",
            "semantic_coherence": semantic_eval,
            "book_coverage": coverage_eval, 
            "chunk_quality": quality_eval,
            "recommendations": self._generate_recommendations(semantic_eval, coverage_eval, quality_eval)
        }
        
        return final_assessment
    
    def _generate_recommendations(self, semantic_eval: Dict, coverage_eval: Dict, quality_eval: Dict) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        # Semantic recommendations
        if semantic_eval.get("overall_relevance_ratio", 0) < 0.6:
            recommendations.append("Consider improving embedding model or chunking strategy for better semantic coherence")
        
        # Coverage recommendations  
        if coverage_eval.get("coverage_ratio", 0) < 0.95:
            recommendations.append(f"Missing {coverage_eval.get('coverage_assessment', {}).get('missing_count', 0)} books - review extraction process")
        
        # Quality recommendations
        if quality_eval.get("chunk_consistency", {}).get("quality_score") != "Good":
            recommendations.append("Chunk sizes are inconsistent - consider adjusting chunking parameters")
        
        if not recommendations:
            recommendations.append("Embedding system is performing well - consider adding LLM contextual enhancement for even better results")
        
        return recommendations

def main():
    """Run evaluation"""
    
    evaluator = EmbeddingEvaluator()
    
    # Run comprehensive evaluation
    results = evaluator.run_comprehensive_evaluation()
    
    # Print results
    print(f"\n📊 Final Assessment: {results['overall_grade']} ({results['overall_score']})")
    
    print(f"\n📚 Book Coverage: {results['book_coverage']['total_books_covered']}/72 books")
    print(f"   Status: {results['book_coverage']['coverage_assessment']['status']}")
    
    print(f"\n🎯 Semantic Coherence: {results['semantic_coherence']['overall_relevance_ratio']:.2f}")
    print(f"   Assessment: {results['semantic_coherence']['evaluation_summary']['semantic_coherence']}")
    
    if not results['chunk_quality'].get('error'):
        print(f"\n📝 Chunk Quality: {results['chunk_quality']['chunk_consistency']['quality_score']}")
        print(f"   Avg words/chunk: {results['chunk_quality']['word_count_stats']['mean']:.1f}")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"   {i}. {rec}")

if __name__ == "__main__":
    main()