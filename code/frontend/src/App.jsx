import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { MainLayout } from './components/layout/MainLayout'
import { Dashboard } from './pages/Dashboard/Dashboard'

const queryClient = new QueryClient()

function InformacionUsuarioPlaceholder() {
  return (
    <div>
      <h1>Información de Usuario</h1>
      <p>Próximamente — feature 015 · Información de Usuario.</p>
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<MainLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/informacion-usuario" element={<InformacionUsuarioPlaceholder />} />
          </Route>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
