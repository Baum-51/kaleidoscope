import { Canvas } from "@react-three/fiber";
import React, { Suspense } from 'react';
import ImagePlane from  './ImagePlane'
import Effects from './Effects'
import type { CanvasViewProps } from "../types/types";


const CanvasView: React.FC<CanvasViewProps> = ({ imageUrl, world }) => {
    return (
        <Canvas>
            <Suspense fallback={null}>
                <ImagePlane imageUrl={imageUrl} />
                <Effects world={world} />
            </Suspense>
        </Canvas>
    )
}

export default CanvasView