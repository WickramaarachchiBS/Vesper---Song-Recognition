"""
FastAPI routes for audio fingerprinting API.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import tempfile
import os
import logging

from app.fingerprinting.audio_utils import load_audio
from app.services.recognize import recognize_song

logger = logging.getLogger(__name__)

router = APIRouter()


class RecognitionResponse(BaseModel):
    """Response model for song recognition."""
    success: bool
    song_id: int = None
    title: str = None
    artist: str = None
    match_count: int = None
    confidence: float = None
    total_fingerprints: int = None
    message: str = None


@router.post("/identify", response_model=RecognitionResponse)
async def identify_song(audio_file: UploadFile = File(...)):
    """
    Identify a song from uploaded audio file.
    
    Accepts WAV, MP3, FLAC, OGG, M4A files.
    
    Args:
        audio_file: Uploaded audio file
    
    Returns:
        RecognitionResponse with song metadata and confidence score
    """
    logger.info(f"Received identification request: {audio_file.filename}")
    
    # Validate file extension
    allowed_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
    file_ext = os.path.splitext(audio_file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Save uploaded file to temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_path = temp_file.name
            content = await audio_file.read()
            temp_file.write(content)
        
        logger.info(f"Saved temporary file: {temp_path}")
        
        # Load audio
        audio_data, sample_rate = load_audio(temp_path)
        
        # Recognize song
        result = recognize_song(audio_data, sample_rate)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        if result:
            return RecognitionResponse(
                success=True,
                song_id=result['song_id'],
                title=result['title'],
                artist=result['artist'],
                match_count=result['match_count'],
                confidence=result['confidence'],
                total_fingerprints=result['total_fingerprints']
            )
        else:
            return RecognitionResponse(
                success=False,
                message="No matching song found in database"
            )
    
    except Exception as e:
        logger.error(f"Error during recognition: {e}")
        
        # Clean up temporary file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
