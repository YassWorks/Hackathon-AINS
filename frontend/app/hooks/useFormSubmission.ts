import { useState } from "react";
import { submitFormData } from "../utils/apiUtils";
import { ApiResponse } from "../types";

export const useFormSubmission = () => {
    const [answer, setAnswer] = useState<string | null>(null);
    const [verdict, setVerdict] = useState<string | null>(null);
    const [explanation, setExplanation] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const handleSubmit = async (prompt: string, files: FileList | null) => {
        if (isLoading) {
            return; // Prevent multiple submissions
        }

        setIsLoading(true);
        setAnswer(null);
        setVerdict(null);
        setExplanation(null);

        try {
            const data: ApiResponse = await submitFormData(prompt, files);
            console.log("Response:", data);

            if (data.Success) {
                setVerdict(data.Success.Verdict);
                setExplanation(data.Success.Explanation);
                setAnswer(`${data.Success.Verdict}: ${data.Success.Explanation}`);
            } else if (data.Error) {
                setAnswer(data.Error);
                setVerdict(null);
                setExplanation(null);
            } else {
                // Fallback for unexpected response format
                setAnswer(data.placeholder || "No response received");
                setVerdict(null);
                setExplanation(null);
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
        explanation,
        isLoading,
        handleSubmit,
    };
};
