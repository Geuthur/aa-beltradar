// React
import React from 'react'
import ReactDOM from "react-dom/client";

// AA Belt Radar
import App from './App.tsx'

const container = document.getElementById('aa-beltradar-root')

if (!container) {
  throw new Error('Belt Radar React mount point was not found.')
}

ReactDOM.createRoot(container).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
