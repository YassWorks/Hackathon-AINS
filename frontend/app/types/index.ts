export interface FormState {
    prompt: string;
    file: FileList | null;
    fileCount: number;
    answer: string | null;
    verdict: string | null;
    explanation: string | null;
    isDragging: boolean;
    showFileList: boolean;
    isLoading: boolean;
}

export interface ApiSuccessResponse {
    Verdict: string;
    Explanation: string;
}

export interface ApiResponse {
    Success?: ApiSuccessResponse;
    Error?: string;
    placeholder?: string;
}
