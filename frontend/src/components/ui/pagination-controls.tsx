import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationControlsProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  isLoading?: boolean;
}

export function PaginationControls({ 
  currentPage, 
  totalPages, 
  onPageChange, 
  isLoading = false 
}: PaginationControlsProps) {
  if (totalPages <= 1) return null;

  const generatePageNumbers = () => {
    const pages = [];
    const delta = 2; // Number of pages to show on each side of current page
    
    for (let i = Math.max(1, currentPage - delta); i <= Math.min(totalPages, currentPage + delta); i++) {
      pages.push(i);
    }
    
    return pages;
  };

  const pageNumbers = generatePageNumbers();

  return (
    <div className="flex items-center justify-center gap-2 py-8">
      {/* Previous Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1 || isLoading}
        className="h-8 w-8 p-0"
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>

      {/* First page if not in range */}
      {pageNumbers[0] > 1 && (
        <>
          <Button
            variant={1 === currentPage ? "default" : "outline"}
            size="sm"
            onClick={() => onPageChange(1)}
            disabled={isLoading}
            className="h-8 w-8 p-0"
          >
            1
          </Button>
          {pageNumbers[0] > 2 && (
            <span className="text-muted-foreground text-sm">...</span>
          )}
        </>
      )}

      {/* Page numbers */}
      {pageNumbers.map((pageNum) => (
        <Button
          key={pageNum}
          variant={pageNum === currentPage ? "default" : "outline"}
          size="sm"
          onClick={() => onPageChange(pageNum)}
          disabled={isLoading}
          className="h-8 w-8 p-0"
        >
          {pageNum}
        </Button>
      ))}

      {/* Last page if not in range */}
      {pageNumbers[pageNumbers.length - 1] < totalPages && (
        <>
          {pageNumbers[pageNumbers.length - 1] < totalPages - 1 && (
            <span className="text-muted-foreground text-sm">...</span>
          )}
          <Button
            variant={totalPages === currentPage ? "default" : "outline"}
            size="sm"
            onClick={() => onPageChange(totalPages)}
            disabled={isLoading}
            className="h-8 w-8 p-0"
          >
            {totalPages}
          </Button>
        </>
      )}

      {/* Next Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages || isLoading}
        className="h-8 w-8 p-0"
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  );
}
