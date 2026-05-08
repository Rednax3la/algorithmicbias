// ============================================================
// Research Dashboard — Bias Charts + Fairness Metrics
// ============================================================

const CHART_COLORS = {
  blue: '#1a56db',
  green: '#057a55',
  red: '#e02424',
  orange: '#c27803',
  purple: '#7e3af2',
  gray: '#6b7280',
  lightBlue: 'rgba(26,86,219,0.15)',
  lightGreen: 'rgba(5,122,85,0.15)',
  lightRed: 'rgba(224,36,36,0.15)',
}

;(async () => {
  try {
    const resp = await fetch('/api/fairness')
    let data

    if (resp.ok) {
      data = await resp.json()
    } else {
      // Fallback to synthetic data when API not available
      data = getSyntheticData()
    }

    renderResearchDashboard(data)
  } catch (e) {
    // API not reachable (e.g. local file open) — use synthetic data
    renderResearchDashboard(getSyntheticData())
  }

  document.getElementById('research-loading').classList.add('hidden')
  document.getElementById('research-content').classList.remove('hidden')
})()

function renderResearchDashboard(data) {
  renderApprovalCharts(data.approval_rates)
  renderFairnessTable(data.models)
  renderFeatureImportance(data.feature_importance)
  renderUserPatterns(data)
  renderDatasetCharts(data)
}

// ── Section 1: Approval rate charts ──────────────────────────
function renderApprovalCharts(rates) {
  // Location
  new Chart(document.getElementById('chart-location').getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Urban', 'Rural'],
      datasets: [{
        data: [
          Math.round(rates.by_location.urban * 100),
          Math.round(rates.by_location.rural * 100)
        ],
        backgroundColor: [CHART_COLORS.blue, CHART_COLORS.red],
        borderRadius: 6,
      }]
    },
    options: barOptions('Approval Rate (%)')
  })

  // Gender
  new Chart(document.getElementById('chart-gender').getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Male', 'Female'],
      datasets: [{
        data: [
          Math.round(rates.by_gender.male * 100),
          Math.round(rates.by_gender.female * 100)
        ],
        backgroundColor: [CHART_COLORS.blue, CHART_COLORS.orange],
        borderRadius: 6,
      }]
    },
    options: barOptions('Approval Rate (%)')
  })

  // Device
  new Chart(document.getElementById('chart-device').getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['Feature Phone', 'Budget', 'Mid-Range', 'High-End'],
      datasets: [{
        data: [
          Math.round(rates.by_device.feature_phone * 100),
          Math.round(rates.by_device.budget * 100),
          Math.round(rates.by_device.mid * 100),
          Math.round(rates.by_device.high_end * 100)
        ],
        backgroundColor: [CHART_COLORS.red, CHART_COLORS.orange, CHART_COLORS.blue, CHART_COLORS.green],
        borderRadius: 6,
      }]
    },
    options: barOptions('Approval Rate (%)')
  })
}

function barOptions(yLabel) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        title: { display: true, text: yLabel, font: { size: 11 } },
        grid: { color: '#f3f4f6' },
        ticks: { callback: v => v + '%' }
      },
      x: { grid: { display: false } }
    }
  }
}

// ── Section 2: Fairness table ─────────────────────────────────
function renderFairnessTable(models) {
  const tbody = document.getElementById('fairness-table-body')
  const rows = []

  const modelLabels = {
    logistic_regression: 'Logistic Regression',
    random_forest: 'Random Forest',
    gradient_boosting: 'Gradient Boosting'
  }

  for (const [key, metrics] of Object.entries(models)) {
    for (const [attr, vals] of Object.entries(metrics)) {
      const di = vals.disparate_impact
      const spd = vals.statistical_parity_difference
      const eod = vals.equal_opportunity_difference

      const diClass = di >= 0.8 ? 'metric-fair' : di >= 0.6 ? 'metric-concern' : 'metric-unfair'
      const spdClass = Math.abs(spd) <= 0.05 ? 'metric-fair' : Math.abs(spd) <= 0.1 ? 'metric-concern' : 'metric-unfair'
      const eodClass = Math.abs(eod) <= 0.05 ? 'metric-fair' : Math.abs(eod) <= 0.1 ? 'metric-concern' : 'metric-unfair'

      const overall = di >= 0.8 && Math.abs(spd) <= 0.05 ? 'Fair'
        : di >= 0.6 && Math.abs(spd) <= 0.1 ? '⚠ Concern'
        : '✗ Unfair'
      const overallClass = overall === 'Fair' ? 'metric-fair' : overall.includes('Concern') ? 'metric-concern' : 'metric-unfair'

      rows.push(`
        <tr>
          <td>${modelLabels[key] || key}</td>
          <td>${attr.replace('_', ' ')}</td>
          <td class="${diClass}">${di.toFixed(3)}</td>
          <td class="${spdClass}">${spd > 0 ? '+' : ''}${spd.toFixed(3)}</td>
          <td class="${eodClass}">${eod > 0 ? '+' : ''}${eod.toFixed(3)}</td>
          <td class="${overallClass}">${overall}</td>
        </tr>`)
    }
  }

  tbody.innerHTML = rows.join('')
}

// ── Section 3: Feature importance ────────────────────────────
function renderFeatureImportance(features) {
  const container = document.getElementById('feature-importance-list')
  const maxVal = Math.max(...features.map(f => f.importance))

  container.innerHTML = features.map(f => {
    const pct = Math.round((f.importance / maxVal) * 100)
    const barColor = f.is_bias_flagged ? CHART_COLORS.red : CHART_COLORS.blue
    return `
      <div class="feature-item">
        <div class="feature-item__name">
          ${f.feature}
          ${f.is_bias_flagged ? '<span class="bias-tag"> ⚠ BIAS</span>' : ''}
        </div>
        <div class="feature-item__bar-wrap">
          <div class="progress-bar">
            <div class="progress-bar__fill" style="width:${pct}%; background:${barColor};"></div>
          </div>
        </div>
        <div class="feature-item__pct">${(f.importance * 100).toFixed(1)}%</div>
      </div>`
  }).join('')
}

// ── Section 4: User patterns (from anonymized_data or synthetic) ──
async function renderUserPatterns(data) {
  let userLocationData, userDeviceData, note

  // Try to pull from Supabase anonymized_data
  try {
    const { data: anonRows, error } = await supabase
      .from('anonymized_data')
      .select('location_type, device_tier, credit_score, approved')
      .limit(500)

    if (!error && anonRows && anonRows.length > 0) {
      // Aggregate by location
      const byLocation = { Urban: [], Rural: [] }
      const byDevice = { feature: [], budget: [], mid: [], high: [] }

      for (const row of anonRows) {
        if (row.location_type && byLocation[row.location_type]) {
          byLocation[row.location_type].push(row.credit_score)
        }
        if (row.device_tier && byDevice[row.device_tier]) {
          byDevice[row.device_tier].push(row.credit_score)
        }
      }

      const avg = arr => arr.length ? (arr.reduce((s, v) => s + v, 0) / arr.length).toFixed(1) : 0

      userLocationData = {
        labels: ['Urban', 'Rural'],
        data: [avg(byLocation.Urban), avg(byLocation.Rural)]
      }
      userDeviceData = {
        labels: ['Feature Phone', 'Budget', 'Mid-Range', 'High-End'],
        data: [avg(byDevice.feature), avg(byDevice.budget), avg(byDevice.mid), avg(byDevice.high)]
      }
      note = `Based on ${anonRows.length} consenting user submissions.`
    }
  } catch (e) { /* Supabase not configured */ }

  // Fall back to synthetic patterns
  if (!userLocationData) {
    userLocationData = { labels: ['Urban', 'Rural'], data: [62.4, 51.8] }
    userDeviceData = { labels: ['Feature Phone', 'Budget', 'Mid-Range', 'High-End'], data: [43.2, 52.1, 61.0, 67.5] }
    note = 'Showing synthetic data patterns. Real user data will appear here once users consent.'
  }

  document.getElementById('user-data-note').textContent = note

  new Chart(document.getElementById('chart-user-location').getContext('2d'), {
    type: 'bar',
    data: {
      labels: userLocationData.labels,
      datasets: [{
        label: 'Avg Credit Score',
        data: userLocationData.data,
        backgroundColor: [CHART_COLORS.blue, CHART_COLORS.red],
        borderRadius: 6,
      }]
    },
    options: barOptions('Average Credit Score')
  })

  new Chart(document.getElementById('chart-user-device').getContext('2d'), {
    type: 'bar',
    data: {
      labels: userDeviceData.labels,
      datasets: [{
        label: 'Avg Credit Score',
        data: userDeviceData.data,
        backgroundColor: [CHART_COLORS.red, CHART_COLORS.orange, CHART_COLORS.blue, CHART_COLORS.green],
        borderRadius: 6,
      }]
    },
    options: barOptions('Average Credit Score')
  })
}

// ── Section 5: Dataset overview ───────────────────────────────
function renderDatasetCharts(data) {
  const stats = data.dataset_stats
  const approvalRate = Math.round(stats.overall_approval_rate * 100)

  // Doughnut: approved vs rejected
  new Chart(document.getElementById('chart-overall').getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Approved', 'Rejected'],
      datasets: [{
        data: [approvalRate, 100 - approvalRate],
        backgroundColor: [CHART_COLORS.green, '#e5e7eb'],
        borderWidth: 0,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' },
        tooltip: { callbacks: { label: ctx => ctx.label + ': ' + ctx.raw + '%' } }
      },
      cutout: '65%'
    }
  })

  // Score distribution (synthetic histogram bins)
  const bins = data.score_distribution || [3, 8, 15, 22, 26, 18, 6, 2]
  const binLabels = ['0-12', '13-25', '26-37', '38-50', '51-62', '63-75', '76-87', '88-100']

  new Chart(document.getElementById('chart-score-dist').getContext('2d'), {
    type: 'bar',
    data: {
      labels: binLabels,
      datasets: [{
        label: 'Applications (%)',
        data: bins,
        backgroundColor: bins.map((_, i) => i <= 2 ? CHART_COLORS.red : i <= 4 ? CHART_COLORS.orange : CHART_COLORS.green),
        borderRadius: 4,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { title: { display: true, text: '% of Applications' }, grid: { color: '#f3f4f6' } },
        x: { title: { display: true, text: 'Score Range' }, grid: { display: false } }
      }
    }
  })
}

// ── Synthetic fallback data ───────────────────────────────────
function getSyntheticData() {
  return {
    models: {
      logistic_regression: {
        gender: { disparate_impact: 0.91, statistical_parity_difference: -0.07, equal_opportunity_difference: -0.06 },
        location: { disparate_impact: 0.63, statistical_parity_difference: -0.19, equal_opportunity_difference: -0.16 },
        device: { disparate_impact: 0.58, statistical_parity_difference: -0.24, equal_opportunity_difference: -0.21 }
      },
      random_forest: {
        gender: { disparate_impact: 0.89, statistical_parity_difference: -0.08, equal_opportunity_difference: -0.07 },
        location: { disparate_impact: 0.61, statistical_parity_difference: -0.21, equal_opportunity_difference: -0.18 },
        device: { disparate_impact: 0.55, statistical_parity_difference: -0.26, equal_opportunity_difference: -0.22 }
      },
      gradient_boosting: {
        gender: { disparate_impact: 0.87, statistical_parity_difference: -0.09, equal_opportunity_difference: -0.08 },
        location: { disparate_impact: 0.59, statistical_parity_difference: -0.23, equal_opportunity_difference: -0.20 },
        device: { disparate_impact: 0.53, statistical_parity_difference: -0.28, equal_opportunity_difference: -0.25 }
      }
    },
    approval_rates: {
      by_location: { urban: 0.68, rural: 0.42 },
      by_gender: { male: 0.61, female: 0.54 },
      by_device: { feature_phone: 0.32, budget: 0.48, mid: 0.63, high_end: 0.74 }
    },
    feature_importance: [
      { feature: 'Repayment Rate', importance: 0.28, is_bias_flagged: false },
      { feature: 'Monthly Income', importance: 0.22, is_bias_flagged: false },
      { feature: 'Account Age', importance: 0.14, is_bias_flagged: false },
      { feature: 'Device Type', importance: 0.11, is_bias_flagged: true },
      { feature: 'M-Pesa Transactions', importance: 0.10, is_bias_flagged: false },
      { feature: 'Location Type', importance: 0.07, is_bias_flagged: true },
      { feature: 'Avg Transaction Amount', importance: 0.05, is_bias_flagged: false },
      { feature: 'Gender', importance: 0.03, is_bias_flagged: true },
    ],
    dataset_stats: { total_applications: 10000, overall_approval_rate: 0.572 },
    score_distribution: [2, 7, 14, 23, 28, 17, 7, 2]
  }
}
