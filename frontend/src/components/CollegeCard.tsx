import { CollegeRecommendation } from '../services/api';
import { useState } from 'react';

interface Props {
    rec: CollegeRecommendation;
}

const importanceColors: Record<string, string> = {
    Critical: 'bg-red-900/50 text-red-300 border-red-700/50',
    Important: 'bg-yellow-900/50 text-yellow-300 border-yellow-700/50',
    'Nice to have': 'bg-slate-700 text-slate-300 border-slate-600',
};

function ScoreBar({ label, value, color = 'bg-brand-500' }: { label: string; value: number; color?: string }) {
    return (
        <div className="space-y-1">
            <div className="flex justify-between text-xs text-slate-400">
                <span>{label}</span>
                <span className="font-semibold text-slate-200">{value.toFixed(0)}</span>
            </div>
            <div className="score-bar-bg">
                <div className={`score-bar-fill ${color}`} style={{ width: `${value}%` }} />
            </div>
        </div>
    );
}

function getScoreColor(score: number): string {
    if (score >= 80) return 'text-emerald-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
}

function getBarColor(score: number): string {
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
}

export default function CollegeCard({ rec }: Props) {
    const [expanded, setExpanded] = useState(false);
    const overall = rec.score_breakdown.overall;

    return (
        <div className="card animate-slide-up border-slate-700/50 hover:border-brand-500/40 transition-all duration-300">
            {/* Header */}
            <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
                <div className="flex items-start gap-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-xl shrink-0
            ${rec.rank === 1 ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/40' :
                            rec.rank === 2 ? 'bg-slate-400/20 text-slate-300 border border-slate-500/40' :
                                rec.rank === 3 ? 'bg-orange-700/20 text-orange-400 border border-orange-600/40' :
                                    'bg-brand-900/30 text-brand-400 border border-brand-700/40'}`}>
                        #{rec.rank}
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">{rec.name}</h3>
                        <p className="text-slate-400 text-sm">📍 {rec.city}, {rec.state} · {rec.stream}</p>
                        <div className="flex flex-wrap gap-1.5 mt-2">
                            {rec.specializations.slice(0, 3).map(s => (
                                <span key={s} className="badge bg-brand-900/40 text-brand-300 border border-brand-700/40 text-xs">{s}</span>
                            ))}
                            {rec.specializations.length > 3 && (
                                <span className="badge bg-slate-800 text-slate-400 border border-slate-700 text-xs">+{rec.specializations.length - 3} more</span>
                            )}
                        </div>
                    </div>
                </div>
                <div className="text-right">
                    <div className={`text-4xl font-extrabold ${getScoreColor(overall)}`}>
                        {overall.toFixed(0)}
                    </div>
                    <div className="text-xs text-slate-500 font-medium uppercase tracking-wide">Match Score</div>
                </div>
            </div>

            {/* Quick Stats Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                {[
                    { label: '💰 Fees', value: `₹${rec.avg_fees_lpa} LPA` },
                    { label: '💼 Placement', value: `${rec.placement_rate}%` },
                    { label: '📈 Avg Salary', value: `₹${rec.avg_salary_lpa} LPA` },
                    { label: '🔬 Internship', value: `${rec.internship_rate}%` },
                ].map(stat => (
                    <div key={stat.label} className="bg-slate-800/60 rounded-xl p-3 text-center">
                        <div className="text-xs text-slate-400 mb-1">{stat.label}</div>
                        <div className="font-semibold text-slate-100 text-sm">{stat.value}</div>
                    </div>
                ))}
            </div>

            {/* Score Bars */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-2 mb-4">
                {(Object.entries(rec.score_breakdown) as [string, number][])
                    .filter(([k]) => k !== 'overall')
                    .map(([key, val]) => (
                        <ScoreBar
                            key={key}
                            label={key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                            value={val}
                            color={getBarColor(val)}
                        />
                    ))}
            </div>

            {/* Why this college */}
            <div className="bg-brand-950/30 border border-brand-800/30 rounded-xl p-4 mb-4">
                <p className="text-sm text-slate-300 leading-relaxed">
                    <span className="text-brand-400 font-semibold">💡 Why this college? </span>
                    {rec.why_this_college}
                </p>
            </div>

            {/* Toggle Expanded */}
            <button
                type="button"
                onClick={() => setExpanded(e => !e)}
                className="w-full text-sm text-brand-400 hover:text-brand-300 py-2 border border-slate-700 rounded-xl hover:border-brand-600 transition-all duration-200"
            >
                {expanded ? '▲ Show Less' : '▼ Show Full Details'}
            </button>

            {/* Expanded Section */}
            {expanded && (
                <div className="mt-6 space-y-6 animate-fade-in">

                    {/* Pros & Cons */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <h4 className="text-sm font-semibold text-emerald-400 mb-3">✅ Pros</h4>
                            <ul className="space-y-2">
                                {rec.pros.map((p, i) => (
                                    <li key={i} className="text-sm text-slate-300 bg-emerald-900/10 border border-emerald-800/20 rounded-lg px-3 py-2">{p}</li>
                                ))}
                            </ul>
                        </div>
                        <div>
                            <h4 className="text-sm font-semibold text-red-400 mb-3">⚠️ Cons</h4>
                            <ul className="space-y-2">
                                {rec.cons.map((c, i) => (
                                    <li key={i} className="text-sm text-slate-300 bg-red-900/10 border border-red-800/20 rounded-lg px-3 py-2">{c}</li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Next Actions */}
                    <div>
                        <h4 className="text-sm font-semibold text-blue-400 mb-3">🎯 Suggested Next Actions</h4>
                        <ol className="space-y-2">
                            {rec.suggested_next_actions.map((action, i) => (
                                <li key={i} className="text-sm text-slate-300 flex gap-3">
                                    <span className="text-brand-400 font-bold shrink-0">{i + 1}.</span>
                                    <span>{action}</span>
                                </li>
                            ))}
                        </ol>
                    </div>

                    {/* Skill Gaps */}
                    <div>
                        <h4 className="text-sm font-semibold text-purple-400 mb-3">🧠 Skill Improvement Plan</h4>
                        <div className="space-y-3">
                            {rec.skill_improvement_plan.map((sg, i) => (
                                <div key={i} className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="font-semibold text-slate-200 text-sm">{sg.skill}</span>
                                        <span className={`badge border text-xs ${importanceColors[sg.importance]}`}>{sg.importance}</span>
                                    </div>
                                    <div className="flex flex-wrap gap-1.5">
                                        {sg.resources.map(r => (
                                            <span key={r} className="text-xs bg-slate-700/60 text-slate-400 px-2 py-1 rounded-lg">{r}</span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Alternate Careers */}
                    {rec.alternate_careers.length > 0 && (
                        <div>
                            <h4 className="text-sm font-semibold text-orange-400 mb-3">🔀 Alternate Career Paths</h4>
                            <div className="flex flex-wrap gap-2">
                                {rec.alternate_careers.map(c => (
                                    <span key={c} className="badge bg-orange-900/30 text-orange-300 border border-orange-700/40 text-xs px-3 py-1.5">{c}</span>
                                ))}
                            </div>
                        </div>
                    )}

                </div>
            )}
        </div>
    );
}
