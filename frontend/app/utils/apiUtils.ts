import { ApiResponse } from "../types";

export const submitFormData = async (
    prompt: string,
    files: FileList | null
): Promise<ApiResponse> => {
    if (!prompt.trim()) {
        throw new Error("Please enter a prompt.");
    }

    const formData = new FormData();
    formData.append("prompt", prompt);

    // Append all files to the FormData if any exist
    if (files && files.length > 0) {
        for (let i = 0; i < files.length; i++) {
            formData.append("files", files[i]);
        }
    }

    const res = await fetch("http://localhost:8000/classify", {
        method: "POST",
        body: formData,
    });

    if (!res.ok) throw new Error("Upload failed");

    return await res.json();
};
