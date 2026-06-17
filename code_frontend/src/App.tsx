import { useEffect, useRef } from 'react'
import * as THREE from 'three';
import './App.css'

import { vertexShader } from './shaders/vertex';
import { fragmentShader } from './shaders/fragment';


const constraints: MediaStreamConstraints = {
  audio: false,
  video: true,
}

function App() {
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // const depthRef = useRef<THREE.DataTexture>(null)
  // const segRef = useRef<THREE.DataTexture>(null)
  const depthRef = useRef<THREE.DataTexture>(
    new THREE.DataTexture(
      new Float32Array(192*192).fill(0.0),
      192,
      192,
      THREE.RedFormat,
      THREE.FloatType
    )
  )
  const segRef = useRef<THREE.DataTexture>(
    new THREE.DataTexture(
      new Uint8Array(192*192).fill(0),
      192,
      192,
      THREE.RedFormat,
    )
  )

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
    // const depthTexture = new THREE.VideoTexture(remoteVideoRef.current)
    const depthValue = depthRef.current
    const segValue = segRef.current

    const material = new THREE.ShaderMaterial({
      uniforms: {
        uTexture: { value: texture },
        // uDepth: { value: depthTexture },
        uDepth: { value: depthValue },
        uTime: {value: 0},
        resolution: { value: new THREE.Vector2(canvasRef.current.width, canvasRef.current.height) },
        uSeg: { value: segValue },
      },
      vertexShader: vertexShader,
      fragmentShader: fragmentShader,
    })

    material.uniforms.resolution.value.set(
      renderer.domElement.width,
      renderer.domElement.height,
    )

    const geometry = new THREE.PlaneGeometry(2, 2)
    const mesh = new THREE.Mesh(geometry, material)
    scene.add(mesh)

    const start = async () => {
      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }

      const pc = new RTCPeerConnection()
      const channel = pc.createDataChannel("result")
      pc.ontrack = (event) => {
        if (remoteVideoRef.current) {
          remoteVideoRef.current.srcObject = event.streams[0]
        }
      }
      // 送信
      stream.getTracks().forEach(track => {
        pc.addTrack(track, stream)
      })
      channel.onmessage = (e) => {
        const data = JSON.parse(e.data)
        if (depthRef.current) {
          const depth = data['depth'].flat()
          depthRef.current.image.data?.set(new Float32Array(depth))
          depthRef.current.needsUpdate = true
        }
        if (segRef.current) {
          const seg = data['seg'].flat()
          segRef.current.image.data?.set(new Uint8Array(seg))
          segRef.current.needsUpdate = true
        }
      }

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
