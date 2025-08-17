import { useState } from "react";
import { Heart } from "lucide-react";
import { cn } from "@/lib/utils";

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

interface MovieCardProps {
  movie: Movie;
  onLike?: (movieId: number, liked: boolean) => void;
  isLiked?: boolean;
  className?: string;
}

export function MovieCard({ movie, onLike, isLiked = false, className }: MovieCardProps) {
  const [liked, setLiked] = useState(isLiked);
  const [isLoading, setIsLoading] = useState(false);

  const handleLike = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    const newLikedState = !liked;
    setLiked(newLikedState);
    
    try {
      await onLike?.(movie.id, newLikedState);
    } catch (error) {
      // Revert on error
      setLiked(!newLikedState);
      console.error("Failed to update like:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={cn("cinema-card rounded-lg overflow-hidden group relative", className)}>
      {/* Movie Poster */}
      <div className="aspect-[2/3] bg-muted relative overflow-hidden">
        {movie.poster_path ? (
          <img 
            src={movie.poster_path} 
            alt={movie.title}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-muted to-muted-foreground/20 flex items-center justify-center">
            <span className="text-4xl font-bold text-muted-foreground opacity-50">
              {movie.title.charAt(0)}
            </span>
          </div>
        )}
        
        {/* Like Button Overlay */}
        <button
          onClick={handleLike}
          disabled={isLoading}
          className={cn(
            "absolute top-3 right-3 p-2 rounded-full bg-black/70 backdrop-blur-sm",
            "cinema-like-btn opacity-0 group-hover:opacity-100 transition-all duration-300",
            "hover:bg-black/90 focus:outline-none focus:ring-2 focus:ring-primary",
            liked && "liked opacity-100"
          )}
          aria-label={liked ? "Unlike movie" : "Like movie"}
        >
          <Heart 
            className={cn(
              "w-5 h-5 transition-colors",
              liked ? "fill-primary text-primary" : "text-white"
            )} 
          />
        </button>

        {/* Rating Badge */}
        {movie.vote_average > 0 && (
          <div className="absolute top-3 left-3 px-2 py-1 bg-accent text-accent-foreground rounded-md text-sm font-bold">
            ★ {movie.vote_average.toFixed(1)}
          </div>
        )}
      </div>

      {/* Movie Info */}
      <div className="p-4">
        <h3 className="font-semibold text-lg leading-tight mb-2 line-clamp-2 group-hover:text-primary transition-colors">
          {movie.title}
        </h3>
        
        <div className="flex items-center justify-between text-sm text-muted-foreground mb-2">
          <span>{movie.year}</span>
          <span className="text-xs text-muted-foreground">
            {movie.runtime}min
          </span>
        </div>
        
        {movie.genres.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {movie.genres.slice(0, 2).map((genre, index) => (
              <span key={index} className="text-xs bg-secondary px-2 py-1 rounded-full">
                {genre}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}