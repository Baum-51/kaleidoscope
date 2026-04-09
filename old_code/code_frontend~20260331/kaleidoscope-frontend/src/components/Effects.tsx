import React from "react";
import {
    EffectComposer,
    Bloom,
    Noise,
    Vignette,
} from '@react-three/postprocessing';
import type { EffectsProps } from "../types/types";

const Effects: React.FC<EffectsProps> = ({ world }) => {
    if (world === 'magic') {
        return (
            <EffectComposer>
                <Bloom intensity={1.5} luminanceThreshold={0.2} />
                <Noise opacity={0.15} />
                <Vignette eskil={false} offeset={0.1} darkness={0.8} />
            </EffectComposer>
        )
    }
    if (world === 'apocalypse') {
        return (
            <EffectComposer>
                <Noise opacity={0.3} />
                <Vignette eskil={false} offset={0.2} darkness={1.2} />
            </EffectComposer>
        )
    }
}

export default Effects