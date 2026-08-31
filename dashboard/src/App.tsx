import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Overview } from './pages/Overview'
import { TenderList } from './pages/TenderList'
import { TenderDetail } from './pages/TenderDetail'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Overview />} />
          <Route path="/tenders" element={<TenderList />} />
          <Route path="/tenders/:tenderId" element={<TenderDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
