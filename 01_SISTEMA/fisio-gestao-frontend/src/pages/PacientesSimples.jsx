import { useState, useEffect } from 'react'
import { Plus, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function Pacientes() {
  const [pacientes, setPacientes] = useState([])
  const [filtros, setFiltros] = useState({
    nome: '',
    ativo: true,
    arquivado: false
  })

  useEffect(() => {
    // Mock data para desenvolvimento
    setPacientes([
      {
        id: 1,
        nome_completo: 'Maria Silva Santos',
        data_nascimento: '1985-03-15',
        genero: 'Feminino',
        telefone: '(51) 99999-9999',
        email: 'maria@email.com',
        ativo: true,
        arquivado: false,
        data_criacao: '2024-01-15T10:00:00'
      },
      {
        id: 2,
        nome_completo: 'João Carlos Oliveira',
        data_nascimento: '1978-07-22',
        genero: 'Masculino',
        telefone: '(51) 88888-8888',
        email: 'joao@email.com',
        ativo: true,
        arquivado: false,
        data_criacao: '2024-01-20T14:30:00'
      }
    ])
  }, [])

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pacientes</h1>
          <p className="text-gray-600 mt-2">
            Gerencie os pacientes cadastrados no sistema
          </p>
        </div>
        
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Novo Paciente
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Buscar por nome..."
                  value={filtros.nome}
                  onChange={(e) => setFiltros({...filtros, nome: e.target.value})}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant={filtros.ativo && !filtros.arquivado ? "default" : "outline"}
                onClick={() => setFiltros({...filtros, ativo: true, arquivado: false})}
              >
                Ativos
              </Button>
              <Button
                variant={filtros.arquivado ? "default" : "outline"}
                onClick={() => setFiltros({...filtros, ativo: false, arquivado: true})}
              >
                Arquivados
              </Button>
              <Button
                variant={!filtros.ativo && !filtros.arquivado ? "default" : "outline"}
                onClick={() => setFiltros({...filtros, ativo: null, arquivado: null})}
              >
                Todos
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Patients List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {pacientes.map((paciente) => (
          <Card key={paciente.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">{paciente.nome_completo}</CardTitle>
                  <p className="text-sm text-gray-500 mt-1">
                    {calcularIdade(paciente.data_nascimento)} anos • {paciente.genero}
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {paciente.telefone && (
                  <p className="text-sm text-gray-600">📞 {paciente.telefone}</p>
                )}
                {paciente.email && (
                  <p className="text-sm text-gray-600">✉️ {paciente.email}</p>
                )}
                <div className="flex justify-between items-center mt-4">
                  <div className="flex gap-2">
                    {/* Badges serão adicionados aqui */}
                  </div>
                  <Button size="sm" variant="outline">
                    Ver Detalhes
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {pacientes.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhum paciente encontrado
            </h3>
            <p className="text-gray-500 mb-4">
              Comece cadastrando seu primeiro paciente no sistema.
            </p>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Cadastrar Primeiro Paciente
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

