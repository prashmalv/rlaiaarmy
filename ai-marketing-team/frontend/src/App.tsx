import { Routes, Route } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { Dashboard } from './pages/Dashboard'
import { DailyRun } from './pages/DailyRun'
import { ContentQueue } from './pages/ContentQueue'
import { LeadsPage } from './pages/LeadsPage'
import { OpportunitiesPage } from './pages/OpportunitiesPage'
import { CalendarPage } from './pages/CalendarPage'
import { GeneratePage } from './pages/GeneratePage'

export default function App() {
  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/run" element={<DailyRun />} />
          <Route path="/content" element={<ContentQueue />} />
          <Route path="/leads" element={<LeadsPage />} />
          <Route path="/opportunities" element={<OpportunitiesPage />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/generate" element={<GeneratePage />} />
        </Routes>
      </main>
    </div>
  )
}
