import React from "react";
import Image from "next/image";

interface FileUploadControlsProps {
    isLoading: boolean;
    fileCount: number;
    onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onUploadClick: () => void;
    onToggleFileList: () => void;
    inputRef: React.RefObject<HTMLInputElement | null>;
}

const FileUploadControls: React.FC<FileUploadControlsProps> = ({
    isLoading,
    fileCount,
    onFileChange,
    onUploadClick,
    onToggleFileList,
    inputRef,
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
                <button
                    type="submit"
                    disabled={isLoading}
                    className={`py-2 text-white rounded-md transition-shadow shadow-md ${
                        isLoading
                            ? "cursor-not-allowed opacity-50"
                            : "cursor-pointer hover:scale-110 transition-transform"
                    }`}
                    onClick={onUploadClick}
                >
                    <Image
                        src="/upload.png"
                        alt="upload"
                        height={80}
                        width={80}
                    />
                </button>
                <div
                    className="text-neutral-500 font-medium text-3xl cursor-pointer hover:text-neutral-300 transition-colors"
                    onClick={onToggleFileList}
                >
                    {fileCount > 0 && (
                        <div>
                            {fileCount} file{fileCount > 1 ? "s" : ""} selected
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default FileUploadControls;
