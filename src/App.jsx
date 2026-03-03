import { useState } from 'react';
import BurnoutForm from './components/BurnoutForm';
import ResultDisplay from './components/ResultDisplay';
import Spinner from './components/Spinner';
import { predictBurnout } from './api';

export default function App() {
  const [text, setText] = useState('');
  const [audioFile, setAudioFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setIsLoading(true);
    setError('');

    try {
      const response = await predictBurnout({ text, audioFile });
      setResult(response);
    } catch (requestError) {
      setResult(null);
      setError(requestError.message || 'Something went wrong while processing your request.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 px-4 py-12 text-slate-100">
      <div className="mx-auto max-w-5xl">
        <header className="mb-10 text-center">
          <p className="mb-3 inline-flex rounded-full border border-indigo-400/30 bg-indigo-500/10 px-4 py-1 text-xs uppercase tracking-widest text-indigo-300">
            Multimodal Burnout Detection
          </p>
          <h1 className="text-4xl font-bold tracking-tight text-white">Aurevia</h1>
          <p className="mx-auto mt-3 max-w-2xl text-slate-400">
            Analyze emotional strain from both written language and voice cues to estimate burnout risk.
          </p>
        </header>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-slate-700/80 bg-slate-800/30 p-6 shadow-glow backdrop-blur">
            <h2 className="mb-5 text-lg font-semibold">Input</h2>
            <BurnoutForm
              text={text}
              onTextChange={setText}
              onAudioChange={setAudioFile}
              audioFile={audioFile}
              onSubmit={handleSubmit}
              isLoading={isLoading}
            />
          </div>

          <div className="space-y-4 rounded-2xl border border-slate-700/80 bg-slate-800/30 p-6 backdrop-blur">
            <h2 className="text-lg font-semibold">Results</h2>
            {isLoading && <Spinner />}
            {error && (
              <div className="rounded-lg border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
                {error}
              </div>
            )}
            {!isLoading && !error && <ResultDisplay result={result} />}
          </div>
        </section>
      </div>
    </main>
  );
}
