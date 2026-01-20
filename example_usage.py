"""
Example script showing how to use the fingerprinting system programmatically.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.fingerprinting.audio_utils import load_audio
from app.services.recognize import recognize_song


def recognize_from_file(audio_file_path: str):
    """
    Recognize a song from an audio file.
    
    Args:
        audio_file_path: Path to audio file to identify
    """
    print(f"Loading audio from: {audio_file_path}")
    
    # Load audio
    audio_data, sample_rate = load_audio(audio_file_path)
    
    print(f"Audio loaded: {len(audio_data)} samples at {sample_rate} Hz")
    print(f"Duration: {len(audio_data) / sample_rate:.2f} seconds")
    
    # Recognize song
    print("\nRecognizing song...")
    result = recognize_song(audio_data, sample_rate)
    
    # Display results
    if result:
        print("\n" + "=" * 60)
        print("🎵 SONG IDENTIFIED!")
        print("=" * 60)
        print(f"Title:      {result['title']}")
        print(f"Artist:     {result['artist']}")
        print(f"Confidence: {result['confidence']:.2f}%")
        print(f"Matches:    {result['match_count']} / {result['total_fingerprints']}")
        print("=" * 60)
    else:
        print("\n❌ No matching song found in database.")
        print("Make sure you have populated the database with reference songs.")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python example_usage.py <audio_file>")
        print("\nExample:")
        print("  python example_usage.py query_audio.wav")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"Error: File not found: {audio_file}")
        sys.exit(1)
    
    recognize_from_file(audio_file)


if __name__ == "__main__":
    main()
