"use client";

import { useState, useRef } from "react";
import Image from "next/image";

export default function Home() {
    const [prompt, setPrompt] = useState<string>("");
    const [file, setFile] = useState<FileList | null>(null);
    const [fileCount, setFileCount] = useState<number>(0);
    const [answer, setAnswer] = useState<string | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const handleSubmit = async () => {
        
    };

    const handleClick = () => {
        inputRef.current?.click();
    };

    const getFile = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files;
        setFile(selectedFile);
        if (selectedFile) {
            setFileCount(selectedFile.length);
        } else {
            setFileCount(0);
        }
    };

    return (
        <div className="px-3 py-40 text-center">
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
