from fastapi import (
    APIRouter, Depends, HTTPException, status, UploadFile, File
)
from fastapi.responses import PlainTextResponse

from src.application.use_cases.movies.import_movies_csv_use_case import (
    ImportMoviesCsvUseCase
)
from src.application.dtos.csv_dto import CsvUploadResponseDTO
from src.infrastructure.api.dependencies.csv_dependencies import (
    get_import_movies_csv_use_case
)
from src.infrastructure.api.dependencies.auth_dependencies import (
    get_current_user
)
from src.domain.entities.user import User

router = APIRouter()


@router.post(
    path="/upload",
    response_model=CsvUploadResponseDTO,
    summary="Upload CSV file to import movies",
    description="Upload a CSV file to import movies into the database. "
    "If a movie with the same title already exists, it will be updated. "
    "The CSV must have the correct structure with required columns."
)
async def upload_movies_csv(
    file: UploadFile = File(..., description="CSV file with movies data"),
    current_user: User = Depends(get_current_user),
    use_case: ImportMoviesCsvUseCase = Depends(get_import_movies_csv_use_case)
):

    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required"
        )

    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted"
        )

    # Validate file size (maximum 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size: 10MB"
        )

    try:
        # Read file content
        content = await file.read()

        # Try to decode as UTF-8
        try:
            csv_content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Try with latin-1 encoding as fallback
                csv_content = content.decode('latin-1')
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File encoding not supported. "
                    "Use UTF-8 or Latin-1"
                )

        # Validate if file is not empty
        if not csv_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file is empty"
            )

        # Process CSV
        result = use_case.execute(csv_content)

        # If there are critical errors, return error status
        if (
            not result.success
            and result.created_count == 0
            and result.updated_count == 0
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing file: {str(e)}"
        )


@router.get(
    path="/template",
    response_class=PlainTextResponse,
    summary="Download CSV template",
    description="Download a CSV template with example data for movie import"
)
def download_csv_template(
    current_user: User = Depends(get_current_user),
    use_case: ImportMoviesCsvUseCase = Depends(get_import_movies_csv_use_case)
):

    try:
        template = use_case.get_csv_template()

        return PlainTextResponse(
            content=template,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; \
                    filename=movies_template.csv"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating template: {str(e)}"
        )


@router.get(
    path="/format-info",
    summary="Get CSV format information",
    description="Get detailed information about the CSV format requirements"
)
def get_csv_format_info(
    current_user: User = Depends(get_current_user)
):

    return {
        "required_columns": ["title"],
        "optional_columns": [
            "overview",
            "release_date",
            "poster_path",
            "backdrop_path",
            "vote_average",
            "vote_count",
            "popularity",
            "genres",
            "runtime",
            "original_language",
            "tmdb_id"
        ],
        "column_descriptions": {
            "title": "Movie title (required, string)",
            "overview": "Movie overview (optional, string)",
            "release_date": "Release date in format YYYY-MM-DD (optional)",
            "poster_path": "Poster path (optional, string)",
            "backdrop_path": "Backdrop path (optional, string)",
            "vote_average": "Average vote from 0.0 to 10.0 (optional, float)",
            "vote_count": "Number of votes, >= 0 (optional, int)",
            "popularity": "Popularity, >= 0.0 (optional, float)",
            "genres": "Genres in JSON array, ex: \
                [\"Action\", \"Comedy\"] (optional)",
            "runtime": "Runtime in minutes, >= 0 (optional, int)",
            "original_language": "Original language (optional, string)",
            "tmdb_id": "TMDB ID, >= 0 (optional, int)"
        },
        "format_rules": [
            "File must be CSV with UTF-8 or Latin-1 encoding",
            "First line must contain the column headers",
            "Title is required and cannot be empty",
            "Date must be in format YYYY-MM-DD",
            "Genres must be a valid JSON array",
            "If a movie with the same title already exists, \
                it will be updated",
            "Maximum file size: 10MB"
        ],
        "example_row": {
            "title": "The Matrix",
            "overview": "A computer hacker learns that \
                reality is a simulation",
            "release_date": "1999-03-31",
            "vote_average": "8.7",
            "vote_count": "23000",
            "popularity": "85.5",
            "genres": "[\"Action\", \"Sci-Fi\"]",
            "runtime": "136",
            "original_language": "en",
            "tmdb_id": "603"
        }
    }
