import React from "react";
import Image from "next/image";

interface SearchFormProps {
    prompt: string;
    isLoading: boolean;
    onPromptChange: (value: string) => void;
    onSubmit: () => void;
}

const SearchForm: React.FC<SearchFormProps> = ({
    prompt,
    isLoading,
    onPromptChange,
    onSubmit,
}) => {
    return (
        <div className="relative w-full max-w-3xl mx-auto">
            <textarea
                placeholder="What fact do you want to check?"
                className={`w-full p-4 pr-25 bg-stone-950 opacity-80 text-white rounded-lg shadow-md resize-none focus:outline-none focus:ring-2 focus:ring-orange-500 text-2xl transition-all duration-200 ${
                    isLoading
                        ? "opacity-50 cursor-not-allowed"
                        : "hover:shadow-lg"
                }`}
                rows={4}
                value={prompt}
                onChange={(e) => onPromptChange(e.target.value)}
                disabled={isLoading}
                onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        onSubmit();
                    }
                }}
            />
            <button
                onClick={onSubmit}
                disabled={isLoading}
                className={`absolute top-2 right-0 z-10 bg-transparent ${
                    isLoading
                        ? "cursor-not-allowed opacity-50"
                        : "hover:scale-130 cursor-pointer"
                }`}
            >
                <Image
                    src="/submit.png"
                    alt="submit"
                    height={100}
                    width={100}
                />
            </button>
        </div>
    );
};

export default SearchForm;
