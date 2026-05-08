import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertCircle, TrendingUp, Users, DollarSign, Activity } from 'lucide-react';

const CreditScoringDashboard = () => {
  const [selectedFeatures, setSelectedFeatures] = useState({
    age: 30,
    monthly_income: 50000,
    mpesa_transactions: 25,
    account_age: 12,
    previous_loans: 2,
    repayment_rate: 0.9,
    location_type: 'Urban',
    gender: 'M',
    device_type: 'Mid_Range_Smartphone',
    education: 'Diploma'
  });

  const [creditScore, setCreditScore] = useState(0);
  const [loanApproval, setLoanApproval] = useState(false);
  const [biasMetrics, setBiasMetrics] = useState({});

  // Simulated data for bias analysis
  const locationBiasData = [
    { location: 'Urban', approvalRate: 0.68, avgScore: 62 },
    { location: 'Rural', approvalRate: 0.52, avgScore: 54 }
  ];

  const genderBiasData = [
    { gender: 'Male', approvalRate: 0.63, avgScore: 59 },
    { gender: 'Female', approvalRate: 0.58, avgScore: 57 }
  ];

  const deviceBiasData = [
    { device: 'Feature Phone', approvalRate: 0.42, count: 1200 },
    { device: 'Budget Smartphone', approvalRate: 0.56, count: 3500 },
    { device: 'Mid Range', approvalRate: 0.65, count: 4200 },
    { device: 'High End', approvalRate: 0.73, count: 1100 }
  ];

  const featureImportance = [
    { feature: 'Monthly Income', importance: 0.25 },
    { feature: 'Repayment Rate', importance: 0.22 },
    { feature: 'Account Age', importance: 0.15 },
    { feature: 'Location Type', importance: 0.12 },
    { feature: 'M-Pesa Transactions', importance: 0.10 },
    { feature: 'Device Type', importance: 0.08 },
    { feature: 'Previous Loans', importance: 0.05 },
    { feature: 'Age', importance: 0.03 }
  ];

  const fairnessMetrics = [
    { metric: 'Disparate Impact (Location)', value: 0.76, threshold: 0.80, status: 'fail' },
    { metric: 'Disparate Impact (Gender)', value: 0.92, threshold: 0.80, status: 'pass' },
    { metric: 'Statistical Parity Diff', value: 0.16, threshold: 0.10, status: 'fail' },
    { metric: 'Equal Opportunity Diff', value: 0.08, threshold: 0.10, status: 'pass' }
  ];

  // Calculate credit score based on selected features
  useEffect(() => {
    let score = 50; // Base score

    // Income contribution
    score += (selectedFeatures.monthly_income / 10000) * 5;
    
    // Account age contribution
    score += (selectedFeatures.account_age / 60) * 10;
    
    // Repayment history
    score += selectedFeatures.repayment_rate * 15;
    
    // Transaction activity
    score += (selectedFeatures.mpesa_transactions / 50) * 5;
    
    // Previous loans (small contribution)
    score += selectedFeatures.previous_loans * 1;

    // Bias factors
    const locationPenalty = selectedFeatures.location_type === 'Rural' ? -8 : 0;
    score += locationPenalty;

    const devicePenalty = {
      'Feature_Phone': -6,
      'Budget_Smartphone': -3,
      'Mid_Range_Smartphone': 0,
      'High_End_Smartphone': 2
    }[selectedFeatures.device_type] || 0;
    score += devicePenalty;

    const genderBias = selectedFeatures.gender === 'F' ? -2 : 1;
    score += genderBias;

    // Education bonus
    const educationBonus = {
      'Primary': -2,
      'Secondary': 0,
      'Certificate': 2,
      'Diploma': 4,
      'Degree': 6,
      'Postgraduate': 8
    }[selectedFeatures.education] || 0;
    score += educationBonus;

    // Clip to 0-100
    score = Math.max(0, Math.min(100, score));
    
    setCreditScore(Math.round(score));
    setLoanApproval(score >= 55);

    // Calculate bias impact
    const withoutBias = score - locationPenalty - devicePenalty - genderBias;
    setBiasMetrics({
      totalBias: score - withoutBias,
      locationImpact: locationPenalty,
      deviceImpact: devicePenalty,
      genderImpact: genderBias
    });
  }, [selectedFeatures]);

  const COLORS = ['#10b981', '#ef4444', '#3b82f6', '#f59e0b'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-xl p-6 mb-6">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Digital Credit Scoring Bias Audit Dashboard
          </h1>
          <p className="text-slate-600">
            Auditing Algorithmic Bias in Digital Lending Using Alternative Financial Data
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Credit Score</p>
                <p className="text-4xl font-bold mt-2">{creditScore}</p>
              </div>
              <Activity className="w-12 h-12 text-blue-200" />
            </div>
          </div>

          <div className={`rounded-lg shadow-lg p-6 text-white ${loanApproval ? 'bg-gradient-to-br from-green-500 to-green-600' : 'bg-gradient-to-br from-red-500 to-red-600'}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm opacity-90">Loan Status</p>
                <p className="text-2xl font-bold mt-2">{loanApproval ? 'Approved' : 'Rejected'}</p>
              </div>
              <TrendingUp className="w-12 h-12 opacity-80" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Bias Impact</p>
                <p className="text-4xl font-bold mt-2">{biasMetrics.totalBias?.toFixed(1)}</p>
              </div>
              <AlertCircle className="w-12 h-12 text-purple-200" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm">Sample Size</p>
                <p className="text-4xl font-bold mt-2">15K</p>
              </div>
              <Users className="w-12 h-12 text-orange-200" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Credit Score Simulator */}
          <div className="bg-white rounded-lg shadow-xl p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Credit Score Simulator</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Age: {selectedFeatures.age}
                </label>
                <input
                  type="range"
                  min="18"
                  max="65"
                  value={selectedFeatures.age}
                  onChange={(e) => setSelectedFeatures({...selectedFeatures, age: parseInt(e.target.value)})}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Monthly Income (KES): {selectedFeatures.monthly_income.toLocaleString()}
                </label>
                <input
                  type="range"
                  min="5000"
                  max="200000"
                  step="5000"
                  value={selectedFeatures.monthly_income}
                  onChange={(e) => setSelectedFeatures({...selectedFeatures, monthly_income: parseInt(e.target.value)})}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  M-Pesa Transactions/Month: {selectedFeatures.mpesa_transactions}
                </label>
                <input
                  type="range"
                  min="1"
                  max="100"
                  value={selectedFeatures.mpesa_transactions}
                  onChange={(e) => setSelectedFeatures({...selectedFeatures, mpesa_transactions: parseInt(e.target.value)})}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Account Age (months): {selectedFeatures.account_age}
                </label>
                <input
                  type="range"
                  min="1"
                  max="60"
                  value={selectedFeatures.account_age}
                  onChange={(e) => setSelectedFeatures({...selectedFeatures, account_age: parseInt(e.target.value)})}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Repayment Rate: {(selectedFeatures.repayment_rate * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={selectedFeatures.repayment_rate}
                  onChange={(e) => setSelectedFeatures({...selectedFeatures, repayment_rate: parseFloat(e.target.value)})}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Location Type</label>
                <select
                  value={selectedFeatures.location_type}
                  onChange={(e) => setSelectedFeatures({...selectedFeatures, location_type: e.target.value})}
                  className="w-full p-2 border border-slate-300 rounded-md"
                >
                  <option value="Urban">Urban</option>
                  <option value="Rural">Rural</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Gender</label>
                <select
                  value={selectedFeatures.gender}
                  onChange={(e) => setSelectedFeatures({...selectedFeatures, gender: e.target.value})}
                  className="w-full p-2 border border-slate-300 rounded-md"
                >
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Device Type</label>
                <select
                  value={selectedFeatures.device_type}
                  onChange={(e) => setSelectedFeatures({...selectedFeatures, device_type: e.target.value})}
                  className="w-full p-2 border border-slate-300 rounded-md"
                >
                  <option value="Feature_Phone">Feature Phone</option>
                  <option value="Budget_Smartphone">Budget Smartphone</option>
                  <option value="Mid_Range_Smartphone">Mid Range Smartphone</option>
                  <option value="High_End_Smartphone">High End Smartphone</option>
                </select>
              </div>
            </div>

            <div className="mt-6 p-4 bg-slate-50 rounded-lg">
              <h3 className="font-semibold text-slate-900 mb-2">Bias Breakdown</h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Location Impact:</span>
                  <span className={biasMetrics.locationImpact < 0 ? 'text-red-600' : 'text-green-600'}>
                    {biasMetrics.locationImpact?.toFixed(1)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Device Impact:</span>
                  <span className={biasMetrics.deviceImpact < 0 ? 'text-red-600' : 'text-green-600'}>
                    {biasMetrics.deviceImpact?.toFixed(1)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Gender Impact:</span>
                  <span className={biasMetrics.genderImpact < 0 ? 'text-red-600' : 'text-green-600'}>
                    {biasMetrics.genderImpact?.toFixed(1)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Feature Importance */}
          <div className="bg-white rounded-lg shadow-xl p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Feature Importance Analysis</h2>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={featureImportance} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="feature" type="category" width={140} />
                <Tooltip />
                <Bar dataKey="importance" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Location Bias Analysis */}
          <div className="bg-white rounded-lg shadow-xl p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Location-Based Bias</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={locationBiasData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="location" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="approvalRate" fill="#10b981" name="Approval Rate" />
                <Bar dataKey="avgScore" fill="#3b82f6" name="Avg Credit Score" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-800">
                <strong>⚠️ Bias Detected:</strong> Rural applicants have 23% lower approval rate
              </p>
            </div>
          </div>

          {/* Device Type Bias */}
          <div className="bg-white rounded-lg shadow-xl p-6">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Device Type Impact</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={deviceBiasData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="device" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="approvalRate" fill="#f59e0b" name="Approval Rate" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded">
              <p className="text-sm text-orange-800">
                <strong>⚠️ Proxy Discrimination:</strong> Device type serves as proxy for socioeconomic status
              </p>
            </div>
          </div>
        </div>

        {/* Fairness Metrics */}
        <div className="bg-white rounded-lg shadow-xl p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Fairness Metrics Evaluation</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {fairnessMetrics.map((metric, idx) => (
              <div key={idx} className="border border-slate-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-slate-700 mb-2">{metric.metric}</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-slate-900">{metric.value.toFixed(2)}</span>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    metric.status === 'pass' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {metric.status === 'pass' ? 'PASS' : 'FAIL'}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-2">Threshold: {metric.threshold.toFixed(2)}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreditScoringDashboard;
