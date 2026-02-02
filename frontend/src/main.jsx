import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  //get rid of string mode in prod
  <StrictMode> 
    <App />
  </StrictMode>,
)
