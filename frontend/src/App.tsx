import { useState, useCallback } from 'react';
import ProfileForm from './components/ProfileForm';
import CollegeCard from './components/CollegeCard';
import CareerCard from './components/CareerCard';
import AnalyticsSummary from './components/AnalyticsSummary';
import { getRecommendations, UserProfileRequest, RecommendationResponse } from './services/api';

type View = 'form' | 'results';

export default function App() {
  const [view, setView] = useState<View>('form');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(async (profile: UserProfileRequest) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getRecommendations(profile);
      setResults(data);
      setView('results');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      const apiError = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(apiError || message || 'Could not connect to backend. Make sure it is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleBack = () => {
    setView('form');
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Navbar */}
      <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-brand-500 to-purple-600 rounded-xl flex items-center justify-center text-lg">🎓</div>
            <div>
              <div className="font-bold text-white text-sm leading-tight">AI Career Intelligence</div>
              <div className="text-xs text-slate-500">College & Career Platform</div>
            </div>
          </div>
          <div className="flex items-center gap-4 text-sm text-slate-400">
            <span className="hidden sm:block">Powered by FastAPI + React</span>
            {view === 'results' && (
              <button onClick={handleBack} className="btn-secondary text-xs px-3 py-1.5">
                ← New Search
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* Hero (form view only) */}
      {view === 'form' && (
        <div className="bg-gradient-to-b from-slate-900 to-slate-950 border-b border-slate-800">
          <div className="max-w-6xl mx-auto px-4 py-12 text-center">
            <div className="inline-flex items-center gap-2 bg-brand-900/40 border border-brand-700/50 rounded-full px-4 py-1.5 text-xs text-brand-300 font-medium mb-6">
              ✨ AI-Powered · Multi-Factor Intelligence
            </div>
            <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-4 leading-tight">
              Find Your Perfect College &<br />
              <span className="bg-gradient-to-r from-brand-400 to-purple-400 bg-clip-text text-transparent">
                Career Path
              </span>
            </h1>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto">
              Get intelligent, personalized recommendations based on your academics, interests, budget, and goals — not just rankings.
            </p>
            <div className="flex flex-wrap justify-center gap-6 mt-8 text-sm text-slate-500">
              <span>✅ 35+ Top Indian Colleges</span>
              <span>✅ 6-Factor AI Scoring</span>
              <span>✅ Skill Gap Analysis</span>
              <span>✅ Career Roadmaps</span>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-10">

        {/* Error Banner */}
        {error && (
          <div className="bg-red-900/30 border border-red-700/50 rounded-xl p-4 mb-6 text-red-300 text-sm animate-fade-in">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Form View */}
        {view === 'form' && (
          <ProfileForm onSubmit={handleSubmit} loading={loading} />
        )}

        {/* Results View */}
        {view === 'results' && results && (
          <div className="space-y-8 animate-fade-in">
            {/* Results Header */}
            <div className="card bg-gradient-to-r from-brand-900/30 to-purple-900/20 border-brand-700/30">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-extrabold text-white">
                    🎉 Hey {results.student_name}, here are your results!
                  </h1>
                  <p className="text-slate-400 mt-1 text-sm">
                    Analyzed <strong className="text-slate-200">{results.total_colleges_analyzed}</strong> colleges ·
                    Found <strong className="text-slate-200">{results.recommendations.length}</strong> best matches ·
                    Stream: <strong className="text-slate-200">{results.stream}</strong>
                  </p>
                </div>
                <button onClick={handleBack} className="btn-secondary text-sm">← Refine Profile</button>
              </div>
            </div>

            {/* Analytics Summary */}
            <AnalyticsSummary summary={results.analytics_summary} />

            {/* College Recommendations */}
            <div>
              <h2 className="section-title mb-2">🏫 College Recommendations</h2>
              <p className="text-slate-400 text-sm mb-6">Ranked by your personalized AI match score. Click "Show Full Details" to see skill gaps, pros/cons, and action steps.</p>
              <div className="space-y-5">
                {results.recommendations.map(rec => (
                  <CollegeCard key={rec.college_id} rec={rec} />
                ))}
              </div>
            </div>

            {/* Career Paths */}
            <CareerCard paths={results.career_paths} />

            {/* Back button */}
            <div className="text-center pt-4">
              <button onClick={handleBack} className="btn-primary px-10">
                ← Search Again with Different Profile
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-16 py-8 text-center text-slate-600 text-sm">
        <p>AI Career & College Intelligence Platform · Built with FastAPI + React + Tailwind CSS</p>
      </footer>
    </div>
  );
}
