/**
 * Unit tests for BackendClient.
 */

import { BackendClient } from '../main/backendClient';
import { RecommendRequest } from '../shared/types';

const MOCK_RESPONSE = {
  source: 'default',
  runes: {
    primaryPath: {
      id: 8000,
      name: 'Precision',
      keystone: { id: 8010, name: 'Conqueror' },
      slots: [],
    },
    secondaryPath: { id: 8400, name: 'Resolve', slots: [] },
    statShards: [],
  },
};

const mockFetch = jest.fn();
global.fetch = mockFetch as typeof fetch;

beforeEach(() => mockFetch.mockReset());

describe('BackendClient', () => {
  const client = new BackendClient('http://localhost:8000');
  const req: RecommendRequest = {
    player_id: 'TestPlayer',
    champion_id: 157,
    enemy_champion_id: 238,
    role: 'MID',
  };

  it('sends POST request and returns recommendation', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => MOCK_RESPONSE,
    } as Response);

    const result = await client.getRecommendation(req);
    expect(result.source).toBe('default');
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/runes/recommend',
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('throws an error on non-OK response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      text: async () => 'Not found',
    } as Response);

    await expect(client.getRecommendation(req)).rejects.toThrow('404');
  });
});
