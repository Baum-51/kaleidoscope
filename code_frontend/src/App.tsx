import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three';
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'


const constraints: MediaStreamConstraints = {
  audio: false,
  video: true,
}

function App() {
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || !remoteVideoRef.current) return

    const scene = new THREE.Scene()
    const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)

    const renderer = new THREE.WebGLRenderer({
      canvas: canvasRef.current
    })
    renderer.setSize(640, 480)

    // video -> texture
    const texture = new THREE.VideoTexture(videoRef.current)
    const depthTexture = new THREE.VideoTexture(remoteVideoRef.current)

    const material = new THREE.ShaderMaterial({
      uniforms: {
        uTexture: { value: texture },
        uDepth: { value: depthTexture },
        uTime: {value: 0},
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D uTexture;
        uniform sampler2D uDepth;
        uniform float uTime;

        varying vec2 vUv;

        float rand(vec2 co) {
          return fract(sin(dot(co, vec2(12.9898,78.233))) * 43758.5453);
        }

        void main() {
          vec2 uv = vUv;
          uv += vec2(
            sin(uv.y * 5.0 + uTime) * 0.02,
            -uTime * 0.1
          );

          vec4 color = texture2D(uTexture, vUv);
          float depth = texture2D(uDepth, vUv).r;
          depth = 1.0 - depth;

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
          // particleDepth = pow(particleDepth, 2.0);
          float particleSize = mix(0.15, 0.05, particleDepth);

          vec2 offset2 = vec2(
            rand(id2),
            rand(id2 + 1.0)
          );

          float d2 = length(f2 - offset2);
          float particle = smoothstep(particleSize, 0.0, particleDepth);
          // float particle = smoothstep(0.1, 0.0, d2);
          if (depth < particle) {
            particle = 0.0;
          }

          float sparkle = 0.7 + 0.3 * sin(uTime + rand(id2)*10.0);
          particle *= sparkle;

          vec3 snowColor = vec3(0.7, 0.7, 1.0);
          vec3 finalColor = color.rgb + particle * snowColor;
          gl_FragColor = vec4(finalColor, 1.0);
        }
      `,
    })

    const geometry = new THREE.PlaneGeometry(2, 2)
    const mesh = new THREE.Mesh(geometry, material)
    scene.add(mesh)

    const start = async () => {
      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }

      const pc = new RTCPeerConnection()
      pc.ontrack = (event) => {
        if (remoteVideoRef.current) {
          remoteVideoRef.current.srcObject = event.streams[0]
        }
      }
      // 送信
      stream.getTracks().forEach(track => {
        pc.addTrack(track, stream)
      })

      // offer作成
      const offer = await pc.createOffer()
      await pc.setLocalDescription(offer)

      // FastAPIに送信
      const res = await fetch("http://localhost:8000/offer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          sdp: pc.localDescription?.sdp,
          type: pc.localDescription?.type
        }),
      })
      const answer = await res.json()
      await pc.setRemoteDescription(answer)
    }

    const startTime = Date.now()
    const render = () => {
      requestAnimationFrame(render)

      const elapsed = (Date.now() - startTime) / 1000
      material.uniforms.uTime.value = elapsed
      renderer.render(scene, camera)
    }

    start()
    render()
  }, []);

  return (
    <div className='App'>
      hello world!!
      <p>Web Camera Sample</p>
      <div style={{display: 'grid'}}>
        <div>
          <h2>Local</h2>
          <video autoPlay playsInline={true} ref={videoRef} style={{ width: '45%'}} />
          <h2>Processed（from backend）</h2>
          <video autoPlay playsInline={true} ref={remoteVideoRef} style={{width: '45%'}} />
          <h2>Processed（from three.js）</h2>
          <canvas ref={canvasRef} />
        </div>
      </div>
    </div>
  )
}

export default App
