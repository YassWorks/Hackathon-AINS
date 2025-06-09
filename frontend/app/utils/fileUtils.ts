// Helper function to get verdict color based on verdict type
export const getVerdictColor = (verdict: string): string => {
    const upperVerdict = verdict.toUpperCase();
    if (upperVerdict === "FACT") return "text-green-400";
    if (upperVerdict === "MYTH") return "text-orange-400";
    if (upperVerdict === "SCAM") return "text-red-400";
    return "text-white"; // default color
};

// Helper function to merge FileList objects
export const mergeFileLists = (
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
export const filterValidFiles = (files: FileList): FileList => {
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

// Helper function to remove file from FileList
export const removeFileFromList = (
    fileList: FileList,
    indexToRemove: number
): FileList => {
    const dataTransfer = new DataTransfer();

    // Add all files except the one to remove
    for (let i = 0; i < fileList.length; i++) {
        if (i !== indexToRemove) {
            dataTransfer.items.add(fileList[i]);
        }
    }

    return dataTransfer.files;
};
