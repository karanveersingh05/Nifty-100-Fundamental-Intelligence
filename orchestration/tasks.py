import sys
import os
import logging
import importlib
from orchestration.celery_app import app

# Ensure the root project directory is in the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importing dynamically because of the numeric prefixes in ETL scripts
extract_module = importlib.import_module("etl.01_extract_from_mysql")
clean_module = importlib.import_module("etl.02_clean_and_transform")
load_module = importlib.import_module("etl.03_load_to_warehouse")
scoring_module = importlib.import_module("analytics.scoring_engine")

@app.task(bind=True)
def run_full_etl_pipeline(self):
    """
    Executes Extract, Clean, and Load sequentially.
    """
    logger.info("Starting the full ETL pipeline.")
    
    # wrapped this in a try-except because source data can be wildly unpredictable and I don't want the worker to die
    try:
        logger.info("Step 1: Extract")
        # Change working directory to project root so relative paths in ETL scripts work correctly
        os.chdir(project_root)
        if os.path.exists(extract_module.SQL_DUMP_FILE):
            extract_module.extract_from_sql()
        else:
            extract_module.extract_from_xlsx()
            
        logger.info("Step 2: Clean and Transform")
        clean_module.main()
        
        logger.info("Step 3: Load to Warehouse")
        load_module.load_data()
        
        logger.info("ETL pipeline completed successfully.")
        
        # chaining the ML scorer to the ETL-no point scoring stale data
        logger.info("Chaining ML scoring task...")
        run_ml_scoring.delay()
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}", exc_info=True)

@app.task(bind=True)
def run_ml_scoring(self):
    """
    Runs the CompanyScorer after the ETL finishes.
    """
    logger.info("Starting the ML scoring engine.")
    try:
        os.chdir(project_root)
        scoring_module.run()
        logger.info("ML scoring engine completed successfully.")
    except Exception as e:
        logger.error(f"ML scoring engine failed: {str(e)}", exc_info=True)
