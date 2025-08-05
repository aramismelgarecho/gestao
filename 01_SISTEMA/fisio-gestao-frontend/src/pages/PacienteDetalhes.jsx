import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, FileText, TrendingUp, Calendar, Download, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export function PacienteDetalhes() {
  const { id } = useParams()
  const [paciente, setPaciente] = useState(null)
  const [prontuario, setProntuario] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    carregarPaciente()
    carregarProntuario()
  }, [id])

  const carregarPaciente = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/pacientes/${id}`)
      const data = await response.json()
      setPaciente(data)
    } catch (error) {
      console.error('Erro ao carregar paciente:', error)
      // Mock data para desenvolvimento
      setPaciente({
        id: 1,
        nome_completo: 'Maria Silva Santos',
        data_nascimento: '1985-03-15',
        genero: 'Feminino',
        telefone: '(51) 99999-9999',
        email: 'maria@email.com',
        endereco_residencial: 'Rua das Flores, 123 - Centro - Porto Alegre/RS',
        profissao: 'Professora',
        estado_civil: 'Casada',
        naturalidade: 'Porto Alegre',
        ativo: true,
        arquivado: false
      })
    }
    setLoading(false)
  }

  const carregarProntuario = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/pacientes/${id}/prontuario`)
      const data = await response.json()
      setProntuario(data)
    } catch (error) {
      console.error('Erro ao carregar prontuário:', error)
      // Mock data para desenvolvimento
      setProntuario({
        avaliacoes: [
          {
            id: 1,
            data_avaliacao: '2024-01-15T10:00:00',
            queixa_principal: 'Dor lombar há 3 meses',
            diagnostico_fisioterapeutico: 'Lombalgia mecânica',
            objetivos_terapeuticos: 'Reduzir dor e melhorar mobilidade'
          }
        ],
        evolucoes: [
          {
            id: 1,
            data_sessao: '2024-01-20T14:00:00',
            procedimentos_realizados: 'Exercícios de fortalecimento',
            resposta_paciente: 'Boa evolução, redução da dor'
          }
        ],
        agendamentos: [
          {
            id: 1,
            data_hora: '2024-01-25T15:00:00',
            status: 'agendado',
            observacoes: 'Sessão de acompanhamento'
          }
        ]
      })
    }
  }

  const calcularIdade = (dataNascimento) => {
    const hoje = new Date()
    const nascimento = new Date(dataNascimento)
    let idade = hoje.getFullYear() - nascimento.getFullYear()
    const mes = hoje.getMonth() - nascimento.getMonth()
    
    if (mes < 0 || (mes === 0 && hoje.getDate() < nascimento.getDate())) {
      idade--
    }
    
    return idade
  }

  const formatarData = (data) => {
    return new Date(data).toLocaleDateString('pt-BR')
  }

  const formatarDataHora = (data) => {
    return new Date(data).toLocaleString('pt-BR')
  }

  const exportarProntuario = () => {
    // TODO: Implementar exportação em PDF
    alert('Funcionalidade de exportação em PDF será implementada')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Carregando...</p>
        </div>
      </div>
    )
  }

  if (!paciente) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900">Paciente não encontrado</h2>
        <Link to="/pacientes">
          <Button className="mt-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Voltar para Pacientes
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/pacientes">
            <Button variant="outline" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{paciente.nome_completo}</h1>
            <p className="text-gray-600 mt-1">
              {calcularIdade(paciente.data_nascimento)} anos • {paciente.genero}
            </p>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button onClick={exportarProntuario} variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Exportar Prontuário
          </Button>
          <Link to={`/avaliacoes?paciente_id=${id}`}>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Nova Avaliação
            </Button>
          </Link>
        </div>
      </div>

      {/* Patient Info */}
      <Card>
        <CardHeader>
          <CardTitle>Informações Pessoais</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Data de Nascimento</label>
              <p className="text-gray-900">{formatarData(paciente.data_nascimento)}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Estado Civil</label>
              <p className="text-gray-900">{paciente.estado_civil || 'Não informado'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Profissão</label>
              <p className="text-gray-900">{paciente.profissao || 'Não informado'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Telefone</label>
              <p className="text-gray-900">{paciente.telefone || 'Não informado'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">E-mail</label>
              <p className="text-gray-900">{paciente.email || 'Não informado'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Naturalidade</label>
              <p className="text-gray-900">{paciente.naturalidade || 'Não informado'}</p>
            </div>
            {paciente.endereco_residencial && (
              <div className="md:col-span-2 lg:col-span-3">
                <label className="text-sm font-medium text-gray-500">Endereço Residencial</label>
                <p className="text-gray-900">{paciente.endereco_residencial}</p>
              </div>
            )}
          </div>
          <div className="flex gap-2 mt-4">
            {paciente.arquivado && (
              <Badge variant="secondary">Arquivado</Badge>
            )}
            {!paciente.ativo && (
              <Badge variant="destructive">Inativo</Badge>
            )}
            {paciente.ativo && !paciente.arquivado && (
              <Badge variant="default">Ativo</Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Prontuário Tabs */}
      <Tabs defaultValue="avaliacoes" className="space-y-4">
        <TabsList>
          <TabsTrigger value="avaliacoes">
            <FileText className="mr-2 h-4 w-4" />
            Avaliações ({prontuario?.avaliacoes?.length || 0})
          </TabsTrigger>
          <TabsTrigger value="evolucoes">
            <TrendingUp className="mr-2 h-4 w-4" />
            Evoluções ({prontuario?.evolucoes?.length || 0})
          </TabsTrigger>
          <TabsTrigger value="agendamentos">
            <Calendar className="mr-2 h-4 w-4" />
            Agendamentos ({prontuario?.agendamentos?.length || 0})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="avaliacoes">
          <div className="space-y-4">
            {prontuario?.avaliacoes?.length > 0 ? (
              prontuario.avaliacoes.map((avaliacao) => (
                <Card key={avaliacao.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">
                          Avaliação - {formatarData(avaliacao.data_avaliacao)}
                        </CardTitle>
                        <p className="text-sm text-gray-500 mt-1">
                          {avaliacao.diagnostico_fisioterapeutico}
                        </p>
                      </div>
                      <Link to={`/avaliacoes/${avaliacao.id}`}>
                        <Button size="sm" variant="outline">
                          Ver Detalhes
                        </Button>
                      </Link>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Queixa Principal</label>
                        <p className="text-gray-900">{avaliacao.queixa_principal}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Objetivos Terapêuticos</label>
                        <p className="text-gray-900">{avaliacao.objetivos_terapeuticos}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Nenhuma avaliação registrada
                  </h3>
                  <p className="text-gray-500 mb-4">
                    Comece criando a primeira avaliação para este paciente.
                  </p>
                  <Link to={`/avaliacoes?paciente_id=${id}`}>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Nova Avaliação
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="evolucoes">
          <div className="space-y-4">
            {prontuario?.evolucoes?.length > 0 ? (
              prontuario.evolucoes.map((evolucao) => (
                <Card key={evolucao.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-lg">
                        Evolução - {formatarDataHora(evolucao.data_sessao)}
                      </CardTitle>
                      <Link to={`/evolucoes/${evolucao.id}`}>
                        <Button size="sm" variant="outline">
                          Ver Detalhes
                        </Button>
                      </Link>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Procedimentos Realizados</label>
                        <p className="text-gray-900">{evolucao.procedimentos_realizados}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Resposta do Paciente</label>
                        <p className="text-gray-900">{evolucao.resposta_paciente}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <TrendingUp className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Nenhuma evolução registrada
                  </h3>
                  <p className="text-gray-500 mb-4">
                    Registre as evoluções das sessões de tratamento.
                  </p>
                  <Link to={`/evolucoes?paciente_id=${id}`}>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Nova Evolução
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="agendamentos">
          <div className="space-y-4">
            {prontuario?.agendamentos?.length > 0 ? (
              prontuario.agendamentos.map((agendamento) => (
                <Card key={agendamento.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">
                          {formatarDataHora(agendamento.data_hora)}
                        </CardTitle>
                        <Badge className={`mt-2 ${
                          agendamento.status === 'confirmado' 
                            ? 'bg-green-100 text-green-800' 
                            : agendamento.status === 'realizado'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {agendamento.status === 'confirmado' ? 'Confirmado' : 
                           agendamento.status === 'realizado' ? 'Realizado' : 'Agendado'}
                        </Badge>
                      </div>
                      <Link to={`/agendamentos/${agendamento.id}`}>
                        <Button size="sm" variant="outline">
                          Ver Detalhes
                        </Button>
                      </Link>
                    </div>
                  </CardHeader>
                  {agendamento.observacoes && (
                    <CardContent>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Observações</label>
                        <p className="text-gray-900">{agendamento.observacoes}</p>
                      </div>
                    </CardContent>
                  )}
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Nenhum agendamento encontrado
                  </h3>
                  <p className="text-gray-500 mb-4">
                    Agende sessões de tratamento para este paciente.
                  </p>
                  <Link to={`/agendamentos?paciente_id=${id}`}>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Novo Agendamento
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

