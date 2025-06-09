import { useState } from "react";
import { submitFormData } from "../utils/apiUtils";
import { ApiResponse } from "../types";

export const useFormSubmission = () => {
    const [answer, setAnswer] = useState<string | null>(null);
    const [verdict, setVerdict] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const handleSubmit = async (prompt: string, files: FileList | null) => {
        if (isLoading) {
            return; // Prevent multiple submissions
        }

        setIsLoading(true);
        setAnswer(null);
        setVerdict(null);

        try {
            const data: ApiResponse = await submitFormData(prompt, files);
            console.log("Response:", data);

            if (data.Success) {
                setAnswer(data.Success);
                setVerdict(data.Success);
            } else if (data.Error) {
                setAnswer(data.Error);
                setVerdict(data.Error);
            } else {
                // Fallback for unexpected response format
                setAnswer(data.placeholder || "No response received");
                setVerdict(null);
            }
        } catch (err) {
            console.error(err);
            alert("Something went wrong!");
        } finally {
            setIsLoading(false);
        }
    };

    return {
        answer,
        verdict,
        isLoading,
        handleSubmit,
    };
};
