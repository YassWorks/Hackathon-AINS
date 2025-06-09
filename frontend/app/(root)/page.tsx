"use client";

import { useState, useRef } from "react";
import DragOverlay from "../components/DragOverlay";
import HeroSection from "../components/HeroSection";
import SearchForm from "../components/SearchForm";
import FileUploadControls from "../components/FileUploadControls";
import FileListModal from "../components/FileListModal";
import LoadingIndicator from "../components/LoadingIndicator";
import ResponseSection from "../components/ResponseSection";
import { useFileUpload } from "../hooks/useFileUpload";
import { useFormSubmission } from "../hooks/useFormSubmission";

export default function Home() {
    const [prompt, setPrompt] = useState<string>("");
    const inputRef = useRef<HTMLInputElement>(null);
    const {
        file,
        fileCount,
        isDragging,
        showFileList,
        handleFileChange,
        removeFile,
        toggleFileList,
        closeFileList,
        handleDragEnter,
        handleDragLeave,
        handleDragOver,
        handleDrop,
    } = useFileUpload();

    const { answer, verdict, isLoading, handleSubmit } = useFormSubmission();

    const onSubmit = async () => {
        await handleSubmit(prompt, file);
    };

    const handleClick = () => {
        inputRef.current?.click();
    };

    return (
        <div
            className="px-3 py-40 text-center min-h-screen"
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
        >
            <DragOverlay isDragging={isDragging} />

            <div>
                <HeroSection />

                <SearchForm
                    prompt={prompt}
                    isLoading={isLoading}
                    onPromptChange={setPrompt}
                    onSubmit={onSubmit}
                />

                <FileUploadControls
                    isLoading={isLoading}
                    fileCount={fileCount}
                    onFileChange={handleFileChange}
                    onUploadClick={handleClick}
                    onToggleFileList={toggleFileList}
                    inputRef={inputRef}
                />
                <FileListModal
                    showFileList={showFileList}
                    fileCount={fileCount}
                    file={file}
                    onClose={closeFileList}
                    onRemoveFile={removeFile}
                />

                <div className="py-4">
                    {isLoading && <LoadingIndicator />}
                    {!isLoading && (
                        <ResponseSection answer={answer} verdict={verdict} />
                    )}
                </div>
            </div>
        </div>
    );
}
