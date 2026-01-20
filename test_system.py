"""
Test script to verify the fingerprinting pipeline.
Run this after setting up the database to test the system.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.fingerprinting.audio_utils import load_audio
from app.fingerprinting.hashing import fingerprint_audio
from app.models.song import Song
from app.models.fingerprint import Fingerprint
from app.database import db


def test_fingerprinting():
    """Test the fingerprinting pipeline."""
    print("=" * 60)
    print("Audio Fingerprinting System - Test Script")
    print("=" * 60)
    
    # Test 1: Database connection
    print("\n[1] Testing database connection...")
    try:
        songs = Song.get_all()
        print(f"✓ Database connected. Found {len(songs)} songs.")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return
    
    # Test 2: Check for audio files in dataset
    print("\n[2] Checking dataset directory...")
    dataset_dir = "dataset"
    if not os.path.exists(dataset_dir):
        print(f"✗ Dataset directory not found: {dataset_dir}")
        print("  Please create 'dataset/' and add WAV files.")
        return
    
    audio_files = [f for f in os.listdir(dataset_dir) 
                   if f.endswith(('.wav', '.mp3', '.flac'))]
    
    if not audio_files:
        print(f"✗ No audio files found in {dataset_dir}")
        print("  Please add WAV, MP3, or FLAC files to the dataset directory.")
        return
    
    print(f"✓ Found {len(audio_files)} audio files:")
    for f in audio_files[:5]:  # Show first 5
        print(f"  - {f}")
    if len(audio_files) > 5:
        print(f"  ... and {len(audio_files) - 5} more")
    
    # Test 3: Test fingerprinting on first file
    print(f"\n[3] Testing fingerprinting on: {audio_files[0]}")
    test_file = os.path.join(dataset_dir, audio_files[0])
    
    try:
        # Load audio
        print("  Loading audio...")
        audio_data, sample_rate = load_audio(test_file, duration=30)  # First 30 seconds
        print(f"  ✓ Loaded {len(audio_data)} samples at {sample_rate} Hz")
        
        # Generate fingerprints
        print("  Generating fingerprints...")
        fingerprints = fingerprint_audio(audio_data, sample_rate)
        print(f"  ✓ Generated {len(fingerprints)} fingerprints")
        
        if fingerprints:
            print(f"  Sample fingerprint: {fingerprints[0][0][:16]}... @ {fingerprints[0][1]:.2f}s")
        
    except Exception as e:
        print(f"  ✗ Fingerprinting failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 4: Database statistics
    print("\n[4] Database statistics:")
    try:
        total_songs = len(Song.get_all())
        total_fingerprints = Fingerprint.get_total_count()
        
        print(f"  Total songs: {total_songs}")
        print(f"  Total fingerprints: {total_fingerprints}")
        
        if total_songs > 0:
            avg_fingerprints = total_fingerprints / total_songs
            print(f"  Average fingerprints per song: {avg_fingerprints:.0f}")
    except Exception as e:
        print(f"  ✗ Failed to get statistics: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print("✓ Database connection: OK")
    print("✓ Audio loading: OK")
    print("✓ Fingerprint generation: OK")
    print("\nNext steps:")
    print("1. Run: python -m app.services.populate_db")
    print("2. Start API: uvicorn app.main:app --reload")
    print("3. Test recognition: POST /api/identify")
    print("=" * 60)


if __name__ == "__main__":
    test_fingerprinting()
