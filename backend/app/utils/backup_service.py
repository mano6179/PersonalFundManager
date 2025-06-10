import os
import subprocess
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MongoBackupService:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    async def create_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"
            
            # Using mongodump for backup
            command = [
                "mongodump",
                f"--uri={os.getenv('MONGODB_URL')}",
                f"--out={backup_path}"
            ]
            
            process = subprocess.run(command, capture_output=True, text=True)
            
            if process.returncode == 0:
                logger.info(f"Backup created successfully at {backup_path}")
                return True
            else:
                logger.error(f"Backup failed: {process.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Backup error: {str(e)}")
            return Falses