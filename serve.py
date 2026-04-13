from waitress import serve
from app import app
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('waitress')

if __name__ == "__main__":
    host = '0.0.0.0'
    port = 8003
    threads = 1  # Sesuaikan dengan beban server
    
    logger.info(f"Starting production server on http://{host}:{port}")
    serve(app, host=host, port=port, threads=threads)
