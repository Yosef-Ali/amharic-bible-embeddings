"""
Catholic Catechism Tool for MCP Server
Provides Catholic doctrine explanations and saint information
"""

from typing import Dict, Any, Optional
import json

class CatechismTool:
    """Tool for accessing Catholic Catechism and doctrinal information"""
    
    def __init__(self):
        self.catechism_data = self._load_catechism_basics()
        self.saints_data = self._load_saints_basics()
    
    def _load_catechism_basics(self) -> Dict[str, str]:
        """Load basic Catholic teachings (can be expanded with real CCC data)"""
        
        return {
            "trinity": "በካቶሊክ እምነት መሰረት፣ እግዚአብሔር አንድ ሆኖ በሶስት ግለሰቦች ይገለጣል፦ አብ፣ ወልድ እና መንፈስ ቅዱስ። ይህ የሶስትነት እምነት የክርስትና እምነት መሰረት ነው።",
            "salvation": "መዳን በኢየሱስ ክርስቶስ አማካይነት የሚገኝ የእግዚአብሔር ነጻ ስጦታ ነው። በእምነት፣ በመጥምቅ እና በአማኝነት ህይወት ይገኛል።",
            "sacraments": "በካቶሊክ ቤተክርስቲያን ሰባት ቅዱሳት ምስጢራት አሉ፦ መጥምቅ፣ ማረጋገጫ፣ ቅዳሴ፣ መንፈሳዊ መፈወስ፣ ቅዱስ ትዳር፣ ቅዱስ ስልጣን እና በሽተኛ ዘይት።",
            "mary": "እመቤታችን ማርያም የእግዚአብሔር እናት፣ ሁሌም ድንግል እና የሰማይ ንግሥት ናት። ኃጢአት ሳትሆን የተወለደች እና ወደ ሰማይ በሥጋዋ የተወሰደች ነች።",
            "mass": "ቅዳሴ የኢየሱስ ክርስቶስ መስዋእት በእንጀራ እና በወይን መልክ እንደገና የሚቀርብበት ቅዱስ ሥነ ሥርዓት ነው።",
            "prayer": "ጸሎት ከእግዚአብሔር ጋር የሚደረግ ንግግር ነው። የሮዛሪዮ ጸሎት፣ የሀሌልያ እና የጌታችን ጸሎት ዋና ዋና የካቶሊክ ጸሎቶች ናቸው።",
            "saints": "ቅዱሳን በሰማይ ያሉ እና ለእኛ የሚመልሱልን የእግዚአብሔር ወዳጆች ናቸው። እነሱን ማክበር እና ምልከታቸውን መጠየቅ የካቶሊክ ባህል ነው።",
            "pope": "ጳጳሱ የቅዱስ ጴጥሮስ ተተኪ እና የአለም አቀፍ ካቶሊክ ቤተክርስቲያን ራስ ነው። በእምነት እና ምግባር ጉዳዮች ላይ የማይሳሳት ውሳኔ ይሰጣል።",
            "purgatory": "ንጽሐና የሚመረቅበት ሰማይ ወደ መግባት የሚያበቃ መካከለኛ ሁኔታ ነው።"
        }
    
    def _load_saints_basics(self) -> Dict[str, Dict]:
        """Load basic saint information (can be expanded)"""
        
        return {
            "mary": {
                "name": "እመቤታችን ማርያም",
                "title": "የእግዚአብሔር እናት",
                "feast_day": "ጃንዋሪ 1",
                "patron_of": ["ሁሉም ሰዎች", "ኢትዮጵያ"],
                "description": "የኢየሱስ ክርስቶስ እናት እና ሁሌም ድንግል"
            },
            "joseph": {
                "name": "ቅዱስ ዮሴፍ",
                "title": "የኢየሱስ የምድር አባት",
                "feast_day": "ማርች 19",
                "patron_of": ["ቤተሰቦች", "ሠራተኞች"],
                "description": "የማርያም ባል እና የኢየሱስ አሳዳጊ አባት"
            },
            "peter": {
                "name": "ቅዱስ ጴጥሮስ",
                "title": "የሐዋርያት ርእሰ",
                "feast_day": "ሰኔ 29",
                "patron_of": ["ጳጳሳት", "ዓሣ አጥማጆች"],
                "description": "የኢየሱስ ቀዳሚ ሐዋርያ እና የመጀመሪያው ጳጳስ"
            },
            "paul": {
                "name": "ቅዱስ ጳውሎስ",
                "title": "የአህዛብ ሐዋርያ",
                "feast_day": "ሰኔ 29",
                "patron_of": ["ሚሲዮናውያን", "ጸሐፊዎች"],
                "description": "ከሐዋርያት ዋና ተሰባኪ እና የአዲስ ኪዳን ፀሐፊ"
            }
        }
    
    async def search(self, query: str, max_results: int = 5, min_similarity: float = 0.3) -> Dict[str, Any]:
        """Search Bible using semantic similarity"""
        
        if not self.embeddings_data:
            return {
                "error": "Bible embeddings not loaded",
                "results": [],
                "success": False
            }
        
        try:
            # Generate query embedding
            model = self._get_model()
            query_embedding = model.encode([query])[0]
            
            # Search all chunks
            results = []
            for chunk in self.embeddings_data["chunks"]:
                if "embedding" in chunk:
                    similarity = self._calculate_similarity(query_embedding, chunk["embedding"])
                    
                    if similarity >= min_similarity:
                        results.append({
                            "similarity": round(similarity, 4),
                            "book": chunk.get("book", "Unknown"),
                            "chapter": chunk.get("chapter", 0),
                            "verse": chunk.get("verse_number", 0),
                            "text": chunk.get("text", ""),
                            "testament": chunk.get("testament", "unknown"),
                            "reference": f"{chunk.get('book', 'Unknown')} {chunk.get('chapter', 0)}:{chunk.get('verse_number', 0)}"
                        })
            
            # Sort and limit
            results.sort(key=lambda x: x["similarity"], reverse=True)
            results = results[:max_results]
            
            return {
                "query": query,
                "results": results,
                "total_found": len(results),
                "search_quality": "excellent" if results and results[0]["similarity"] > 0.7 else 
                                "good" if results and results[0]["similarity"] > 0.5 else
                                "fair" if results else "poor",
                "success": True
            }
        
        except Exception as e:
            return {
                "error": f"Search failed: {str(e)}",
                "results": [],
                "success": False
            }
    
    async def explain_teaching(self, topic: str, detail_level: str = "intermediate") -> str:
        """Explain Catholic teaching on a specific topic"""
        
        topic_key = topic.lower().strip()
        
        # Check if we have basic teaching information
        if topic_key in self.catechism_data:
            basic_explanation = self.catechism_data[topic_key]
            
            if detail_level == "basic":
                return basic_explanation
            elif detail_level == "advanced":
                return f"{basic_explanation}\n\nዝርዝር ማብራርያ፦ ይህ ጉዳይ ስለ ካቶሊክ እምነት ጥልቅ አስተምህሮ ያስፈልገዋል። የመጽሐፍ ቅዱስ ማጣቀሻዎችን እና የአባቶች ትምህርቶችን ያካትታል።"
            else:  # intermediate
                return f"{basic_explanation}\n\nተጨማሪ መረጃ ለማግኘት የቅዱሳን መጻሕፍት እና የካቶሊክ ቤተክርስቲያን ይፋዊ ትምህርቶችን ማየት ይቻላል።"
        
        # If topic not found in our basic data
        return f"'{topic}' ላይ ስላለው የካቶሊክ ትምህርት ተጨማሪ መረጃ ያስፈልጋል። የካቶሊክ ካቴኪዝም መጽሐፍን ወይም የካቶሊክ ቤተክርስቲያን ይፋዊ ዶክመንቶችን ማየት ይመከራል።"
    
    async def get_saint_info(self, saint_name: str, search_type: str = "name") -> str:
        """Get information about a Catholic saint"""
        
        saint_key = saint_name.lower().strip()
        
        # Try to find saint in our basic data
        for key, saint_data in self.saints_data.items():
            if (key == saint_key or 
                saint_key in saint_data["name"].lower() or
                any(saint_key in alias.lower() for alias in saint_data.get("aliases", []))):
                
                return f"""ቅዱስ መረጃ፦ {saint_data['name']}

ማዕረግ፦ {saint_data['title']}
የበዓል ቀን፦ {saint_data['feast_day']}
የ...መጠበቂያ ቅዱስ፦ {', '.join(saint_data['patron_of'])}

ማብራርያ፦ {saint_data['description']}"""
        
        return f"ስለ '{saint_name}' ቅዱስ ተጨማሪ መረጃ ያስፈልጋል። የቅዱሳን መጽሐፍ ወይም የካቶሊክ ቤተክርስቲያን ይፋዊ ዶክመንቶች ማየት ይመከራል።"
    
    async def search_catechism(self, topic: str) -> Dict[str, Any]:
        """Search Catholic Catechism for specific topics"""
        
        # This would integrate with actual CCC database
        # For now, return basic structure
        
        return {
            "topic": topic,
            "catechism_references": [],
            "church_documents": [],
            "biblical_foundations": [],
            "practical_applications": [],
            "note": "Full Catechism integration pending - this is a placeholder"
        }