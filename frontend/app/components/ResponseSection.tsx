import React from "react";
import { getVerdictColor } from "../utils/fileUtils";

interface ResponseSectionProps {
    answer: string | null;
    verdict: string | null;
    explanation: string | null;
}

const ResponseSection: React.FC<ResponseSectionProps> = ({
    answer,
    verdict,
    explanation,
}) => {
    if (!answer && !verdict) return null;

    return (
        <div className="w-full max-w-7xl mx-auto bg-stone-950 opacity-90 text-white p-6 rounded-lg space-y-6">
            {verdict && (
                <div>
                    <h3 className="text-xl font-semibold mb-3">
                        Final Verdict:
                    </h3>
                    <p
                        className={`text-3xl font-bold ${getVerdictColor(
                            verdict
                        )}`}
                    >
                        {verdict.toUpperCase()}
                    </p>
                </div>
            )}

            {explanation && (
                <div className="border-t border-stone-700 pt-4">
                    <h3 className="text-xl font-semibold mb-3">
                        Explanation:
                    </h3>
                    <p className="text-left text-2xl leading-relaxed text-stone-200">
                        {explanation}
                    </p>
                </div>
            )}

            {answer && !verdict && (
                <div>
                    <h2 className="text-xl font-bold mb-3">Response:</h2>
                    <p className="text-lg leading-relaxed text-stone-200">
                        {answer}
                    </p>
                </div>
            )}
        </div>
    );
};

export default ResponseSection;
