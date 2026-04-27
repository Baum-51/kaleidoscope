const common = `
    float rand(vec2 co) {
        return fract(sin(dot(co, vec2(12.9898,78.233))) * 43758.5453);
    }
    float getGray(vec2 uv) {
        vec3 color = texture2D(uTexture, uv).rgb;
        return dot(color.rgb, vec3(0.299, 0.587, 0.114));
    }
`
const snow = `
    float getParticle(vec2 uv, float depth, float uTime) {
        // 粒子のサイズ
        float scale = mix(30.0, 8.0, depth);
        vec2 gv = uv * scale;

        // セル
        vec2 id = floor(gv);

        float t = uTime;
        float wind = (rand(id + 2.0) - 0.5) * 0.1;
        float fall = t * (0.2 + rand(id)) * 0.1;
        vec2 motion = vec2(wind * t, fall);

        vec2 gv2 = (vUv + motion) * scale;
        vec2 id2 = floor(gv2);
        vec2 f2 = fract(gv2);
        float particleDepth = rand(id2);
        
        // 奥に寄せる
        particleDepth = pow(particleDepth, 2.0);

        vec2 offset2 = vec2(
        rand(id2),
        rand(id2 + 1.0)
        );

        float d2 = length(f2 - offset2);

        float particleSize = mix(0.15, 0.05, particleDepth);
        float particle = smoothstep(particleSize, 0.0, d2);
        float occlusion = smoothstep(particleDepth - 0.05, particleDepth, depth);
        particle *= occlusion;

        float sparkle = 0.7 + 0.3 * sin(uTime + rand(id2)*10.0);
        return particle * sparkle;
    }
`

const getSegColor = `
        vec3 getColor(int label) {
            if (label == 0) return vec3(0.2, 0.4, 1.0); // 空
            if (label == 1) return vec3(1.0, 0.8, 0.6); // 建物
            if (label == 2) return vec3(0.2, 1.0, 0.4); // 植物
            if (label == 3) return vec3(0.5, 0.5, 0.5); // 道
            return vec3(1.0);
        }
`

export const fragmentShader = `
    uniform sampler2D uTexture;
    uniform sampler2D uDepth;
    uniform float uTime;
    uniform vec2 resolution;

    uniform sampler2D uSeg;

    varying vec2 vUv;

    ${common}
    ${snow}
    ${getSegColor}

    void main() {
        vec2 uv = vUv;
        vec2 baseUv = uv; // 元の座標

        vec2 effectUv = baseUv;
        effectUv += vec2(
        sin(baseUv.y * 5.0 + uTime) * 0.02,
        -uTime * 0.1
        );

        vec4 color = texture2D(uTexture, vUv);
        float depth = texture2D(uDepth, vUv).r;
        depth = 1.0 - depth;

        float particle = getParticle(uv, depth, uTime);

        vec2 texel = 1.0 / resolution;

        float tl = getGray(uv + texel * vec2(-1.0, 1.0));
        float tc = getGray(uv + texel * vec2( 0.0, 1.0));
        float tr = getGray(uv + texel * vec2( 1.0, 1.0));

        float ml = getGray(uv + texel * vec2(-1.0, 0.0));
        float mr = getGray(uv + texel * vec2( 1.0, 0.0));

        float bl = getGray(uv + texel * vec2(-1.0, -1.0));
        float bc = getGray(uv + texel * vec2( 0.0, -1.0));
        float br = getGray(uv + texel * vec2( 1.0, -1.0));

        float gx =
            -1.0 * tl + 1.0 * tr +
            -2.0 * ml + 2.0 * mr +
            -1.0 * bl + 1.0 * br;
        float gy =
            -1.0 * tl -2.0 * tc -1.0 * tr +
             1.0 * bl +2.0 * bc +1.0 * br;

        float edge = length(vec2(gx, gy));

        float seg = texture2D(uSeg, vUv).r;
        int label = int(seg * 255.0);

        vec3 baseColor = texture2D(uTexture, vUv).rgb;

        vec3 segColor = baseColor * getColor(label);;

        

        vec3 snowColor = vec3(0.7, 0.7, 1.0);
        vec3 finalColor = color.rgb - edge + particle * snowColor * 2.0 + segColor;
        gl_FragColor = vec4(finalColor, 1.0);
    }
`