import React, { useState } from 'react';
import CanvasView from './components/CanvasView'
import type { WorldType } from './types/types'

function App() {
  const [imageUrl, setImageUrl] = useState<string>('')
  const [world, setWorld] = useState<WorldType>('magic')

  return (
    <>
      <input
        type='file'
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
          const file = e.target.files?.[0]
          if (file) {
            setImageUrl(URL.createObjectURL(file))
          }
        }}
      />
      
      <select
        value={world}
        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => 
          setWorld(e.target.value as WorldType)
        }
      >
        <option value='magic'>魔法世界</option>
        <option value='apocalypse'>滅亡世界</option>
      </select>

      <CanvasView imageUrl={imageUrl} world={world} />
    </>
  )
}

export default App