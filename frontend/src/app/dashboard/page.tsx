'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    'https://file-data-extractor.onrender.com'

interface User {
    id: number
    email: string
    username: string
    tier: string
}

interface Document {
    id: number
    original_filename: string
    file_type: string
    status: string
    created_at: string
}

export default function DashboardPage() {
    const router = useRouter()
    const [user, setUser] = useState<User | null>(null)
    const [documents, setDocuments] = useState<Document[]>([])
    const [stats, setStats] = useState({ documents_processed: 0, total_exports: 0 })
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const handleLogout = useCallback(() => {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/')
    }, [router])

    const fetchDashboardData = useCallback(async (token: string) => {
        try {
            setError(null)
            // Fetch user stats
            const statsRes = await fetch(`${API_BASE_URL}/api/auth/stats`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (statsRes.ok) {
                const statsData = await statsRes.json()
                setStats(statsData)
            } else if (statsRes.status === 401 || statsRes.status === 403) {
                handleLogout()
                return
            }

            // Fetch recent documents
            const docsRes = await fetch(`${API_BASE_URL}/api/documents?limit=5`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (docsRes.ok) {
                const docsData = await docsRes.json()
                setDocuments(docsData)
            } else if (docsRes.status === 401 || docsRes.status === 403) {
                handleLogout()
                return
            }
        } catch (error) {
            console.error('Error fetching dashboard data:', error)
            setError('Unable to load dashboard data. Please try again.')
        } finally {
            setLoading(false)
        }
    }, [handleLogout])

    useEffect(() => {
        // Check authentication
        const token = localStorage.getItem('token')
        const userStr = localStorage.getItem('user')

        if (!token || !userStr) {
            router.push('/auth/login')
            return
        }

        setUser(JSON.parse(userStr))
        fetchDashboardData(token)
    }, [fetchDashboardData, router])

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#F0F5F9] via-[#E8EFF5] to-[#C9D6DF]">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#52616B] mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading dashboard...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#F0F5F9] via-[#E8EFF5] to-[#C9D6DF]">
            {/* Header */}
            <header className="glass-strong border-b border-[#C9D6DF]">
                <div className="container mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <Link href="/" className="text-2xl">📄</Link>
                            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#52616B] to-[#1E2022]">
                                Dashboard
                            </h1>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm text-gray-600">
                                {user?.username}
                            </span>
                            <button
                                onClick={handleLogout}
                                className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <div className="container mx-auto px-4 py-8">
                {error && (
                    <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                        {error}
                    </div>
                )}

                {/* Welcome Banner */}
                <div className="glass rounded-2xl p-8 mb-8 border border-[#C9D6DF]">
                    <h2 className="text-3xl font-bold text-gray-900 mb-2">
                        Welcome back, {user?.username}! 👋
                    </h2>
                    <p className="text-gray-600">
                        Tier: <span className="font-semibold text-[#52616B] uppercase">{user?.tier}</span>
                    </p>
                </div>

                {/* Stats Cards */}
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                    <div className="glass rounded-2xl p-6 border border-[#C9D6DF]">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Documents Processed</p>
                                <p className="text-3xl font-bold text-gray-900 mt-2">
                                    {stats.documents_processed}
                                </p>
                            </div>
                            <div className="text-4xl">📄</div>
                        </div>
                    </div>

                    <div className="glass rounded-2xl p-6 border border-[#C9D6DF]">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Total Exports</p>
                                <p className="text-3xl font-bold text-gray-900 mt-2">
                                    {stats.total_exports}
                                </p>
                            </div>
                            <div className="text-4xl">⬇️</div>
                        </div>
                    </div>

                    <div className="glass rounded-2xl p-6 border border-[#C9D6DF]">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600">Account Tier</p>
                                <p className="text-3xl font-bold text-gray-900 mt-2 uppercase">
                                    {user?.tier}
                                </p>
                            </div>
                            <div className="text-4xl">⭐</div>
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                    <Link
                        href="/ai-notes"
                            className="glass rounded-2xl p-6 border border-[#C9D6DF] hover:border-[#52616B] transform hover:scale-105 transition-all duration-300"
                    >
                        <div className="flex items-center space-x-4">
                            <div className="text-5xl">🚀</div>
                            <div>
                                    <h3 className="text-xl font-bold text-gray-900">Process New Document</h3>
                                    <p className="text-gray-600">Upload and extract text with AI</p>
                            </div>
                        </div>
                    </Link>

                    <button className="glass rounded-2xl p-6 border border-[#C9D6DF] hover:border-[#52616B] transform hover:scale-105 transition-all duration-300 text-left">
                        <div className="flex items-center space-x-4">
                            <div className="text-5xl">📋</div>
                            <div>
                                <h3 className="text-xl font-bold text-gray-900">View All Documents</h3>
                                <p className="text-gray-600">Browse your document history</p>
                            </div>
                        </div>
                    </button>
                </div>

                {/* Recent Documents */}
                <div className="glass rounded-2xl p-8 border border-[#C9D6DF]">
                    <h3 className="text-2xl font-bold text-gray-900 mb-6">Recent Documents</h3>

                    {documents.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="text-6xl mb-4">📭</div>
                            <p className="text-gray-600 mb-4">No documents yet</p>
                            <Link
                                href="/ai-notes"
                                className="inline-block px-6 py-3 bg-[#1E2022] hover:bg-[#52616B] text-[#F0F5F9] font-semibold rounded-xl hover:shadow-lg transform hover:scale-105 transition-all"
                            >
                                Upload Your First Document
                            </Link>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {documents.map((doc) => (
                                <div key={doc.id} className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-200">
                                    <div className="flex items-center space-x-4">
                                        <div className="text-2xl">
                                            {doc.file_type === 'pdf' ? '📄' : doc.file_type === 'docx' ? '📝' : '🖼️'}
                                        </div>
                                        <div>
                                            <p className="font-semibold text-gray-900">{doc.original_filename}</p>
                                            <p className="text-sm text-gray-500">
                                                {new Date(doc.created_at).toLocaleDateString()} • {doc.status}
                                            </p>
                                        </div>
                                    </div>
                                    <button className="px-4 py-2 text-[#52616B] hover:bg-[#F0F5F9] rounded-lg transition">
                                        View
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
