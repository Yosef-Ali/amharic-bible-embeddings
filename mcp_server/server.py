#!/usr/bin/env python3
"""
Catholic Teaching Assistant MCP Server
Provides Catholic doctrine, Bible search, and liturgical tools via MCP protocol
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path to access existing modules
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
import mcp.types as types

# Import our existing components
from config.settings import settings, EMBEDDINGS_DIR
from mcp_server.tools.bible_search import BibleSearchTool
from mcp_server.tools.catechism_tool import CatechismTool
from mcp_server.tools.liturgical_calendar import LiturgicalCalendarTool
from mcp_server.tools.catholic_prayers import CatholicPrayersTool

# Initialize MCP server
app = Server("catholic-teaching-assistant")

# Initialize tools
bible_search_tool = None
catechism_tool = None
calendar_tool = None
prayers_tool = None

@app.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available Catholic teaching resources"""
    
    return [
        Resource(
            uri="catholic://bible/amharic",
            name="Amharic Bible Database",
            description="Semantic search across 31 biblical books with 17K+ verses",
            mimeType="application/json"
        ),
        Resource(
            uri="catholic://catechism/ccc",
            name="Catholic Catechism",
            description="Catholic Church teachings and doctrine",
            mimeType="text/plain"
        ),
        Resource(
            uri="catholic://calendar/liturgical",
            name="Liturgical Calendar",
            description="Daily readings, feast days, and liturgical seasons",
            mimeType="application/json"
        ),
        Resource(
            uri="catholic://prayers/traditional",
            name="Catholic Prayers",
            description="Traditional Catholic prayers and devotions",
            mimeType="text/plain"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read specific Catholic teaching resources"""
    
    if uri == "catholic://bible/amharic":
        return json.dumps({
            "description": "Amharic Bible semantic search database",
            "books": 31,
            "verses": 17587,
            "testaments": ["old", "new"],
            "languages": ["amharic", "english"],
            "embedding_model": settings.EMBEDDING_MODEL
        }, ensure_ascii=False)
    
    elif uri == "catholic://catechism/ccc":
        return "Catholic Catechism resource - doctrinal teachings of the Catholic Church"
    
    elif uri == "catholic://calendar/liturgical":
        return json.dumps({
            "description": "Liturgical calendar with daily readings and feast days",
            "coverage": "Full liturgical year",
            "languages": ["amharic", "english"]
        })
    
    elif uri == "catholic://prayers/traditional":
        return "Traditional Catholic prayers including rosary, novenas, and daily prayers"
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available Catholic teaching tools"""
    
    return [
        Tool(
            name="search_bible",
            description="Search the Amharic Bible using semantic similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query in Amharic or English"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 5)",
                        "default": 5
                    },
                    "min_similarity": {
                        "type": "number",
                        "description": "Minimum similarity score (0.0-1.0, default: 0.3)",
                        "default": 0.3
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="explain_catholic_teaching",
            description="Explain Catholic doctrine and teachings on specific topics",
            inputSchema={
                "type": "object", 
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Catholic teaching topic to explain"
                    },
                    "detail_level": {
                        "type": "string",
                        "enum": ["basic", "intermediate", "advanced"],
                        "description": "Level of detail for explanation",
                        "default": "intermediate"
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="get_daily_readings",
            description="Get Catholic daily Mass readings for specified date",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format (default: today)"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["amharic", "english"],
                        "description": "Language for readings",
                        "default": "amharic"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_catholic_prayer",
            description="Retrieve Catholic prayers by type or occasion",
            inputSchema={
                "type": "object",
                "properties": {
                    "prayer_type": {
                        "type": "string", 
                        "enum": ["our_father", "hail_mary", "glory_be", "rosary", "angelus", "te_deum", "morning_offering"],
                        "description": "Type of Catholic prayer"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["amharic", "english", "latin"],
                        "description": "Prayer language",
                        "default": "amharic"
                    },
                    "occasion": {
                        "type": "string",
                        "description": "Specific occasion or intention for prayer"
                    }
                },
                "required": ["prayer_type"]
            }
        ),
        Tool(
            name="get_saint_info",
            description="Get information about Catholic saints",
            inputSchema={
                "type": "object",
                "properties": {
                    "saint_name": {
                        "type": "string",
                        "description": "Name of the Catholic saint"
                    },
                    "search_type": {
                        "type": "string",
                        "enum": ["name", "feast_day", "patron_of"],
                        "description": "How to search for the saint",
                        "default": "name"
                    }
                },
                "required": ["saint_name"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls for Catholic teaching assistance"""
    
    global bible_search_tool, catechism_tool, calendar_tool, prayers_tool
    
    try:
        if name == "search_bible":
            if not bible_search_tool:
                bible_search_tool = BibleSearchTool()
            
            query = arguments["query"]
            max_results = arguments.get("max_results", 5)
            min_similarity = arguments.get("min_similarity", 0.3)
            
            results = await bible_search_tool.search(query, max_results, min_similarity)
            
            return [TextContent(
                type="text",
                text=json.dumps(results, ensure_ascii=False, indent=2)
            )]
        
        elif name == "explain_catholic_teaching":
            if not catechism_tool:
                catechism_tool = CatechismTool()
            
            topic = arguments["topic"]
            detail_level = arguments.get("detail_level", "intermediate")
            
            explanation = await catechism_tool.explain_teaching(topic, detail_level)
            
            return [TextContent(
                type="text", 
                text=explanation
            )]
        
        elif name == "get_daily_readings":
            if not calendar_tool:
                calendar_tool = LiturgicalCalendarTool()
            
            date = arguments.get("date")
            language = arguments.get("language", "amharic")
            
            readings = await calendar_tool.get_daily_readings(date, language)
            
            return [TextContent(
                type="text",
                text=json.dumps(readings, ensure_ascii=False, indent=2)
            )]
        
        elif name == "get_catholic_prayer":
            if not prayers_tool:
                prayers_tool = CatholicPrayersTool()
            
            prayer_type = arguments["prayer_type"]
            language = arguments.get("language", "amharic")
            occasion = arguments.get("occasion")
            
            prayer = await prayers_tool.get_prayer(prayer_type, language, occasion)
            
            return [TextContent(
                type="text",
                text=prayer
            )]
        
        elif name == "get_saint_info":
            if not catechism_tool:
                catechism_tool = CatechismTool()
            
            saint_name = arguments["saint_name"]
            search_type = arguments.get("search_type", "name")
            
            saint_info = await catechism_tool.get_saint_info(saint_name, search_type)
            
            return [TextContent(
                type="text",
                text=saint_info
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

async def main():
    """Run the Catholic Teaching Assistant MCP server"""
    
    # Import transport - this would typically be done via MCP client
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream,
            InitializationOptions(
                server_name="catholic-teaching-assistant",
                server_version="1.0.0",
                capabilities={
                    "resources": {},
                    "tools": {}
                }
            )
        )

if __name__ == "__main__":
    asyncio.run(main())