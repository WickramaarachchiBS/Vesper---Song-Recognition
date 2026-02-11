"""
Configuration settings for the audio fingerprinting system.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "VesperSongData"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "admin"
    DB_SSLMODE: str = "prefer"
    
    # Audio processing parameters
    SAMPLE_RATE: int = 44100  # Target sample rate for all audio
    
    # Spectrogram parameters
    WINDOW_SIZE: int = 4096  # FFT window size
    HOP_SIZE: int = 512  # Hop size for STFT
    
    # Peak detection parameters
    PEAK_NEIGHBORHOOD_SIZE: int = 10  # Neighborhood size for local maxima
    MIN_AMPLITUDE: float = 10.0  # Minimum amplitude threshold for peaks
    
    # Fingerprinting parameters
    FAN_VALUE: int = 5  # Number of target peaks per anchor
    MIN_TIME_DELTA: int = 0  # Minimum time difference (in frames)
    MAX_TIME_DELTA: int = 200  # Maximum time difference (in frames)
    
    # Recognition parameters
    MIN_MATCH_COUNT: int = 5  # Minimum matches required for recognition
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# Global settings instance
settings = Settings()
