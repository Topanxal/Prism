"""
Observability Service
"""

import logging
import sys

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("prism")

# Helper functions
def log_template_hit(**kwargs):
    logger.info(f"template_hit: {kwargs}")

def log_generation_duration(**kwargs):
    logger.info(f"generation_duration: {kwargs}")

def log_failure_classification(**kwargs):
    logger.error(f"failure_classification: {kwargs}")

def log_revision_event(**kwargs):
    logger.info(f"revision_event: {kwargs}")

# Patch LoggerAdapter-like behavior for structured logging convenience
# In a real app, use structlog or similar. Here we just wrap logging calls.
class StructuredLogger:
    def __init__(self, logger):
        self.logger = logger
    
    def info(self, msg, **kwargs):
        self.logger.info(f"{msg} {kwargs}")
        
    def error(self, msg, **kwargs):
        self.logger.error(f"{msg} {kwargs}")
        
    def warning(self, msg, **kwargs):
        self.logger.warning(f"{msg} {kwargs}")

logger = StructuredLogger(logger)
