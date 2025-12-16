'use client'

import dynamic from 'next/dynamic'

const Dashboard = dynamic(() => import('../../components/Dashboard'), {
    ssr: false,
    loading: () => (
        <div className="min-h-screen bg-dark-900 flex items-center justify-center">
            <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
        </div>
    )
})

export default function DashboardPage() {
    return <Dashboard />
}
