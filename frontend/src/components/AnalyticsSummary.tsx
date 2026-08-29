interface Props {
    summary: Record<string, string | number>;
}

export default function AnalyticsSummary({ summary }: Props) {
    const entries = Object.entries(summary);

    return (
        <div className="card">
            <h2 className="section-title mb-4">📊 Analytics Snapshot</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                {entries.map(([key, value]) => (
                    <div key={key} className="bg-slate-800/60 rounded-xl p-4 border border-slate-700/50">
                        <div className="text-xs text-slate-500 mb-1 uppercase tracking-wide font-medium">
                            {key.replace(/_/g, ' ')}
                        </div>
                        <div className="text-base font-semibold text-slate-100 leading-snug">{String(value)}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
