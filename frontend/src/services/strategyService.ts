import api from './api';

export const strategyService = {
  // Content Pillars
  async getPillars(brandId: number) {
    const res = await api.get(`/content-pillars/by-brand/${brandId}/`);
    return res.data;
  },
  async createPillar(data: { brand?: number; name: string; description?: string; target_percentage: number; color_code?: string }) {
    const res = await api.post('/content-pillars/', data);
    return res.data;
  },
  async updatePillar(id: number, data: Record<string, unknown>) {
    const res = await api.patch(`/content-pillars/${id}/`, data);
    return res.data;
  },
  async deletePillar(id: number) {
    await api.delete(`/content-pillars/${id}/`);
  },
  async getPillarCompliance(brandId: number) {
    const res = await api.get(`/brands/${brandId}/pillar-compliance/`);
    return res.data;
  },

  // Competitors
  async getCompetitors(brandId: number) {
    const res = await api.get(`/competitor-profiles/by-brand/${brandId}/`);
    return res.data;
  },
  async addCompetitor(data: { brand?: number; platform: string; handle_or_url: string }) {
    const res = await api.post('/competitor-profiles/', data);
    return res.data;
  },
  async deleteCompetitor(id: number) {
    await api.delete(`/competitor-profiles/${id}/`);
  },
  async triggerCrawl(brandId: number, competitorId?: number) {
    const data = competitorId ? { competitor_id: competitorId } : {};
    const res = await api.post(`/brands/${brandId}/competitors/crawl/`, data);
    return res.data;
  },
  async getInsights(brandId: number) {
    const res = await api.get(`/brands/${brandId}/competitors/insights/`);
    return res.data;
  },

  // Brand Templates
  async getTemplates(brandId?: number) {
    const params = brandId ? { brand: brandId } : {};
    const res = await api.get('/brand-templates/', { params });
    return res.data;
  },
  async createTemplate(data: FormData) {
    const res = await api.post('/brand-templates/', data);
    return res.data;
  },

  // Ideas
  async generateIdeas(data: { brand_id: number; pillar_id?: number; platform?: string; count?: number }) {
    const res = await api.post('/ideas/generate/', data);
    return res.data;
  },
  async regenerateIdea(ideaId: number) {
    const res = await api.post(`/ideas/${ideaId}/regenerate/`);
    return res.data;
  },
  async addIdeaToCalendar(ideaId: number) {
    const res = await api.post(`/ideas/${ideaId}/add-to-calendar/`);
    return res.data;
  },
  async getTrending(platform?: string) {
    const params = platform ? { platform } : {};
    const res = await api.get('/trending/', { params });
    return res.data;
  },

  // Brand DNA
  async generateDNA(brandId: number, websiteUrl: string) {
    const res = await api.post(`/brands/${brandId}/generate-dna/`, { website_url: websiteUrl });
    return res.data;
  },
  async getDNAStatus(brandId: number) {
    const res = await api.get(`/brands/${brandId}/dna-status/`);
    return res.data;
  },
};

export default strategyService;
