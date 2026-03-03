function ScoreRow({ label, value }) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-900/70 px-4 py-3">
      <span className="text-sm text-slate-300">{label}</span>
      <span className="font-semibold text-slate-100">{value.toFixed(4)}</span>
    </div>
  );
}

export default function ResultDisplay({ result }) {
  if (!result) {
    return (
      <div className="rounded-2xl border border-slate-700/80 bg-slate-900/50 p-6 text-sm text-slate-400">
        Submit text and audio to see burnout analysis results.
      </div>
    );
  }

  const highRisk = result.burnoutPrediction === 'High';

  return (
    <div className="space-y-3 rounded-2xl border border-slate-700/80 bg-slate-900/70 p-6">
      <ScoreRow label="Text burnout score" value={result.textBurnoutScore} />
      <ScoreRow label="Voice burnout score" value={result.voiceBurnoutScore} />
      <ScoreRow label="Final burnout score" value={result.finalBurnoutScore} />

      <div
        className={`mt-3 rounded-lg border px-4 py-3 text-sm font-semibold ${
          highRisk
            ? 'border-rose-500/40 bg-rose-500/10 text-rose-300'
            : 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300'
        }`}
      >
        Burnout prediction: {result.burnoutPrediction}
      </div>
    </div>
  );
}
