import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Sidebar } from '@/components/Sidebar'
import { Header } from '@/components/Header'
import { Dashboard } from '@/pages/Dashboard'
import { Pacientes } from '@/pages/PacientesSimples'
import { PacienteDetalhes } from '@/pages/PacienteDetalhes'
import { Avaliacoes, Evolucoes, Agendamentos, Procedimentos } from '@/pages/index'
import './App.css'

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/pacientes" element={<Pacientes />} />
              <Route path="/pacientes/:id" element={<PacienteDetalhes />} />
              <Route path="/avaliacoes" element={<Avaliacoes />} />
              <Route path="/evolucoes" element={<Evolucoes />} />
              <Route path="/agendamentos" element={<Agendamentos />} />
              <Route path="/procedimentos" element={<Procedimentos />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App

