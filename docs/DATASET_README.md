# Dataset Directory

Place your reference audio files here for database population.

## Supported Formats
- WAV (recommended)
- MP3
- FLAC
- OGG
- M4A

## File Naming Convention

For best results, name your files descriptively:
```
Artist Name - Song Title.wav
```

Example:
```
The Beatles - Hey Jude.wav
Queen - Bohemian Rhapsody.mp3
```

## Usage

1. Add audio files to this directory
2. Run the population script:
   ```bash
   python -m app.services.populate_db
   ```

The script will automatically:
- Extract title and artist from filename (or use filename as title)
- Generate fingerprints
- Store in PostgreSQL database

## Notes

- Longer songs generate more fingerprints (better recognition)
- High quality audio files work best
- Mono conversion happens automatically
- All files are resampled to 44.1 kHz
