import api from './api';
import type { Post, PlatformType } from '../types';

interface AnalyticsSummary {
  total_likes: number;
  total_shares: number;
  total_comments: number;
  total_views: number;
  total_impressions: number;
  engagement_rate: number;
}

interface PlatformAnalytics {
  platform: PlatformType;
  likes: number;
  shares: number;
  comments: number;
  views: number;
  impressions: number;
  engagement_rate: number;
  post_count: number;
}

interface AnalyticsTrend {
  date: string;
  value: number;
}

export const analyticsService = {
  // Summary
  async getSummary(days?: number): Promise<AnalyticsSummary> {
    const params = days ? { days } : {};
    const response = await api.get<AnalyticsSummary>('/analytics/summary/', { params });
    return response.data;
  },

  // Platform breakdown
  async getPlatformAnalytics(days?: number): Promise<Record<PlatformType, PlatformAnalytics>> {
    const params = days ? { days } : {};
    const response = await api.get<Record<PlatformType, PlatformAnalytics>>('/analytics/platforms/', { params });
    return response.data;
  },

  // Trends
  async getTrends(metric?: string, days?: number): Promise<AnalyticsTrend[]> {
    const params: Record<string, string | number> = {};
    if (metric) params.metric = metric;
    if (days) params.days = days;
    const response = await api.get<AnalyticsTrend[]>('/analytics/trends/', { params });
    return response.data;
  },

  // Top posts
  async getTopPosts(metric?: string, limit?: number): Promise<Post[]> {
    const params: Record<string, string | number> = {};
    if (metric) params.metric = metric;
    if (limit) params.limit = limit;
    const response = await api.get<Post[]>('/analytics/top-posts/', { params });
    return response.data;
  },

  // Combined analytics data for dashboard
  async getDashboardData(days: number = 30): Promise<{
    summary: AnalyticsSummary;
    platforms: Record<PlatformType, PlatformAnalytics>;
    trends: AnalyticsTrend[];
    topPosts: Post[];
  }> {
    const [summary, platforms, trends, topPosts] = await Promise.all([
      this.getSummary(days),
      this.getPlatformAnalytics(days),
      this.getTrends('likes', days),
      this.getTopPosts('likes', 5),
    ]);

    return { summary, platforms, trends, topPosts };
  },
};

export default analyticsService;
