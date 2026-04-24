/**
 * Client-side export helpers — no extra library needed.
 * Supports CSV, JSON, Markdown, and basic HTML→PDF (via browser print).
 */

function downloadBlob(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  URL.revokeObjectURL(url)
}

/** Convert array of objects → CSV string */
function toCSV(rows: Record<string, any>[], headers?: string[]): string {
  if (!rows.length) return ''
  const keys = headers || Object.keys(rows[0])
  const escape = (v: any) => {
    const s = v == null ? '' : Array.isArray(v) ? v.join('; ') : String(v)
    return s.includes(',') || s.includes('"') || s.includes('\n')
      ? `"${s.replace(/"/g, '""')}"` : s
  }
  return [keys.join(','), ...rows.map(r => keys.map(k => escape(r[k])).join(','))].join('\n')
}

/** Export posts */
export function exportPosts(posts: any[], format: 'csv' | 'json' | 'md') {
  const ts = new Date().toISOString().slice(0, 10)

  if (format === 'json') {
    downloadBlob(JSON.stringify(posts, null, 2), `posts_${ts}.json`, 'application/json')
    return
  }

  if (format === 'csv') {
    const rows = posts.map(p => ({
      id: p.id, platform: p.platform, content_type: p.content_type,
      title: p.title, body: p.body, hashtags: (p.hashtags || []).join(' '),
      status: p.status, created_at: p.created_at, image_prompt: p.image_prompt || '',
    }))
    downloadBlob(toCSV(rows), `posts_${ts}.csv`, 'text/csv')
    return
  }

  if (format === 'md') {
    const md = posts.map(p =>
      `## [${p.platform?.toUpperCase()}] ${p.title || p.body?.slice(0, 60)}\n` +
      `**Status:** ${p.status}  |  **Type:** ${p.content_type}  |  **Date:** ${p.created_at?.slice(0,10)}\n\n` +
      `${p.body}\n\n` +
      (p.hashtags?.length ? `*Tags: ${p.hashtags.join(' ')}*\n\n` : '') +
      (p.image_prompt ? `*Image prompt: ${p.image_prompt}*\n\n` : '') +
      `---\n`
    ).join('\n')
    downloadBlob(`# RightLeftAI Content Posts\n*Exported ${ts}*\n\n${md}`, `posts_${ts}.md`, 'text/markdown')
  }
}

/** Export leads */
export function exportLeads(leads: any[], format: 'csv' | 'json' | 'md') {
  const ts = new Date().toISOString().slice(0, 10)

  if (format === 'json') {
    downloadBlob(JSON.stringify(leads, null, 2), `leads_${ts}.json`, 'application/json')
    return
  }

  if (format === 'csv') {
    const rows = leads.map(l => ({
      id: l.id, name: l.name, email: l.email, company: l.company,
      designation: l.designation, domain: l.domain, status: l.status,
      tags: (l.tags || []).join('; '), notes: l.notes, created_at: l.created_at,
    }))
    downloadBlob(toCSV(rows), `leads_${ts}.csv`, 'text/csv')
    return
  }

  if (format === 'md') {
    const md = leads.map(l =>
      `### ${l.name} — ${l.company}\n` +
      `- **Email:** ${l.email}\n- **Domain:** ${l.domain}\n- **Designation:** ${l.designation}\n` +
      `- **Status:** ${l.status}\n` +
      (l.tags?.length ? `- **Tags:** ${l.tags.join(', ')}\n` : '') +
      (l.notes ? `- **Notes:** ${l.notes}\n` : '') + '\n'
    ).join('')
    downloadBlob(`# RightLeftAI Leads\n*Exported ${ts}*\n\n${md}`, `leads_${ts}.md`, 'text/markdown')
  }
}

/** Export opportunities */
export function exportOpportunities(opps: any[], format: 'csv' | 'json' | 'md') {
  const ts = new Date().toISOString().slice(0, 10)

  if (format === 'json') {
    downloadBlob(JSON.stringify(opps, null, 2), `opportunities_${ts}.json`, 'application/json')
    return
  }

  if (format === 'csv') {
    const rows = opps.map(o => ({
      id: o.id, title: o.title, domain: o.domain, priority: o.priority,
      relevant_product: o.relevant_product, status: o.status,
      summary: o.summary, action_suggested: o.action_suggested,
      source_url: o.source_url, discovered_at: o.discovered_at,
    }))
    downloadBlob(toCSV(rows), `opportunities_${ts}.csv`, 'text/csv')
    return
  }

  if (format === 'md') {
    const md = opps.map(o =>
      `### [${o.priority}] ${o.title}\n` +
      `- **Domain:** ${o.domain}  |  **Product:** ${o.relevant_product}  |  **Status:** ${o.status}\n\n` +
      `${o.summary}\n\n**Action:** ${o.action_suggested}\n\n` +
      (o.source_url ? `*Source: ${o.source_url}*\n\n` : '') + `---\n`
    ).join('\n')
    downloadBlob(`# RightLeftAI Opportunities\n*Exported ${ts}*\n\n${md}`, `opportunities_${ts}.md`, 'text/markdown')
  }
}

/** Export calendar plan */
export function exportCalendar(calendar: any, format: 'json' | 'md' | 'csv') {
  const ts = new Date().toISOString().slice(0, 10)

  if (format === 'json') {
    downloadBlob(JSON.stringify(calendar, null, 2), `calendar_${ts}.json`, 'application/json')
    return
  }

  if (format === 'csv') {
    const rows = (calendar.days || []).flatMap((d: any) => [
      { day: d.day, date: d.date, platform: 'LinkedIn',   type: d.linkedin?.content_type, title: d.linkedin?.title,              angle: d.linkedin?.angle,         cta: d.linkedin?.cta },
      { day: d.day, date: d.date, platform: 'Instagram',  type: d.instagram?.content_type, title: d.instagram?.caption_angle,   angle: '',                        cta: '' },
      { day: d.day, date: d.date, platform: 'Email',      type: d.email_idea?.target_domain, title: d.email_idea?.subject_line, angle: d.email_idea?.angle,       cta: '' },
    ])
    downloadBlob(toCSV(rows, ['day','date','platform','type','title','angle','cta']), `calendar_${ts}.csv`, 'text/csv')
    return
  }

  if (format === 'md') {
    const days = (calendar.days || []).map((d: any) =>
      `## ${d.day} — ${d.date}\n\n` +
      `### LinkedIn\n**${d.linkedin?.content_type?.replace('_',' ')}** · ${d.linkedin?.title}\n${d.linkedin?.angle || ''}\n${d.linkedin?.cta ? `*CTA: ${d.linkedin.cta}*` : ''}\n\n` +
      `### Instagram\n**${d.instagram?.content_type}** · ${d.instagram?.caption_angle}\n${(d.instagram?.hashtags || []).slice(0,5).join(' ')}\n\n` +
      `### Email\n**${d.email_idea?.target_domain}** · ${d.email_idea?.subject_line}\n${d.email_idea?.angle || ''}\n\n---\n`
    ).join('\n')

    const md = `# RightLeftAI Weekly Content Calendar\n**Theme:** ${calendar.week_theme}\n*Exported ${ts}*\n\n${calendar.cmo_notes ? `> ${calendar.cmo_notes}\n\n` : ''}${days}` +
      (calendar.weekly_thought_leadership_topic ? `\n## Thought Leadership Article\n${calendar.weekly_thought_leadership_topic}\n` : '')

    downloadBlob(md, `calendar_${ts}.md`, 'text/markdown')
  }
}

/** Print any HTML element as PDF via browser */
export function printAsPDF(title = 'RightLeftAI Export') {
  document.title = title
  window.print()
}
