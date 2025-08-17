import { useState, useEffect } from "react";
import { AuthForm } from "@/components/ui/auth-form";
import { Header } from "@/components/dashboard/header";
import { MovieGrid } from "@/components/dashboard/movie-grid";
import { apiClient, type Movie, type MovieListResponse, type RecommendationAlgorithm } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Loader2 } from "lucide-react";

export function MovieApp() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authLoading, setAuthLoading] = useState(false);
  const [movies, setMovies] = useState<Movie[]>([]);
  const [moviesPage, setMoviesPage] = useState(1);
  const [moviesTotalPages, setMoviesTotalPages] = useState(1);
  const [recommendations, setRecommendations] = useState<{
    popularity: Movie[];
    collaborative: Movie[];
    content_based: Movie[];
  }>({
    popularity: [],
    collaborative: [],
    content_based: []
  });
  const [likedMovies, setLikedMovies] = useState<Set<number>>(new Set());
  const { toast } = useToast();

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (apiClient.isAuthenticated()) {
          setIsAuthenticated(true);
          await loadMovieData();
        } else {
          setIsLoading(false);
        }
      } catch (error) {
        console.error("Error checking authentication:", error);
        apiClient.logout();
        setIsAuthenticated(false);
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const loadMovieData = async (page: number = 1) => {
    try {
      setIsLoading(true);
      
      // Load movies with pagination
      const moviesResponse = await apiClient.getMovies(page, 20);
      setMovies(moviesResponse.movies);
      setMoviesPage(moviesResponse.page);
      setMoviesTotalPages(moviesResponse.total_pages);

      // Load recommendations for all algorithms (only on first load)
      if (page === 1) {
        const [popularRecs, collaborativeRecs, contentRecs] = await Promise.all([
          apiClient.getRecommendations('popularity', 1, 20).catch(() => ({ movies: [] as Movie[] })),
          apiClient.getRecommendations('collaborative', 1, 20).catch(() => ({ movies: [] as Movie[] })),
          apiClient.getRecommendations('content_based', 1, 20).catch(() => ({ movies: [] as Movie[] }))
        ]);

        setRecommendations({
          popularity: popularRecs.movies,
          collaborative: collaborativeRecs.movies,
          content_based: contentRecs.movies
        });
      }

      // Extract liked movies from recommendations to set initial state
      // Since we don't have a dedicated "liked movies" endpoint, we'll track them locally
      if (page === 1) {
        setLikedMovies(new Set());
      }
      
    } catch (error) {
      console.error("Failed to load movie data:", error);
      toast({
        title: "Erro ao carregar filmes",
        description: "Por favor, tente atualizar a página",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePageChange = async (page: number) => {
    await loadMovieData(page);
    // Scroll to top when changing pages
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLogin = async (username: string, password: string) => {
    try {
      setAuthLoading(true);
      const response = await apiClient.login(username, password);
      
      setIsAuthenticated(true);
      
      toast({
        title: "Bem-vindo de volta!",
        description: "Você fez login com sucesso."
      });

      await loadMovieData();
    } catch (error) {
      toast({
        title: "Falha no login",
        description: error instanceof Error ? error.message : "Verifique suas credenciais",
        variant: "destructive"
      });
    } finally {
      setAuthLoading(false);
    }
  };

  const handleRegister = async (email: string, username: string, password: string) => {
    try {
      setAuthLoading(true);
      await apiClient.register(email, username, password);
      
      toast({
        title: "Conta criada!",
        description: "Bem-vindo ao Rurax - CineMatch. Faça login para começar!"
      });
    } catch (error) {
      toast({
        title: "Falha no registro",
        description: error instanceof Error ? error.message : "Tente novamente",
        variant: "destructive"
      });
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    apiClient.logout();
    setIsAuthenticated(false);
    setMovies([]);
    setRecommendations({
      popularity: [],
      collaborative: [],
      content_based: []
    });
    setLikedMovies(new Set());
    
    toast({
      title: "Sessão encerrada",
      description: "Volte em breve para descobrir mais filmes!"
    });
  };

  const handleLike = async (movieId: number, liked: boolean) => {
    try {
      const response = await apiClient.toggleLike(movieId);
      
      if (response.is_liked) {
        setLikedMovies(prev => new Set([...prev, movieId]));
        toast({
          title: "Filme curtido!",
          description: "Adicionado às suas preferências"
        });
      } else {
        setLikedMovies(prev => {
          const newSet = new Set(prev);
          newSet.delete(movieId);
          return newSet;
        });
        toast({
          title: "Curtida removida",
          description: "Removido das suas preferências"
        });
      }

      // Refresh collaborative recommendations after like/unlike
      setTimeout(async () => {
        try {
          const newCollaborativeRecs = await apiClient.getRecommendations('collaborative', 1, 20);
          setRecommendations(prev => ({
            ...prev,
            collaborative: newCollaborativeRecs.movies
          }));
        } catch (error) {
          console.error("Failed to refresh recommendations:", error);
        }
      }, 1000);
    } catch (error) {
      toast({
        title: "Falha ao atualizar preferência",
        description: "Tente novamente",
        variant: "destructive"
      });
      throw error; // Re-throw to trigger revert in MovieCard
    }
  };

  // Show auth form if not authenticated
  if (!isAuthenticated) {
    return (
      <AuthForm
        onLogin={handleLogin}
        onRegister={handleRegister}
        isLoading={authLoading}
      />
    );
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen cinema-backdrop flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Carregando sua experiência cinematográfica...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen cinema-backdrop">
      <Header onLogout={handleLogout} />
      
      <main className="container mx-auto px-4 py-8 space-y-12">
        {/* All Movies */}
        <MovieGrid
          movies={movies}
          title="🎬 Descobrir Filmes"
          onLike={handleLike}
          likedMovies={likedMovies}
          currentPage={moviesPage}
          totalPages={moviesTotalPages}
          onPageChange={handlePageChange}
          isLoading={isLoading}
        />

        {/* Popularity-based Recommendations */}
        {recommendations.popularity.length > 0 && (
          <MovieGrid
            movies={recommendations.popularity}
            title="🔥 Mais Populares"
            onLike={handleLike}
            likedMovies={likedMovies}
          />
        )}

        {/* Collaborative Filtering Recommendations */}
        {recommendations.collaborative.length > 0 && (
          <MovieGrid
            movies={recommendations.collaborative}
            title="✨ Recomendados para Você (Colaborativo)"
            onLike={handleLike}
            likedMovies={likedMovies}
          />
        )}

        {/* Content-based Recommendations */}
        {recommendations.content_based.length > 0 && (
          <MovieGrid
            movies={recommendations.content_based}
            title="🎯 Baseado em Conteúdo"
            onLike={handleLike}
            likedMovies={likedMovies}
          />
        )}
      </main>
    </div>
  );
}