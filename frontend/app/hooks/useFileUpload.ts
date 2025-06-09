import { useState } from "react";
import { FormState } from "../types";
import {
    mergeFileLists,
    filterValidFiles,
    removeFileFromList,
} from "../utils/fileUtils";

export const useFileUpload = () => {
    const [file, setFile] = useState<FileList | null>(null);
    const [fileCount, setFileCount] = useState<number>(0);
    const [isDragging, setIsDragging] = useState<boolean>(false);
    const [showFileList, setShowFileList] = useState<boolean>(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFiles = e.target.files;
        if (selectedFiles) {
            const validFiles = filterValidFiles(selectedFiles);
            const mergedFiles = mergeFileLists(file, validFiles);
            setFile(mergedFiles);
            setFileCount(mergedFiles.length);
        }
    };

    const removeFile = (indexToRemove: number) => {
        if (file) {
            const newFileList = removeFileFromList(file, indexToRemove);
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

    const closeFileList = () => {
        setShowFileList(false);
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
    return {
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
    };
};
