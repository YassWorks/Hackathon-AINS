import React from "react";

interface FileUploadSectionProps {
    inputRef: React.RefObject<HTMLInputElement>;
    onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    isLoading: boolean;
}

const FileUploadSection: React.FC<FileUploadSectionProps> = ({
    inputRef,
    onFileChange,
    isLoading,
}) => {
    return (
        <div className="py-4 flex flex-col items-center space-y-4">
            <div className="flex items-center space-x-4">
                <label className="text-white text-2xl opacity-60">
                    Import photos and audio
                </label>
                <input
                    type="file"
                    accept="image/*,audio/*,.png,.jpg,.jpeg,.gif,.webp,.mp3,.wav,.m4a,.ogg"
                    multiple
                    className="hidden"
                    onChange={onFileChange}
                    ref={inputRef}
                    disabled={isLoading}
                />
            </div>
        </div>
    );
};

export default FileUploadSection;
