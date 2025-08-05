import { useState, useEffect } from 'react'
import { Plus, Search, Filter, MoreHorizontal, Archive, Edit, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu'
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Link } from 'react-router-dom'

export function Pacientes() {
  const [pacientes, setPacientes] = useState([])
  const [filtros, setFiltros] = useState({
    nome: '',
    ativo: true,
    arquivado: false
  })
  const [dialogAberto, setDialogAberto] = useState(false)
  const [pacienteEditando, setPacienteEditando] = useState(null)
  const [formData, setFormData] = useState({
    nome_completo: '',
    data_nascimento: '',
    genero: '',
    telefone: '',
    email: '',
    endereco_residencial: '',
    profissao: '',
    estado_civil: '',
    naturalidade: '',
    local_nascimento: '',
    endereco_comercial: ''
  })

  useEffect(() => {
    carregarPacientes()
  }, [filtros])

  const carregarPacientes = async () => {
    try {
      const params = new URLSearchParams()
      if (filtros.nome) params.append('nome', filtros.nome)
      if (filtros.ativo !== null) params.append('ativo', filtros.ativo)
      if (filtros.arquivado !== null) params.append('arquivado', filtros.arquivado)

      const response = await fetch(`http://localhost:5000/api/pacientes?${params}`)
      const data = await response.json()
      setPacientes(data)
    } catch (error) {
      console.error('Erro ao carregar pacientes:', error)
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
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const url = pacienteEditando 
        ? `http://localhost:5000/api/pacientes/${pacienteEditando.id}`
        : 'http://localhost:5000/api/pacientes'
      
      const method = pacienteEditando ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          fisioterapeuta_id: 1 // TODO: Pegar do contexto de autenticação
        }),
      })

      if (response.ok) {
        setDialogAberto(false)
        setPacienteEditando(null)
        setFormData({
          nome_completo: '',
          data_nascimento: '',
          genero: '',
          telefone: '',
          email: '',
          endereco_residencial: '',
          profissao: '',
          estado_civil: '',
          naturalidade: '',
          local_nascimento: '',
          endereco_comercial: ''
        })
        carregarPacientes()
      }
    } catch (error) {
      console.error('Erro ao salvar paciente:', error)
    }
  }

  const editarPaciente = (paciente) => {
    setPacienteEditando(paciente)
    setFormData({
      nome_completo: paciente.nome_completo || '',
      data_nascimento: paciente.data_nascimento || '',
      genero: paciente.genero || '',
      telefone: paciente.telefone || '',
      email: paciente.email || '',
      endereco_residencial: paciente.endereco_residencial || '',
      profissao: paciente.profissao || '',
      estado_civil: paciente.estado_civil || '',
      naturalidade: paciente.naturalidade || '',
      local_nascimento: paciente.local_nascimento || '',
      endereco_comercial: paciente.endereco_comercial || ''
    })
    setDialogAberto(true)
  }

  const arquivarPaciente = async (pacienteId, arquivar = true) => {
    try {
      const response = await fetch(`http://localhost:5000/api/pacientes/${pacienteId}/arquivar`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ arquivar }),
      })

      if (response.ok) {
        carregarPacientes()
      }
    } catch (error) {
      console.error('Erro ao arquivar paciente:', error)
    }
  }

  const excluirPaciente = async (pacienteId) => {
    if (confirm('Tem certeza que deseja excluir este paciente?')) {
      try {
        const response = await fetch(`http://localhost:5000/api/pacientes/${pacienteId}`, {
          method: 'DELETE',
        })

        if (response.ok) {
          carregarPacientes()
        }
      } catch (error) {
        console.error('Erro ao excluir paciente:', error)
      }
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
        
        <Dialog open={dialogAberto} onOpenChange={setDialogAberto}>
          <DialogTrigger asChild>
            <Button onClick={() => {
              setPacienteEditando(null)
              setFormData({
                nome_completo: '',
                data_nascimento: '',
                genero: '',
                telefone: '',
                email: '',
                endereco_residencial: '',
                profissao: '',
                estado_civil: '',
                naturalidade: '',
                local_nascimento: '',
                endereco_comercial: ''
              })
            }}>
              <Plus className="mr-2 h-4 w-4" />
              Novo Paciente
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {pacienteEditando ? 'Editar Paciente' : 'Novo Paciente'}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="nome_completo">Nome Completo *</Label>
                  <Input
                    id="nome_completo"
                    value={formData.nome_completo}
                    onChange={(e) => setFormData({...formData, nome_completo: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="data_nascimento">Data de Nascimento *</Label>
                  <Input
                    id="data_nascimento"
                    type="date"
                    value={formData.data_nascimento}
                    onChange={(e) => setFormData({...formData, data_nascimento: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="genero">Gênero</Label>
                  <Select value={formData.genero} onValueChange={(value) => setFormData({...formData, genero: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o gênero" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Masculino">Masculino</SelectItem>
                      <SelectItem value="Feminino">Feminino</SelectItem>
                      <SelectItem value="Outro">Outro</SelectItem>
                      <SelectItem value="Prefiro não informar">Prefiro não informar</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="estado_civil">Estado Civil</Label>
                  <Select value={formData.estado_civil} onValueChange={(value) => setFormData({...formData, estado_civil: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o estado civil" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Solteiro(a)">Solteiro(a)</SelectItem>
                      <SelectItem value="Casado(a)">Casado(a)</SelectItem>
                      <SelectItem value="Divorciado(a)">Divorciado(a)</SelectItem>
                      <SelectItem value="Viúvo(a)">Viúvo(a)</SelectItem>
                      <SelectItem value="União Estável">União Estável</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="telefone">Telefone</Label>
                  <Input
                    id="telefone"
                    value={formData.telefone}
                    onChange={(e) => setFormData({...formData, telefone: e.target.value})}
                    placeholder="(00) 00000-0000"
                  />
                </div>
                <div>
                  <Label htmlFor="email">E-mail</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="profissao">Profissão</Label>
                  <Input
                    id="profissao"
                    value={formData.profissao}
                    onChange={(e) => setFormData({...formData, profissao: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="naturalidade">Naturalidade</Label>
                  <Input
                    id="naturalidade"
                    value={formData.naturalidade}
                    onChange={(e) => setFormData({...formData, naturalidade: e.target.value})}
                  />
                </div>
                <div className="md:col-span-2">
                  <Label htmlFor="local_nascimento">Local de Nascimento</Label>
                  <Input
                    id="local_nascimento"
                    value={formData.local_nascimento}
                    onChange={(e) => setFormData({...formData, local_nascimento: e.target.value})}
                  />
                </div>
                <div className="md:col-span-2">
                  <Label htmlFor="endereco_residencial">Endereço Residencial</Label>
                  <Textarea
                    id="endereco_residencial"
                    value={formData.endereco_residencial}
                    onChange={(e) => setFormData({...formData, endereco_residencial: e.target.value})}
                    rows={2}
                  />
                </div>
                <div className="md:col-span-2">
                  <Label htmlFor="endereco_comercial">Endereço Comercial</Label>
                  <Textarea
                    id="endereco_comercial"
                    value={formData.endereco_comercial}
                    onChange={(e) => setFormData({...formData, endereco_comercial: e.target.value})}
                    rows={2}
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setDialogAberto(false)}>
                  Cancelar
                </Button>
                <Button type="submit">
                  {pacienteEditando ? 'Atualizar' : 'Cadastrar'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
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
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => editarPaciente(paciente)}>
                      <Edit className="mr-2 h-4 w-4" />
                      Editar
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => arquivarPaciente(paciente.id, !paciente.arquivado)}>
                      <Archive className="mr-2 h-4 w-4" />
                      {paciente.arquivado ? 'Desarquivar' : 'Arquivar'}
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={() => excluirPaciente(paciente.id)}
                      className="text-red-600"
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Excluir
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
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
                    {paciente.arquivado && (
                      <Badge variant="secondary">Arquivado</Badge>
                    )}
                    {!paciente.ativo && (
                      <Badge variant="destructive">Inativo</Badge>
                    )}
                  </div>
                  <Link to={`/pacientes/${paciente.id}`}>
                    <Button size="sm" variant="outline">
                      Ver Detalhes
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {pacientes.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Users className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhum paciente encontrado
            </h3>
            <p className="text-gray-500 mb-4">
              Comece cadastrando seu primeiro paciente no sistema.
            </p>
            <Button onClick={() => setDialogAberto(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Cadastrar Primeiro Paciente
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

