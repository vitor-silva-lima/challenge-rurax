import { useState, useEffect } from "react";
import { AuthForm } from "@/components/ui/auth-form";
import { Header } from "@/components/dashboard/header";
import { MovieGrid } from "@/components/dashboard/movie-grid";
import { apiClient, type Movie, type MovieListResponse, type RecommendationAlgorithm, type CsvUploadResponse } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Loader2 } from "lucide-react";

export function MovieApp() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authLoading, setAuthLoading] = useState(false);
  const [movies, setMovies] = useState<Movie[]>([]);
  const [moviesPage, setMoviesPage] = useState(1);
  const [moviesTotalPages, setMoviesTotalPages] = useState(1);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<RecommendationAlgorithm>('popularity');
  const [recommendations, setRecommendations] = useState<Movie[]>([]);
  const [recommendationsPage, setRecommendationsPage] = useState(1);
  const [recommendationsTotalPages, setRecommendationsTotalPages] = useState(1);
  const { toast } = useToast();

  // Configurar callback de logout automático
  useEffect(() => {
    apiClient.setLogoutCallback(() => {
      setIsAuthenticated(false);
      setMovies([]);
      setRecommendations([]);
      
      toast({
        title: "Sessão expirada",
        description: "Sua sessão expirou. Faça login novamente para continuar.",
        variant: "destructive"
      });
    });
  }, [toast]);

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
      const moviesResponse = await apiClient.getMovies(page, 10);
      setMovies(moviesResponse.movies);
      setMoviesPage(moviesResponse.page);
      setMoviesTotalPages(moviesResponse.total_pages);

      // Load initial recommendations (only on first load)
      if (page === 1) {
        await loadRecommendations(selectedAlgorithm, 1);
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

  const loadRecommendations = async (algorithm: RecommendationAlgorithm, page: number = 1) => {
    try {
      const recommendationsResponse = await apiClient.getRecommendations(algorithm, page, 10);
      setRecommendations([...recommendationsResponse.movies]); // Force re-render with spread operator
      setRecommendationsPage(recommendationsResponse.page);
      setRecommendationsTotalPages(recommendationsResponse.total_pages);
    } catch (error) {
      console.error(`Failed to load ${algorithm} recommendations:`, error);
      setRecommendations([]);
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
    setRecommendations([]);
    
    toast({
      title: "Sessão encerrada",
      description: "Volte em breve para descobrir mais filmes!"
    });
  };

  const handleCsvUploadSuccess = async (result: CsvUploadResponse) => {
    // Recarregar dados após upload bem-sucedido
    try {
      await loadMovieData(1); // Voltar para primeira página
      await loadRecommendations(selectedAlgorithm, 1); // Recarregar recomendações
    } catch (error) {
      console.error("Erro ao recarregar dados após upload:", error);
    }
  };

  const handleLike = async (movieId: number, liked: boolean) => {
    try {
      const response = await apiClient.toggleLike(movieId);
      
      // Show feedback to user
      if (response.is_liked) {
        toast({
          title: "Filme curtido!",
          description: "Adicionado às suas preferências"
        });
      } else {
        toast({
          title: "Curtida removida",
          description: "Removido das suas preferências"
        });
      }

      // Refresh both listings after like/unlike
      setTimeout(async () => {
        try {
          // Refresh "🎬 Descobrir Filmes" list on current page
          const moviesResponse = await apiClient.getMovies(moviesPage, 10);
          setMovies([...moviesResponse.movies]); // Force re-render with spread operator
          
          // Refresh recommendations list on current page (only if we have recommendations)
          if (recommendations.length > 0 || recommendationsPage > 0) {
            await loadRecommendations(selectedAlgorithm, recommendationsPage);
          }
        } catch (error) {
          console.error("Failed to refresh data after like:", error);
        }
      }, 500);
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
      <Header onLogout={handleLogout} onCsvUploadSuccess={handleCsvUploadSuccess} />
      
      <main className="container mx-auto px-4 py-8 space-y-12">
        {/* Informational Banner */}
        <div className="bg-gradient-to-r from-blue-600/10 to-purple-600/10 border border-blue-500/20 rounded-lg p-6 mb-8">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-foreground mb-2">
                💡 Como melhorar suas recomendações
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                Curta os filmes que você gosta clicando no coração ❤️. Quanto mais filmes você curtir, 
                melhor nossos algoritmos de recomendação entenderão seu gosto e poderão sugerir filmes 
                personalizados para você e outros usuários com preferências similares.
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                  🎯 Recomendações personalizadas
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                  🤝 Filtragem colaborativa
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                  📊 Análise de conteúdo
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* All Movies */}
        <MovieGrid
          movies={movies}
          title="🎬 Descobrir Filmes"
          onLike={handleLike}
          currentPage={moviesPage}
          totalPages={moviesTotalPages}
          onPageChange={handlePageChange}
          isLoading={isLoading}
        />

        {/* Algorithm Selection */}
        <div className="flex items-center gap-4 mb-6">
          <label htmlFor="algorithm-select" className="text-lg font-semibold text-foreground">
            Algoritmo de Recomendação:
          </label>
          <select
            id="algorithm-select"
            value={selectedAlgorithm}
            onChange={(e) => {
              const algorithm = e.target.value as RecommendationAlgorithm;
              setSelectedAlgorithm(algorithm);
              loadRecommendations(algorithm, 1);
            }}
            className="px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="popularity">🔥 Mais Populares</option>
            <option value="collaborative">✨ Filtragem Colaborativa</option>
            <option value="content_based">🎯 Baseado em Conteúdo</option>
          </select>
        </div>

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <MovieGrid
            movies={recommendations}
            title={`Recomendações - ${selectedAlgorithm === 'popularity' ? '🔥 Mais Populares' : selectedAlgorithm === 'collaborative' ? '✨ Filtragem Colaborativa' : '🎯 Baseado em Conteúdo'}`}
            onLike={handleLike}
            currentPage={recommendationsPage}
            totalPages={recommendationsTotalPages}
            onPageChange={(page) => loadRecommendations(selectedAlgorithm, page)}
            isLoading={isLoading}
          />
        )}
      </main>
    </div>
  );
}