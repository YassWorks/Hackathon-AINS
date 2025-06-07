"use client";

import { useState, useRef } from "react";
import Image from "next/image";

export default function Home() {
    const [prompt, setPrompt] = useState<string>("");
    const [file, setFile] = useState<FileList | null>(null);
    const [fileCount, setFileCount] = useState<number>(0);
    const [answer, setAnswer] = useState<string | null>(null);
    const [isDragging, setIsDragging] = useState<boolean>(false);
    const inputRef = useRef<HTMLInputElement>(null);
    
    const handleSubmit = async () => {
        
    };

    const handleClick = () => {
        inputRef.current?.click();
    };

    // Helper function to merge FileList objects
    const mergeFileLists = (existingFiles: FileList | null, newFiles: FileList): FileList => {
        const dataTransfer = new DataTransfer();
        
        // Add existing files
        if (existingFiles) {
            for (let i = 0; i < existingFiles.length; i++) {
                dataTransfer.items.add(existingFiles[i]);
            }
        }
        
        // Add new files (check for duplicates by name and size)
        for (let i = 0; i < newFiles.length; i++) {
            const newFile = newFiles[i];
            let isDuplicate = false;
            
            if (existingFiles) {
                for (let j = 0; j < existingFiles.length; j++) {
                    if (existingFiles[j].name === newFile.name && existingFiles[j].size === newFile.size) {
                        isDuplicate = true;
                        break;
                    }
                }
            }
            
            if (!isDuplicate) {
                dataTransfer.items.add(newFile);
            }
        }
        
        return dataTransfer.files;
    };

    // Helper function to filter valid files
    const filterValidFiles = (files: FileList): FileList => {
        const validExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp3', '.wav', '.m4a', '.ogg'];
        const validTypes = ['image/', 'audio/'];
        const dataTransfer = new DataTransfer();
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const isValidType = validTypes.some(type => file.type.startsWith(type));
            const isValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
            
            if (isValidType || isValidExtension) {
                dataTransfer.items.add(file);
            }
        }
        
        return dataTransfer.files;
    };

    const getFile = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFiles = e.target.files;
        if (selectedFiles) {
            const validFiles = filterValidFiles(selectedFiles);
            const mergedFiles = mergeFileLists(file, validFiles);
            setFile(mergedFiles);
            setFileCount(mergedFiles.length);
        }
    };    // Drag and drop handlers
    const handleDragEnter = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        
        // Only hide overlay if we're leaving the main container
        // Check if the related target is outside the current target
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
        const x = e.clientX;
        const y = e.clientY;
        
        // If mouse is outside the container bounds, hide the overlay
        if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
            setIsDragging(false);
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        // Ensure overlay stays visible
        setIsDragging(true);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        
        const droppedFiles = e.dataTransfer.files;
        if (droppedFiles && droppedFiles.length > 0) {
            const validFiles = filterValidFiles(droppedFiles);
            const mergedFiles = mergeFileLists(file, validFiles);
            setFile(mergedFiles);
            setFileCount(mergedFiles.length);
        }
    };    
    
    return (
        <div 
            className="px-3 py-40 text-center min-h-screen"
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
        >            {/* Drag overlay */}
            {isDragging && (
                <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center pointer-events-none">
                    <div className="bg-gradient-to-br from-stone-900 to-black text-white p-8 rounded-lg border-2 border-dashed border-white">
                        <div className="text-2xl font-bold mb-2">Drop files here</div>
                        <div className="text-sm opacity-70">Images and audio files only</div>
                    </div>
                </div>
            )}
            
            <div className="py-4 text-4xl font-bold">MYTH CHASER</div>

            <div className="relative w-full max-w-lg mx-auto">
                <textarea
                    placeholder="What fact do you want to check today?"
                    className="w-full p-4 pr-12 rounded-md bg-gradient-to-br from-stone-900 to-black text-white placeholder-grey-400 resize-none focus:outline-none"
                    rows={4}
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                ></textarea>

                <button
                    onClick={handleSubmit}
                    className="absolute top-4 right-4 z-10 bg-transparent hover:rotate-45 hover:scale-130 transition-transform cursor-pointer"
                >
                    <Image
                        src="/submit.png"
                        alt="submit"
                        height={17}
                        width={17}
                    />
                </button>
            </div>

            <div className="py-4 flex flex-col items-center space-y-4">
                <div className="flex items-center space-x-4">
                    <label className="text-white text-sm opacity-60">
                        Import photos and audio
                    </label>
                    <input
                        type="file"
                        accept="image/*,audio/*,.png,.jpg,.jpeg,.gif,.webp,.mp3,.wav,.m4a,.ogg"
                        multiple
                        className="hidden"
                        onChange={getFile}
                        ref={inputRef}
                    />
                    <button
                        type="submit"
                        className="px-4 py-2 bg-gradient-to-br from-stone-900 to-black text-white rounded-md transition-shadow shadow-md cursor-pointer hover:scale-110 transition-transform"
                        onClick={handleClick}
                    >
                        <Image
                            src="/upload.png"
                            alt="upload"
                            height="17"
                            width="17"
                        />
                    </button>
                    <div className="text-neutral-500 font-medium text-xs">
                        {fileCount > 0 && (
                            <div>
                                {fileCount} file{fileCount > 1 ? 's' : ''} selected
                            </div>
                        )}
                    </div>
                </div>
            </div>
            <div className="py-4">
                {answer && (
                    <div className="w-full max-w-lg mx-auto bg-gradient-to-br from-stone-900 to-black text-white p-4 rounded-md">
                        <h2 className="text-xl font-bold">Response:</h2>
                        <p>{answer}</p>
                    </div>
                )}
            </div>
        </div>
    );
}
