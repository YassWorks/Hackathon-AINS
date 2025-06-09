"use client";

import { useState, useRef } from "react";
import Image from "next/image";

export default function Home() {
    const [prompt, setPrompt] = useState<string>("");
    const [file, setFile] = useState<FileList | null>(null);
    const [fileCount, setFileCount] = useState<number>(0);
    const [answer, setAnswer] = useState<string | null>(null);
    const [verdict, setVerdict] = useState<string | null>(null);
    const [isDragging, setIsDragging] = useState<boolean>(false);
    const [showFileList, setShowFileList] = useState<boolean>(false);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const inputRef = useRef<HTMLInputElement>(null);

    // Helper function to get verdict color
    const getVerdictColor = (verdict: string): string => {
        const upperVerdict = verdict.toUpperCase();
        if (upperVerdict === "FACT") return "text-green-400";
        if (upperVerdict === "MYTH") return "text-orange-400";
        if (upperVerdict === "SCAM") return "text-red-400";
        return "text-white"; // default color
    };

    const handleSubmit = async () => {
        if (!prompt.trim()) {
            alert("Please enter a prompt.");
            return;
        }

        if (isLoading) {
            return; // Prevent multiple submissions
        }

        setIsLoading(true);
        setAnswer(null);
        setVerdict(null);

        const formData = new FormData();
        formData.append("prompt", prompt);

        // Append all files to the FormData if any exist
        if (file && file.length > 0) {
            for (let i = 0; i < file.length; i++) {
                formData.append("files", file[i]);
            }
        }

        try {
            const res = await fetch("http://localhost:8000/classify", {
                method: "POST",
                body: formData,
            });

            if (!res.ok) throw new Error("Upload failed");
            const data = await res.json();
            console.log("Response:", data);

            if (data.Success) {
                setAnswer(data.Success);
                setVerdict(data.Success);
            } else if (data.Error) {
                setAnswer(data.Error);
                setVerdict(data.Error);
            } else {
                // Fallback for unexpected response format
                setAnswer(data.placeholder || "No response received");
                setVerdict(null);
            }
            const fileCount = file ? file.length : 0;
        } catch (err) {
            console.error(err);
            alert("Something went wrong!");
        } finally {
            setIsLoading(false);
        }
    };

    const handleClick = () => {
        inputRef.current?.click();
    };

    const removeFile = (indexToRemove: number) => {
        if (file) {
            const dataTransfer = new DataTransfer();

            // Add all files except the one to remove
            for (let i = 0; i < file.length; i++) {
                if (i !== indexToRemove) {
                    dataTransfer.items.add(file[i]);
                }
            }

            const newFileList = dataTransfer.files;
            setFile(newFileList);
            setFileCount(newFileList.length);

            // Close the modal if no files left
            if (newFileList.length === 0) {
                setShowFileList(false);
            }
        }
    };

    const toggleFileList = () => {
        if (fileCount > 0) {
            setShowFileList(!showFileList);
        }
    };

    // Helper function to merge FileList objects
    const mergeFileLists = (
        existingFiles: FileList | null,
        newFiles: FileList
    ): FileList => {
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
                    if (
                        existingFiles[j].name === newFile.name &&
                        existingFiles[j].size === newFile.size
                    ) {
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
        const validExtensions = [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
            ".mp3",
            ".wav",
            ".m4a",
            ".ogg",
        ];
        const validTypes = ["image/", "audio/"];
        const dataTransfer = new DataTransfer();

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const isValidType = validTypes.some((type) =>
                file.type.startsWith(type)
            );
            const isValidExtension = validExtensions.some((ext) =>
                file.name.toLowerCase().endsWith(ext)
            );

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
    };

    // Drag and drop handlers
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
        if (
            x < rect.left ||
            x > rect.right ||
            y < rect.top ||
            y > rect.bottom
        ) {
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
        >
            {/* Drag & Drop overlay */}
            {isDragging && (
                <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center pointer-events-none">
                    <div className="bg-gradient-to-br from-stone-900 to-black text-white p-8 rounded-lg border-2 border-dashed border-white">
                        <div className="text-2xl font-bold mb-2">
                            Drop files here
                        </div>
                        <div className="text-sm opacity-70">
                            Images and audio files only
                        </div>
                    </div>
                </div>
            )}

            <div>

                <div className="py-4 text-9xl font-bold text-gray-300">
                    MYTH CHASER
                </div>
                <div className="py-4 text-2xl font-medium text-gray-400">
                    Anti-scam and myth-busting utility powered by AI
                </div>

                <br></br>
                <br></br>
                <div className="relative w-full max-w-3xl mx-auto">
                    {" "}
                    <textarea
                        placeholder="What fact do you want to check?"
                        className={`w-full p-4 pr-25 bg-stone-950 opacity-80 text-white rounded-lg shadow-md resize-none focus:outline-none focus:ring-2 focus:ring-orange-500 text-2xl transition-all duration-200 ${
                            isLoading
                                ? "opacity-50 cursor-not-allowed"
                                : "hover:shadow-lg"
                        }`}
                        rows={4}
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        disabled={isLoading}
                    ></textarea>
                    <button
                        onClick={handleSubmit}
                        disabled={isLoading}
                        className={`absolute top-2 right-0 z-10 bg-transparent ${
                            isLoading
                                ? "cursor-not-allowed opacity-50"
                                : "hover:scale-130 cursor-pointer"
                        }`}
                    >
                        {isLoading ? (
                            <div className="w-[32px] h-[32px] border-4 border-white border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                            <Image
                                src="/submit.png"
                                alt="submit"
                                height={100}
                                width={100}
                            />
                        )}
                    </button>
                </div>
                <div className="py-4 flex flex-col items-center space-y-4">
                    <div className="flex items-center space-x-4">
                        <label className="text-white text-2xl opacity-60">
                            Import photos and audio
                        </label>{" "}
                        <input
                            type="file"
                            accept="image/*,audio/*,.png,.jpg,.jpeg,.gif,.webp,.mp3,.wav,.m4a,.ogg"
                            multiple
                            className="hidden"
                            onChange={getFile}
                            ref={inputRef}
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={isLoading}
                            className={` py-2 text-white rounded-md transition-shadow shadow-md ${
                                isLoading
                                    ? "cursor-not-allowed opacity-50"
                                    : "cursor-pointer hover:scale-110 transition-transform"
                            }`}
                            onClick={handleClick}
                        >
                            <Image
                                src="/upload.png"
                                alt="upload"
                                height={80}
                                width={80}
                            />
                        </button>{" "}
                        <div
                            className="text-neutral-500 font-medium text-3xl cursor-pointer hover:text-neutral-300 transition-colors"
                            onClick={toggleFileList}
                        >
                            {fileCount > 0 && (
                                <div>
                                    {fileCount} file{fileCount > 1 ? "s" : ""}{" "}
                                    selected
                                </div>
                            )}
                        </div>{" "}
                    </div>
                </div>

                {/* File List Modal */}
                {showFileList && fileCount > 0 && (
                    <div className="fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center p-10 backdrop-blur-lg">
                        <div className="bg-stone-900 text-white p-0 rounded-xl max-w-4xl w-full shadow-2xl border border-stone-600/50 transform transition-all duration-300 ease-out scale-100 opacity-100">
                        
                            {/* Header */}
                            <div className="bg-stone-800 px-12 py-8 rounded-t-xl border-b border-stone-600/30">
                                <div className="flex justify-between items-center">
                                    <div>
                                        <h3 className="text-3xl font-bold text-white">
                                            Selected Files
                                        </h3>
                                        <p className="text-xl text-stone-300">
                                            {fileCount} file
                                            {fileCount > 1 ? "s" : ""} ready to
                                            upload
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => setShowFileList(false)}
                                        className="text-stone-400 hover:text-white hover:bg-stone-600 w-8 h-8 flex items-center justify-center transition-all duration-200 text-3xl font-bold"
                                        title="Close"
                                    >
                                        X
                                    </button>
                                </div>
                            </div>

                            {/* File List */}
                            <div className="max-h-[600px] overflow-y-auto custom-scrollbar">
                                <div className="p-6">
                                    {file &&
                                        Array.from(file).map(
                                            (selectedFile, index) => (
                                                <div
                                                    key={index}
                                                    className="group flex items-center justify-between p-8 m-4 hover:bg-stone-700 rounded-xl transition-all duration-200 border border-transparent hover:border-stone-500/30"
                                                >
                                                    <div className="flex items-center flex-1 min-w-0">
                                                        <div className="text-xl font-semibold text-white truncate group-hover:text-blue-200 transition-colors">
                                                            {selectedFile.name}
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center flex-1 min-w-0">
                                                        <div className="flex items-center space-x-4 mt-2">
                                                            <span className="text-lg text-stone-400 bg-stone-800/50 px-4 py-3 rounded-full">
                                                                {(
                                                                    selectedFile.size / 1024
                                                                ).toFixed(
                                                                    1
                                                                )}{" "}
                                                                KB
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center flex-1 min-w-0">
                                                        <span className="text-lg text-stone-500 capitalize">
                                                            {selectedFile.type.split(
                                                                "/"
                                                            )[0] || "file"}
                                                        </span>
                                                    </div>

                                                    {/* Remove Button */}
                                                    <button
                                                        onClick={() =>
                                                            removeFile(index)
                                                        }
                                                        className="ml-8 w-8 h-8 bg-red-500/20 hover:bg-red-500 text-red-400 hover:text-white flex items-center justify-center transition-all duration-200 hover:scale-110 group-hover:opacity-100 opacity-80"
                                                        title="Remove file"
                                                    >
                                                        <span className="text-2xl font-bold">
                                                            X
                                                        </span>
                                                    </button>

                                                </div>
                                            )
                                        )}
                                </div>
                            </div>

                            {/* Footer */}
                            <div className="bg-stone-800 to-stone-700 px-12 py-6 rounded-b-xl border-t border-stone-600/30">
                                <div className="flex justify-between items-center text-lg text-stone-300">
                                    <span>
                                        Total:{" "}
                                        {file
                                            ? (
                                                  Array.from(file).reduce(
                                                      (acc, f) => acc + f.size,
                                                      0
                                                  ) / 1024
                                              ).toFixed(1)
                                            : 0}{" "}
                                        KB
                                    </span>
                                    <span>Click × to remove files</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
                
                {" "}
                <div className="py-4">
                    {isLoading && (
                        <div className="w-full max-w-lg mx-auto bg-stone-900 opacity-90 to-black text-white p-6 rounded-md">
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
                                <p className="text-lg font-medium">
                                    Analyzing your query...
                                </p>
                                <p className="text-sm text-stone-400">
                                    This may take a moment
                                </p>
                            </div>
                        </div>
                    )}

                    {!isLoading && answer && (
                        <div className="w-full max-w-lg mx-auto bg-stone-900 opacity-90 text-white p-4 rounded-md space-y-4">
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
                    )}
                </div>
            </div>

        </div>
    );
}
