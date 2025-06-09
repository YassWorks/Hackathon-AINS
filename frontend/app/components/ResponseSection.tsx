import React from "react";
import { getVerdictColor } from "../utils/fileUtils";

interface ResponseSectionProps {
    answer: string | null;
    verdict: string | null;
}

const ResponseSection: React.FC<ResponseSectionProps> = ({
    answer,
    verdict,
}) => {
    if (!answer) return null;

    return (
        <div className="w-full max-w-lg mx-auto bg-stone-950 opacity-90 text-white p-4 rounded-md space-y-4">
            <div>
                <h2 className="text-xl font-bold">Response:</h2>
            </div>

            {verdict && (
                <div className="border-t border-stone-700 pt-4">
                    <h3 className="text-lg font-semibold mb-2">
                        Final Verdict:
                    </h3>
                    <p
                        className={`text-xl font-bold ${getVerdictColor(
                            verdict
                        )}`}
                    >
                        {verdict.toUpperCase()}
                    </p>
                </div>
            )}
        </div>
    );
};

export default ResponseSection;
