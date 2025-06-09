import React from "react";
import Image from "next/image";

interface SubmitButtonProps {
    onClick: () => void;
    isLoading: boolean;
}

const SubmitButton: React.FC<SubmitButtonProps> = ({ onClick, isLoading }) => {
    return (
        <button
            onClick={onClick}
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
    );
};

export default SubmitButton;
