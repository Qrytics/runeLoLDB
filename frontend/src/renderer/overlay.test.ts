/**
 * Unit tests for the overlay renderer.
 * These run in Node.js via Jest with no browser environment required.
 */

import { renderOverlay } from '../renderer/overlay';
import { RecommendResponse } from '../shared/types';

const SAMPLE_RECOMMENDATION: RecommendResponse = {
  source: 'player_history',
  runes: {
    primaryPath: {
      id: 8000,
      name: 'Precision',
      keystone: { id: 8010, name: 'Conqueror' },
      slots: [
        { id: 9111, name: 'Triumph' },
        { id: 9104, name: 'Legend: Alacrity' },
        { id: 8014, name: 'Last Stand' },
      ],
    },
    secondaryPath: {
      id: 8400,
      name: 'Resolve',
      slots: [
        { id: 8429, name: 'Bone Plating' },
        { id: 8451, name: 'Overgrowth' },
      ],
    },
    statShards: [
      { id: 5008, name: 'Adaptive Force' },
      { id: 5008, name: 'Adaptive Force' },
      { id: 5002, name: 'Armor' },
    ],
  },
};

describe('renderOverlay', () => {
  it('renders waiting state when recommendation is null', () => {
    const html = renderOverlay(null);
    expect(html).toContain('Waiting for champion select');
    expect(html).toContain('waiting');
  });

  it('renders active state with recommendation data', () => {
    const html = renderOverlay(SAMPLE_RECOMMENDATION);
    expect(html).toContain('Conqueror');
    expect(html).toContain('Precision');
    expect(html).toContain('Resolve');
    expect(html).toContain('Bone Plating');
    expect(html).toContain('Auto Import Runes');
  });

  it('shows player history source label', () => {
    const html = renderOverlay(SAMPLE_RECOMMENDATION);
    expect(html).toContain('Player History');
  });

  it('shows pro data source label', () => {
    const rec: RecommendResponse = {
      ...SAMPLE_RECOMMENDATION,
      source: 'pro_data',
      win_rate: 0.54,
      sample_size: 1000,
    };
    const html = renderOverlay(rec);
    expect(html).toContain('Pro / High-Elo Data');
    expect(html).toContain('54.0%');
    expect(html).toContain('1,000 games');
  });

  it('shows default source label', () => {
    const rec: RecommendResponse = {
      ...SAMPLE_RECOMMENDATION,
      source: 'default',
    };
    const html = renderOverlay(rec);
    expect(html).toContain('Champion Default');
  });

  it('renders matchup difficulty when provided', () => {
    const rec: RecommendResponse = {
      ...SAMPLE_RECOMMENDATION,
      matchup_difficulty: 'Hard',
      matchup_win_rate: 0.42,
    };
    const html = renderOverlay(rec);
    expect(html).toContain('Hard');
    expect(html).toContain('42.0%');
  });

  it('renders all stat shards', () => {
    const html = renderOverlay(SAMPLE_RECOMMENDATION);
    expect(html).toContain('Adaptive Force');
    expect(html).toContain('Armor');
  });
});
