// API client for the movie recommendation backend

const API_BASE_URL = "https://challengerurax-backend-phgfsd-b5e01d-212-85-11-41.traefik.me/api/v1";

// Simplified auth - no user info needed, just token validation

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
  is_liked: boolean;
}

interface MovieListResponse {
  movies: Movie[];
  total: number;
  page: number;
  total_pages: number;
  per_page: number;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
}

interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

interface LoginRequest {
  username: string;
  password: string;
}

interface LikeToggleRequest {
  movie_id: number;
}

interface LikeToggleResponse {
  movie_id: number;
  is_liked: boolean;
  like: {
    id: number;
    user_id: number;
    movie_id: number;
    created_at: string;
  } | null;
}

interface CsvUploadResponse {
  success: boolean;
  message: string;
  total_rows: number;
  created_count: number;
  updated_count: number;
  errors: string[];
}

interface ValidationError {
  detail: Array<{
    loc: (string | number)[];
    msg: string;
    type: string;
  }>;
}

type RecommendationAlgorithm = 'popularity' | 'collaborative' | 'content_based';

class ApiClient {
  private baseURL: string;
  private token: string | null = null;
  private onLogoutCallback?: () => void;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem("auth_token");
  }

  // Método para registrar callback de logout
  setLogoutCallback(callback: () => void): void {
    this.onLogoutCallback = callback;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      // Verificar se é erro de autenticação/autorização
      if (response.status === 401 || response.status === 403) {
        // Fazer logout automático
        this.logout();
        
        // Disparar callback se registrado
        if (this.onLogoutCallback) {
          this.onLogoutCallback();
        }
        
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.message || `Sessão expirada. Faça login novamente.`
        );
      }
      
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.message || `HTTP error! status: ${response.status}`
      );
    }

    return response.json();
  }

  // Auth methods
  async login(username: string, password: string): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>("/auth/login-json", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });

    this.token = response.access_token;
    localStorage.setItem("auth_token", response.access_token);
    return response;
  }

  async register(email: string, username: string, password: string): Promise<void> {
    await this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, username, password }),
    });
  }

  logout(): void {
    this.token = null;
    localStorage.removeItem("auth_token");
  }

  // Movie methods
  async getMovies(page: number = 1, perPage: number = 10): Promise<MovieListResponse> {
    return this.request<MovieListResponse>(`/movies/?page=${page}&per_page=${perPage}`);
  }

  async getRecommendations(
    algorithm: RecommendationAlgorithm = 'collaborative', 
    page: number = 1, 
    perPage: number = 10
  ): Promise<MovieListResponse> {
    return this.request<MovieListResponse>(
      `/recommendations/?algorithm=${algorithm}&page=${page}&per_page=${perPage}`
    );
  }

  async toggleLike(movieId: number): Promise<LikeToggleResponse> {
    return this.request<LikeToggleResponse>("/likes/toggle", {
      method: "POST",
      body: JSON.stringify({ movie_id: movieId }),
    });
  }

  // CSV methods
  async downloadCsvTemplate(): Promise<Blob> {
    const url = `${this.baseURL}/csv/template`;
    const headers: Record<string, string> = {};

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      method: "GET",
      headers,
    });

    if (!response.ok) {
      // Verificar se é erro de autenticação/autorização
      if (response.status === 401 || response.status === 403) {
        this.logout();
        if (this.onLogoutCallback) {
          this.onLogoutCallback();
        }
        throw new Error("Sessão expirada. Faça login novamente.");
      }
      throw new Error(`Erro ao baixar template: ${response.status}`);
    }

    return response.blob();
  }

  async uploadCsv(file: File): Promise<CsvUploadResponse> {
    const url = `${this.baseURL}/csv/upload`;
    const formData = new FormData();
    formData.append('file', file);

    const headers: Record<string, string> = {};

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      method: "POST",
      headers,
      body: formData,
    });

    const responseData = await response.json();

    if (!response.ok) {
      // Verificar se é erro de autenticação/autorização
      if (response.status === 401 || response.status === 403) {
        this.logout();
        if (this.onLogoutCallback) {
          this.onLogoutCallback();
        }
        throw new Error("Sessão expirada. Faça login novamente.");
      }
      
      if (response.status === 422) {
        const validationError = responseData as ValidationError;
        const errorMessages = validationError.detail.map(err => err.msg).join(', ');
        throw new Error(`Erro de validação: ${errorMessages}`);
      }
      throw new Error(responseData.message || `Erro no upload: ${response.status}`);
    }

    return responseData as CsvUploadResponse;
  }

  // Utility methods
  isAuthenticated(): boolean {
    return !!this.token;
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
export type { 
  Movie, 
  MovieListResponse, 
  AuthResponse, 
  LikeToggleResponse, 
  CsvUploadResponse,
  ValidationError,
  RecommendationAlgorithm 
};