"""
FastAPI routes for audio fingerprinting API.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import tempfile
import os
import logging

from app.fingerprinting.audio_utils import load_audio
from app.config import settings
from app.services.recognize import recognize_song, recognize_song_from_peaks

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


class PeakPoint(BaseModel):
    """Single peak coordinate from client-side extraction."""
    freq_idx: int = Field(..., ge=0)
    time_idx: int = Field(..., ge=0)


class PeakRecognitionRequest(BaseModel):
    """Request model for lightweight peak-based recognition."""
    schema_version: str = "1.0"
    clip_duration_seconds: Optional[float] = Field(default=None, gt=0)
    sample_rate_hz: int = settings.SAMPLE_RATE
    hop_size: int = settings.HOP_SIZE
    window_size: int = settings.WINDOW_SIZE
    peaks: List[PeakPoint] = Field(..., min_length=1)
    client_meta: Optional[Dict[str, str]] = None


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


@router.post("/identify-peaks", response_model=RecognitionResponse)
async def identify_song_from_peaks(request: PeakRecognitionRequest):
    """
    Identify a song from pre-extracted peak points.

    This endpoint is optimized for mobile clients that run peak extraction
    on-device and send only lightweight feature data.
    """
    if request.schema_version != "1.0":
        raise HTTPException(
            status_code=400,
            detail="Unsupported schema_version. Expected '1.0'."
        )

    if request.sample_rate_hz != settings.SAMPLE_RATE:
        raise HTTPException(
            status_code=400,
            detail=f"sample_rate_hz must be {settings.SAMPLE_RATE}"
        )

    if request.hop_size != settings.HOP_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"hop_size must be {settings.HOP_SIZE}"
        )

    if request.window_size != settings.WINDOW_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"window_size must be {settings.WINDOW_SIZE}"
        )

    logger.info(f"Received peak-based identification request with {len(request.peaks)} peaks")

    try:
        peaks = [(peak.freq_idx, peak.time_idx) for peak in request.peaks]
        result = recognize_song_from_peaks(peaks)

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

        return RecognitionResponse(
            success=False,
            message="No matching song found in database"
        )

    except Exception as e:
        logger.error(f"Error during peak-based recognition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
