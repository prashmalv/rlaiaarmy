import { Routes, Route } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { NewProject } from './pages/NewProject'
import { ProjectDashboard } from './pages/ProjectDashboard'
import { ProjectsList } from './pages/ProjectsList'
import { Home } from './pages/Home'

export default function App() {
  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/new" element={<NewProject />} />
          <Route path="/projects" element={<ProjectsList />} />
          <Route path="/projects/:id" element={<ProjectDashboard />} />
        </Routes>
      </main>
    </div>
  )
}
