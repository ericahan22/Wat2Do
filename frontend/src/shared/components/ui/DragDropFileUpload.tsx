import { useState, useRef, useCallback } from 'react';
import { Upload, X, Image as ImageIcon, CheckCircle } from 'lucide-react';
import { cn } from '@/shared/lib/utils';

interface DragDropFileUploadProps {
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  preview?: string | null;
  error?: string;
  disabled?: boolean;
  accept?: string;
  maxSize?: number; // in MB
}

export const DragDropFileUpload = ({
  onFileSelect,
  onFileRemove,
  preview,
  error,
  disabled = false,
  accept = "image/jpeg,image/png,image/webp",
  maxSize = 10
}: DragDropFileUploadProps) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [dragError, setDragError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback((file: File): string | null => {
    const validTypes = accept.split(',').map(type => type.trim());
    const isValidType = validTypes.some(type => {
      if (type.startsWith('.')) {
        return file.name.toLowerCase().endsWith(type);
      }
      return file.type === type;
    });

    if (!isValidType) {
      return `File type not supported. Please use: ${accept}`;
    }

    if (file.size > maxSize * 1024 * 1024) {
      return `File size must be less than ${maxSize}MB`;
    }

    return null;
  }, [accept, maxSize]);

  const handleFile = useCallback((file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setDragError(validationError);
      return;
    }
    
    setDragError(null);
    onFileSelect(file);
  }, [validateFile, onFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragOver(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  }, [disabled, handleFile]);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  }, [handleFile]);

  const handleClick = useCallback(() => {
    if (!disabled) {
      fileInputRef.current?.click();
    }
  }, [disabled]);

  const handleRemove = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    setDragError(null);
    onFileRemove();
  }, [onFileRemove]);

  return (
    <div className="space-y-4">
      {/* Drag and Drop Area */}
      <div
        className={cn(
          "relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 cursor-pointer",
          "hover:border-blue-400 hover:bg-blue-50/50 dark:hover:border-blue-500 dark:hover:bg-blue-950/30",
          isDragOver && "border-blue-500 bg-blue-50 dark:bg-blue-950/40 scale-[1.02]",
          disabled && "opacity-50 cursor-not-allowed",
          error || dragError 
            ? "border-red-300 bg-red-50/50 dark:border-red-800 dark:bg-red-950/20" 
            : "border-gray-300 dark:border-gray-600",
          preview && "border-green-300 bg-green-50/50 dark:border-green-700 dark:bg-green-950/20"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          onChange={handleFileInputChange}
          className="hidden"
          disabled={disabled}
        />

        {preview ? (
          <div className="space-y-4">
            <div className="relative inline-block group">
              <img
                src={preview}
                alt="Preview"
                className="max-h-48 max-w-full rounded-lg shadow-sm object-contain transition-transform group-hover:scale-105"
              />
              <button
                type="button"
                onClick={handleRemove}
                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-all duration-200 hover:scale-110 shadow-lg"
                disabled={disabled}
                title="Remove image"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <p className="text-sm text-green-600 dark:text-green-400 font-medium flex items-center justify-center gap-1">
              <CheckCircle className="h-4 w-4" />
              Image uploaded successfully
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="mx-auto w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
              {isDragOver ? (
                <Upload className="h-8 w-8 text-blue-500 dark:text-blue-400" />
              ) : (
                <ImageIcon className="h-8 w-8 text-gray-400 dark:text-gray-500" />
              )}
            </div>
            
            <div className="space-y-2">
              <p className="text-lg font-medium text-gray-900 dark:text-gray-100">
                {isDragOver ? "Drop your image here" : "Upload event screenshot"}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Drag and drop an image, or click to browse
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500">
                Supports: JPEG, PNG, WebP • Max size: {maxSize}MB
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Error Messages */}
      {(error || dragError) && (
        <div className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/30 p-3 rounded-md border border-red-200 dark:border-red-900/50">
          {error || dragError}
        </div>
      )}
    </div>
  );
};
