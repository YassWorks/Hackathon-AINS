import React from "react";

interface DragOverlayProps {
    isDragging: boolean;
}

const DragOverlay: React.FC<DragOverlayProps> = ({ isDragging }) => {
    if (!isDragging) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center pointer-events-none">
            <div className="bg-gradient-to-br from-stone-900 to-black text-white p-8 rounded-lg border-2 border-dashed border-white">
                <div className="text-2xl font-bold mb-2">Drop files here</div>
                <div className="text-sm opacity-70">
                    Images and audio files only
                </div>
            </div>
        </div>
    );
};

export default DragOverlay;
