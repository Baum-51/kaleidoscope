import React, { useState} from "react"

function App() {
  const [world, setworld] = useState<string>("magic");
  const [file, setFile] = useState<File | null>(null);
  const [originalUrl, setOriginalUrl] = useState<string>("");
  const [imageUrl, setImageUrl] = useState<string>("");
  const [slider, setSlider] = useState<number>(50);

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    
    setFile(f);
    setOriginalUrl(URL.createObjectURL(f));
  };

  const handleUpload = async() => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("world_type", world);

    const res = await fetch("/transform", {
      method: "POST",
      body: formData
    });

    const blob = await res.blob();
    setImageUrl(URL.createObjectURL(blob));
  };

  const baseStyle = {
  position: "absolute" as const,
  width: "100%",
  height: "100%",
  objectFit: "contain" as const,
  left: 0
};


  return (
    <div>
      <input type="file" onChange={handleFile} />

      <select onChange={(e) => setworld(e.target.value)}>
        <option value="magic">魔法世界</option>
        <option value="ruin">滅亡世界</option>
      </select>

      <button onClick={handleUpload}>変換</button>

      {/* スライダー */}
      <div style={{
        position: "relative",
        width: "500px",
        height: "500px",
        margin: "auto",
        marginTop: "20px"
      }}>
        {/* 元画像 */}
        {originalUrl && (
          <img
            src={originalUrl}
            style={baseStyle}
          />
        )}
        {/* 変換画像 */}
        {imageUrl && (
          <img
            src={imageUrl}
            style={{
              ...baseStyle,
              clipPath: `inset(0 ${100 - slider}% 0 0)`
            }}
          />
        )}

        {/* スライダーUI */}
        <input
          type="range"
          min="0"
          max="100"
          value={slider}
          onChange={(e) => setSlider(Number(e.target.value))}
          style={{
            position: "absolute",
            bottom: "10px",
            width: "100%",
            left: 0
          }}
        />
        <div style={{
          position: "absolute",
          left: `${slider}%`,
          top: 0,
          bottom: 0,
          width: "2px",
          background: "white"
        }}></div>
      </div>
    </div>
  )
};

export default App