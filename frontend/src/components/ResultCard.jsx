const scoreRowStyles =
  'flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-4 py-3';

const normalizePrediction = (prediction) => {
  if (typeof prediction === 'string') {
    const lowered = prediction.toLowerCase();
    if (lowered === 'high' || lowered === 'low') {
      return lowered;
    }
  }

  return Number(prediction) >= 0.5 || Number(prediction) === 1 ? 'high' : 'low';
};

const formatScore = (score) => Number(score).toFixed(3);

const ResultCard = ({ result }) => {
  const prediction = normalizePrediction(result.burnout_prediction);
  const predictionStyles =
    prediction === 'high'
      ? 'bg-red-100 text-red-700 ring-red-200'
      : 'bg-emerald-100 text-emerald-700 ring-emerald-200';

  return (
    <section className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">Results</h2>

      <div className={scoreRowStyles}>
        <span className="text-slate-600">Text Burnout Score</span>
        <strong className="font-semibold text-slate-900">{formatScore(result.text_score)}</strong>
      </div>

      <div className={scoreRowStyles}>
        <span className="text-slate-600">Voice Burnout Score</span>
        <strong className="font-semibold text-slate-900">{formatScore(result.voice_score)}</strong>
      </div>

      <div className={scoreRowStyles}>
        <span className="text-slate-600">Final Burnout Score</span>
        <strong className="font-semibold text-slate-900">{formatScore(result.final_score)}</strong>
      </div>

      <div className="mt-2 flex items-center justify-between">
        <span className="text-sm uppercase tracking-wide text-slate-500">Prediction</span>
        <span className={`rounded-full px-3 py-1 text-sm font-semibold ring-1 ${predictionStyles}`}>
          {prediction === 'high' ? 'High Burnout Risk' : 'Low Burnout Risk'}
        </span>
      </div>
    </section>
  );
};

export default ResultCard;
