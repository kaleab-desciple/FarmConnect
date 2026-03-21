import { BrowserRouter } from 'react-router-dom'
import AppLayout from '@components/layout/AppLayout'
import AppRouter from '@/app/router'

function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <AppRouter />
      </AppLayout>
    </BrowserRouter>
  )
}

export default App
