/**
 * HTTP client for the RuneLoLDB FastAPI backend.
 */

import { RecommendRequest, RecommendResponse } from '../shared/types';

export class BackendClient {
  constructor(private readonly baseUrl: string) {}

  async getRecommendation(req: RecommendRequest): Promise<RecommendResponse> {
    const response = await fetch(`${this.baseUrl}/api/runes/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Backend error ${response.status}: ${text}`);
    }
    return response.json() as Promise<RecommendResponse>;
  }
}
