import { useState, useEffect } from 'react'
import { Users, Calendar, FileText, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Link } from 'react-router-dom'

export function Dashboard() {
  const [stats, setStats] = useState({
    totalPacientes: 0,
    agendamentosHoje: 0,
    avaliacoesPendentes: 0,
    evolucoesSemana: 0
  })

  const [agendamentosHoje, setAgendamentosHoje] = useState([])

  useEffect(() => {
    // TODO: Buscar dados reais da API
    setStats({
      totalPacientes: 45,
      agendamentosHoje: 8,
      avaliacoesPendentes: 3,
      evolucoesSemana: 24
    })

    setAgendamentosHoje([
      { id: 1, paciente: 'Maria Silva', horario: '09:00', status: 'confirmado' },
      { id: 2, paciente: 'João Santos', horario: '10:30', status: 'agendado' },
      { id: 3, paciente: 'Ana Costa', horario: '14:00', status: 'confirmado' },
      { id: 4, paciente: 'Pedro Lima', horario: '15:30', status: 'agendado' },
    ])
  }, [])

  const statCards = [
    {
      title: 'Total de Pacientes',
      value: stats.totalPacientes,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      link: '/pacientes'
    },
    {
      title: 'Agendamentos Hoje',
      value: stats.agendamentosHoje,
      icon: Calendar,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      link: '/agendamentos'
    },
    {
      title: 'Avaliações Pendentes',
      value: stats.avaliacoesPendentes,
      icon: FileText,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      link: '/avaliacoes'
    },
    {
      title: 'Evoluções esta Semana',
      value: stats.evolucoesSemana,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      link: '/evolucoes'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Bem-vindo ao sistema de gestão para fisioterapeutas
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Link key={index} to={stat.link}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    {stat.title}
                  </CardTitle>
                  <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                    <Icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-gray-900">
                    {stat.value}
                  </div>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </div>

      {/* Quick Actions and Today's Schedule */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Ações Rápidas</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link to="/pacientes">
              <Button className="w-full justify-start" variant="outline">
                <Users className="mr-2 h-4 w-4" />
                Cadastrar Novo Paciente
              </Button>
            </Link>
            <Link to="/agendamentos">
              <Button className="w-full justify-start" variant="outline">
                <Calendar className="mr-2 h-4 w-4" />
                Agendar Consulta
              </Button>
            </Link>
            <Link to="/avaliacoes">
              <Button className="w-full justify-start" variant="outline">
                <FileText className="mr-2 h-4 w-4" />
                Nova Avaliação
              </Button>
            </Link>
            <Link to="/evolucoes">
              <Button className="w-full justify-start" variant="outline">
                <TrendingUp className="mr-2 h-4 w-4" />
                Registrar Evolução
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Today's Schedule */}
        <Card>
          <CardHeader>
            <CardTitle>Agendamentos de Hoje</CardTitle>
          </CardHeader>
          <CardContent>
            {agendamentosHoje.length > 0 ? (
              <div className="space-y-3">
                {agendamentosHoje.map((agendamento) => (
                  <div 
                    key={agendamento.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <div className="font-medium text-gray-900">
                        {agendamento.paciente}
                      </div>
                      <div className="text-sm text-gray-500">
                        {agendamento.horario}
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      agendamento.status === 'confirmado' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {agendamento.status === 'confirmado' ? 'Confirmado' : 'Agendado'}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                Nenhum agendamento para hoje
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

