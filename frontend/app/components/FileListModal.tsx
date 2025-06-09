import React from "react";

interface FileListModalProps {
    showFileList: boolean;
    fileCount: number;
    file: FileList | null;
    onClose: () => void;
    onRemoveFile: (index: number) => void;
}

const FileListModal: React.FC<FileListModalProps> = ({
    showFileList,
    fileCount,
    file,
    onClose,
    onRemoveFile,
}) => {
    if (!showFileList || fileCount === 0) return null;

    return (
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
                                {fileCount} file{fileCount > 1 ? "s" : ""} ready
                                to upload
                            </p>
                        </div>
                        <button
                            onClick={onClose}
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
                            Array.from(file).map((selectedFile, index) => (
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
                                                ).toFixed(1)}{" "}
                                                KB
                                            </span>
                                        </div>
                                    </div>
                                    <div className="flex items-center flex-1 min-w-0">
                                        <span className="text-lg text-stone-500 capitalize">
                                            {selectedFile.type.split("/")[0] ||
                                                "file"}
                                        </span>
                                    </div>

                                    {/* Remove Button */}
                                    <button
                                        onClick={() => onRemoveFile(index)}
                                        className="ml-8 w-8 h-8 bg-red-500/20 hover:bg-red-500 text-red-400 hover:text-white flex items-center justify-center transition-all duration-200 hover:scale-110 group-hover:opacity-100 opacity-80"
                                        title="Remove file"
                                    >
                                        <span className="text-2xl font-bold">
                                            X
                                        </span>
                                    </button>
                                </div>
                            ))}
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
    );
};

export default FileListModal;
