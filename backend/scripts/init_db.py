#!/usr/bin/env python3
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# flake8: noqa: E402
from sqlalchemy import text
from src.infrastructure.database.connection import engine, SessionLocal
from src.infrastructure.database.models import MovieModel, UserModel, LikeModel
from src.infrastructure.config.logging import configure_logging, get_logger


logger = get_logger(__name__)


def create_tables():
    """Create all tables in the database."""
    try:
        # Import all models to register them
        from src.infrastructure.database.connection import Base

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


def check_database_connection() -> bool:
    """Check if the database connection is working."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified successfully")
        return True
    except Exception as e:
        logger.error(f"Error verifying database connection: {e}")
        return False


def load_sample_data():
    """Load sample data."""
    db = SessionLocal()

    try:
        # Check if movies already exist
        movie_count = db.query(MovieModel).count()

        if movie_count == 0:
            logger.info("Loading sample movies...")

            sample_movies = [
                MovieModel(
                    title="O Poderoso Chefão",
                    overview="""
                    A história da família Corleone,
                    uma das mais poderosas famílias da máfia italiana.
                    """,
                    release_date="1972-03-24",
                    vote_average=9.2,
                    vote_count=1500000,
                    popularity=95.5,
                    genres='["Crime", "Drama"]',
                    runtime=175,
                    original_language="en"
                ),
                MovieModel(
                    title="Cidade de Deus",
                    overview="""
                    A história de crianças e adolescentes
                    de uma favela carioca.
                    """,
                    release_date="2002-08-30",
                    vote_average=8.6,
                    vote_count=750000,
                    popularity=88.2,
                    genres='["Crime", "Drama"]',
                    runtime=130,
                    original_language="pt"
                ),
                MovieModel(
                    title="Pulp Fiction",
                    overview="""
                    Histórias entrelaçadas de crime em Los Angeles.
                    """,
                    release_date="1994-10-14",
                    vote_average=8.9,
                    vote_count=2000000,
                    popularity=92.1,
                    genres='["Crime", "Drama"]',
                    runtime=154,
                    original_language="en"
                ),
                MovieModel(
                    title="Matrix",
                    overview="""
                    Um hacker descobre a verdade sobre sua realidade.
                    """,
                    release_date="1999-03-31",
                    vote_average=8.7,
                    vote_count=1800000,
                    popularity=89.3,
                    genres='["Ação", "Ficção científica"]',
                    runtime=136,
                    original_language="en"
                ),
                MovieModel(
                    title="Forrest Gump",
                    overview="A vida extraordinária de um homem comum.",
                    release_date="1994-07-06",
                    vote_average=8.8,
                    vote_count=1900000,
                    popularity=91.7,
                    genres='["Drama", "Romance"]',
                    runtime=142,
                    original_language="en"
                )
            ]

            db.add_all(sample_movies)
            db.commit()

            logger.info(f"Loaded {len(sample_movies)} sample movies")
        else:
            logger.info("Movies already exist in the database")

    except Exception as e:
        logger.error(f"Error loading initial data: {e}")
        db.rollback()
    finally:
        db.close()


def init_db():
    """Initialize the database."""
    configure_logging()
    logger.info("Initializing database...")

    # Check connection
    if not check_database_connection():
        raise Exception("Unable to connect to the database")

    # Create tables
    create_tables()

    # Load initial data
    load_sample_data()

    logger.info("Database initialized successfully")


if __name__ == "__main__":
    print("Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
