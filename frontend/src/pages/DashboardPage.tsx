import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  LayoutDashboard, 
  FileText, 
  Search, 
  Target, 
  BookOpen, 
  TrendingUp,
  Users,
  Briefcase,
  Award
} from 'lucide-react'
import { api } from '@/services/auth'

// Mock data for dashboard
const mockStats = {
  totalCVs: 3,
  activeCVs: 1,
  jobMatches: 12,
  recommendations: 5,
  profileCompletion: 85,
}

const mockRecentActivity = [
  {
    id: 1,
    type: 'cv_upload',
    title: 'CV subido',
    description: 'CV_Developer_React.pdf',
    time: 'Hace 2 horas',
  },
  {
    id: 2,
    type: 'job_match',
    title: 'Nuevo match',
    description: 'Senior Frontend Developer en TechCorp',
    time: 'Hace 5 horas',
  },
  {
    id: 3,
    type: 'recommendation',
    title: 'Nueva recomendación',
    description: 'Aprende GraphQL para mejorar tus habilidades',
    time: 'Hace 1 día',
  },
]

const mockTopSkills = [
  { name: 'JavaScript', level: 4, jobs: 45 },
  { name: 'React', level: 4, jobs: 38 },
  { name: 'TypeScript', level: 3, jobs: 32 },
  { name: 'Node.js', level: 3, jobs: 28 },
  { name: 'Python', level: 2, jobs: 15 },
]

export default function DashboardPage() {
  const [selectedCV, setSelectedCV] = useState<string | null>(null)

  const { data: user } = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const response = await api.get('/auth/me')
      return response.data.data
    },
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Bienvenido de vuelta, {user?.name || 'Usuario'}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Search className="mr-2 h-4 w-4" />
            Buscar ofertas
          </Button>
          <Button>
            <FileText className="mr-2 h-4 w-4" />
            Subir CV
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CVs Totales</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.totalCVs}</div>
            <p className="text-xs text-muted-foreground">
              {mockStats.activeCVs} activos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Matches</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.jobMatches}</div>
            <p className="text-xs text-muted-foreground">
              +2 esta semana
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recomendaciones</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.recommendations}</div>
            <p className="text-xs text-muted-foreground">
              3 pendientes
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Perfil Completo</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.profileCompletion}%</div>
            <Progress value={mockStats.profileCompletion} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Skills Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Tus Habilidades Principales</CardTitle>
            <CardDescription>
              Basado en el análisis de tus CVs
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockTopSkills.map((skill, index) => (
                <div key={skill.name} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                      <span className="text-xs font-medium">{index + 1}</span>
                    </div>
                    <div>
                      <p className="font-medium">{skill.name}</p>
                      <p className="text-sm text-muted-foreground">
                        Nivel {skill.level}/5 • {skill.jobs} ofertas
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-20">
                      <Progress value={(skill.level / 5) * 100} className="h-2" />
                    </div>
                    <Badge variant="outline">{skill.level}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Actividad Reciente</CardTitle>
            <CardDescription>
              Tus últimas acciones en el sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockRecentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {activity.type === 'cv_upload' && (
                      <FileText className="h-5 w-5 text-blue-500" />
                    )}
                    {activity.type === 'job_match' && (
                      <Target className="h-5 w-5 text-green-500" />
                    )}
                    {activity.type === 'recommendation' && (
                      <BookOpen className="h-5 w-5 text-purple-500" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{activity.title}</p>
                    <p className="text-sm text-muted-foreground truncate">
                      {activity.description}
                    </p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Acciones Rápidas</CardTitle>
          <CardDescription>
            ¿Qué te gustaría hacer hoy?
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Button variant="outline" className="h-20 flex-col space-y-2">
              <FileText className="h-6 w-6" />
              <span>Subir CV</span>
            </Button>
            <Button variant="outline" className="h-20 flex-col space-y-2">
              <Search className="h-6 w-6" />
              <span>Buscar Ofertas</span>
            </Button>
            <Button variant="outline" className="h-20 flex-col space-y-2">
              <Target className="h-6 w-6" />
              <span>Ver Matches</span>
            </Button>
            <Button variant="outline" className="h-20 flex-col space-y-2">
              <BookOpen className="h-6 w-6" />
              <span>Aprender</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}