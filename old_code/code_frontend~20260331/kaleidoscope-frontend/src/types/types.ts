export type WorldType = 'magic' | 'apocalypse'

export interface CanvasViewProps {
    imageUrl: string;
    world: WorldType;
};

export interface ImagePlaneProps {
    imageUrl: string;
};

export interface EffectsProps {
    world: WorldType
}