import { useState } from 'react';
import { predictBurnout } from './api';
import Loader from './components/Loader';
import ResultCard from './components/ResultCard';

const App = () => {
  const [text, setText] = useState('');
  const [audioFile, setAudioFile] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const onSubmit = async (event) => {
    event.preventDefault();

    if (!text.trim()) {
      setError('Please enter text input before submitting.');
      return;
    }

    if (!audioFile) {
      setError('Please upload a .wav audio file before submitting.');
      return;
    }

    setError('');
    setResult(null);
    setIsLoading(true);

    try {
      const response = await predictBurnout({ text: text.trim(), audioFile });
      setResult(response);
    } catch (err) {
      setError(err.message || 'Unable to complete burnout analysis right now.');
    } finally {
      setIsLoading(false);
    }
  };

  const onFileChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      setAudioFile(null);
      return;
    }

    const isWav = file.type === 'audio/wav' || file.name.toLowerCase().endsWith('.wav');
    if (!isWav) {
      setAudioFile(null);
      setError('Only .wav files are supported by the backend.');
      event.target.value = '';
      return;
    }

    setError('');
    setAudioFile(file);
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-aurora-50 px-6 py-10 text-slate-900">
      <div className="mx-auto w-full max-w-3xl space-y-8">
        <header className="space-y-3 text-center">
          <p className="inline-flex rounded-full bg-aurora-100 px-3 py-1 text-xs font-semibold uppercase tracking-widest text-aurora-700">
            Aurevia
          </p>
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Multimodal Burnout Detection</h1>
          <p className="text-sm text-slate-600 sm:text-base">
            Submit reflective text and a voice sample to estimate burnout risk from language and vocal patterns.
          </p>
        </header>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <form className="space-y-6" onSubmit={onSubmit}>
            <div className="space-y-2">
              <label htmlFor="text-input" className="text-sm font-medium text-slate-700">
                Text Input
              </label>
              <textarea
                id="text-input"
                rows={6}
                value={text}
                onChange={(event) => setText(event.target.value)}
                placeholder="Describe how you are feeling lately..."
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none transition focus:border-aurora-500 focus:ring-2 focus:ring-aurora-100"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="audio-upload" className="text-sm font-medium text-slate-700">
                Audio Upload (.wav)
              </label>
              <input
                id="audio-upload"
                type="file"
                accept=".wav,audio/wav"
                onChange={onFileChange}
                className="block w-full cursor-pointer rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-700 file:mr-4 file:rounded-lg file:border-0 file:bg-aurora-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-aurora-700 hover:file:bg-aurora-50"
              />
              {audioFile && <p className="text-xs text-slate-500">Selected: {audioFile.name}</p>}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-xl bg-aurora-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-aurora-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoading ? 'Analyzing...' : 'Analyze Burnout Risk'}
            </button>
          </form>

          <div className="mt-6 min-h-7">
            {isLoading && <Loader />}
            {error && !isLoading && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
          </div>
        </section>

        {result && !isLoading && <ResultCard result={result} />}
      </div>
    </main>
  );
};

export default App;
