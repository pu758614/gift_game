import { Routes, Route } from 'react-router-dom'
import FormPage from './pages/FormPage'
import ConfirmPage from './pages/ConfirmPage'
import SuccessPage from './pages/SuccessPage'
import GalleryPage from './pages/GalleryPage'
import ExchangePage from './pages/ExchangePage'
import VotingPage from './pages/VotingPage'
import ResultPage from './pages/ResultPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<FormPage />} />
      <Route path="/confirm/:giftId" element={<ConfirmPage />} />
      <Route path="/success/:giftId" element={<SuccessPage />} />
      <Route path="/gallery" element={<GalleryPage />} />
      <Route path="/exchange" element={<ExchangePage />} />
      <Route path="/voting" element={<VotingPage />} />
      <Route path="/result" element={<ResultPage />} />
    </Routes>
  )
}

export default App
