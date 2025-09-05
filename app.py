#!/usr/bin/env python3
"""
Liturgical Calendar Search Interface
Western + Eastern Orthodox traditions
"""

import streamlit as st
import json
import numpy as np
import datetime
from pathlib import Path
from sentence_transformers import SentenceTransformer
import sys
import pandas as pd

# Add project to path
sys.path.append(str(Path(__file__).parent))

from src.calendar_calculator import liturgical_manager

st.set_page_config(
    page_title="Liturgical Calendar Search",
    page_icon="🗓️", 
    layout="wide"
)

@st.cache_resource
def load_model():
    """Load embedding model"""
    return SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

@st.cache_data
def load_liturgical_db():
    """Load liturgical database"""
    db_file = Path(__file__).parent / "data/liturgical_database_2025.json"
    
    if not db_file.exists():
        return None
    
    with open(db_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_readings(query: str, db_data: dict, model, tradition_filter: str = "both", top_k: int = 10):
    """Search liturgical readings"""
    
    # Generate query embedding
    query_embedding = model.encode([query])[0]
    
    # Filter by tradition if specified
    readings = db_data["readings"]
    if tradition_filter != "both":
        readings = [r for r in readings if r["tradition"] == tradition_filter]
    
    # Calculate similarities
    results = []
    for reading in readings:
        reading_embedding = np.array(reading["embedding"])
        
        similarity = np.dot(query_embedding, reading_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(reading_embedding)
        )
        
        results.append({
            **reading,
            "similarity": float(similarity)
        })
    
    # Sort and return top results
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]

def get_readings_for_date(target_date: datetime.date, db_data: dict):
    """Get readings for specific date"""
    
    date_str = target_date.isoformat()
    
    # Find readings for this date
    western_readings = None
    eastern_readings = None
    
    for reading in db_data["readings"]:
        if reading["date"] == date_str:
            if reading["tradition"] == "western":
                western_readings = reading
            elif reading["tradition"] == "ethiopian":
                eastern_readings = reading
    
    return western_readings, eastern_readings

def main():
    """Main Streamlit application"""
    
    st.title("🗓️ Liturgical Calendar & Readings Search")
    st.markdown("*Western Catholic + Eastern Orthodox traditions with semantic search*")
    
    # Load data
    with st.spinner("Loading liturgical database..."):
        db_data = load_liturgical_db()
        model = load_model()
    
    if not db_data:
        st.error("❌ No liturgical database found!")
        st.info("Run `python scripts/build_liturgical_db.py` first")
        st.stop()
    
    st.success(f"✅ Loaded {db_data['total_readings']} liturgical readings for {db_data['year']}")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Today's Readings", "🔍 Search Readings", "📊 Calendar View", "ℹ️ About"])
    
    with tab1:
        st.header("Today's Liturgical Readings")
        
        # Get today's info
        today = datetime.date.today()
        today_info = liturgical_manager.get_daily_info(today)
        
        # Display calendar information
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Western (Roman Catholic)")
            st.write(f"**Date**: {today.strftime('%B %d, %Y')}")
            st.write(f"**Liturgical Year**: {today_info['western']['liturgical_year']}")
            st.write(f"**Season**: {today_info['western']['season_info']['season']}")
            st.write(f"**Liturgical Color**: {today_info['western']['season_info']['liturgical_color']}")
            
        with col2:
            st.subheader("⛪ Eastern Orthodox (Ethiopian)")
            eth_date = today_info['ethiopian']['date']
            st.write(f"**Ethiopian Date**: {eth_date['formatted']}")
            st.write(f"**Season**: {today_info['ethiopian']['season']}")
            fasting_info = today_info['ethiopian']['is_fasting_day']
            st.write(f"**Fasting**: {'Yes' if fasting_info['is_fasting'] else 'No'}")
            
            if fasting_info['is_fasting']:
                st.info(f"Fasting Rules: {', '.join(fasting_info['fasting_rules'])}")
        
        # Get actual readings for today
        western_readings, eastern_readings = get_readings_for_date(today, db_data)
        
        if western_readings or eastern_readings:
            st.subheader("📖 Today's Scripture Readings")
            
            reading_col1, reading_col2 = st.columns(2)
            
            with reading_col1:
                if western_readings:
                    st.markdown("**Western Tradition:**")
                    readings = western_readings.get("readings", {})
                    
                    for reading_type in ["first_reading", "responsorial_psalm", "gospel"]:
                        if reading_type in readings:
                            reading = readings[reading_type]
                            st.write(f"**{reading_type.title()}**: {reading.get('reference', 'TBD')}")
                            if reading.get('theme'):
                                st.caption(f"Theme: {reading['theme']}")
            
            with reading_col2:
                if eastern_readings:
                    st.markdown("**Eastern Orthodox:**") 
                    readings = eastern_readings.get("readings", {})
                    
                    for reading_type in ["old_testament", "epistle", "gospel"]:
                        if reading_type in readings:
                            reading = readings[reading_type]
                            st.write(f"**{reading_type.title()}**: {reading.get('reference', 'TBD')}")
                            if reading.get('theme'):
                                st.caption(f"Theme: {reading['theme']}")
    
    with tab2:
        st.header("🔍 Search Liturgical Readings")
        
        # Search interface
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            search_query = st.text_input(
                "Search readings by theme, season, or content:",
                placeholder="Christmas, forgiveness, healing, Lent..."
            )
        
        with col2:
            tradition_filter = st.selectbox(
                "Tradition:",
                ["both", "western", "ethiopian"]
            )
        
        with col3:
            max_results = st.selectbox("Results:", [5, 10, 20], index=1)
        
        search_button = st.button("🔍 Search Readings", type="primary")
        
        if search_button and search_query:
            with st.spinner("Searching liturgical readings..."):
                results = search_readings(search_query, db_data, model, tradition_filter, max_results)
            
            if results:
                st.subheader(f"📖 Search Results for '{search_query}'")
                
                for i, result in enumerate(results, 1):
                    tradition_icon = "🌍" if result["tradition"] == "western" else "⛪"
                    
                    with st.expander(f"{i}. {tradition_icon} {result['date']} - {result['tradition'].title()} (Score: {result['similarity']:.3f})"):
                        
                        # Date and tradition info
                        day_info = result["day_info"]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Date**: {result['date']}")
                            st.write(f"**Weekday**: {day_info['weekday']}")
                            
                        with col2:
                            if result["tradition"] == "western":
                                season_info = day_info['western']['season_info']
                                st.write(f"**Season**: {season_info['season']}")
                                st.write(f"**Color**: {season_info['liturgical_color']}")
                            else:
                                eth_info = day_info['ethiopian']
                                st.write(f"**Season**: {eth_info['season']}")
                                fasting = "Yes" if eth_info['is_fasting_day']['is_fasting'] else "No"
                                st.write(f"**Fasting**: {fasting}")
                        
                        # Readings
                        readings = result.get("readings", {})
                        if readings:
                            st.markdown("**📜 Scripture Readings:**")
                            
                            for reading_type, reading_data in readings.items():
                                if isinstance(reading_data, dict) and reading_data.get('reference'):
                                    st.write(f"• **{reading_type.replace('_', ' ').title()}**: {reading_data['reference']}")
                                    if reading_data.get('theme'):
                                        st.caption(f"  Theme: {reading_data['theme']}")
            else:
                st.warning("No readings found. Try different search terms.")
    
    with tab3:
        st.header("📊 Liturgical Calendar View")
        
        # Calendar month view
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Date picker
            selected_date = st.date_input(
                "Select date to view:",
                datetime.date.today(),
                min_value=datetime.date(2025, 1, 1),
                max_value=datetime.date(2025, 12, 31)
            )
        
        with col2:
            view_mode = st.radio("View Mode:", ["Both Traditions", "Western Only", "Eastern Only"])
        
        if selected_date:
            # Get info for selected date
            date_info = liturgical_manager.get_daily_info(selected_date)
            
            st.subheader(f"Liturgical Information for {selected_date.strftime('%B %d, %Y')}")
            
            if view_mode in ["Both Traditions", "Western Only"]:
                with st.container():
                    st.markdown("### 🌍 Western (Roman Catholic)")
                    western = date_info['western']
                    
                    info_cols = st.columns(3)
                    with info_cols[0]:
                        st.metric("Liturgical Year", western['liturgical_year'])
                    with info_cols[1]:
                        st.metric("Season", western['season_info']['season'])
                    with info_cols[2]:
                        st.metric("Color", western['season_info']['liturgical_color'])
            
            if view_mode in ["Both Traditions", "Eastern Only"]:
                with st.container():
                    st.markdown("### ⛪ Eastern Orthodox (Ethiopian)")
                    eastern = date_info['ethiopian']
                    
                    info_cols = st.columns(3)
                    with info_cols[0]:
                        st.metric("Ethiopian Date", eastern['date']['formatted'])
                    with info_cols[1]:
                        st.metric("Season", eastern['season'])
                    with info_cols[2]:
                        fasting_status = "Fasting" if eastern['is_fasting_day']['is_fasting'] else "Non-Fasting"
                        st.metric("Fasting Status", fasting_status)
                    
                    if eastern['is_fasting_day']['is_fasting']:
                        st.info(f"**Fasting Rules**: {', '.join(eastern['is_fasting_day']['fasting_rules'])}")
    
    with tab4:
        st.header("ℹ️ About This System")
        
        st.markdown("""
        ### 🎯 Purpose
        This system provides semantic search across liturgical readings from both Western Catholic and Eastern Orthodox traditions, specifically including the Ethiopian Orthodox calendar system.
        
        ### 🔧 Features
        - **Dual Calendar Support**: Western liturgical year + Ethiopian Orthodox calendar
        - **Local Processing**: No API restrictions or content filtering
        - **Semantic Search**: Find readings by theme, not just keywords
        - **Cross-Tradition Comparison**: Explore both liturgical traditions
        - **Authentic Sources**: Ready for real OCR'd prayer book content
        
        ### 📅 Calendar Systems
        
        **Western (Roman Catholic)**:
        - 3-year lectionary cycle (A, B, C)
        - Liturgical seasons: Advent, Christmas, Lent, Easter, Ordinary Time
        - Daily Mass readings: Old Testament, Psalm, New Testament, Gospel
        
        **Eastern Orthodox (Ethiopian)**:
        - Ethiopian calendar (13 months)
        - Liturgical seasons aligned with Ethiopian traditions
        - Fasting calendar integration
        - Saints' commemorations and feast days
        
        ### 🔮 Integration with Your OCR Project
        This system is designed to work with your authentic prayer book OCR project:
        1. **Prayer embeddings** from OCR'd prayer books
        2. **Liturgical readings** from this calendar system  
        3. **Cross-references** between prayers and readings
        4. **Complete spiritual resource** for Ethiopian faithful
        """)
        
        # Statistics
        if db_data:
            st.subheader("📊 Database Statistics")
            
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            
            with stats_col1:
                st.metric("Total Days", db_data['total_days'])
            with stats_col2:
                st.metric("Western Entries", db_data['western_entries'])
            with stats_col3:
                st.metric("Eastern Entries", db_data['eastern_entries'])
        
        st.subheader("🚀 Next Steps")
        st.info("""
        1. **Add Authentic Readings**: Replace templates with real biblical texts
        2. **OCR Integration**: Connect with your prayer book OCR project
        3. **Enhanced Search**: Add cross-references between prayers and readings
        4. **Mobile App**: Create mobile-friendly version for daily use
        """)

    # Sidebar with quick navigation
    with st.sidebar:
        st.header("🗓️ Quick Navigation")
        
        # Today's quick info
        today = datetime.date.today()
        today_info = liturgical_manager.get_daily_info(today)
        
        st.subheader("Today:")
        st.write(f"📅 {today.strftime('%B %d')}")
        st.write(f"🌍 Western: {today_info['western']['season_info']['season']}")
        st.write(f"⛪ Ethiopian: {today_info['ethiopian']['season']}")
        
        # Quick date jumps
        st.subheader("⚡ Quick Dates:")
        
        # Calculate important dates
        today_year = today.year
        christmas = datetime.date(today_year, 12, 25)
        epiphany = datetime.date(today_year + 1, 1, 6) if today.month == 12 else datetime.date(today_year, 1, 6)
        
        quick_dates = [
            ("Today", today),
            ("Christmas", christmas),
            ("Epiphany", epiphany)
        ]
        
        for name, date in quick_dates:
            if st.button(f"📅 {name} ({date.strftime('%m/%d')})"):
                st.experimental_set_query_params(selected_date=date.isoformat())
        
        # Database info
        if db_data:
            st.subheader("📊 Database Info")
            st.write(f"Year: {db_data['year']}")
            st.write(f"Total Readings: {db_data['total_readings']}")
            
            tradition_breakdown = f"Western: {db_data['western_entries']}\nEastern: {db_data['eastern_entries']}"
            st.text(tradition_breakdown)

if __name__ == "__main__":
    main()
