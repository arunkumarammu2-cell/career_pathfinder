/**
 * API Service Layer — typed Axios client for the career intelligence backend.
 */

import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

const client = axios.create({
    baseURL: API_BASE,
    headers: { 'Content-Type': 'application/json' },
    timeout: 30000,
});

// ─── Types ───────────────────────────────────────────────────

export interface AcademicScores {
    maths?: number;
    physics?: number;
    chemistry?: number;
    biology?: number;
    computer_science?: number;
    english?: number;
    economics?: number;
    accountancy?: number;
    overall_percentile: number;
}

export interface UserProfileRequest {
    name: string;
    stream: 'Science' | 'Commerce' | 'Arts';
    academic_scores: AcademicScores;
    interests: string[];
    budget_lpa: number;
    preferred_states: string[];
    preferred_cities: string[];
    learning_style: 'theory' | 'practical' | 'mixed';
    career_goals: string[];
    top_n: number;
}

export interface ScoreBreakdown {
    academic_compatibility: number;
    interest_alignment: number;
    budget_fit: number;
    location_preference: number;
    reputation_score: number;
    career_outcome: number;
    overall: number;
}

export interface SkillGap {
    skill: string;
    importance: 'Critical' | 'Important' | 'Nice to have';
    resources: string[];
}

export interface CareerPath {
    career_title: string;
    path_type: string;
    avg_salary_range: string;
    year_wise_roadmap: string[];
    required_skills: string[];
    recommended_certifications: string[];
}

export interface CollegeRecommendation {
    rank: number;
    college_id: string;
    name: string;
    state: string;
    city: string;
    stream: string;
    avg_fees_lpa: number;
    placement_rate: number;
    avg_salary_lpa: number;
    internship_rate: number;
    higher_studies_rate: number;
    industry_exposure: number;
    specializations: string[];
    score_breakdown: ScoreBreakdown;
    why_this_college: string;
    pros: string[];
    cons: string[];
    suggested_next_actions: string[];
    skill_improvement_plan: SkillGap[];
    alternate_careers: string[];
}

export interface RecommendationResponse {
    student_name: string;
    stream: string;
    total_colleges_analyzed: number;
    recommendations: CollegeRecommendation[];
    career_paths: CareerPath[];
    analytics_summary: Record<string, string | number>;
}

export interface HealthResponse {
    status: string;
    version: string;
    dataset_loaded: boolean;
    total_colleges: number;
}

// ─── API Functions ──────────────────────────────────────────

export async function getRecommendations(profile: UserProfileRequest): Promise<RecommendationResponse> {
    const { data } = await client.post<RecommendationResponse>('/recommend', profile);
    return data;
}

export async function checkHealth(): Promise<HealthResponse> {
    const { data } = await client.get<HealthResponse>('/health');
    return data;
}

export async function getSampleProfile(): Promise<UserProfileRequest> {
    const { data } = await client.get<UserProfileRequest>('/sample-profile');
    return data;
}
