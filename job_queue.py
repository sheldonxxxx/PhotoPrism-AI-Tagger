from sqlalchemy import create_engine, Column, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import enum
import logging
from typing import Tuple, Union, Dict
from sqlalchemy.dialects.mysql import ENUM
import constants

Base = declarative_base()

class PhotoStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class PhotoTask(Base):
    __tablename__ = 'photo_tasks'
    
    photo_uid = Column(String(255), primary_key=True)
    worker_id = Column(String(100), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String(500), nullable=True)
    
    if constants.DP:
        status = Column(
            ENUM('pending', 'processing', 'completed', 'failed',
                name='photo_status_enum'),
            nullable=False,
            default='pending'
        )
    else:
        status = Column(String(20), nullable=False, default='pending')


class PhotoProcessor:
    def __init__(self, worker_id: str = 'worker1'):
        """
        Initialize PhotoProcessor
        
        Args:
            db_type: 'sqlite' or 'mariadb'
            db_config: For SQLite: path to db file, For MariaDB: connection config dict
            worker_id: Unique identifier for this worker
        """
        if constants.DP:
            self.db_type = 'mariadb'
        else:
            self.db_type = 'sqlite'
            
        self.worker_id = worker_id
        self.logger = logging.getLogger(__name__)
        
        if constants.DP:
            if not all([constants.DB_HOST, 
                        constants.DB_PORT, 
                        constants.DB_USER, 
                        constants.DB_PASSWORD, 
                        constants.DB_DATABASE]):
                raise ValueError("Database setting missing in DP mode!!")
            db_url = (f"mysql+pymysql://{constants.DB_USER}:{constants.DB_PASSWORD}@"
                f"{constants.DB_HOST}:{constants.DB_PORT}/{constants.DB_DATABASE}")
        else:
            db_url = f"sqlite:///{constants.DB_PATH}"
            
        self.TaskModel = PhotoTask

        self.engine = create_engine(db_url, 
                                  pool_recycle=3600 if self.db_type=='mariadb' else -1)
        
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def try_acquire_photo(self, photo_uid: str) -> bool:
        session = self.Session()
        try:
            query = session.query(self.TaskModel).filter_by(photo_uid=photo_uid)
            
            # Use FOR UPDATE if MariaDB
            if self.db_type == 'mariadb':
                query = query.with_for_update()
            
            task = query.first()
            
            if not task:
                task = self.TaskModel(
                    photo_uid=photo_uid,
                    status='pending'
                )
                session.add(task)
                session.flush()
            
            if task.status == 'completed':
                self.logger.info(f"Photo {photo_uid} already completed, will skip")
                return False
            
            if task.status == 'processing':
                self.logger.info(f"Photo {photo_uid} is being processed by worker {task.worker_id}, will skip")
                return False
            
            task.status = 'processing'
            task.worker_id = self.worker_id
            task.started_at = datetime.utcnow()
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error acquiring photo {photo_uid}: {str(e)}")
            return False
        finally:
            session.close()

    def mark_complete(self, photo_uid: str, error_message: str = None) -> bool:
        session = self.Session()
        try:
            query = session.query(self.TaskModel).filter_by(photo_uid=photo_uid)
            
            if self.db_type == 'mariadb':
                query = query.with_for_update()
                
            task = query.first()
            
            if task:
                task.completed_at = datetime.utcnow()
                if error_message:
                    task.status = 'failed'
                    task.error_message = error_message
                else:
                    task.status = 'completed'
                session.commit()
                return True
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error marking photo task complete: {str(e)}")
            return False
        finally:
            session.close()

    def cleanup_stale_tasks(self, hours: int = 24) -> None:
        """Clean up tasks that have been stuck in processing state"""
        session = self.Session()
        try:
            stale_time = datetime.utcnow() - timedelta(hours=hours)
            stale_tasks = (session.query(self.TaskModel)
                         .filter(self.TaskModel.status == 'processing',
                                self.TaskModel.started_at < stale_time)
                         .all())
            
            for task in stale_tasks:
                task.status = 'pending'
                task.worker_id = None
                task.started_at = None
            
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error cleaning up stale tasks: {str(e)}")
        finally:
            session.close()

# Usage examples
def sqlite_example():
    # SQLite configuration
    db_path = "photo_tasks.db"
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create processor instance for SQLite
    processor = PhotoProcessor(db_type='sqlite', db_config=db_path, worker_id="worker1")
    
    # Process a photo
    success, message = processor.process_photo("photo123")
    print(f"SQLite Result: {message}")

def mariadb_example():
    # MariaDB configuration
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'your_username',
        'password': 'your_password',
        'database': 'photo_db'
    }
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create processor instance for MariaDB
    processor = PhotoProcessor(db_type='mariadb', db_config=db_config, worker_id="worker1")
    
    # Process a photo
    success, message = processor.process_photo("photo123")
    print(f"MariaDB Result: {message}")

if __name__ == "__main__":
    # Choose which example to run
    sqlite_example()
    # mariadb_example()