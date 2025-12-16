import { useState, useEffect } from 'react'
import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Users, CheckCircle, XCircle, DollarSign, TrendingUp } from 'lucide-react'
import axios from 'axios'

import { API_BASE_URL } from '../constants'

export default function Dashboard() {
    const [stats, setStats] = useState(null)
    const [applications, setApplications] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const [statsRes, appsRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/api/stats`),
                axios.get(`${API_BASE_URL}/api/admin/applications`)
            ])
            setStats(statsRes.data)
            setApplications(appsRes.data)
        } catch (err) {
            console.error("Error fetching dashboard data:", err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-dark-900 text-primary-400">
                <div className="animate-spin w-8 h-8 border-4 border-current border-t-transparent rounded-full" />
            </div>
        )
    }

    const COLORS = ['#10b981', '#ef4444', '#f59e0b']

    const pieData = [
        { name: 'Approved', value: stats?.approved_loans || 0 },
        { name: 'Rejected', value: stats?.rejected_loans || 0 },
        { name: 'Pending', value: stats?.pending || 0 },
    ]

    return (
        <div className="min-h-screen bg-dark-900 p-8 text-dark-50">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-400 to-secondary-400 bg-clip-text text-transparent">
                            Banker Dashboard
                        </h1>
                        <p className="text-dark-400 mt-1">Real-time overview of loan applications</p>
                    </div>
                    <button
                        onClick={fetchData}
                        className="p-2 bg-dark-800 hover:bg-dark-700 rounded-lg text-dark-400 hover:text-white transition-colors"
                    >
                        <TrendingUp className="w-5 h-5" />
                    </button>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <StatCard
                        title="Total Applications"
                        value={stats?.total_conversations || 0}
                        icon={<Users className="w-6 h-6 text-blue-400" />}
                        color="bg-blue-500/10 border-blue-500/20"
                    />
                    <StatCard
                        title="Approved"
                        value={stats?.approved_loans || 0}
                        icon={<CheckCircle className="w-6 h-6 text-success-400" />}
                        color="bg-success-500/10 border-success-500/20"
                    />
                    <StatCard
                        title="Rejected"
                        value={stats?.rejected_loans || 0}
                        icon={<XCircle className="w-6 h-6 text-danger-400" />}
                        color="bg-danger-500/10 border-danger-500/20"
                    />
                    <StatCard
                        title="Disbursal Pending"
                        value={`₹${(stats?.approved_loans * 500000 / 10000000).toFixed(1)}Cr`} // Mock calculation
                        icon={<DollarSign className="w-6 h-6 text-warning-400" />}
                        color="bg-warning-500/10 border-warning-500/20"
                    />
                </div>

                {/* Charts Section */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Approval Distribution */}
                    <div className="bg-dark-800 p-6 rounded-xl border border-dark-700 shadow-xl">
                        <h3 className="text-lg font-semibold mb-6">Approval Status</h3>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {pieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1a1d2d', borderColor: '#2d3342' }}
                                        itemStyle={{ color: '#fff' }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="flex justify-center gap-4 mt-4 text-sm">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-success-500" /> Approved
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-danger-500" /> Rejected
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-warning-500" /> Pending
                            </div>
                        </div>
                    </div>

                    {/* Recent List */}
                    <div className="lg:col-span-2 bg-dark-800 p-6 rounded-xl border border-dark-700 shadow-xl overflow-hidden">
                        <h3 className="text-lg font-semibold mb-6">Recent Applications</h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead>
                                    <tr className="border-b border-dark-700 text-dark-400 text-sm">
                                        <th className="pb-3 px-4">Applicant</th>
                                        <th className="pb-3 px-4">Amount</th>
                                        <th className="pb-3 px-4">Purpose</th>
                                        <th className="pb-3 px-4">Score</th>
                                        <th className="pb-3 px-4">Status</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-dark-700">
                                    {applications.map((app) => (
                                        <tr key={app.id} className="text-sm hover:bg-dark-700/50 transition-colors">
                                            <td className="py-3 px-4 font-medium">{app.name}</td>
                                            <td className="py-3 px-4">₹{(app.amount || 0).toLocaleString()}</td>
                                            <td className="py-3 px-4">{app.type}</td>
                                            <td className="py-3 px-4">
                                                <span className="px-2 py-1 bg-dark-700 rounded text-xs">
                                                    {app.score}
                                                </span>
                                            </td>
                                            <td className="py-3 px-4">
                                                <StatusBadge status={app.status} />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

function StatCard({ title, value, icon, color }) {
    return (
        <div className={`p-6 rounded-xl border ${color} bg-dark-800 shadow-lg`}>
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-dark-400 text-sm font-medium">{title}</h3>
                {icon}
            </div>
            <p className="text-2xl font-bold text-white">{value}</p>
        </div>
    )
}

function StatusBadge({ status }) {
    const styles = {
        APPROVED: 'bg-success-500/20 text-success-400 border-success-500/30',
        REJECTED: 'bg-danger-500/20 text-danger-400 border-danger-500/30',
        IN_PROGRESS: 'bg-primary-500/20 text-primary-400 border-primary-500/30',
        None: 'bg-dark-700/50 text-dark-400 border-dark-600'
    }

    const label = status || 'In Progress'
    const style = styles[status] || styles.IN_PROGRESS

    return (
        <span className={`px-2 py-1 rounded-md text-xs border ${style}`}>
            {label}
        </span>
    )
}
