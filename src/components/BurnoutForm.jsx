import { useRef } from 'react';

export default function BurnoutForm({
  text,
  onTextChange,
  onAudioChange,
  audioFile,
  onSubmit,
  isLoading,
}) {
  const fileInputRef = useRef(null);

  return (
    <form onSubmit={onSubmit} className="space-y-5">
      <div>
        <label htmlFor="text-input" className="mb-2 block text-sm font-medium text-slate-200">
          Text input
        </label>
        <textarea
          id="text-input"
          value={text}
          onChange={(event) => onTextChange(event.target.value)}
          placeholder="Describe how you've been feeling recently..."
          rows={6}
          className="w-full resize-none rounded-xl border border-slate-700 bg-slate-900/80 px-4 py-3 text-slate-100 outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-400/40"
          disabled={isLoading}
          required
        />
      </div>

      <div>
        <label htmlFor="audio-input" className="mb-2 block text-sm font-medium text-slate-200">
          Audio upload (.wav)
        </label>
        <input
          ref={fileInputRef}
          id="audio-input"
          type="file"
          accept=".wav,audio/wav"
          className="block w-full cursor-pointer rounded-xl border border-dashed border-slate-600 bg-slate-900/80 px-4 py-3 text-sm text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-indigo-500 file:px-3 file:py-2 file:text-sm file:font-medium file:text-white hover:border-indigo-400"
          onChange={(event) => onAudioChange(event.target.files?.[0] || null)}
          disabled={isLoading}
          required
        />
        <p className="mt-2 text-xs text-slate-400">
          {audioFile ? `Selected file: ${audioFile.name}` : 'No file selected.'}
        </p>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="inline-flex w-full items-center justify-center rounded-xl bg-indigo-500 px-5 py-3 font-semibold text-white shadow-md shadow-indigo-500/20 transition hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isLoading ? 'Analyzing...' : 'Detect Burnout'}
      </button>
    </form>
  );
}
