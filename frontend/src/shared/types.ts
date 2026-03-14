/** Shared TypeScript types for RuneLoLDB. */

export interface RuneSlot {
  id: number;
  name: string;
}

export interface RunePath {
  id: number;
  name: string;
  keystone?: RuneSlot;
  slots: RuneSlot[];
}

export interface RunePage {
  primaryPath: RunePath;
  secondaryPath: RunePath;
  statShards: RuneSlot[];
}

export type RecommendationSource = 'player_history' | 'default' | 'pro_data';

export interface RecommendResponse {
  runes: RunePage;
  source: RecommendationSource;
  win_rate?: number;
  sample_size?: number;
  matchup_difficulty?: string;
  matchup_win_rate?: number;
}

export interface RecommendRequest {
  player_id: string;
  champion_id: number;
  enemy_champion_id: number;
  role: string;
}

export interface MatchResultPayload {
  player_id: string;
  match_id: string;
  champion_id: number;
  enemy_champion_id: number;
  role: string;
  runes: RunePage;
  win: boolean;
}

export interface ChampSelectSession {
  localPlayerCellId: number;
  myTeam: Array<{
    cellId: number;
    championId: number;
    assignedPosition: string;
  }>;
  theirTeam: Array<{
    cellId: number;
    championId: number;
  }>;
}

export interface IpcChannels {
  // Renderer → Main
  REQUEST_RECOMMENDATION: 'request-recommendation';
  IMPORT_RUNES: 'import-runes';
  // Main → Renderer
  RECOMMENDATION_RESULT: 'recommendation-result';
  CHAMP_SELECT_UPDATE: 'champ-select-update';
  ERROR: 'error';
}
