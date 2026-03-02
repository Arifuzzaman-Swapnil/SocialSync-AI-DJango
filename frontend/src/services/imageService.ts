import api from './api';
import type {
  ImageGeneration,
  SavedImage,
  UserLogo,
  PromptTemplate,
  UserImageSettings,
} from '../types';

export interface GenerateImageRequest {
  prompt: string;
  title?: string;
  negative_prompt?: string;
  provider?: 'gemini' | 'openai';
  style?: string;
  size?: string;
  quality?: string;
  logo_id?: number | null;
  logo_position?: string;
  logo_size?: number;
  logo_opacity?: number;
  enhance_prompt?: boolean;
  add_lighting?: string;
  camera_angle?: string;
  product_image?: File;
  product_position?: string;
  product_scale?: number;
}

export interface RefinePromptRequest {
  brand_name?: string;
  industry?: string;
  description?: string;
  target_audience?: string;
  ideas?: string[];
  topics?: string[];
  caption_snippet?: string;
  user_prompt: string;
  style?: string;
}

export interface RefinePromptResponse {
  refined_prompt: string;
  used_prompt?: string;
}

export const imageService = {
  // Prompt refinement (link prompt)
  async refinePrompt(data: RefinePromptRequest): Promise<RefinePromptResponse> {
    const response = await api.post<RefinePromptResponse>('/ai-image/refine-prompt/', data);
    return response.data;
  },

  // Generation
  async generate(data: GenerateImageRequest): Promise<ImageGeneration> {
    if (data.product_image) {
      const formData = new FormData();
      formData.append('prompt', data.prompt);
      if (data.title) formData.append('title', data.title);
      if (data.negative_prompt) formData.append('negative_prompt', data.negative_prompt);
      if (data.provider) formData.append('provider', data.provider);
      if (data.style) formData.append('style', data.style);
      if (data.size) formData.append('size', data.size);
      if (data.quality) formData.append('quality', data.quality);
      if (data.logo_id != null) formData.append('logo_id', String(data.logo_id));
      if (data.logo_position) formData.append('logo_position', data.logo_position);
      if (data.logo_size != null) formData.append('logo_size', String(data.logo_size));
      if (data.logo_opacity != null) formData.append('logo_opacity', String(data.logo_opacity));
      if (data.enhance_prompt != null) formData.append('enhance_prompt', String(data.enhance_prompt));
      if (data.add_lighting) formData.append('add_lighting', data.add_lighting);
      if (data.camera_angle) formData.append('camera_angle', data.camera_angle);
      formData.append('product_image', data.product_image);
      if (data.product_position) formData.append('product_position', data.product_position);
      if (data.product_scale != null) formData.append('product_scale', String(data.product_scale));
      const response = await api.post<ImageGeneration>('/ai-image/generate/', formData);
      return response.data;
    }
    const response = await api.post<ImageGeneration>('/ai-image/generate/', data);
    return response.data;
  },

  async getHistory(): Promise<ImageGeneration[]> {
    const response = await api.get<ImageGeneration[]>('/ai-image/history/');
    return response.data;
  },

  // Settings
  async getSettings(): Promise<UserImageSettings> {
    const response = await api.get<UserImageSettings>('/ai-image/settings/');
    return response.data;
  },

  async updateSettings(data: Partial<UserImageSettings>): Promise<UserImageSettings> {
    const response = await api.patch<UserImageSettings>('/ai-image/settings/', data);
    return response.data;
  },

  // Logos
  async getLogos(): Promise<UserLogo[]> {
    const response = await api.get<UserLogo[]>('/ai-image/logos/');
    return response.data;
  },

  async uploadLogo(file: File, name: string, isDefault?: boolean): Promise<UserLogo> {
    const formData = new FormData();
    formData.append('logo_file', file);
    formData.append('name', name);
    if (isDefault) formData.append('is_default', 'true');

    const response = await api.post<UserLogo>('/ai-image/logos/', formData);
    return response.data;
  },

  async deleteLogo(id: number): Promise<void> {
    await api.delete(`/ai-image/logos/${id}/`);
  },

  async setDefaultLogo(id: number): Promise<UserLogo> {
    const response = await api.post<UserLogo>(`/ai-image/logos/${id}/set_default/`);
    return response.data;
  },

  // Saved Images
  async getSaved(): Promise<SavedImage[]> {
    const response = await api.get<SavedImage[]>('/ai-image/saved/');
    return response.data;
  },

  async saveImage(data: {
    name: string;
    image_file: string;
    original_prompt: string;
    source_generation?: number;
    style?: string;
    provider?: string;
    tags?: string;
  }): Promise<SavedImage> {
    const response = await api.post<SavedImage>('/ai-image/saved/', data);
    return response.data;
  },

  async deleteSavedImage(id: number): Promise<void> {
    await api.delete(`/ai-image/saved/${id}/`);
  },

  // Templates
  async getTemplates(): Promise<PromptTemplate[]> {
    const response = await api.get<PromptTemplate[]>('/ai-image/templates/');
    return response.data;
  },

  async createTemplate(data: Partial<PromptTemplate>): Promise<PromptTemplate> {
    const response = await api.post<PromptTemplate>('/ai-image/templates/', data);
    return response.data;
  },

  async deleteTemplate(id: number): Promise<void> {
    await api.delete(`/ai-image/templates/${id}/`);
  },
};

export default imageService;
