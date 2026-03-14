/**
 * Overlay HTML renderer.
 *
 * Generates the HTML string for the champion-select rune overlay panel.
 * Kept as a pure function so it is trivial to unit-test without a DOM.
 */

import { RecommendResponse, RunePage } from '../shared/types';

// ---------------------------------------------------------------------------
// Source labels
// ---------------------------------------------------------------------------

const SOURCE_LABELS: Record<string, string> = {
  player_history: '📖 Player History',
  default: '📋 Champion Default',
  pro_data: '🏆 Pro / High-Elo Data',
};

// ---------------------------------------------------------------------------
// Sub-component renderers
// ---------------------------------------------------------------------------

function renderRuneSlot(slot: { id: number; name: string }): string {
  return `<span class="rune-slot" title="${slot.name}">${slot.name}</span>`;
}

function renderRunePath(path: RunePage['primaryPath'], isPrimary: boolean): string {
  const keystoneHtml = isPrimary && path.keystone
    ? `<div class="keystone">${renderRuneSlot(path.keystone)}</div>`
    : '';
  const slotsHtml = path.slots
    .map((s) => renderRuneSlot(s))
    .join('');
  return `
    <div class="rune-path ${isPrimary ? 'primary' : 'secondary'}">
      <div class="path-name">${path.name}</div>
      ${keystoneHtml}
      <div class="path-slots">${slotsHtml}</div>
    </div>`;
}

function renderStats(rec: RecommendResponse): string {
  const parts: string[] = [];
  if (rec.win_rate !== undefined) {
    parts.push(`Win Rate: <strong>${(rec.win_rate * 100).toFixed(1)}%</strong>`);
  }
  if (rec.sample_size !== undefined) {
    parts.push(`Sample: <strong>${rec.sample_size.toLocaleString()} games</strong>`);
  }
  if (rec.matchup_win_rate !== undefined) {
    parts.push(
      `Matchup WR: <strong>${(rec.matchup_win_rate * 100).toFixed(1)}%</strong>`,
    );
  }
  if (rec.matchup_difficulty) {
    const icon =
      rec.matchup_difficulty === 'Hard'
        ? '🔴'
        : rec.matchup_difficulty === 'Medium'
        ? '🟡'
        : '🟢';
    parts.push(`Difficulty: <strong>${icon} ${rec.matchup_difficulty}</strong>`);
  }
  if (!parts.length) return '';
  return `<div class="stats">${parts.join(' &nbsp;|&nbsp; ')}</div>`;
}

// ---------------------------------------------------------------------------
// Main overlay renderer
// ---------------------------------------------------------------------------

/** Render the full overlay HTML. Returns a waiting message when rec is null. */
export function renderOverlay(rec: RecommendResponse | null): string {
  if (!rec) {
    return `
      <div class="overlay waiting">
        <div class="header">RuneLoLDB</div>
        <div class="waiting-msg">Waiting for champion select…</div>
      </div>`;
  }

  const sourceLabel = SOURCE_LABELS[rec.source] ?? rec.source;

  return `
    <div class="overlay active">
      <div class="header">
        <span class="title">RuneLoLDB</span>
        <span class="source-badge">${sourceLabel}</span>
      </div>

      ${renderStats(rec)}

      <div class="rune-pages">
        ${renderRunePath(rec.runes.primaryPath, true)}
        ${renderRunePath(rec.runes.secondaryPath, false)}
      </div>

      <div class="stat-shards">
        <div class="section-label">Stat Shards</div>
        ${rec.runes.statShards.map((s) => renderRuneSlot(s)).join('')}
      </div>

      <button id="import-btn" class="import-btn">⚡ Auto Import Runes</button>
    </div>`;
}
