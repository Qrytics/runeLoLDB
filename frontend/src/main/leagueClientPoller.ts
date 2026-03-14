/**
 * League Client API poller.
 *
 * Polls the backend at a fixed interval to detect champion-select state
 * changes and fires callbacks when the player enters or exits champ select.
 */

import { ChampSelectSession } from '../shared/types';

export interface LeagueClientPollerOptions {
  pollIntervalMs?: number;
  onChampSelectEntered: (session: ChampSelectSession) => void | Promise<void>;
  onChampSelectExited: () => void;
}

const DEFAULT_INTERVAL_MS = 3000;

export class LeagueClientPoller {
  private intervalId: ReturnType<typeof setInterval> | null = null;
  private inChampSelect = false;
  private opts: Required<LeagueClientPollerOptions>;

  constructor(opts: LeagueClientPollerOptions) {
    this.opts = {
      pollIntervalMs: opts.pollIntervalMs ?? DEFAULT_INTERVAL_MS,
      onChampSelectEntered: opts.onChampSelectEntered,
      onChampSelectExited: opts.onChampSelectExited,
    };
  }

  start(): void {
    if (this.intervalId !== null) return;
    this.intervalId = setInterval(() => this.poll(), this.opts.pollIntervalMs);
  }

  stop(): void {
    if (this.intervalId !== null) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  private async poll(): Promise<void> {
    try {
      const session = await this.fetchChampSelectSession();
      if (session) {
        if (!this.inChampSelect) {
          this.inChampSelect = true;
        }
        await this.opts.onChampSelectEntered(session);
      } else {
        if (this.inChampSelect) {
          this.inChampSelect = false;
          this.opts.onChampSelectExited();
        }
      }
    } catch {
      // LCU not available — silently ignore until it comes up.
    }
  }

  /**
   * Fetch the current champ-select session from the League Client.
   * Returns null when not in champ select or client is unavailable.
   *
   * The actual HTTP call is made through the backend proxy endpoint so that
   * SSL certificate issues with the LCU are handled server-side.
   */
  private async fetchChampSelectSession(): Promise<ChampSelectSession | null> {
    const baseUrl = process.env.BACKEND_URL ?? 'http://localhost:8000';
    const response = await fetch(`${baseUrl}/lcu/champ-select`);
    if (!response.ok) return null;
    const data = await response.json();
    return data as ChampSelectSession;
  }
}
