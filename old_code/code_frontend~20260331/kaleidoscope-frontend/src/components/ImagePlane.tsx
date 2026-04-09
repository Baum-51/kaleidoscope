import React from "react";
import { useLoader } from '@react-three/fiber';
import * as THREE  from 'three';
import type { ImagePlaneProps } from "../types/types";

const ImagePlane: React.FC<ImagePlaneProps> = ({ imageUrl }) => {
    const texture = useLoader(THREE.TextureLoader, imageUrl)

    return (
        <mesh>
            <planeGeometry args={[5, 5]} />
            <meshBasicMaterial map={texture} />
        </mesh>
    )
}

export default ImagePlane