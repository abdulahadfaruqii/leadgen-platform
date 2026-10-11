export interface Business {
  id: string;
  name: string;
  slug: string;
  category: string;
  country: string;
  state: string;
  city: string;
  address?: string;
  website?: string;
  phone?: string;
  email?: string;
  google_rating?: number;
  google_review_count?: number;
  lead_score?: number;
  website_quality_score?: number;
  mobile_responsive?: boolean;
  seo_score?: number;
  detected_technologies?: string[];
  missing_features?: string[];
  social_profiles?: Record<string, string>;
  status: string;
  discovered_at: string;
}

export interface Lead {
  id: string;
  business_id: string;
  business?: Business;
  overall_score: number;
  website_quality_score?: number;
  digital_presence_score?: number;
  technology_score?: number;
  social_activity_score?: number;
  review_score?: number;
  growth_score?: number;
  opportunity_score?: number;
  qualification_reasons?: string[];
  priority: string;
  recommended_services?: ServiceRecommendation[];
  outreach_status: string;
  last_contact_date?: string;
  next_follow_up_date?: string;
  contact_attempts: number;
  notes?: string;
  ai_summary?: string;
  qualified_at: string;
}

export interface ServiceRecommendation {
  service_id: string;
  service_name: string;
  description: string;
  fit_score: number;
  reasons: string[];
  estimated_impact: string;
  ai_insight?: string;
  pitch_angle?: string;
}

export interface Campaign {
  id: string;
  name: string;
  description?: string;
  target_country: string;
  target_state?: string;
  target_city?: string;
  target_categories: string[];
  services: string[];
  status: string;
  progress_percent: number;
  businesses_found: number;
  leads_qualified: number;
  outreach_sent: number;
  responses_received: number;
  scheduled_start?: string;
  started_at?: string;
  completed_at?: string;
}

export interface OutreachMessage {
  id: string;
  business_id: string;
  lead_id?: string;
  channel: string;
  message_type: string;
  subject?: string;
  body: string;
  body_html?: string;
  status: string;
  scheduled_at?: string;
  sent_at?: string;
  opened_at?: string;
  replied_at?: string;
  requires_approval: boolean;
  approved_at?: string;
  sequence_position: number;
}

export interface DashboardMetrics {
  total_businesses_found: number;
  total_leads_qualified: number;
  total_outreach_sent: number;
  total_responses: number;
  avg_lead_score: number;
  conversion_rate: number;
  top_categories: { name: string; count: number }[];
  top_countries: { name: string; count: number }[];
  score_distribution: { range: string; count: number }[];
  weekly_activity: { week: string; businesses: number; leads: number; outreach: number }[];
  outreach_funnel?: {
    sent: number;
    opened: number;
    clicked: number;
    replied: number;
  };
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  subscription_tier: string;
  monthly_lead_quota: number;
  monthly_leads_used: number;
}
