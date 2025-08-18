import csv
import io
from typing import List, Dict, Any
from datetime import datetime, timezone

from src.domain.entities.movie import Movie
from src.domain.repositories.movie_repository import MovieRepository
from src.application.dtos.csv_dto import (
    MovieCsvRowDTO,
    CsvUploadResponseDTO
)


class ImportMoviesCsvUseCase:

    def __init__(self, movie_repository: MovieRepository):
        self.movie_repository = movie_repository

    def execute(self, csv_content: str) -> CsvUploadResponseDTO:

        errors = []
        movies_to_create = []
        movies_to_update = []
        total_rows = 0

        try:
            # Parse CSV
            csv_data = self._parse_csv(csv_content)
            total_rows = len(csv_data)

            if total_rows == 0:
                return CsvUploadResponseDTO(
                    success=False,
                    message="CSV file is empty or does not contain valid data",
                    total_rows=0,
                    created_count=0,
                    updated_count=0,
                    errors=["CSV file is empty"]
                )

            # Validar estrutura do CSV
            structure_errors = self._validate_csv_structure(csv_data)
            if structure_errors:
                return CsvUploadResponseDTO(
                    success=False,
                    message="CSV structure is invalid",
                    total_rows=total_rows,
                    created_count=0,
                    updated_count=0,
                    errors=structure_errors
                )

            # Process each row
            for row_index, row_data in enumerate(csv_data, start=1):
                try:
                    # Validate row data
                    movie_dto = MovieCsvRowDTO(**row_data)

                    # Check if movie already exists (by title)
                    existing_movie = self.movie_repository.get_by_title(
                        movie_dto.title
                    )

                    if existing_movie:
                        # Update existing movie
                        updated_movie = self._update_movie_from_dto(
                            existing_movie, movie_dto
                        )
                        movies_to_update.append(updated_movie)
                    else:
                        # Create new movie
                        new_movie = self._create_movie_from_dto(movie_dto)
                        movies_to_create.append(new_movie)

                except Exception as e:
                    error_msg = f"Linha {row_index}: {str(e)}"
                    errors.append(error_msg)

            # Save movies to database
            created_count = 0
            updated_count = 0

            try:
                # Save new movies
                for movie in movies_to_create:
                    self.movie_repository.save(movie)
                    created_count += 1

                # Update existing movies
                for movie in movies_to_update:
                    self.movie_repository.save(movie)
                    updated_count += 1

            except Exception as e:
                errors.append(f"Error saving to database: {str(e)}")

            # Prepare response
            success = len(errors) == 0
            if success:
                message = (
                    f"Import completed successfully! "
                    f"{created_count} movies created, "
                    f"{updated_count} movies updated."
                )
            else:
                message = (
                    f"Import completed with {len(errors)} error(s). "
                    f"{created_count} movies created, "
                    f"{updated_count} movies updated."
                )

            return CsvUploadResponseDTO(
                success=success,
                message=message,
                total_rows=total_rows,
                created_count=created_count,
                updated_count=updated_count,
                errors=errors
            )

        except Exception as e:
            return CsvUploadResponseDTO(
                success=False,
                message=f"Internal error: {str(e)}",
                total_rows=total_rows,
                created_count=0,
                updated_count=0,
                errors=[str(e)]
            )

    def _parse_csv(self, csv_content: str) -> List[Dict[str, Any]]:

        csv_file = io.StringIO(csv_content)
        csv_reader = csv.DictReader(csv_file)

        data = []
        for row in csv_reader:
            # Remove spaces from keys and values
            clean_row = {}
            for key, value in row.items():
                clean_key = key.strip() if key else key
                clean_value = value.strip() if value else value
                # Convert empty values to None
                if clean_value == '' or clean_value is None:
                    clean_value = None
                clean_row[clean_key] = clean_value
            data.append(clean_row)

        return data

    def _validate_csv_structure(self, csv_data: List[Dict]) -> List[str]:

        errors = []

        if not csv_data:
            errors.append("CSV does not contain data")
            return errors

        # Required columns
        required_columns = {'title'}

        # Optional columns allowed
        optional_columns = {
            'overview', 'release_date', 'poster_path', 'backdrop_path',
            'vote_average', 'vote_count', 'popularity', 'genres',
            'runtime', 'original_language', 'tmdb_id'
        }

        all_allowed_columns = required_columns | optional_columns

        # Verificar cabeçalhos
        first_row = csv_data[0]
        csv_columns = set(first_row.keys())

        # Verificar colunas obrigatórias
        missing_required = required_columns - csv_columns
        if missing_required:
            errors.append(
                f"Required columns missing: {', '.join(missing_required)}"
            )

        # Verificar colunas não permitidas
        invalid_columns = csv_columns - all_allowed_columns
        if invalid_columns:
            errors.append(
                f"Invalid columns: {', '.join(invalid_columns)}"
            )

        return errors

    def _create_movie_from_dto(self, movie_dto: MovieCsvRowDTO) -> Movie:

        return Movie(
            id=None,
            title=movie_dto.title,
            overview=movie_dto.overview,
            release_date=movie_dto.release_date,
            poster_path=movie_dto.poster_path,
            backdrop_path=movie_dto.backdrop_path,
            vote_average=movie_dto.vote_average or 0.0,
            vote_count=movie_dto.vote_count or 0,
            popularity=movie_dto.popularity or 0.0,
            genres=movie_dto.genres,
            runtime=movie_dto.runtime,
            original_language=movie_dto.original_language,
            tmdb_id=movie_dto.tmdb_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    def _update_movie_from_dto(
        self, existing_movie: Movie, movie_dto: MovieCsvRowDTO
    ) -> Movie:
        """Update an existing Movie entity with data from DTO."""

        # Update fields if provided in CSV
        if movie_dto.overview is not None:
            existing_movie.overview = movie_dto.overview
        if movie_dto.release_date is not None:
            existing_movie.release_date = movie_dto.release_date
        if movie_dto.poster_path is not None:
            existing_movie.poster_path = movie_dto.poster_path
        if movie_dto.backdrop_path is not None:
            existing_movie.backdrop_path = movie_dto.backdrop_path
        if movie_dto.vote_average is not None:
            existing_movie.vote_average = movie_dto.vote_average
        if movie_dto.vote_count is not None:
            existing_movie.vote_count = movie_dto.vote_count
        if movie_dto.popularity is not None:
            existing_movie.popularity = movie_dto.popularity
        if movie_dto.genres is not None:
            existing_movie.genres = movie_dto.genres
        if movie_dto.runtime is not None:
            existing_movie.runtime = movie_dto.runtime
        if movie_dto.original_language is not None:
            existing_movie.original_language = movie_dto.original_language
        if movie_dto.tmdb_id is not None:
            existing_movie.tmdb_id = movie_dto.tmdb_id

        existing_movie.updated_at = datetime.now(timezone.utc)

        return existing_movie

    def get_csv_template(self) -> str:
        """Return a CSV template with example data."""

        template = """title,overview,release_date,poster_path,backdrop_path,vote_average,vote_count,popularity,genres,runtime,original_language,tmdb_id
"The Matrix","A computer hacker learns that reality is a simulation","1999-03-31","/poster.jpg","/backdrop.jpg",8.7,23000,85.5,"[""Action"", ""Sci-Fi""]",136,en,603
"Inception","A thief who steals corporate secrets through dream-sharing technology","2010-07-16","/inception.jpg","/inception_backdrop.jpg",8.8,25000,90.2,"[""Action"", ""Thriller"", ""Sci-Fi""]",148,en,27205"""

        return template
