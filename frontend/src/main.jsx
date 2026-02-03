import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  //strict mode is just for dev (its like debug=true)
  <StrictMode>
    <App />
  </StrictMode>,
)
