import React from "react";

const LoadingIndicator: React.FC = () => {
    return (
        <div className="w-full max-w-lg mx-auto bg-stone-950 opacity-90 to-black text-white p-6 rounded-md">
            <div className="flex flex-col items-center space-y-4">
                <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                    <div
                        className="w-2 h-2 bg-white rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                        className="w-2 h-2 bg-white rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                    ></div>
                </div>
                <p className="text-lg font-medium">Analyzing your query...</p>
                <p className="text-sm text-stone-400">This may take a moment</p>
            </div>
        </div>
    );
};

export default LoadingIndicator;
