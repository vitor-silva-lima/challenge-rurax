import { MovieCard } from "@/components/ui/movie-card";
import { PaginationControls } from "@/components/ui/pagination-controls";

interface Movie {
  id: number;
  title: string;
  overview: string;
  release_date: string;
  poster_path: string;
  backdrop_path: string;
  vote_average: number;
  vote_count: number;
  popularity: number;
  genres: string[];
  runtime: number;
  original_language: string;
  tmdb_id: number;
  year: string;
  created_at: string;
  updated_at: string;
}

interface MovieGridProps {
  movies: Movie[];
  title: string;
  onLike?: (movieId: number, liked: boolean) => void;
  likedMovies?: Set<number>;
  className?: string;
  // Pagination props
  currentPage?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
  isLoading?: boolean;
}

export function MovieGrid({ 
  movies, 
  title, 
  onLike, 
  likedMovies = new Set(), 
  className,
  currentPage,
  totalPages,
  onPageChange,
  isLoading = false
}: MovieGridProps) {
  if (movies.length === 0) {
    return (
      <section className={className}>
        <h2 className="text-2xl font-bold mb-6">{title}</h2>
        <div className="text-center py-12 text-muted-foreground">
          <p>Nenhum filme encontrado nesta seção.</p>
        </div>
      </section>
    );
  }

  return (
    <section className={className}>
      <h2 className="text-2xl font-bold mb-6 gradient-primary bg-clip-text text-transparent">
        {title}
      </h2>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-6">
        {movies.map((movie) => (
          <MovieCard
            key={movie.id}
            movie={movie}
            onLike={onLike}
            isLiked={likedMovies.has(movie.id)}
          />
        ))}
      </div>

      {/* Pagination Controls */}
      {currentPage && totalPages && onPageChange && (
        <PaginationControls
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={onPageChange}
          isLoading={isLoading}
        />
      )}
    </section>
  );
}