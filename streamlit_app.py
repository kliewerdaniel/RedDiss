import streamlit as st
from agents.scraper import scrape_reddit
from agents.sanitizer import clean_text
from agents.theme_extractor import extract_themes
from agents.lyrics_generator import generate_lyrics
from agents.flow_refiner import refine_flow
from agents.tts_engine import text_to_speech
from agents.beat_sync import sync_to_beat
from agents.mastering import master_audio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def main():
    st.title("Reddit Diss Track Generator")
    st.write("Turn Reddit posts into diss tracks! 🎵")

    # Input section
    st.header("Input")
    reddit_url = st.text_input("Enter Reddit Post URL", placeholder="https://reddit.com/r/...")

    # Settings section
    st.header("Settings")
    
    # Style selection
    style = st.selectbox(
        "Diss Track Style",
        ["Aggressive", "Playful", "Sarcastic"],
        help="Choose the overall tone of the diss track"
    )
    
    # Sliders in columns
    col1, col2 = st.columns([1, 1])
    with col1:
        flow_complexity = st.slider(
            "Flow Complexity",
            min_value=1,
            max_value=10,
            value=5,
            help="Higher values create more complex rhyme schemes"
        )
    
    with col2:
        beat_intensity = st.slider(
            "Beat Intensity",
            min_value=1,
            max_value=10,
            value=5,
            help="Controls the energy level of the beat"
        )
    
    # Center the generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Generate Diss Track", use_container_width=True):
            if reddit_url:
                try:
                    with st.spinner("Analyzing Reddit post..."):
                        # Process flow
                        post_data = await scrape_reddit(reddit_url)
                        cleaned_data = await clean_text(post_data)
                        themes = await extract_themes(cleaned_data)
                        
                        # Generate lyrics with style parameter
                        lyrics = await generate_lyrics(themes, style)

                        # Refine flow based on complexity
                        refined_lyrics = await refine_flow(lyrics, flow_complexity)

                        # Display generated lyrics
                        st.subheader("Generated Lyrics")
                        st.text_area(
                            label="Generated lyrics content",
                            value=refined_lyrics,
                            height=200,
                            label_visibility="collapsed"
                        )

                        # Generate audio
                        with st.spinner("Generating audio..."):
                            voice = await text_to_speech(refined_lyrics)
                            # Use voice track directly since we don't have beats yet
                            synced_audio = voice
                            # Master and get final track path
                            final_track_path = await master_audio(synced_audio)

                            # Copy to temporary location
                            temp_path = "temp_diss_track.wav"
                            import shutil
                            shutil.copy2(final_track_path, temp_path)

                            # Audio playback
                            st.subheader("Listen to Your Diss Track")
                            st.audio(temp_path)

                            # Download button
                            with open(temp_path, "rb") as f:
                                st.download_button(
                                    "Download Diss Track",
                                    f,
                                    file_name="diss_track.wav",
                                    mime="audio/wav"
                                )

                            # Clean up
                            os.remove(temp_path)

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.warning("Please enter a Reddit URL")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
