import React, { useState, useCallback } from 'react';
import {
    UserProfileRequest,
    AcademicScores,
    getSampleProfile,
} from '../services/api';

interface Props {
    onSubmit: (profile: UserProfileRequest) => void;
    loading: boolean;
}

const INTEREST_OPTIONS = [
    'AI', 'Software Engineering', 'Data Science', 'Medicine', 'Business',
    'Finance', 'Design', 'Government Jobs', 'Research', 'Law',
    'Architecture', 'Marketing', 'Entrepreneurship', 'Cybersecurity',
];

const DEFAULT_SCORES: AcademicScores = {
    maths: 0, physics: 0, chemistry: 0, biology: 0,
    computer_science: 0, english: 70, economics: 0, accountancy: 0,
    overall_percentile: 75,
};

const STREAM_SUBJECTS: Record<string, (keyof AcademicScores)[]> = {
    Science: ['maths', 'physics', 'chemistry', 'biology', 'computer_science', 'english', 'overall_percentile'],
    Commerce: ['maths', 'economics', 'accountancy', 'english', 'overall_percentile'],
    Arts: ['english', 'economics', 'overall_percentile'],
};

const SUBJECT_LABELS: Record<string, string> = {
    maths: 'Mathematics', physics: 'Physics', chemistry: 'Chemistry',
    biology: 'Biology', computer_science: 'Computer Science', english: 'English',
    economics: 'Economics', accountancy: 'Accountancy', overall_percentile: 'Entrance Exam Percentile',
};

export default function ProfileForm({ onSubmit, loading }: Props) {
    const [profile, setProfile] = useState<UserProfileRequest>({
        name: '',
        stream: 'Science',
        academic_scores: { ...DEFAULT_SCORES },
        interests: [],
        budget_lpa: 5,
        preferred_states: [],
        preferred_cities: [],
        learning_style: 'mixed',
        career_goals: [],
        top_n: 5,
    });

    const [careerInput, setCareerInput] = useState('');
    const [stateInput, setStateInput] = useState('');
    const [cityInput, setCityInput] = useState('');

    const handleField = (key: keyof UserProfileRequest, value: unknown) => {
        setProfile(p => ({ ...p, [key]: value }));
    };

    const handleScore = (key: keyof AcademicScores, value: string) => {
        setProfile(p => ({
            ...p,
            academic_scores: { ...p.academic_scores, [key]: parseFloat(value) || 0 },
        }));
    };

    const toggleInterest = (interest: string) => {
        setProfile(p => ({
            ...p,
            interests: p.interests.includes(interest)
                ? p.interests.filter(i => i !== interest)
                : [...p.interests, interest],
        }));
    };

    const addTag = (
        field: 'career_goals' | 'preferred_states' | 'preferred_cities',
        value: string,
        setter: (v: string) => void
    ) => {
        const trimmed = value.trim();
        if (trimmed && !profile[field].includes(trimmed)) {
            handleField(field, [...profile[field], trimmed]);
        }
        setter('');
    };

    const removeTag = (field: 'career_goals' | 'preferred_states' | 'preferred_cities', tag: string) => {
        handleField(field, profile[field].filter(t => t !== tag));
    };

    const loadSample = useCallback(async () => {
        try {
            const sample = await getSampleProfile();
            setProfile(sample);
        } catch {
            // fallback if API not yet running
            setProfile({
                name: 'Rahul Sharma', stream: 'Science',
                academic_scores: { maths: 92, physics: 88, chemistry: 85, biology: 0, computer_science: 95, english: 80, economics: 0, accountancy: 0, overall_percentile: 94 },
                interests: ['AI', 'Software Engineering', 'Data Science'],
                budget_lpa: 5, preferred_states: ['Maharashtra', 'Karnataka'],
                preferred_cities: ['Mumbai', 'Bangalore'], learning_style: 'practical',
                career_goals: ['Software Engineer', 'Data Scientist'], top_n: 5,
            });
        }
    }, []);

    const subjects = STREAM_SUBJECTS[profile.stream] || STREAM_SUBJECTS.Science;

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!profile.name.trim()) { alert('Please enter your name'); return; }
        if (profile.interests.length === 0) { alert('Please select at least one interest'); return; }
        if (profile.career_goals.length === 0) { alert('Please add at least one career goal'); return; }
        onSubmit(profile);
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-8 animate-fade-in">

            {/* Header */}
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                    <h2 className="section-title">Your Academic Profile</h2>
                    <p className="text-slate-400 text-sm">Fill in your details to get personalized recommendations</p>
                </div>
                <button type="button" onClick={loadSample} className="btn-secondary text-sm">
                    ✨ Load Sample Profile
                </button>
            </div>

            {/* Basic Info */}
            <div className="card space-y-4">
                <h3 className="text-lg font-semibold text-brand-400">👤 Basic Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="label">Full Name</label>
                        <input
                            className="input-field"
                            placeholder="e.g. Rahul Sharma"
                            value={profile.name}
                            onChange={e => handleField('name', e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="label">Stream</label>
                        <select
                            className="input-field"
                            value={profile.stream}
                            onChange={e => {
                                handleField('stream', e.target.value);
                                handleField('academic_scores', { ...DEFAULT_SCORES });
                            }}
                        >
                            <option value="Science">🔬 Science</option>
                            <option value="Commerce">📊 Commerce</option>
                            <option value="Arts">🎨 Arts</option>
                        </select>
                    </div>
                    <div>
                        <label className="label">Learning Style</label>
                        <select
                            className="input-field"
                            value={profile.learning_style}
                            onChange={e => handleField('learning_style', e.target.value)}
                        >
                            <option value="theory">📚 Theory-oriented</option>
                            <option value="practical">🛠️ Practical-oriented</option>
                            <option value="mixed">⚖️ Mixed</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Academic Scores */}
            <div className="card space-y-4">
                <h3 className="text-lg font-semibold text-brand-400">📊 Academic Scores</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {subjects.map(subj => (
                        <div key={subj}>
                            <label className="label">{SUBJECT_LABELS[subj]} {subj === 'overall_percentile' ? '(%)' : '(out of 100)'}</label>
                            <input
                                type="number"
                                min={0}
                                max={100}
                                step={0.5}
                                className="input-field"
                                placeholder={subj === 'overall_percentile' ? '0-100 percentile' : '0-100'}
                                value={profile.academic_scores[subj] || ''}
                                onChange={e => handleScore(subj, e.target.value)}
                            />
                        </div>
                    ))}
                </div>
            </div>

            {/* Interests */}
            <div className="card space-y-4">
                <h3 className="text-lg font-semibold text-brand-400">🎯 Interests & Passions</h3>
                <p className="text-slate-400 text-sm">Select all that apply</p>
                <div className="flex flex-wrap gap-2">
                    {INTEREST_OPTIONS.map(interest => (
                        <button
                            key={interest}
                            type="button"
                            onClick={() => toggleInterest(interest)}
                            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 border ${profile.interests.includes(interest)
                                    ? 'bg-brand-600 border-brand-500 text-white shadow-lg shadow-brand-500/20'
                                    : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-brand-600'
                                }`}
                        >
                            {interest}
                        </button>
                    ))}
                </div>
            </div>

            {/* Career Goals */}
            <div className="card space-y-4">
                <h3 className="text-lg font-semibold text-brand-400">🚀 Career Goals</h3>
                <div className="flex gap-2">
                    <input
                        className="input-field"
                        placeholder="e.g. Software Engineer, Entrepreneur..."
                        value={careerInput}
                        onChange={e => setCareerInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addTag('career_goals', careerInput, setCareerInput))}
                    />
                    <button type="button" onClick={() => addTag('career_goals', careerInput, setCareerInput)}
                        className="btn-secondary shrink-0">Add</button>
                </div>
                <div className="flex flex-wrap gap-2">
                    {profile.career_goals.map(g => (
                        <span key={g} className="badge bg-emerald-900/50 text-emerald-300 border border-emerald-700/50">
                            {g}
                            <button type="button" onClick={() => removeTag('career_goals', g)} className="ml-2 hover:text-white">×</button>
                        </span>
                    ))}
                </div>
            </div>

            {/* Budget & Location */}
            <div className="card space-y-4">
                <h3 className="text-lg font-semibold text-brand-400">💰 Budget & Location</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="label">Annual Budget (LPA): ₹{profile.budget_lpa} LPA</label>
                        <input
                            type="range" min={0.5} max={15} step={0.5}
                            className="w-full accent-brand-500"
                            value={profile.budget_lpa}
                            onChange={e => handleField('budget_lpa', parseFloat(e.target.value))}
                        />
                        <div className="flex justify-between text-xs text-slate-500 mt-1">
                            <span>₹0.5 LPA</span><span>₹15 LPA</span>
                        </div>
                    </div>
                    <div className="space-y-3">
                        <div>
                            <label className="label">Preferred States</label>
                            <div className="flex gap-2">
                                <input className="input-field" placeholder="e.g. Maharashtra"
                                    value={stateInput} onChange={e => setStateInput(e.target.value)}
                                    onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addTag('preferred_states', stateInput, setStateInput))}
                                />
                                <button type="button" onClick={() => addTag('preferred_states', stateInput, setStateInput)} className="btn-secondary shrink-0">Add</button>
                            </div>
                            <div className="flex flex-wrap gap-2 mt-2">
                                {profile.preferred_states.map(s => (
                                    <span key={s} className="badge bg-blue-900/50 text-blue-300 border border-blue-700/50">
                                        {s} <button type="button" onClick={() => removeTag('preferred_states', s)} className="ml-1 hover:text-white">×</button>
                                    </span>
                                ))}
                            </div>
                        </div>
                        <div>
                            <label className="label">Preferred Cities</label>
                            <div className="flex gap-2">
                                <input className="input-field" placeholder="e.g. Mumbai"
                                    value={cityInput} onChange={e => setCityInput(e.target.value)}
                                    onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addTag('preferred_cities', cityInput, setCityInput))}
                                />
                                <button type="button" onClick={() => addTag('preferred_cities', cityInput, setCityInput)} className="btn-secondary shrink-0">Add</button>
                            </div>
                            <div className="flex flex-wrap gap-2 mt-2">
                                {profile.preferred_cities.map(c => (
                                    <span key={c} className="badge bg-purple-900/50 text-purple-300 border border-purple-700/50">
                                        {c} <button type="button" onClick={() => removeTag('preferred_cities', c)} className="ml-1 hover:text-white">×</button>
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Number of Recommendations */}
            <div className="card">
                <label className="label">Number of Recommendations: {profile.top_n}</label>
                <input
                    type="range" min={1} max={10} step={1}
                    className="w-full accent-brand-500"
                    value={profile.top_n}
                    onChange={e => handleField('top_n', parseInt(e.target.value))}
                />
                <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>1</span><span>10</span>
                </div>
            </div>

            {/* Submit */}
            <button type="submit" disabled={loading} className="btn-primary w-full text-lg py-4">
                {loading
                    ? <span className="flex items-center justify-center gap-3"><span className="animate-spin">⚙️</span> Analyzing your profile...</span>
                    : '🎓 Get My Personalized Recommendations'}
            </button>
        </form>
    );
}
