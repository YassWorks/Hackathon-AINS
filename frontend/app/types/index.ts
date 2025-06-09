export interface FormState {
    prompt: string;
    file: FileList | null;
    fileCount: number;
    answer: string | null;
    verdict: string | null;
    isDragging: boolean;
    showFileList: boolean;
    isLoading: boolean;
}

export interface ApiResponse {
    Success?: string;
    Error?: string;
    placeholder?: string;
}
