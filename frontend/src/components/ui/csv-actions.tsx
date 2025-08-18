import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Download, Upload, FileSpreadsheet, Loader2, FileText, CheckCircle } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { apiClient, type CsvUploadResponse } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface CsvActionsProps {
  onUploadSuccess?: (result: CsvUploadResponse) => void;
}

export function CsvActions({ onUploadSuccess }: CsvActionsProps) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleDownloadTemplate = async () => {
    try {
      setIsDownloading(true);
      const blob = await apiClient.downloadCsvTemplate();
      
      // Criar URL do blob e fazer download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'template_filmes.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast({
        title: "Template baixado!",
        description: "O arquivo template_filmes.csv foi baixado com sucesso.",
      });
    } catch (error) {
      console.error("Erro ao baixar template:", error);
      toast({
        title: "Erro no download",
        description: error instanceof Error ? error.message : "Falha ao baixar o template",
        variant: "destructive",
      });
    } finally {
      setIsDownloading(false);
    }
  };

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Verificar se é um arquivo CSV
    if (!file.name.toLowerCase().endsWith('.csv')) {
      toast({
        title: "Arquivo inválido",
        description: "Por favor, selecione um arquivo CSV.",
        variant: "destructive",
      });
      return;
    }

    try {
      setIsUploading(true);
      setUploadProgress("Iniciando upload...");
      
      // Toast de loading persistente
      const loadingToast = toast({
        title: "📤 Fazendo upload do arquivo...",
        description: (
          <div className="flex items-center gap-2 mt-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Processando {file.name}</span>
          </div>
        ),
        duration: Infinity, // Toast persistente
      });

      setUploadProgress("Enviando arquivo para o servidor...");
      const result = await apiClient.uploadCsv(file);

      // Dismiss loading toast
      loadingToast.dismiss();
      
      // Mostrar resultado do upload
      if (result.success) {
        toast({
          title: "✅ Upload realizado com sucesso!",
          description: (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="font-medium">Arquivo processado com sucesso</span>
              </div>
              <div className="text-sm text-muted-foreground space-y-1">
                <div>📊 Total de linhas: {result.total_rows}</div>
                <div>🆕 Filmes criados: {result.created_count}</div>
                <div>🔄 Filmes atualizados: {result.updated_count}</div>
                {result.errors.length > 0 && (
                  <div className="text-orange-600">⚠️ Erros encontrados: {result.errors.length}</div>
                )}
              </div>
            </div>
          ),
          duration: 5000,
        });

        // Mostrar erros detalhados se houver
        if (result.errors.length > 0) {
          setTimeout(() => {
            toast({
              title: "⚠️ Detalhes dos erros encontrados:",
              description: (
                <div className="max-h-32 overflow-y-auto text-sm">
                  {result.errors.slice(0, 5).map((error, index) => (
                    <div key={index} className="text-red-600 mb-1">• {error}</div>
                  ))}
                  {result.errors.length > 5 && (
                    <div className="text-muted-foreground">... e mais {result.errors.length - 5} erros</div>
                  )}
                </div>
              ),
              variant: "destructive",
              duration: 8000,
            });
          }, 2000);
        }

        // Chamar callback se fornecido
        onUploadSuccess?.(result);
      } else {
        toast({
          title: "❌ Falha no upload",
          description: result.message,
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Erro no upload:", error);
      
      // Dismiss loading toast if it exists
      if (loadingToast) {
        loadingToast.dismiss();
      }
      
      toast({
        title: "❌ Erro no upload",
        description: error instanceof Error ? error.message : "Falha ao fazer upload do arquivo",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      setUploadProgress("");
      // Limpar o input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="gap-2">
            {isUploading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <FileSpreadsheet className="w-4 h-4" />
            )}
            {isUploading ? "Processando..." : "Gerenciar CSV"}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56 cinema-card border-border/50" align="end">
          <DropdownMenuItem 
            className="cursor-pointer"
            onClick={handleDownloadTemplate}
            disabled={isDownloading}
          >
            {isDownloading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Download className="mr-2 h-4 w-4" />
            )}
            Baixar Template CSV
          </DropdownMenuItem>
          
          <DropdownMenuSeparator />
          
          <DropdownMenuItem 
            className="cursor-pointer"
            onClick={handleFileSelect}
            disabled={isUploading}
          >
            {isUploading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Upload className="mr-2 h-4 w-4" />
            )}
            {isUploading ? (
              <div className="flex flex-col w-full">
                <span>Fazendo Upload...</span>
                {uploadProgress && (
                  <span className="text-xs text-muted-foreground mt-1">
                    {uploadProgress}
                  </span>
                )}
              </div>
            ) : (
              "Fazer Upload CSV"
            )}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Input de arquivo oculto */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        onChange={handleFileUpload}
        className="hidden"
      />
    </>
  );
}
