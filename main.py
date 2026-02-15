"""
Analytics Service - Main Entry Point.

HOI (Human-Object Interaction) Engagement Detection Service.
Uses Depth Anything v2 for depth-aware interaction detection.

Optimized async pipeline for real-time events.
No multiprocessing - direct async processing for minimal latency.

Examples
--------
Run the service from command line::

    python main.py
"""

import asyncio
import signal
from typing import Optional

# Use uvloop for better async performance (2-4x faster)
try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    _UVLOOP_ENABLED = True
except ImportError:
    _UVLOOP_ENABLED = False

from utils.logger import setup_logger

setup_logger()

from core import configs
from analytics_service import EngagementAnalyticsService
from services import ensure_topics_exist
from utils import logger

# Try to import YOLO (optional dependency)
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("ultralytics not available. Object detection will be disabled.")

# Try to import depth estimation (for HOI detection)
try:
    import torch
    DEPTH_AVAILABLE = torch.cuda.is_available() or True  # CPU fallback available
except ImportError:
    DEPTH_AVAILABLE = False
    logger.warning("torch not available. Depth estimation will be disabled.")





async def main() -> None:
    """
    Main entry point for the HOI Engagement Analytics Service.

    Initializes logging, ensures Kafka topics exist, sets up signal
    handlers, and runs the service until shutdown.

    Features:
    - Depth Anything v2 for depth estimation
    - Depth-aware HOI detection (HOLDING, TOUCHING, USING, NEAR, TALKING, etc.)
    - YOLO for object detection
    - Multi-camera support
    - Temporal smoothing for stable detections

    Raises
    ------
    Exception
        Re-raises any unhandled service exception.
    """
    logger.info("=" * 60)
    logger.info("HOI Engagement Analytics Service")
    logger.info("=" * 60)
    logger.info(f"Input topic: {configs.kafka_topic_input}")
    logger.info(f"Output topic: {configs.kafka_topic_output}")
    logger.info("Architecture: Direct Async Pipeline (no multiprocessing)")
    logger.info(f"Event loop: {'uvloop (high-performance)' if _UVLOOP_ENABLED else 'asyncio (default)'}")
    logger.info(f"HOI Detection: {'Enabled' if configs.hoi_enabled else 'Disabled'}")
    if configs.hoi_enabled:
        logger.info(f"Depth Model: {configs.hoi_depth_model_variant}")
        logger.info(f"Depth Device: {configs.hoi_depth_model_device}")
    logger.info("=" * 60)

    # Ensure required Kafka topics exist
    logger.info("Ensuring Kafka topics exist...")
    try:
        await ensure_topics_exist([
            configs.kafka_topic_input,
            configs.kafka_topic_output,
        ])
        logger.info("✓ Kafka topics verified/created")
    except Exception as e:
        logger.error(f"Failed to connect to Kafka at {configs.kafka_bootstrap_servers}")
        logger.error(f"Error: {e}")
        logger.error("Please ensure Kafka is running and accessible.")
        logger.error("You can:")
        logger.error("  1. Start Kafka: docker-compose up -d (if using Docker)")
        logger.error("  2. Update config.yaml with correct Kafka bootstrap servers")
        logger.error("  3. Check Kafka is running: kafka-topics.sh --list --bootstrap-server localhost:9092")
        raise

    # Create and run service
    service = EngagementAnalyticsService()

    # Setup signal handlers
    loop = asyncio.get_event_loop()

    def signal_handler():
        """Handle shutdown signals gracefully."""
        logger.info("Received shutdown signal")
        asyncio.create_task(service.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            pass

    try:
        await service.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except NotImplementedError as nie:
        logger.exception(f"Not Implemented exception. {nie}")
    except Exception as e:
        logger.exception(f"Service error: {e}")
        raise
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
