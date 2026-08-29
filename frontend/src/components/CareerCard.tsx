import { CareerPath } from '../services/api';
import { useState } from 'react';

interface Props {
    paths: CareerPath[];
}

const pathTypeColors: Record<string, string> = {
    Private: 'bg-blue-900/40 text-blue-300 border-blue-700/40',
    Government: 'bg-emerald-900/40 text-emerald-300 border-emerald-700/40',
    Startup: 'bg-purple-900/40 text-purple-300 border-purple-700/40',
    Research: 'bg-orange-900/40 text-orange-300 border-orange-700/40',
    'Government/Private': 'bg-teal-900/40 text-teal-300 border-teal-700/40',
    'Private/Startup': 'bg-pink-900/40 text-pink-300 border-pink-700/40',
};

function getPathColor(type: string): string {
    return pathTypeColors[type] || 'bg-slate-700 text-slate-300 border-slate-600';
}

export default function CareerCard({ paths }: Props) {
    const [activeTab, setActiveTab] = useState(0);

    if (!paths.length) return null;
    const current = paths[activeTab];

    return (
        <div className="card space-y-5">
            <h2 className="section-title">🗺️ Career Roadmaps</h2>

            {/* Tabs */}
            {paths.length > 1 && (
                <div className="flex flex-wrap gap-2">
                    {paths.map((p, i) => (
                        <button
                            key={i}
                            onClick={() => setActiveTab(i)}
                            className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all duration-200 ${i === activeTab
                                    ? 'bg-brand-600 border-brand-500 text-white'
                                    : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-brand-600'
                                }`}
                        >
                            {p.career_title}
                        </button>
                    ))}
                </div>
            )}

            {/* Career Info */}
            <div className="flex flex-wrap items-center gap-3">
                <h3 className="text-xl font-bold text-white">{current.career_title}</h3>
                <span className={`badge border text-xs ${getPathColor(current.path_type)}`}>{current.path_type}</span>
                <span className="badge bg-yellow-900/40 text-yellow-300 border-yellow-700/40 text-xs">
                    💰 {current.avg_salary_range}
                </span>
            </div>

            {/* Year-wise Roadmap */}
            <div>
                <h4 className="text-sm font-semibold text-brand-400 mb-3">📅 Year-wise Roadmap</h4>
                <div className="relative pl-4">
                    <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-gradient-to-b from-brand-500 to-transparent rounded" />
                    <div className="space-y-3">
                        {current.year_wise_roadmap.map((step, i) => (
                            <div key={i} className="flex gap-3 items-start">
                                <div className="w-2 h-2 rounded-full bg-brand-500 shrink-0 mt-1.5 -ml-5 border-2 border-slate-950" />
                                <p className="text-sm text-slate-300">{step}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Skills & Certifications */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <h4 className="text-sm font-semibold text-purple-400 mb-2">🛠️ Required Skills</h4>
                    <div className="flex flex-wrap gap-1.5">
                        {current.required_skills.map(s => (
                            <span key={s} className="badge bg-purple-900/30 text-purple-300 border border-purple-700/40 text-xs">{s}</span>
                        ))}
                    </div>
                </div>
                <div>
                    <h4 className="text-sm font-semibold text-emerald-400 mb-2">🎓 Recommended Certifications</h4>
                    <ul className="space-y-1">
                        {current.recommended_certifications.map(c => (
                            <li key={c} className="text-xs text-slate-400 flex gap-1.5"><span className="text-emerald-500">✓</span>{c}</li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}
