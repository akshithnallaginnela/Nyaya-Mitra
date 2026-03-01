"""
Setup script for downloading and installing NLP models.
Run this script after installing requirements.txt to set up spaCy models.
"""
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def install_spacy_model(model_name: str) -> bool:
    """
    Install a spaCy model.
    
    Args:
        model_name: Name of the spaCy model to install
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Installing spaCy model: {model_name}")
        subprocess.check_call([
            sys.executable, "-m", "spacy", "download", model_name
        ])
        logger.info(f"Successfully installed {model_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {model_name}: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("Starting NLP models setup...")
    
    # Install English spaCy model
    success = install_spacy_model("en_core_web_sm")
    
    if success:
        logger.info("✓ NLP models setup completed successfully")
        logger.info("\nNote: IndicNLP models for Hindi and regional languages")
        logger.info("will be configured when the indic-nlp-library is integrated.")
    else:
        logger.error("✗ NLP models setup failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
